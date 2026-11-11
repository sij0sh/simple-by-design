from copy import deepcopy
import unittest

from support import REQUEST, CANDIDATE, PASS, NEED, BLOCKED, RESOLVED, REVISE, DispatchError
from engine import router


class RouterTests(unittest.TestCase):
    def test_zero_gap_path_needs_only_candidate_and_review(self):
        draft = router.new(REQUEST)
        review = router.advance(draft, CANDIDATE)
        final = router.advance(review, PASS)
        self.assertEqual((draft['prompt'], review['prompt'], final['status']),
                         ('draft', 'review', 'publishing'))
        self.assertEqual(draft['request'], final['request'])
        self.assertEqual(final['candidate'], {k: CANDIDATE[k] for k in ('summary', 'criteria', 'decisions')})
        self.assertNotEqual(draft['ticket'], review['ticket'])
        self.assertEqual(review['ticket'], final['ticket'])
        self.assertIsNone(draft['candidate'])  # Pure transitions.

    def test_every_route_including_material_review_need(self):
        draft = router.new(REQUEST)
        for source in (draft, router.advance(draft, CANDIDATE)):
            resolve = router.advance(source, NEED)
            blocked = router.advance(resolve, BLOCKED)
            self.assertEqual(blocked['status'], 'blocked')
            self.assertEqual(blocked['need'], {k: v for k, v in NEED.items() if k != 'status'})
            redraft = router.advance(blocked, RESOLVED)
            self.assertEqual(redraft['prompt'], 'draft')
            self.assertIsNone(redraft['need'])
            self.assertIsNone(redraft['blocker'])
            self.assertEqual(redraft['resolutions'], [{'type': 'intent', 'question': NEED['question'],
                                                    'answer': RESOLVED['answer'], 'basis': RESOLVED['basis']}])
            self.assertEqual(router.advance(redraft, CANDIDATE)['prompt'], 'review')
        review = router.advance(draft, CANDIDATE)
        redraft = router.advance(review, REVISE)
        self.assertEqual(redraft['prompt'], 'draft')
        self.assertEqual(redraft['candidate'], review['candidate'])
        self.assertEqual(redraft['feedback'], REVISE['gaps'])
        self.assertEqual(router.advance(redraft, CANDIDATE)['feedback'], [])
        with self.assertRaises(DispatchError):
            router.advance(redraft, PASS)  # Cannot approve a draft or reuse an old review.

    def test_invalid_results_never_mutate_the_input(self):
        states = [router.new(REQUEST)]
        states += [router.advance(states[0], CANDIDATE), router.advance(states[0], NEED)]
        no_alternative = {k: v for k, v in CANDIDATE['decisions'][0].items() if k != 'alternative'}
        malformed = [None, [], '', 1, {}, {'status': []}, {'status': 'DONE'},
                     {**CANDIDATE, 'summary': ''},
                     {**CANDIDATE, 'summary': '  '},
                     {**CANDIDATE, 'summary': 123},
                     {**CANDIDATE, 'next': 'DONE'},
                     {**CANDIDATE, 'criteria': []},
                     {**CANDIDATE, 'decisions': [no_alternative]},
                     {**CANDIDATE, 'decisions': [{**CANDIDATE['decisions'][0], 'revisit': ''}]},
                     {**CANDIDATE, 'decisions': [{'id': 'D1', 'choice': 'x', 'basis': 'x', 'alternative': 'x', 'tradeoff': 'x', 'revisit': 'x'}, {'id': 'D1', 'choice': 'x', 'basis': 'x', 'alternative': 'x', 'tradeoff': 'x', 'revisit': 'x'}]},
                     {**NEED, 'type': 'choice'},
                     {k: v for k, v in NEED.items() if k != 'witness'},
                     {'status': 'blocked', 'question': 'q', 'needs': None},
                     {'status': 'resolved', 'answer': 'x', 'basis': ''},
                     {k: v for k, v in PASS.items() if k != 'defeater'},
                     {**PASS, 'basis': 'bad\x00text'},
                     {'status': 'revise', 'gaps': []},
                     {'status': 'revise', 'gaps': [{**REVISE['gaps'][0], 'check': 'style'}]}]
        for state in states:
            for result in malformed:
                with self.subTest(prompt=state['prompt'], result=result):
                    before = deepcopy(state)
                    with self.assertRaises(DispatchError):
                        router.advance(state, result)
                    self.assertEqual(state, before)

    def test_corrupt_checkpoint_fields_fail_cleanly(self):
        good = router.new(REQUEST)
        for field in good:
            for value in (None, [], {}, True, 99):
                with self.subTest(field=field, value=value):
                    bad = {**good, field: value}
                    if value == good[field] and type(value) is type(good[field]):
                        continue
                    # None is valid for the optional objects.
                    if field in ('need', 'blocker', 'candidate', 'review') and value is None:
                        continue
                    with self.assertRaises(DispatchError):
                        router.validate(bad)
        for bad in ({}, {**good, 'extra': 'no'},
                    {**good, 'run_id': '../escape'}, {**good, 'status': 'complete'},
                    {**good, 'prompt': 'review'}, {**good, 'prompt': 'resolve'},
                    {**good, 'status': 'blocked'}):
            with self.assertRaises(DispatchError):
                router.validate(bad)
        with self.assertRaisesRegex(DispatchError, 'legacy'):
            router.validate({**good, 'schema_version': 1})


if __name__ == '__main__':
    unittest.main()
