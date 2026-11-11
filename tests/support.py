"""Small test data builders; fixtures are not agent-behavior evaluations."""

from copy import deepcopy
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from engine import ledger  # noqa: E402


def task(**changes):
    value = {"request": "Design the requested solution, without implementing it.",
             "constraints": ["Design only"], "permissions": ["Inspect test fixtures"],
             "criteria": [{"id": "adequate", "text": "Candidate satisfies the stated design requirement"}],
             "independent_review": False}
    value.update(changes)
    return value


def evidence(key="observed", kind="observed", authority="observation", **changes):
    value = {"id": key, "type": "evidence", "kind": kind, "authority": authority,
             "source": "fixture.py:1-4", "claim": "Fixture observation"}
    value.update(changes)
    return value


def question(key="q", kind="fact", **changes):
    value = {"id": key, "type": "question", "kind": kind, "resolver": ledger.RESOLVERS[kind],
             "text": "Which outcome is supported?", "required": True,
             "witness": {"form": "pair", "a": "A", "b": "B", "difference": "Changes required behavior"},
             "consequence": "An incorrect design", "next": "Seek discriminating evidence"}
    value.update(changes)
    return value


def answer(key="a", q="q", sources=None, **changes):
    value = {"id": key, "type": "answer", "question": q, "text": "Observed A",
             "resolver": "observation", "evidence": sources or ["observed"], "mode": "established"}
    value.update(changes)
    return value


def choice(key="a", q="q", sources=None, **changes):
    value = answer(key, q, sources, resolver="policy", policy="simplest",
                   alternatives=[{"option": "B", "rejected_because": "Unneeded complexity"}],
                   rationale="A meets present needs", tradeoff="No generalization", revisit="A concrete second need")
    value.update(changes)
    return value


def design(key="design", **changes):
    value = {"id": key, "type": "design", "text": "The adequate candidate solution",
             "verification": "Future implementation test; not claimed as passing"}
    value.update(changes)
    return value


def check(key="check", design_id="design", **changes):
    value = {"id": key, "type": "check", "criterion": "adequate", "design": design_id,
             "result": "passed", "evidence": ["observed"], "explanation": "Design comparison supported by cited basis"}
    value.update(changes)
    return value


def review(revision, **changes):
    value = {"revision": revision, "reviewer": "local unit-test fixture, not independent review",
             "independent": False, "reviewed": sorted(ledger.REVIEW_SCOPE), "findings": []}
    value.update(changes)
    return value


def reopen(targets=None, **changes):
    value = {"id": "reopen", "type": "reopen", "targets": targets or ["observed"],
             "trigger": "contradiction", "cause": {"kind": "observed", "authority": "observation",
             "source": "new fixture observation", "claim": "Earlier premise is contradicted"}}
    value.update(changes)
    return value


def add(document, record, finish=False):
    return ledger.append(document, record, len(document["events"]), finish=finish)


def ready(**task_changes):
    document = ledger.create("task", task(**task_changes))
    for record in (evidence(), design(), check()):
        document = add(document, record)
    return document


def changed(value, **changes):
    result = deepcopy(value)
    result.update(changes)
    return result
