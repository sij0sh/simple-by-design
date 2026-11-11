"""POSIX persistence owner: task paths, kernel locks, atomic JSON replacement."""

from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import stat
import tempfile
import time

from . import ledger


def decode(raw):
    """Reject duplicate keys and non-JSON constants instead of silently normalizing."""
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ledger.LedgerError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def constant(value):
        raise ledger.LedgerError(f"invalid JSON constant: {value}")

    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)
    except (ValueError, RecursionError) as error:
        raise ledger.LedgerError(f"invalid JSON: {error}") from error


class Store:
    def __init__(self, directory, lock_timeout=5.0):
        self.directory = Path(directory)
        self.lock_timeout = lock_timeout

    def _path(self, task_id):
        ledger.identifier(task_id)
        ledger.require(not self.directory.is_symlink(), "state directory must not be a symlink")
        return self.directory / f"{task_id}.json"

    @staticmethod
    def _open(path, flags):
        fd = os.open(path, flags | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600)
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            os.close(fd)
            raise ledger.LedgerError(f"not a regular file: {path}")
        return fd

    @contextmanager
    def _lock(self, task_id):
        self._path(task_id)
        self.directory.mkdir(parents=True, exist_ok=True)
        fd = self._open(self.directory / f".{task_id}.lock", os.O_CREAT | os.O_RDWR)
        deadline = time.monotonic() + self.lock_timeout
        try:
            while True:
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    if time.monotonic() >= deadline:
                        raise ledger.LedgerError(f"timed out waiting for task lock: {task_id}")
                    time.sleep(0.01)
            yield
        finally:
            # Never unlink lock files: waiters must continue using the same inode.
            os.close(fd)

    def load(self, task_id):
        path = self._path(task_id)
        with os.fdopen(self._open(path, os.O_RDONLY), encoding="utf-8") as stream:
            document = decode(stream.read())
        ledger.require(isinstance(document, dict) and document.get("task_id") == task_id,
                       "state task ID does not match filename")
        ledger.project(document)
        return document

    def show(self, task_id, at=None, history=False):
        document = self.load(task_id)
        if at is not None:
            ledger.require(type(at) is int and 1 <= at <= len(document["events"]), "snapshot revision out of range")
            document["events"] = document["events"][:at]
        view = ledger.project(document)
        if history:
            view["events"] = document["events"]
        return view

    def _write(self, path, document):
        # Validate/encode before opening a temporary file; original stays untouched on failure.
        raw = json.dumps(document, ensure_ascii=False, allow_nan=False, indent=2) + "\n"
        fd, temporary = tempfile.mkstemp(prefix=f".{path.stem}.", suffix=".tmp", dir=self.directory)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, path)
            directory_fd = os.open(self.directory, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def new(self, task_id, task):
        document = ledger.create(task_id, task)
        with self._lock(task_id):
            path = self._path(task_id)
            ledger.require(not os.path.lexists(path), f"task already exists: {task_id}")
            self._write(path, document)
        return ledger.project(document)

    def record(self, task_id, data, at, finish=False):
        with self._lock(task_id):
            document = self.load(task_id)
            updated = ledger.append(document, data, at, finish=finish)
            self._write(self._path(task_id), updated)
        return ledger.project(updated)
