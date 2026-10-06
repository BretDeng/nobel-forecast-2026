import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from finalization import digest, verify_finalized
import fetch
import review


class FinalizationTests(unittest.TestCase):
    def test_sealed_snapshot_and_reviews_cannot_change(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'data').mkdir()
            snapshot = {'fetchedAt': '2026-10-05T08:35:00+00:00', 'pages': []}
            reviews = {'answer': {'reviewed': True}}
            final = {'snapshotHash': digest(snapshot), 'reviewsHash': digest(reviews)}
            (root / 'data/finalized.json').write_text(json.dumps({'medicine': final}))
            self.assertEqual(verify_finalized('medicine', root, snapshot, reviews), final)
            with self.assertRaises(ValueError):
                verify_finalized('medicine', root, {**snapshot, 'pages': [1]}, reviews)
            with self.assertRaises(ValueError):
                verify_finalized('medicine', root, snapshot, {})
            self.assertIsNone(verify_finalized('physics', root, {}, {}))

    def test_sealed_category_never_fetches_even_if_clock_is_before_cutoff(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'data').mkdir()
            (root / 'data/finalized.json').write_text('{"medicine": {"sealed": true}}')
            with patch.object(fetch, 'ROOT', root), patch.object(fetch, 'is_open', return_value=True), patch.object(fetch.subprocess, 'run') as run:
                self.assertEqual(fetch.sync_fetch(Path('/cli'), {'medicine'}), set())
                with self.assertRaises(fetch.DeadlineReached):
                    fetch.fetch(Path('/cli'), 'medicine', 'https://www.zhihu.com/question/1')
                run.assert_not_called()

    def test_explicit_review_selection_cannot_reopen_sealed_category(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'data').mkdir()
            (root / 'data/finalized.json').write_text('{"medicine": {"sealed": true}}')
            (root / 'data/reviews.json').write_text('{}')
            with patch.object(review, 'ROOT', root), patch.object(review, 'CATEGORIES', [('medicine', '医学', '', '1', 'M')]), patch.object(review.subprocess, 'run') as run:
                self.assertEqual(review.review_pending(Path('/cli'), True, {'medicine'})['calls'], 0)
                run.assert_not_called()
