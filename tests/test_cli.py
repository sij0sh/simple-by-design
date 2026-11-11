import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

from support import ROOT, check, design, evidence, review, task

CLI = ROOT / "scripts" / "sbd.py"


class CliTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def run_cli(self, *arguments, data=None, raw=None, expected=0):
        process = subprocess.run([sys.executable, str(CLI), *arguments], cwd=self.root,
                                 input=raw if raw is not None else json.dumps(data),
                                 text=True, capture_output=True, timeout=10)
        self.assertEqual(process.returncode, expected, process.stderr)
        if expected:
            self.assertFalse(process.stdout)
            self.assertNotIn("Traceback", process.stderr)
            return process.stderr
        return json.loads(process.stdout)

    def test_new_show_resume_record_finish_historical_show(self):
        self.assertEqual(self.run_cli("new", "greeting", data=task())["revision"], 1)
        for revision, record in enumerate((evidence(), design(), check()), 1):
            self.assertEqual(self.run_cli("record", "greeting", "--at", str(revision), data=record)["revision"], revision + 1)
        complete = self.run_cli("finish", "greeting", "--at", "4", data=review(4))
        self.assertEqual(complete["completion"]["certifies"], 4)
        self.assertEqual(self.run_cli("show", "greeting")["status"], "complete")
        snapshot = self.run_cli("show", "greeting", "--at", "4", "--history")
        self.assertEqual(snapshot["status"], "active")
        self.assertEqual(len(snapshot["events"]), 4)
        self.run_cli("new", "greeting", data=task(), expected=2)
        self.run_cli("record", "greeting", "--at", "5", data=evidence("later"), expected=2)

    def test_malformed_json_ids_missing_state_and_required_revision_fail_cleanly(self):
        for raw in ("", "{", "null", "[]", '{"request":1,"request":2}', '{"request":NaN}'):
            self.run_cli("new", "task", raw=raw, expected=2)
        self.run_cli("new", "../outside", data=task(), expected=2)
        self.run_cli("show", "missing", expected=2)
        self.run_cli("record", "missing", data=evidence(), expected=2)
        self.run_cli("new", "task", data=task())
        self.run_cli("record", "task", "--at", "1", data={"type": []}, expected=2)
        self.run_cli("record", "task", "--at", "1", data={"type": "evidence", "id": "bad"}, expected=2)
        self.assertEqual(self.run_cli("show", "task")["revision"], 1)

    def test_explicit_root_works_from_unrelated_directory(self):
        project = self.root / "project"
        project.mkdir()
        self.run_cli("--root", str(project), "new", "task", data=task())
        self.assertTrue((project / ".agents" / "sbd-adaptive" / "task.json").exists())
        self.assertFalse((self.root / ".agents").exists())

    def test_documented_negative_control_runs_verbatim_without_questions(self):
        document = (ROOT / "references" / "ledger.md").read_text()
        example = re.search(r"```sh\n(.*?)\n```", document, re.S).group(1)
        process = subprocess.run(["sh", "-e"], input=example, text=True, capture_output=True,
                                 cwd=self.root, env={**os.environ, "S": str(ROOT)}, timeout=10)
        self.assertEqual(process.returncode, 0, process.stderr)
        view = self.run_cli("show", "greeting", "--history")
        self.assertEqual(view["status"], "complete")
        self.assertEqual(len(view["events"]), 5)
        self.assertFalse(any(r["type"] == "question" for r in view["records"].values()))

    def test_skill_frontmatter_and_relative_reference_links(self):
        skill = (ROOT / "SKILL.md").read_text()
        frontmatter = re.match(r"---\n(.*?)\n---\n", skill, re.S).group(1)
        self.assertIn("name: simple-by-design-adaptive", frontmatter)
        self.assertRegex(frontmatter, r"description: .+")
        for file in [ROOT / "SKILL.md", *sorted((ROOT / "references").glob("*.md"))]:
            for destination in re.findall(r"\]\(([^)]+)\)", file.read_text()):
                self.assertTrue((file.parent / destination).is_file(), f"broken link in {file}: {destination}")
        self.assertFalse((ROOT / "workflows").exists())


if __name__ == "__main__":
    unittest.main()
