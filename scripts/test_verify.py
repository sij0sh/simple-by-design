"""Run: python3 -m unittest discover -s scripts -p 'test_*.py'. No tool installs."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent


class VerifyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "scripts").mkdir()
        (self.root / "languages").mkdir()
        self.repo = self.root / "repo"
        self.repo.mkdir()
        shutil.copy(ROOT / "verify.sh", self.root / "scripts/verify.sh")
        self.profile("printf 'checked\\n'")

    def profile(self, command):
        (self.root / "languages/python.md").write_text(
            f"# Test profile\n```verify\n{command}\n```\n"
        )

    def run_verify(self, *args, command=None):
        env = os.environ.copy()
        env.pop("SBD_VERIFY_CMD", None)
        if command is not None:
            env["SBD_VERIFY_CMD"] = command
        return subprocess.run(
            ["bash", str(self.root / "scripts/verify.sh"), *args],
            cwd=self.repo, env=env, text=True, capture_output=True,
        )

    def test_unknown_stack_strict_fails(self):
        self.assertEqual(self.run_verify("--strict").returncode, 1)
        self.assertEqual(self.run_verify().returncode, 0)

    def test_missing_tool_strict_fails(self):
        self.profile("sbd_nonexistent_tool_827364")
        self.assertEqual(self.run_verify("--strict", "--only=python").returncode, 1)
        self.assertIn("skip", self.run_verify("--only=python").stdout)

    def test_selected_profile_runs(self):
        result = self.run_verify("--strict", "--only=python")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("1 checks", result.stdout)

    def test_failure_not_suppressed_as_baseline(self):
        self.profile("false")
        self.assertEqual(self.run_verify("--only=python").returncode, 1)

    def test_empty_verify_block_fails(self):
        self.profile("# no checks")
        self.assertEqual(self.run_verify("--only=python").returncode, 1)

    def test_unclosed_verify_block_fails(self):
        (self.root / "languages/python.md").write_text("```verify\ntrue\n")
        self.assertEqual(self.run_verify("--strict", "--only=python").returncode, 1)

    def test_unknown_profile_is_usage_error(self):
        self.assertEqual(self.run_verify("--only=../python").returncode, 2)

    def test_entrypoint_authoritative_over_fallback(self):
        self.profile("sbd_nonexistent_tool_827364")
        result = self.run_verify("--strict", "--only=python", command="true")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("python:", result.stdout)

    def test_shell_entrypoint_executes_without_first_word_guess(self):
        result = self.run_verify("--strict", command="SBD_VALUE=yes; test $SBD_VALUE = yes")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_profile_assignment_executes(self):
        self.profile('SBD_VALUE=yes; test "$SBD_VALUE" = yes')
        result = self.run_verify("--strict", "--only=python")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("skip", result.stdout.splitlines()[2])

    def test_profile_assignment_failure_never_skipped(self):
        self.profile("SBD_VALUE=yes; false")
        self.assertEqual(self.run_verify("--only=python").returncode, 1)

    def test_profile_quoted_executable(self):
        executable = self.repo / "check tool"
        executable.write_text("#!/bin/sh\nexit 0\n")
        executable.chmod(0o755)
        self.profile('"./check tool"')
        result = self.run_verify("--strict", "--only=python")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_missing_entrypoint_command_never_passes(self):
        self.assertEqual(self.run_verify(command="sbd_nonexistent_tool_827364").returncode, 1)

    def test_make_entrypoint(self):
        (self.repo / "Makefile").write_text("verify:\n\t@true\n")
        result = self.run_verify("--strict")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("make verify", result.stdout)


if __name__ == "__main__":
    unittest.main()
