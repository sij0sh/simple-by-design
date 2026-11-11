import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from support import CLI, REQUEST, CANDIDATE, PASS, NEED, BLOCKED, RESOLVED, DispatchError, Store
from engine.state import decode


def body(result):
    return {key: value for key, value in result.items() if key != "status"}


def artifact(root, state):
    return root / f".agents/artifacts/solution-design-{state['ticket']}.md"


class StateTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.store = Store(self.root)
        self.initial = self.store.start(REQUEST)
        self.path = self.store.path

    def submit(self, result):
        return self.store.submit(self.store.load()['ticket'], result)

    def test_start_resume_and_explicit_new_run_after_completion(self):
        self.assertEqual(self.path, self.root / '.agents/decision.json')
        self.assertEqual(Store(self.root).resume(), self.initial)
        self.assertEqual(self.store.start(REQUEST), self.initial)
        before = self.path.read_bytes()
        with self.assertRaisesRegex(DispatchError, 'different request'):
            self.store.start('New request')
        self.assertEqual(self.path.read_bytes(), before)
        review = self.submit(CANDIDATE)
        complete = self.submit(PASS)
        self.assertEqual(complete, {'schema_version': 3, 'phase': 'complete',
                                    'ticket': review['ticket']})
        self.assertEqual(Store(self.root).resume(), complete)
        path = artifact(self.root, complete)
        text = path.read_text()
        for value in (CANDIDATE['summary'], CANDIDATE['decisions'][0]['alternative'], PASS['defeater']):
            self.assertIn(value, text)
        self.assertIn(REQUEST, text)
        self.assertFalse((self.root / '.agents/sbd-adaptive').exists())
        new = self.store.start(REQUEST)  # Explicit --request is sufficient after DONE.
        self.assertNotEqual(new['ticket'], complete['ticket'])
        self.assertTrue(path.is_file())
        with self.assertRaisesRegex(DispatchError, 'duplicate'):
            self.store.submit(complete['ticket'], PASS)
        self.assertEqual(self.store.resume(), new)

    def test_missing_resume_creates_nothing_and_legacy_state_is_untouched(self):
        missing = self.root / 'other'
        missing.mkdir()
        self.assertIsNone(Store(missing).resume())
        self.assertEqual(list(missing.iterdir()), [])
        with self.assertRaises(DispatchError):
            Store(missing).submit('anything', CANDIDATE)
        legacy = self.path.parent / 'legacy.json'
        legacy.write_text('{"events": ["old data"]}')
        self.submit(CANDIDATE)
        self.submit(PASS)
        self.assertEqual(legacy.read_text(), '{"events": ["old data"]}')

    def test_blocked_resume_keeps_ticket_request_candidate_and_open(self):
        review = self.submit(CANDIDATE)
        self.submit(NEED)
        blocked = self.submit(BLOCKED)
        self.assertEqual(Store(self.root).resume(), blocked)
        self.assertEqual(blocked['candidate'], review['candidate'])
        self.assertEqual(blocked['open'], {**body(NEED), 'blocked_on': body(BLOCKED)})
        resolved = self.submit(RESOLVED)
        self.assertEqual(resolved['request'], REQUEST)
        self.assertEqual(resolved['phase'], 'draft')
        self.assertEqual(resolved['resolutions'][0]['answer'], 'Use English.')
        self.assertEqual(resolved['candidate'], review['candidate'])
        self.assertNotIn('open', resolved)
        with self.assertRaises(DispatchError):
            self.submit(PASS)

    def test_stale_invalid_duplicate_results_do_not_advance(self):
        review = self.submit(CANDIDATE)
        before = self.path.read_bytes()
        for ticket, result in ((self.initial['ticket'], CANDIDATE),
                               ('../escape', PASS), (review['ticket'], {'status': 'pass'})):
            with self.assertRaises(DispatchError):
                self.store.submit(ticket, result)
            self.assertEqual(self.path.read_bytes(), before)
        complete = self.submit(PASS)
        with self.assertRaisesRegex(DispatchError, 'duplicate'):
            self.store.submit(complete['ticket'], PASS)
        self.assertEqual(len(list((self.root / '.agents/artifacts').glob('*.md'))), 1)

    def test_replace_and_fsync_failure_preserve_old_checkpoint(self):
        before = self.path.read_bytes()
        for target in ('engine.state.os.replace', 'engine.state.os.fsync'):
            with patch(target, side_effect=OSError('interrupted write')):
                with self.assertRaises(OSError):
                    self.submit(CANDIDATE)
            self.assertEqual(self.path.read_bytes(), before)
            self.assertFalse(list(self.path.parent.glob('*.tmp')))
        self.submit(CANDIDATE)  # Lock released on error.

    def test_failure_after_checkpoint_replace_requires_reload(self):
        fsync, replace = os.fsync, os.replace
        replaced = False

        def after_replace(source, target):
            nonlocal replaced
            replace(source, target)
            replaced = True

        def fail_directory(fd):
            if replaced:
                raise OSError('directory sync failure after rename')
            return fsync(fd)

        with patch('engine.state.os.replace', side_effect=after_replace), \
                patch('engine.state.os.fsync', side_effect=fail_directory):
            with self.assertRaises(OSError):
                self.submit(CANDIDATE)
        self.assertEqual(self.store.resume()['phase'], 'review')
        with self.assertRaisesRegex(DispatchError, 'stale'):
            self.store.submit(self.initial['ticket'], CANDIDATE)

    def test_publication_failure_is_pending_not_done_and_exact_replay_finishes(self):
        review = self.submit(CANDIDATE)
        atomic = self.store._atomic

        def fail_artifact(path, raw):
            if path.suffix == '.md':
                raise OSError('publication failed')
            return atomic(path, raw)

        with patch.object(self.store, '_atomic', side_effect=fail_artifact):
            with self.assertRaisesRegex(OSError, 'publication'):
                self.submit(PASS)
        self.assertEqual(self.store.load()['phase'], 'publishing')
        with self.assertRaisesRegex(DispatchError, 'exact passing'):
            self.store.submit(review['ticket'], {**PASS, 'basis': 'different review'})
        complete = self.store.submit(review['ticket'], PASS)
        self.assertEqual(complete['phase'], 'complete')
        self.assertTrue(artifact(self.root, complete).exists())

    def test_crash_after_artifact_before_completion_recovers_on_bare_resume(self):
        self.submit(CANDIDATE)
        write = self.store._write

        def fail_complete(document):
            if document['phase'] == 'complete':
                raise OSError('crash before completion checkpoint')
            return write(document)

        with patch.object(self.store, '_write', side_effect=fail_complete):
            with self.assertRaises(OSError):
                self.submit(PASS)
        pending = self.store.load()
        self.assertEqual(pending['phase'], 'publishing')
        path = artifact(self.root, pending)
        before = path.read_bytes()
        self.assertEqual(Store(self.root).resume()['phase'], 'complete')
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(len(list((self.root / '.agents/artifacts').glob('*.md'))), 1)

    def test_failure_after_artifact_replace_resyncs_before_completing(self):
        self.submit(CANDIDATE)
        atomic = self.store._atomic

        def fail_after_publish(path, raw):
            atomic(path, raw)
            if path.suffix == '.md':
                raise OSError('directory sync may have failed')

        with patch.object(self.store, '_atomic', side_effect=fail_after_publish):
            with self.assertRaises(OSError):
                self.submit(PASS)
        with patch.object(self.store, '_atomic', wraps=atomic) as retried:
            self.store.resume()
        self.assertEqual([call.args[0].suffix for call in retried.call_args_list], ['.md', '.json'])

    def test_existing_conflicting_artifact_is_never_overwritten(self):
        review = self.submit(CANDIDATE)
        path = artifact(self.root, review)
        path.parent.mkdir()
        path.write_text('other content')
        with self.assertRaisesRegex(DispatchError, 'different content'):
            self.submit(PASS)
        self.assertEqual(path.read_text(), 'other content')
        self.assertEqual(self.store.load()['phase'], 'publishing')

    def test_corruption_fails_closed_for_reads_starts_and_submissions(self):
        valid = self.path.read_text()
        bad_values = ['{', '[]', valid.replace('"schema_version": 3', '"schema_version": 999'),
                      valid.replace('"schema_version": 3', '"schema_version": 3, "schema_version": 3'),
                      valid.replace('"schema_version": 3', '"schema_version": NaN'),
                      valid.replace('"phase": "draft"', '"phase": []'),
                      valid.replace('"schema_version": 3', '"schema_version": 2')]
        for raw in bad_values:
            self.path.write_text(raw)
            for action in (self.store.resume, lambda: self.store.start(REQUEST),
                           lambda: self.store.submit(self.initial['ticket'], CANDIDATE)):
                with self.assertRaises(DispatchError):
                    action()
                self.assertEqual(self.path.read_text(), raw)
        for raw in ('{"a":1,"a":2}', 'Infinity', 'NaN', '{'):
            with self.assertRaises(DispatchError):
                decode(raw)

    def test_managed_symlink_ancestors_and_nonregular_targets_are_rejected(self):
        outside = self.root / 'outside'
        outside.mkdir()
        root = self.root / 'project'
        root.mkdir()
        linked = root / '.agents'
        linked.symlink_to(outside, target_is_directory=True)
        for action in (Store(root).resume, lambda: Store(root).start(REQUEST)):
            with self.assertRaises(DispatchError):
                action()
        self.assertEqual(list(outside.iterdir()), [])
        target = self.root / 'outside-file'
        target.write_text('do not change')
        self.path.unlink()
        self.path.symlink_to(target)
        for action in (self.store.resume, lambda: self.store.start(REQUEST)):
            with self.assertRaises((OSError, DispatchError)):
                action()
        self.assertEqual(target.read_text(), 'do not change')
        self.path.unlink()
        os.mkfifo(self.path)
        with self.assertRaises(DispatchError):
            self.store.resume()

    def test_lock_and_artifact_symlinks_rejected(self):
        target = self.root / 'outside-file'
        target.write_text('safe')
        lock = self.path.parent / '.decision.lock'
        lock.unlink()
        lock.symlink_to(target)
        with self.assertRaises(OSError):
            self.submit(CANDIDATE)
        lock.unlink()
        review = self.submit(CANDIDATE)
        artifacts = self.root / '.agents/artifacts'
        artifacts.symlink_to(self.path.parent, target_is_directory=True)
        with self.assertRaises(DispatchError):
            self.submit(PASS)
        artifacts.unlink()
        artifacts.mkdir()
        artifact(self.root, review).symlink_to(target)
        with self.assertRaises(OSError):
            self.store.resume()
        self.assertEqual(target.read_text(), 'safe')

    def test_private_permissions_and_ignored_leftover_temporary(self):
        self.assertEqual(self.path.stat().st_mode & 0o777, 0o600)
        (self.path.parent / '.decision.dead.tmp').write_text('partial')
        self.assertEqual(self.store.resume(), self.initial)
        self.submit(CANDIDATE)
        complete = self.submit(PASS)
        self.assertEqual(artifact(self.root, complete).stat().st_mode & 0o777, 0o600)

    def test_created_directory_names_are_synced_even_on_retry(self):
        sync = self.store._sync_directory
        artifacts = self.root / '.agents/artifacts'
        # Simulate mkdir succeeding before its parent sync fails.
        artifacts.mkdir()
        with patch.object(self.store, '_sync_directory', wraps=sync) as calls:
            self.store._directories(artifacts, create=True)
        self.assertEqual([call.args[0] for call in calls.call_args_list],
                         [self.root, self.root / '.agents'])

    def test_concurrent_final_results_publish_exactly_once(self):
        self.submit(CANDIDATE)
        self.concurrent_submission(PASS)
        self.assertEqual(self.store.resume()['phase'], 'complete')
        self.assertEqual(len(list((self.root / '.agents/artifacts').glob('*.md'))), 1)

    def test_two_cli_writers_only_one_advances_the_ticket(self):
        self.concurrent_submission(CANDIDATE)
        self.assertEqual(self.store.load()['phase'], 'review')

    def test_legacy_location_and_schema_fail_closed(self):
        legacy_root = self.root / 'legacy-project'
        legacy_dir = legacy_root / '.agents/sbd-adaptive'
        legacy_dir.mkdir(parents=True)
        legacy = legacy_dir / 'run.json'
        legacy.write_text('{"schema_version": 2, "events": ["old"]}')
        for action in (Store(legacy_root).resume,
                       lambda: Store(legacy_root).start(REQUEST),
                       lambda: Store(legacy_root).submit('anything', CANDIDATE)):
            with self.assertRaisesRegex(DispatchError, 'legacy'):
                action()
        self.assertEqual(list(legacy_root.iterdir()), [legacy_root / '.agents'])
        self.assertEqual(sorted(path.name for path in (legacy_root / '.agents').iterdir()),
                         ['sbd-adaptive'])
        self.assertEqual(legacy.read_text(), '{"schema_version": 2, "events": ["old"]}')

        new = legacy_root / '.agents/decision.json'
        new.write_text(json.dumps({'schema_version': 3, 'phase': 'complete',
                                   'ticket': 'a' * 32}))
        self.assertEqual(Store(legacy_root).resume()['phase'], 'complete')
        self.assertEqual(new.read_text(), json.dumps({'schema_version': 3, 'phase': 'complete',
                                                       'ticket': 'a' * 32}))
        self.assertEqual(legacy.read_text(), '{"schema_version": 2, "events": ["old"]}')

        new.write_text(json.dumps({'schema_version': 2, 'phase': 'draft',
                                   'ticket': 'a' * 32, 'request': REQUEST}))
        with self.assertRaisesRegex(DispatchError, 'legacy'):
            Store(legacy_root).resume()

    def concurrent_submission(self, result):
        ticket = self.store.load()['ticket']
        processes = []
        for _ in range(2):
            process = subprocess.Popen([sys.executable, str(CLI), '--root', str(self.root),
                                        'done', ticket], stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            processes.append(process)
            process.stdin.write(json.dumps(result))
            process.stdin.close()
            process.stdin = None
        outcomes = [p.communicate(timeout=10) for p in processes]
        self.assertEqual(sorted(p.returncode for p in processes), [0, 2])
        self.assertTrue(any('stale or duplicate' in err for _, err in outcomes))

    def test_lock_timeout_and_process_death_release(self):
        code = ("import fcntl,sys,time; f=open(sys.argv[1], 'r+'); "
                "fcntl.flock(f,fcntl.LOCK_EX); print('locked',flush=True); time.sleep(60)")
        process = subprocess.Popen([sys.executable, '-c', code, str(self.path.parent / '.decision.lock')],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            self.assertEqual(process.stdout.readline().strip(), 'locked')
            with self.assertRaisesRegex(DispatchError, 'timed out'):
                Store(self.root, lock_timeout=0.05).submit(self.initial['ticket'], CANDIDATE)
            process.kill()
            process.communicate(timeout=5)
            self.assertEqual(Store(self.root, lock_timeout=0.2).submit(self.initial['ticket'], CANDIDATE)['phase'], 'review')
        finally:
            if process.poll() is None:
                process.kill()
                process.communicate()


if __name__ == '__main__':
    unittest.main()
