from copy import deepcopy
import unittest

from support import add, answer, changed, check, choice, design, evidence, ledger, question, ready, reopen, review, task


class LedgerTests(unittest.TestCase):
    def assertRejected(self, document, record, pattern=None, finish=False):
        original = deepcopy(document)
        with self.assertRaisesRegex(ledger.LedgerError, pattern or "."):
            add(document, record, finish=finish)
        self.assertEqual(document, original, "rejected input mutated caller's history")

    def test_zero_questions_completes_with_supported_candidate_and_parent_review(self):
        document = ready()
        original = deepcopy(document)
        complete = add(document, review(4), finish=True)
        view = ledger.project(complete)
        self.assertEqual(view["status"], "complete")
        self.assertEqual(view["completion"]["certifies"], 4)
        self.assertEqual(view["revision"], 5)
        self.assertFalse(any(r["type"] == "question" for r in view["records"].values()))
        self.assertEqual(document, original)

    def test_empty_ledger_and_missing_checks_cannot_complete(self):
        document = ledger.create("task", task())
        self.assertRejected(document, review(1), "candidate design", finish=True)
        document = add(document, design())
        self.assertRejected(document, review(2), "unsupported design criterion", finish=True)
        with self.assertRaises(ledger.LedgerError):
            ledger.create("task", task(criteria=[]))

    def test_every_required_criterion_and_current_design_must_pass(self):
        document = ready(criteria=[{"id": "adequate", "text": "First"}, {"id": "other", "text": "Second"}])
        self.assertRejected(document, review(4), "other", finish=True)
        document = add(document, check("other-check", criterion="other"))
        document = add(document, check("failed", result="failed"))
        self.assertRejected(document, review(6), "adequate", finish=True)
        document = add(document, check("fixed"))
        document = add(document, design("replacement"))
        view = ledger.project(document)
        self.assertFalse(view["records"]["design"]["valid"])
        self.assertEqual(view["checks"], {})
        self.assertRejected(document, review(8), "criterion", finish=True)
        self.assertRejected(document, check("stale-check"), "current design")

    def test_unresolved_optional_question_also_needs_explicit_disposition(self):
        document = add(ready(), question(required=False))
        self.assertRejected(document, review(5), "unresolved question", finish=True)

    def test_intent_never_resolved_by_policy_observation_or_assumption(self):
        document = add(ready(), question(kind="intent"))
        self.assertRejected(document, answer(), "wrong answer resolver")
        self.assertRejected(document, answer(resolver="requester"), "requester evidence")
        self.assertRejected(document, answer(resolver="requester", mode="provisional"), "intent cannot")
        document = add(document, evidence("user", "documented", "requester"))
        document = add(document, answer(resolver="requester", sources=["user"]))
        self.assertEqual(ledger.project(document)["records"]["q"]["status"], "resolved")

    def test_fact_requires_observation_not_document_or_inference(self):
        for kind, authority in (("inferred", "inference"), ("unknown", "unknown"), ("documented", "project")):
            document = add(ready(), question())
            document = add(document, evidence("basis", kind, authority))
            self.assertRejected(document, answer(sources=["basis"]), "requires observations")
        document = add(add(ready(), question()), answer())
        self.assertEqual(ledger.project(document)["records"]["q"]["status"], "resolved")

    def test_requester_factual_observation_is_not_restricted_to_intent(self):
        document = add(ready(), question())
        document = add(document, evidence("testimony", "observed", "requester",
                                         source="Requester factual observation", claim="Observed deployed setting"))
        document = add(document, answer(sources=["testimony"]))
        self.assertEqual(ledger.project(document)["records"]["q"]["status"], "resolved")

    def test_provisional_fact_needs_reversal_detection_revisit_and_inferred_basis(self):
        document = add(ready(), question())
        document = add(document, evidence("guess", "inferred", "inference"))
        provisional = answer(sources=["guess"], mode="provisional", reversal="Replace a local constant",
                             detect="Design review compares the real requirement", revisit="Before implementation")
        for field in ("reversal", "detect", "revisit"):
            invalid = deepcopy(provisional)
            del invalid[field]
            self.assertRejected(document, invalid)
        self.assertRejected(document, changed(provisional, evidence=["observed"]), "inferred evidence")
        document = add(document, provisional)
        self.assertEqual(ledger.project(document)["records"]["q"]["status"], "provisional")

    def test_choice_requires_consequential_decision_metadata_and_policy_basis(self):
        document = add(ready(), question(kind="choice"))
        selected = choice()
        for field in ("policy", "alternatives", "rationale", "tradeoff", "revisit"):
            invalid = deepcopy(selected)
            del invalid[field]
            self.assertRejected(document, invalid)
        self.assertRejected(document, changed(selected, alternatives=[]), "alternatives")
        self.assertRejected(document, changed(selected, policy="requirements"), "requester")
        self.assertRejected(document, changed(selected, policy="defaults"), "project evidence")
        document = add(document, evidence("defaults", "documented", "project"))
        document = add(document, changed(selected, policy="defaults", evidence=["defaults"]))
        self.assertEqual(ledger.project(document)["records"]["q"]["resolution"], "a")

    def test_no_witness_no_question_and_pair_must_differ(self):
        document = ready()
        for invalid in ({}, {"form": "pair", "a": "A", "b": "A", "difference": "none"},
                        {"form": "defeater", "claim": "x", "condition": "y"},
                        {"form": "check", "criterion": "absent", "failure": "missing"}):
            self.assertRejected(document, question(witness=invalid))
        document = add(document, question(witness={"form": "defeater", "claim": "A", "condition": "B", "impact": "C"}))
        document = add(document, question("q2", witness={"form": "check", "criterion": "adequate", "failure": "Evidence missing"}))
        self.assertEqual(len(ledger.project(document)["records"]), 5)

    def test_deferral_cannot_hide_a_required_question_or_invent_scope(self):
        document = add(ready(), question())
        deferred = {"type": "defer", "id": "deferred", "question": "q", "boundary": "Future execution only",
                    "owner": "implementer", "reason": "Out of current scope", "trigger": "Implementation approval",
                    "evidence": ["observed"]}
        self.assertRejected(document, deferred, "required question")
        document = add(ready(), question(required=False))
        self.assertRejected(document, deferred, "requester-sourced")
        document = add(document, evidence("scope", "documented", "requester"))
        document = add(document, changed(deferred, evidence=["scope"]))
        document = add(document, review(7), finish=True)
        self.assertEqual(ledger.project(document)["status"], "complete")

    def test_dependency_dag_and_unanswered_dependency_refusal(self):
        document = ready()
        self.assertRejected(document, question(depends_on=["q"]), "self references")
        self.assertRejected(document, question(depends_on=["future"]), "unknown reference")
        self.assertRejected(document, question(depends_on=["observed"]), "earlier questions")
        document = add(document, question())
        document = add(document, question("q2", depends_on=["q"]))
        self.assertRejected(document, answer("a2", "q2"), "unanswered dependency")
        document = add(document, answer())
        document = add(document, answer("a2", "q2"))
        self.assertEqual(ledger.project(document)["records"]["q2"]["status"], "resolved")
        self.assertRejected(document, question("q", depends_on=["q2"]), "immutable")

    def test_contradiction_transitively_reopens_questions_design_and_checks(self):
        document = ledger.create("task", task())
        for record in (evidence(), question(), answer(), question("q2", depends_on=["q"]),
                       answer("a2", "q2"), design(depends_on=["q2"]), check()):
            document = add(document, record)
        document = add(document, review(8), finish=True)
        document = add(document, reopen())
        view = ledger.project(document)
        self.assertEqual(view["status"], "active")
        self.assertIsNone(view["completion"])
        self.assertIsNone(view["design"])
        self.assertEqual(view["checks"], {})
        for key in ("q", "q2"):
            self.assertEqual(view["records"][key]["status"], "open")
        for key in ("observed", "a", "a2", "design", "check"):
            self.assertFalse(view["records"][key]["valid"], key)
        self.assertEqual(document["events"][-2]["data"]["type"], "completion")
        self.assertRejected(document, design("bad", depends_on=["a2"]), "invalidated")

    def test_replacing_resolution_invalidates_dependents_without_reusing_id(self):
        document = add(add(ready(), question()), answer())
        document = add(document, design("dependent", depends_on=["q"]))
        document = add(document, answer("replacement-answer"))
        view = ledger.project(document)
        self.assertEqual(view["records"]["q"]["resolution"], "replacement-answer")
        self.assertFalse(view["records"]["a"]["valid"])
        self.assertFalse(view["records"]["dependent"]["valid"])
        self.assertIsNone(view["design"])

    def test_reopening_resolution_reopens_question_even_if_not_direct_target(self):
        document = add(add(ready(), question()), answer())
        document = add(document, reopen(["a"]))
        self.assertEqual(ledger.project(document)["records"]["q"]["status"], "open")

    def test_invalidated_basis_cannot_be_reused_during_automatic_replacement(self):
        document = add(add(ready(), question()), answer())
        document = add(document, evidence("derived", depends_on=["q"]))
        self.assertRejected(document, answer("replacement", sources=["derived"]), "invalidated")
        self.assertRejected(document, design("d2", depends_on=["design"]), "invalidated")

    def test_stale_final_and_separately_recorded_evaluation_are_not_completion_tokens(self):
        document = ready()
        evaluation = review(4)
        document = add(document, {"type": "evaluation", "id": "review", **evaluation})
        self.assertRejected(document, evaluation, "stale evaluation", finish=True)
        with self.assertRaisesRegex(ledger.LedgerError, "stale revision"):
            ledger.append(document, review(5), 4, finish=True)
        self.assertRejected(document, review(5, reviewed=["design"]), "review must cover", finish=True)

    def test_independence_required_means_local_review_blocks(self):
        document = ready(independent_review=True)
        self.assertRejected(document, review(4), "independent review", finish=True)
        # This validates a claim's shape, not whether an independent human/agent existed.
        self.assertEqual(ledger.project(add(document, review(4, independent=True), finish=True))["status"], "complete")

    def test_surviving_findings_are_recorded_questions_and_block_finish(self):
        document = add(ready(), question())
        evaluation = review(5, findings=["q"])
        self.assertRejected(document, evaluation, "still has findings", finish=True)
        self.assertRejected(document, {"type": "evaluation", "id": "e", **review(5, findings=["absent"])}, "unknown reference")
        document = add(document, {"type": "evaluation", "id": "e", **evaluation})
        self.assertEqual(ledger.project(document)["records"]["e"]["findings"], ["q"])

    def test_pause_is_blocked_and_explicit_evidence_can_resume(self):
        document = add(ready(), {"type": "pause", "id": "blocked", "reason": "Need authority", "needs": "Requester response"})
        self.assertEqual(ledger.project(document)["status"], "blocked")
        self.assertRejected(document, review(5), "not active", finish=True)
        document = add(document, evidence("response", "documented", "requester"))
        self.assertEqual(ledger.project(document)["status"], "active")

    def test_complete_only_accepts_cited_reopening_and_preserves_original_authority(self):
        document = add(ready(), review(4), finish=True)
        self.assertRejected(document, evidence("later"), "explicit reopening")
        self.assertRejected(document, review(5), "not active", finish=True)
        self.assertRejected(document, changed(reopen(), cause={"kind": "inferred", "authority": "inference", "source": "guess", "claim": "maybe"}), "cited observation")
        original_task = deepcopy(ledger.project(document)["task"])
        document = add(document, reopen(["design"]))
        self.assertEqual(ledger.project(document)["task"], original_task)
        document = add(document, design("revised"))
        document = add(document, check("rechecked", design_id="revised"))
        document = add(document, review(8), finish=True)
        self.assertEqual(ledger.project(document)["completion"]["certifies"], 8)
        self.assertEqual(sum(e["data"]["type"] == "completion" for e in document["events"]), 2)

    def test_record_command_cannot_forge_control_events(self):
        self.assertRejected(ready(), {"type": "completion", "evaluation": review(4)}, "use new/finish")
        self.assertRejected(ready(), {"type": "task"}, "use new/finish")

    def test_malformed_shapes_fail_with_ledger_errors(self):
        document = ready()
        malformed = [None, [], {}, {"type": []}, changed(question(), kind=[]),
                     changed(question(), witness={"form": []}), changed(evidence("e"), kind=[]),
                     changed(evidence("e"), authority=[]), changed(question(), depends_on=[{}]),
                     changed(question(), required="true"), changed(question(), typo="field"),
                     changed(question(), id="../escape"), changed(check("c"), criterion=[]),
                     changed(check("c"), result=[])]
        for record in malformed:
            with self.subTest(record=record):
                self.assertRejected(document, record)
        document = add(document, question(kind="choice"))
        for record in (changed(choice(), policy=[]), changed(choice(), alternatives=[None]),
                       changed(choice(), mode=[])):
            self.assertRejected(document, record)

    def test_field_type_mutations_fail_cleanly_or_remain_valid(self):
        document = ready()
        for record in (evidence("user", "documented", "requester"), question(), answer(),
                       question("intent", "intent"), question("choice", "choice")):
            document = add(document, record)
        templates = [evidence("new"), question("new"), answer("new"), choice("new", "choice"),
                     design("new"), check("new"), reopen(id="new"),
                     {"type": "pause", "id": "new", "reason": "blocked", "needs": "requester"},
                     {"type": "evaluation", "id": "new", **review(len(document["events"]))}]
        for template in templates:
            for field in template:
                for value in (None, [], {}, "", 0, 1, True, False, [None], [[]], [{}]):
                    with self.subTest(kind=template["type"], field=field, value=value):
                        try:
                            add(document, changed(template, **{field: value}))
                        except ledger.LedgerError:
                            pass

    def test_replay_rejects_corrupt_schema_revision_timestamp_or_transition(self):
        document = ready()
        bad_documents = []
        for field, value in (("schema_version", 2), ("schema_version", True), ("events", []), ("task_id", "../x")):
            bad_documents.append(changed(document, **{field: value}))
        for field, value in (("revision", 7), ("time", "not a date"), ("time", "2026-01-01"),
                             ("data", {"type": "check", "id": "bad"})):
            corrupt = deepcopy(document)
            corrupt["events"][-1][field] = value
            bad_documents.append(corrupt)
        for corrupt in bad_documents:
            with self.subTest(document=corrupt):
                with self.assertRaises(ledger.LedgerError):
                    ledger.project(corrupt)


if __name__ == "__main__":
    unittest.main()
