import json
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
import unittest

from support import ROOT, CLI, REQUEST, CANDIDATE, PASS, NEED, BLOCKED, RESOLVED, Store
from engine.prompts import render, return_command
from engine import router


class CliTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="sbd project's ")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def cli(self, *args, data=None, expected=0):
        process = subprocess.run([sys.executable, str(CLI), '--root', str(self.root), *args],
                                 input=data, capture_output=True, text=True, cwd='/')
        self.assertEqual(process.returncode, expected, process.stderr)
        return process

    def submit(self, result, expected=0):
        ticket = Store(self.root).load()['ticket']
        return self.cli('done', ticket, data=json.dumps(result), expected=expected)

    def test_ordinary_task_finishes_in_three_calls_with_current_prompt_only(self):
        first = self.cli('--request', REQUEST).stdout
        self.assertIn('TASK: draft', first)
        self.assertNotIn('TASK: review', first)
        self.assertNotIn('TASK: resolve', first)
        second = self.submit(CANDIDATE).stdout
        self.assertIn('TASK: review', second)
        self.assertIn(CANDIDATE['text'], second)
        self.assertNotIn('TASK: draft', second)
        third = self.submit(PASS).stdout
        self.assertTrue(third.startswith('DONE: .agents/artifacts/solution-design-'))
        self.assertEqual(self.cli().stdout, third)
        self.assertEqual(len(list((self.root / '.agents/artifacts').glob('*.md'))), 1)

    def test_no_run_prints_start_usage_and_creates_no_files(self):
        output = self.cli().stdout
        self.assertIn('--request', output)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_invalid_input_has_repair_hint_without_advancing(self):
        self.cli('--request', REQUEST)
        path = Store(self.root).path
        before = path.read_bytes()
        for data in ('{', '[]', '{"status":"candidate"}',
                     '{"status":"candidate","status":"candidate","text":"x"}',
                     '{"status":NaN}', '{"status":"candidate","text":"x","next":"DONE"}'):
            process = self.cli('done', Store(self.root).load()['ticket'], data=data, expected=2)
            self.assertIn('Resume:', process.stderr)
            self.assertNotIn('DONE:', process.stdout)
            self.assertEqual(path.read_bytes(), before)
        self.cli('--request', 'different', expected=2)
        self.assertEqual(path.read_bytes(), before)
        self.cli('done', 'bad-ticket', data=json.dumps(CANDIDATE), expected=2)
        self.assertEqual(path.read_bytes(), before)

    def test_blocked_reissue_and_acquired_answer_use_same_command(self):
        self.cli('--request', REQUEST)
        self.submit(NEED)
        output = self.submit(BLOCKED).stdout
        self.assertIn('BLOCKED', output)
        self.assertEqual(self.cli().stdout, output)
        self.assertIn('Requester answer.', output)
        self.assertIn('TASK: draft', self.submit(RESOLVED).stdout)

    def test_printed_command_is_executable_from_another_cwd_with_quoted_paths(self):
        self.cli('--request', REQUEST)
        document = Store(self.root).load()
        command = return_command(document, CLI, self.root)
        process = subprocess.run(shlex.split(command), input=json.dumps(CANDIDATE),
                                 cwd='/', capture_output=True, text=True)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertIn('TASK: review', process.stdout)

    def test_usage_and_obsolete_api_are_rejected(self):
        for args in (('done',), ('new', 'old'), ('--request', REQUEST, 'done', 'ticket')):
            self.cli(*args, expected=2)
        self.assertIn('Focused design prompts', self.cli('--help').stdout)
        self.cli('--request', ' ', expected=2)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_skill_entry_and_ordinary_static_instruction_budgets(self):
        skill = (ROOT / 'SKILL.md').read_text()
        self.assertTrue(skill.startswith('---\nname: simple-by-design-adaptive\n'))
        self.assertIn('disable-model-invocation: true', skill)
        body = skill.split('---', 2)[2]
        self.assertLessEqual(len(body.split()), 100)
        self.assertGreaterEqual(1 - len(body.split()) / 2127, .95)
        self.assertNotRegex(body, r'references/|\]\(')
        document = router.new(REQUEST)
        outputs = [render(document, CLI, self.root)]
        outputs.append(render(router.advance(document, CANDIDATE), CLI, self.root))
        ordinary = len(body.split())
        for output in outputs:
            # Count the entire emitted static surface, not just template strings.
            start = output.index('{\n')
            end = output.index('\n\nReturn JSON:', start)
            ordinary += len((output[:start] + output[end:]).split())
        self.assertLessEqual(ordinary, 400)
        for path in (ROOT / 'SKILL.md', ROOT / 'README.md'):
            for link in re.findall(r'\]\(([^)]+)\)', path.read_text()):
                self.assertTrue((path.parent / link).is_file(), link)
        self.assertFalse((ROOT / 'references').exists())
        self.assertFalse((ROOT / 'scripts/engine/ledger.py').exists())

    def test_large_original_request_and_candidate_are_not_truncated(self):
        request = 'request-start ' + 'x' * 30000 + ' request-end'
        draft = router.new(request)
        candidate = 'candidate-start ' + 'y' * 30000 + ' candidate-end'
        review = router.advance(draft, {'status': 'candidate', 'text': candidate})
        for document in (draft, review):
            output = render(document, CLI, self.root)
            self.assertIn(request, output)
        self.assertIn(candidate, render(review, CLI, self.root))


if __name__ == '__main__':
    unittest.main()
