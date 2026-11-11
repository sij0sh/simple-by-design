"""Scripted result sequences check protocol only, not actual agent adherence."""

import tempfile
import unittest

from support import Store, DispatchError


class ScenarioFixtures(unittest.TestCase):
    def run_design(self, request, draft, basis):
        with tempfile.TemporaryDirectory() as root:
            store = Store(root)
            state = store.start(request)
            state = store.submit(state['ticket'], {'status': 'candidate', 'text': draft})
            state = store.submit(state['ticket'], {'status': 'pass', 'basis': basis})
            self.assertEqual(state['status'], 'complete')
            self.assertEqual(state['request'], request)
            return state

    def test_precise_trivial_design_needs_no_resolve_prompt(self):
        state = self.run_design('Design a command printing Hello once; no questions needed.',
                                'Use a single print. No implementation; test exact output when authorized.',
                                'Local review: request covered; no tests run.')
        self.assertIsNone(state['need'])

    def test_reversible_choice_is_not_a_required_question(self):
        state = self.run_design('Design a local scratch cache; format is implementer choice.',
                                'Choose JSON rather than a database for this small cache; migrate if size warrants.',
                                'Local review: reversible choice and revisit condition adequate.')
        self.assertIn('JSON', state['candidate'])

    def test_report_only_scope_is_preserved_in_original_request(self):
        state = self.run_design('Report-only design; do not edit the target repository.',
                                'Propose one function; no files edited. Verification is future work.',
                                'Local review: report-only scope honored; tests not run.')
        self.assertIn('do not edit', state['request'])

    def test_unobserved_fact_can_remain_an_explicit_conditional(self):
        state = self.run_design('Design diagnosis for intermittent timeout; no production access.',
                                'Network loss is a hypothesis, not an observed cause. Compare packet loss with server timing when authorized.',
                                'Local review: diagnosis conditional; unavailable evidence not invented.')
        self.assertIn('hypothesis', state['candidate'])

    def test_material_correction_requires_new_candidate_and_review(self):
        with tempfile.TemporaryDirectory() as root:
            store = Store(root)
            state = store.start('Design report-only output preserving the original greeting.')
            state = store.submit(state['ticket'], {'status': 'candidate', 'text': 'Print a changed greeting.'})
            old_ticket = state['ticket']
            state = store.submit(old_ticket, {'status': 'revise', 'feedback': 'Restore original greeting.'})
            self.assertIn('Restore', Store(root).resume()['feedback'])
            with self.assertRaises(DispatchError):
                store.submit(old_ticket, {'status': 'pass', 'basis': 'stale review'})
            with self.assertRaises(DispatchError):
                store.submit(state['ticket'], {'status': 'pass', 'basis': 'cannot pass draft'})
            state = store.submit(state['ticket'], {'status': 'candidate', 'text': 'Preserve original greeting.'})
            state = store.submit(state['ticket'], {'status': 'pass', 'basis': 'Local re-review against original request; no tests run.'})
            self.assertEqual(state['status'], 'complete')

    def test_consequential_intent_blocks_then_resumes_with_requester_answer(self):
        self.blocked_case('Design greeting; intended language unknown.',
                          'Which language?', 'Changes externally visible output.',
                          'Requester language preference.', 'English, per requester.')

    def test_unavailable_required_independence_can_be_reported_blocked(self):
        self.blocked_case('Design greeting; independent review is required.',
                          'Can an independent reviewer be provided?',
                          'Required assurance cannot be supplied by local review.',
                          'Independent reviewer access.', 'Independent reviewer supplied separate findings.')

    def blocked_case(self, request, question, consequence, needs, answer):
        with tempfile.TemporaryDirectory() as root:
            store = Store(root)
            state = store.start(request)
            state = store.submit(state['ticket'], {'status': 'need', 'question': question, 'consequence': consequence})
            state = store.submit(state['ticket'], {'status': 'blocked', 'question': question, 'needs': needs})
            resumed = Store(root).resume()
            self.assertEqual(resumed, state)
            self.assertEqual(resumed['status'], 'blocked')
            self.assertFalse(resumed['artifact'])
            state = store.submit(resumed['ticket'], {'status': 'resolved', 'text': answer, 'basis': 'Acquired resolver response.'})
            self.assertEqual(state['prompt'], 'draft')
            self.assertEqual(state['request'], request)


if __name__ == '__main__':
    unittest.main()
