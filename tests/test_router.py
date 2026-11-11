from copy import deepcopy
import unittest

from support import REQUEST, CANDIDATE, PASS, NEED, BLOCKED, RESOLVED, DispatchError
from engine import router


class RouterTests(unittest.TestCase):
    def test_zero_gap_path_needs_only_candidate_and_review(self):
        draft = router.new(REQUEST)
        review = router.advance(draft, CANDIDATE)
        final = router.advance(review, PASS)
        self.assertEqual((draft['prompt'], review['prompt'], final['status']),
                         ('draft', 'review', 'publishing'))
        self.assertEqual(draft['request'], final['request'])
        self.assertEqual(final['candidate'], CANDIDATE['text'])
        self.assertNotEqual(draft['ticket'], review['ticket'])
        self.assertEqual(review['ticket'], final['ticket'])
        self.assertEqual(draft['candidate'], '')  # Pure transitions.

    def test_every_route_including_material_review_need(self):
        draft = router.new(REQUEST)
        for source in (draft, router.advance(draft, CANDIDATE)):
            resolve = router.advance(source, NEED)
            blocked = router.advance(resolve, BLOCKED)
            self.assertEqual(blocked['status'], 'blocked')
            self.assertEqual(blocked['need'], {k: NEED[k] for k in ('question', 'consequence')})
            redraft = router.advance(blocked, RESOLVED)
            self.assertEqual(redraft['prompt'], 'draft')
            self.assertIsNone(redraft['need'])
            self.assertIsNone(redraft['blocker'])
            self.assertIn(RESOLVED['basis'], redraft['basis'])
            self.assertEqual(router.advance(redraft, CANDIDATE)['prompt'], 'review')
        review = router.advance(draft, CANDIDATE)
        redraft = router.advance(review, {'status': 'revise', 'feedback': 'Preserve the original greeting.'})
        self.assertEqual(redraft['prompt'], 'draft')
        self.assertEqual(redraft['candidate'], CANDIDATE['text'])
        self.assertIn('original greeting', redraft['feedback'])
        with self.assertRaises(DispatchError):
            router.advance(redraft, PASS)  # Cannot approve a draft or reuse an old review.

    def test_invalid_results_never_mutate_the_input(self):
        states = [router.new(REQUEST)]
        states += [router.advance(states[0], CANDIDATE), router.advance(states[0], NEED)]
        malformed = [None, [], '', 1, {}, {'status': []}, {'status': 'DONE'},
                     {'status': 'candidate', 'text': ''},
                     {'status': 'candidate', 'text': '  '},
                     {'status': 'candidate', 'text': 123},
                     {'status': 'candidate', 'text': 'x', 'next': 'DONE'},
                     {'status': 'need', 'question': 'q'},
                     {'status': 'blocked', 'question': 'q', 'needs': None},
                     {'status': 'resolved', 'text': 'x', 'basis': ''},
                     {'status': 'pass', 'basis': 'bad\x00text'}]
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
                    # None is valid for the two optional objects.
                    if field in ('need', 'blocker') and value is None:
                        continue
                    with self.assertRaises(DispatchError):
                        router.validate(bad)
        for bad in ({}, {**good, 'extra': 'no'},
                    {**good, 'run_id': '../escape'}, {**good, 'status': 'complete'},
                    {**good, 'prompt': 'review'}, {**good, 'prompt': 'resolve'},
                    {**good, 'status': 'blocked'}):
            with self.assertRaises(DispatchError):
                router.validate(bad)


if __name__ == '__main__':
    unittest.main()
