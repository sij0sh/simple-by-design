"""Deterministic semantic-contract fixtures, NOT autonomous agent evaluations."""

import unittest

from support import add, answer, choice, design, evidence, ledger, question, review, task


class ScenarioFixtures(unittest.TestCase):
    def test_feature_intent_waits_for_requester_not_engineering_default(self):
        document = ledger.create("feature", task(request="Design notifications; delivery scope is unspecified"))
        document = add(document, question(kind="intent", text="Email, in-app, or both?",
            witness={"form": "pair", "a": "Email delivery", "b": "In-app only", "difference": "Different wanted behavior"}))
        document = add(document, evidence("convention", "documented", "project", claim="Most existing features use email"))
        with self.assertRaisesRegex(ledger.LedgerError, "requester evidence"):
            add(document, answer(resolver="requester", sources=["convention"]))
        document = add(document, {"type": "pause", "id": "ask", "reason": "Intent unresolved", "needs": "Requester's delivery scope"})
        self.assertEqual(ledger.project(document)["status"], "blocked")

    def test_refactor_preserves_observed_order_rather_than_assuming_equivalence(self):
        document = ledger.create("refactor", task(request="Design a behavior-preserving simplification"))
        for record in (
            evidence(claim="fixture caller exposes insertion order"),
            question(text="May the refactor sort returned items?", witness={"form": "defeater",
                     "claim": "Sorting is behavior-neutral", "condition": "Caller observes insertion order", "impact": "Changed output"}),
            answer(text="No: caller observes order"),
            design(text="Keep insertion order and simplify only internal duplication", depends_on=["q"]),
        ):
            document = add(document, record)
        self.assertIn("q", ledger.project(document)["records"]["design"]["depends_on"])

    def test_incident_hypothesis_does_not_become_confirmed_cause(self):
        document = ledger.create("incident", task(request="Design an investigation for intermittent 502 responses"))
        document = add(document, question(text="Does connection exhaustion cause the 502s?"))
        document = add(document, evidence("correlation", "inferred", "inference", claim="Errors correlate with load"))
        with self.assertRaisesRegex(ledger.LedgerError, "requires observations"):
            add(document, answer(sources=["correlation"], text="Exhaustion is confirmed"))
        document = add(document, {"type": "pause", "id": "logs", "reason": "Cause unobserved", "needs": "Authorized discriminating connection/log observations"})
        self.assertEqual(ledger.project(document)["records"]["q"]["status"], "open")

    def test_architectural_choice_retains_rival_tradeoff_and_revisit(self):
        document = ledger.create("architecture", task(request="Design local durable state for a single process"))
        document = add(document, evidence("policy", "documented", "project", claim="Prefer smallest conventional adequate solution"))
        document = add(document, question(kind="choice", text="Flat file or database?"))
        selected = choice(sources=["policy"], policy="defaults", text="Atomic JSON document",
                          alternatives=[{"option": "Database", "rejected_because": "No query or multi-host requirement"}],
                          tradeoff="Whole-document rewrite", revisit="Measured state scale exceeds adequate latency")
        document = add(document, selected)
        self.assertEqual(ledger.project(document)["records"]["a"]["alternatives"][0]["option"], "Database")

    def test_security_unknown_deployment_cannot_support_confirmed_exploitability(self):
        document = ledger.create("security", task(request="Report-only security design assessment",
                                                   permissions=["Read supplied source; no exploitation"]))
        document = add(document, evidence("deployment", "unknown", "unknown", claim="Proxy authentication is unknown"))
        document = add(document, question(text="Can an untrusted principal reach the handler?"))
        with self.assertRaises(ledger.LedgerError):
            add(document, answer(sources=["deployment"], text="Confirmed unauthenticated access"))
        document = add(document, design(text="Conditional assessment; request deployment controls before asserting exploitability"))
        with self.assertRaisesRegex(ledger.LedgerError, "unknown evidence"):
            add(document, {"type": "check", "id": "bad-check", "criterion": "adequate", "design": "design",
                           "result": "passed", "evidence": ["deployment"], "explanation": "Would be unsupported"})
        self.assertEqual(ledger.project(document)["task"]["permissions"], ["Read supplied source; no exploitation"])

    def test_clarification_only_task_stays_blocked_without_invented_intent(self):
        document = ledger.create("clarification", task(request="Design the requested output format; the format is unspecified"))
        document = add(document, question(kind="intent", text="Which consumer and format?"))
        document = add(document, {"type": "pause", "id": "requester", "reason": "Output contract missing", "needs": "Consumer's required format"})
        with self.assertRaises(ledger.LedgerError):
            add(document, review(3), finish=True)
        self.assertIsNone(ledger.project(document)["design"])


if __name__ == "__main__":
    unittest.main()
