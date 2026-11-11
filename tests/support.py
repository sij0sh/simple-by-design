"""Shared imports and small result fixtures; these are not real-agent trials."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from engine.router import DispatchError
from engine.state import Store

CLI = ROOT / "scripts" / "sbd.py"
REQUEST = "Design a report-only greeting command. Print Hello once; do not implement it."
CANDIDATE = {"status": "candidate", "text": "Use one print('Hello') command. Alternative: a new CLI framework, unnecessary here. Report only; no implementation. Verify one output line when authorized; tests not run."}
PASS = {"status": "pass", "basis": "Local review, not independent. Covers the greeting and report-only scope; planned tests are not reported as executed."}
NEED = {"status": "need", "question": "Which output language is required?", "consequence": "Changes the user-visible greeting."}
BLOCKED = {"status": "blocked", "question": "Which language?", "needs": "Requester answer."}
RESOLVED = {"status": "resolved", "text": "Use English.", "basis": "Requester explicitly answered English."}
