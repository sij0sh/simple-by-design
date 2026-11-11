"""Scripted result sequences check protocol only, not actual agent adherence."""

import tempfile
import unittest

from support import Store, DispatchError, PASS


def candidate(summary, criteria=('Checkable outcome.',), decisions=()):
    return {'status': 'candidate', 'summary': summary, 'criteria': list(criteria),
            'decisions': list(decisions)}


def decision(id, choice, alternative='Serious rival.', revisit='Assumption fails.'):
    return {'id': id, 'choice': choice, 'basis': 'assumption: typical load.',
            'alternative': alternative, 'tradeoff': 'Simpler, less flexible.', 'revisit': revisit}


def gap(check, witness, target='D1'):
    return {'status': 'revise', 'gaps': [{'check': check, 'witness': witness, 'decision': target}]}


def need(type, question, witness):
    return {'status': 'need', 'type': type, 'question': question, 'witness': witness,
            'consequence': 'Changes the design.'}


class ScenarioFixtures(unittest.TestCase):
    def run_steps(self, request, *results):
        with tempfile.TemporaryDirectory() as root:
            store = Store(root)
            state = store.start(request)
            for result in results:
                state = store.submit(state['ticket'], result)
            if state['status'] == 'complete':
                state['text'] = (store.root / state['artifact']).read_text()
            return state

    def test_trivial_task_without_decisions_passes_with_no_resolve(self):
        state = self.run_steps('Design a command printing Hello once.',
                               candidate('Single print.', ['Prints exactly one line: Hello.']), PASS)
        self.assertEqual(state['status'], 'complete')
        self.assertEqual(state['resolutions'], [])
        self.assertIn('None consequential.', state['text'])

    def test_pair_witness_routes_intent_to_requester_then_passes(self):
        state = self.run_steps(
            'Design a greeting; language unstated.',
            need('intent', 'Which language?', 'Hello and Hola both fit; requester would differ.'),
            {'status': 'blocked', 'question': 'Which language?', 'needs': 'Requester answer.'},
            {'status': 'resolved', 'answer': 'English.', 'basis': 'Requester said English.'},
            candidate('Print Hello.'), PASS)
        self.assertEqual(state['status'], 'complete')
        self.assertIn('(intent) Which language? → English.', state['text'])

    def test_criteria_pass_while_goal_fails_forces_targeted_revise(self):
        weak = candidate('Cache results.', ['Cache returns a value.'], [decision('D1', 'In-memory dict.')])
        with tempfile.TemporaryDirectory() as root:
            store = Store(root)
            state = store.start('Design a cache that never serves stale prices.')
            state = store.submit(state['ticket'], weak)
            state = store.submit(state['ticket'], gap('defeater', 'A stale value also satisfies the criterion.'))
            self.assertEqual(state['prompt'], 'draft')
            self.assertEqual(state['feedback'][0]['decision'], 'D1')
            self.assertEqual(state['candidate'], {k: v for k, v in weak.items() if k != 'status'})
            with self.assertRaises(DispatchError):
                store.submit(state['ticket'], PASS)  # Cannot approve a draft.
            fixed = candidate('Cache with TTL below price update interval.',
                              ['No read returns a price older than its update interval.'],
                              [decision('D1', 'In-memory dict with TTL.')])
            state = store.submit(state['ticket'], fixed)
            self.assertEqual(state['feedback'], [])
            state = store.submit(state['ticket'], PASS)
            self.assertEqual(state['status'], 'complete')

    def test_decision_missing_alternative_is_rejected_structurally(self):
        with tempfile.TemporaryDirectory() as root:
            store = Store(root)
            state = store.start('Design storage.')
            bare = {k: v for k, v in decision('D1', 'SQLite.').items() if k != 'alternative'}
            with self.assertRaises(DispatchError):
                store.submit(state['ticket'], candidate('Use SQLite.', decisions=[bare]))

    def test_fact_gap_and_explicit_deferral_both_accumulate(self):
        state = self.run_steps(
            'Design diagnosis for intermittent timeout; no production access.',
            need('fact', 'Is packet loss observed?', 'Loss vs slow server give different fixes.'),
            {'status': 'resolved', 'answer': 'Unobserved; stays assumption.', 'basis': 'No access granted.'},
            candidate('Compare loss with server timing when authorized.',
                      decisions=[decision('D1', 'Assume network loss.', revisit='Server timing dominates.')]),
            need('intent', 'Alert threshold?', 'Paging at 1% vs 5% differs to on-call.'),
            {'status': 'resolved', 'answer': 'deferred: requester decides after trial.', 'basis': 'Requester deferred.'},
            candidate('Same, threshold deferred.', decisions=[decision('D1', 'Assume network loss.')]),
            PASS)
        self.assertEqual([r['type'] for r in state['resolutions']], ['fact', 'intent'])
        self.assertIn('deferred: requester decides', state['text'])


if __name__ == '__main__':
    unittest.main()
