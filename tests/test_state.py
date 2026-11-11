import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from support import ROOT, evidence, ledger, review, task
from engine.state import Store, decode

CLI = ROOT / "scripts" / "sbd.py"


class StateTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.directory = self.root / ".agents" / "sbd-adaptive"
        self.store = Store(self.directory)
        self.store.new("task", task())

    def test_new_refuses_existing_task_and_read_never_creates_missing_state(self):
        before = (self.directory / "task.json").read_bytes()
        with self.assertRaisesRegex(ledger.LedgerError, "already exists"):
            self.store.new("task", task())
        self.assertEqual((self.directory / "task.json").read_bytes(), before)
        missing = Store(self.root / "missing")
        with self.assertRaises(FileNotFoundError):
            missing.show("task")
        self.assertFalse(missing.directory.exists())

    def test_resume_history_and_historical_snapshot_survive_new_store_instance(self):
        self.store.record("task", evidence(), at=1)
        self.store.record("task", evidence("second"), at=2)
        resumed = Store(self.directory)
        self.assertEqual(resumed.show("task")["revision"], 3)
        snapshot = resumed.show("task", at=2, history=True)
        self.assertEqual(snapshot["revision"], 2)
        self.assertEqual(len(snapshot["events"]), 2)
        self.assertNotIn("second", snapshot["records"])
        for at in (0, -1, 4, True):
            with self.assertRaises(ledger.LedgerError):
                resumed.show("task", at=at)

    def test_stale_and_invalid_writes_leave_bytes_untouched(self):
        self.store.record("task", evidence(), at=1)
        path = self.directory / "task.json"
        before = path.read_bytes()
        for operation in (lambda: self.store.record("task", evidence("other"), at=1),
                          lambda: self.store.record("task", {"type": "bad"}, at=2),
                          lambda: self.store.record("task", review(2), at=2, finish=True)):
            with self.assertRaises(ledger.LedgerError):
                operation()
            self.assertEqual(path.read_bytes(), before)

    def test_replace_failure_keeps_old_document_and_cleans_temporary(self):
        path = self.directory / "task.json"
        before = path.read_bytes()
        with patch("engine.state.os.replace", side_effect=OSError("simulated interrupted replace")):
            with self.assertRaisesRegex(OSError, "interrupted"):
                self.store.record("task", evidence(), at=1)
        self.assertEqual(path.read_bytes(), before)
        self.assertFalse(list(self.directory.glob("*.tmp")))
        self.assertEqual(self.store.show("task")["revision"], 1)
        # The writer lock also released on failure.
        self.store.record("task", evidence(), at=1)

    def test_fsync_before_replace_failure_keeps_old_document(self):
        before = (self.directory / "task.json").read_bytes()
        with patch("engine.state.os.fsync", side_effect=OSError("simulated fsync failure")):
            with self.assertRaises(OSError):
                self.store.record("task", evidence(), at=1)
        self.assertEqual((self.directory / "task.json").read_bytes(), before)
        self.assertFalse(list(self.directory.glob("*.tmp")))

    def test_error_after_replace_requires_reload_not_assuming_rollback(self):
        fsync = os.fsync
        calls = 0

        def fail_directory(fd):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("directory sync failure after rename")
            return fsync(fd)

        with patch("engine.state.os.fsync", side_effect=fail_directory):
            with self.assertRaises(OSError):
                self.store.record("task", evidence(), at=1)
        self.assertEqual(self.store.show("task")["revision"], 2)
        with self.assertRaisesRegex(ledger.LedgerError, "stale"):
            self.store.record("task", evidence("retry"), at=1)

    def test_corruption_unsupported_schema_duplicate_keys_and_nan_fail_closed(self):
        path = self.directory / "task.json"
        valid = path.read_text()
        corruptions = ["{", "[]", valid.replace('"schema_version": 1', '"schema_version": 999'),
                       valid.replace('"schema_version": 1', '"schema_version": 1, "schema_version": 1'),
                       valid.replace('"schema_version": 1', '"schema_version": NaN'),
                       valid.replace('"task_id": "task"', '"task_id": "other"')]
        for raw in corruptions:
            with self.subTest(raw=raw):
                path.write_text(raw)
                with self.assertRaises(ledger.LedgerError):
                    self.store.show("task")
                with self.assertRaises(ledger.LedgerError):
                    self.store.record("task", evidence(), at=1)
                with self.assertRaises(ledger.LedgerError):
                    self.store.new("task", task())
                self.assertEqual(path.read_text(), raw)
        with self.assertRaises(ledger.LedgerError):
            decode('{"a":1,"a":2}')

    def test_task_ids_cannot_escape_directory(self):
        for key in ("../escape", "/tmp/escape", "x/y", "x\\y", ".", "..", "UPPER", "a" * 65, "", "café"):
            with self.subTest(key=key):
                with self.assertRaises(ledger.LedgerError):
                    self.store.new(key, task())

    def test_symlink_and_fifo_targets_and_locks_are_rejected_without_writes(self):
        outside = self.root / "outside"
        outside.write_text("do not change")
        (self.directory / "linked.json").symlink_to(outside)
        (self.directory / ".badlock.lock").symlink_to(outside)
        for action in (lambda: self.store.show("linked"),
                       lambda: self.store.new("linked", task()),
                       lambda: self.store.new("badlock", task())):
            with self.assertRaises((OSError, ledger.LedgerError)):
                action()
        self.assertEqual(outside.read_text(), "do not change")
        os.mkfifo(self.directory / "fifo.json")
        with self.assertRaises(ledger.LedgerError):
            self.store.show("fifo")
        alias = self.root / "alias"
        alias.symlink_to(self.directory, target_is_directory=True)
        with self.assertRaises(ledger.LedgerError):
            Store(alias).show("task")

    def test_private_file_permissions_and_ignored_leftover_temporary(self):
        self.assertEqual((self.directory / "task.json").stat().st_mode & 0o777, 0o600)
        (self.directory / ".task.dead.tmp").write_text("partial interrupted write")
        self.assertEqual(self.store.show("task")["revision"], 1)

    def test_two_cli_writers_same_expected_revision_only_one_commits(self):
        processes = []
        for key in ("one", "two"):
            process = subprocess.Popen([sys.executable, str(CLI), "--root", str(self.root), "record", "task", "--at", "1"],
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            processes.append(process)
            process.stdin.write(json.dumps(evidence(key)))
            process.stdin.close()
            process.stdin = None
        outcomes = [p.communicate(timeout=10) for p in processes]
        self.assertEqual(sorted(p.returncode for p in processes), [0, 2])
        self.assertTrue(any("stale revision" in stderr for _, stderr in outcomes))
        view = self.store.show("task", history=True)
        self.assertEqual(view["revision"], 2)
        self.assertEqual(len(view["records"]), 1)

    def test_lock_timeout_and_process_death_release_without_stale_timer(self):
        code = ("import fcntl,sys,time; f=open(sys.argv[1], 'r+'); "
                "fcntl.flock(f,fcntl.LOCK_EX); print('locked',flush=True); time.sleep(60)")
        process = subprocess.Popen([sys.executable, "-c", code, str(self.directory / ".task.lock")],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            self.assertEqual(process.stdout.readline().strip(), "locked")
            with self.assertRaisesRegex(ledger.LedgerError, "timed out"):
                Store(self.directory, lock_timeout=0.05).record("task", evidence(), at=1)
            process.kill()
            process.communicate(timeout=5)
            self.assertEqual(Store(self.directory, lock_timeout=0.2).record("task", evidence(), at=1)["revision"], 2)
        finally:
            if process.poll() is None:
                process.kill()
                process.communicate()


if __name__ == "__main__":
    unittest.main()
