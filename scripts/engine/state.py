"""POSIX checkpoint owner: safe paths, writer mutex and atomic publication.

The mutex protects CLI transactions only, not the agent's other tools.
"""

from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import stat
import tempfile
import time

from . import router
from .router import DispatchError, require


def decode(raw):
    """Reject duplicate keys and non-JSON constants."""
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def constant(value):
        raise DispatchError(f"invalid JSON constant: {value}")

    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)
    except (ValueError, RecursionError) as error:
        raise DispatchError(f"invalid JSON: {error}") from error


class Store:
    def __init__(self, root, lock_timeout=5.0):
        self.root = Path(root).resolve()
        self.directory = self.root / ".agents"
        self.path = self.directory / "decision.json"
        self.legacy = self.directory / "sbd-adaptive" / "run.json"
        self.lock_timeout = lock_timeout

    def _directories(self, directory, create=False):
        """Reject symlinks in every managed ancestor below the chosen project root."""
        current = self.root
        for part in directory.relative_to(self.root).parts:
            current = current / part
            if create:
                try:
                    current.mkdir(mode=0o700)
                except FileExistsError:
                    pass
            try:
                mode = current.lstat().st_mode
            except FileNotFoundError:
                if not create:
                    return
                raise
            require(stat.S_ISDIR(mode), f"not a real directory: {current}")
            if create:
                # Also sync existing names: a prior mkdir may have been interrupted
                # before its parent sync. Files inside alone cannot make that durable.
                self._sync_directory(current.parent)

    @staticmethod
    def _sync_directory(path):
        fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    @staticmethod
    def _regular(path):
        try:
            mode = path.lstat().st_mode
        except FileNotFoundError:
            return
        require(stat.S_ISREG(mode), f"not a regular file: {path}")

    @staticmethod
    def _open(path, flags):
        fd = os.open(path, flags | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600)
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            os.close(fd)
            raise DispatchError(f"not a regular file: {path}")
        return fd

    @contextmanager
    def _lock(self):
        self._directories(self.directory, create=True)
        fd = self._open(self.directory / ".decision.lock", os.O_CREAT | os.O_RDWR)
        deadline = time.monotonic() + self.lock_timeout
        try:
            while True:
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    if time.monotonic() >= deadline:
                        raise DispatchError("timed out waiting for checkpoint writer; retry")
                    time.sleep(0.01)
            yield
        finally:
            # Do not unlink: all waiters must continue using the same inode.
            os.close(fd)

    def _read(self, path):
        self._directories(path.parent)
        with os.fdopen(self._open(path, os.O_RDONLY), encoding="utf-8") as stream:
            return stream.read()

    def load(self):
        return router.validate(decode(self._read(self.path)))

    def _load_optional(self):
        try:
            return self.load()
        except FileNotFoundError:
            if os.path.lexists(self.legacy):
                raise DispatchError(
                    "legacy checkpoint at .agents/sbd-adaptive/run.json; "
                    "move .agents/sbd-adaptive aside, then start with --request")
            return None

    def _atomic(self, path, raw):
        self._directories(path.parent, create=True)
        self._regular(path)
        fd, temporary = tempfile.mkstemp(prefix=f".{path.stem}.", suffix=".tmp", dir=path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, path)
            self._sync_directory(path.parent)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def _write(self, document):
        router.validate(document)
        self._atomic(self.path, json.dumps(document, ensure_ascii=False, allow_nan=False, indent=2) + "\n")

    @staticmethod
    def _artifact(document):
        candidate, review = document["candidate"], document["review"]
        lines = ["# Solution design", "", "## Request", "", document["request"], "",
                 "## Summary", "", candidate["summary"], "", "## Criteria", ""]
        lines += [f"- {item}" for item in candidate["criteria"]]
        lines += ["", "## Decisions", ""]
        for decision in candidate["decisions"]:
            lines += [f"### {decision['id']}", ""]
            lines += [f"- **{key.capitalize()}:** {decision[key]}"
                      for key in ("choice", "basis", "alternative", "tradeoff", "revisit")]
            lines.append("")
        if not candidate["decisions"]:
            lines += ["None consequential.", ""]
        if document.get("resolutions"):
            lines += ["## Resolutions", ""]
            lines += [f"- ({item['type']}) {item['question']} → {item['answer']} (basis: {item['basis']})"
                      for item in document["resolutions"]]
            lines.append("")
        lines += ["## Review", ""]
        lines += [f"- **{key.capitalize()}:** {review[key]}" for key in ("pair", "defeater", "decision", "basis")]
        lines += ["", "Design complete, not implementation. Verification/review claims are supplied "
                  "by the agent, not independently checked by the CLI.", ""]
        return "\n".join(lines)

    def _finish(self, document):
        """Replay a durable passing review without publishing a second artifact."""
        path = self.root / router.artifact_path(document)
        expected = self._artifact(document)
        try:
            existing = self._read(path)
        except FileNotFoundError:
            pass
        else:
            require(existing == expected, f"artifact exists with different content: {path}")
        # An earlier replace might have succeeded before a directory-fsync failure.
        # Publish the same bytes to establish durability before marking complete.
        self._atomic(path, expected)
        complete = {"schema_version": 3, "phase": "complete", "ticket": document["ticket"]}
        self._write(complete)
        return complete

    def start(self, request):
        router.require(router.text(request), "--request must be nonempty text")
        # Fail on legacy state before creating the writer lock or state directory.
        self._load_optional()
        with self._lock():
            current = self._load_optional()
            if current is not None and current["phase"] != "complete":
                require(current["request"] == request,
                        "a different request is active; resume with the bare invocation")
                return self._finish(current) if current["phase"] == "publishing" else current
            document = router.new(request)
            self._write(document)
            return document

    def resume(self):
        # A no-state usage query must not create any project files.
        current = self._load_optional()
        if current is None:
            return None
        with self._lock():
            current = self.load()
            return self._finish(current) if current["phase"] == "publishing" else current

    def submit(self, ticket, result):
        # Missing state is an error, not an implicit new run.
        require(self._load_optional() is not None, "no active run; start with --request TEXT")
        with self._lock():
            current = self.load()
            require(current["ticket"] == ticket and current["phase"] != "complete",
                    "stale or duplicate ticket; resume with the bare invocation")
            if current["phase"] == "publishing":
                require(result == {"status": "pass", **current["review"]},
                        "publication pending; resume or replay the exact passing result")
                return self._finish(current)
            updated = router.advance(current, result)
            self._write(updated)
            return self._finish(updated) if updated["phase"] == "publishing" else updated
