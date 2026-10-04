import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import deadlines
import fetch
import review


class DeadlineTests(unittest.TestCase):
    def test_cutoffs_in_hong_kong_time(self):
        hk = timezone(timedelta(hours=8))
        expected = {'medicine': '2026-10-05 16:30', 'physics': '2026-10-06 16:45',
                    'chemistry': '2026-10-07 16:45', 'literature': '2026-10-08 18:00',
                    'economics': '2026-10-12 16:45'}
        for key, value in expected.items():
            self.assertEqual(deadlines.cutoff(key).astimezone(hk).strftime('%Y-%m-%d %H:%M'), value)

    def test_boundary_and_other_prizes_still_open(self):
        stop = deadlines.cutoff('medicine')
        self.assertTrue(deadlines.is_open('medicine', stop - timedelta(microseconds=1)))
        self.assertFalse(deadlines.is_open('medicine', stop))
        self.assertTrue(deadlines.is_open('physics', stop))
        self.assertFalse(deadlines.is_open('medicine', stop + timedelta(days=1)))

    def test_frozen_fetch_never_calls_cli(self):
        with patch('deadlines.utc_now', return_value=deadlines.cutoff('medicine')), patch('fetch.subprocess.run') as run:
            with self.assertRaises(fetch.DeadlineReached):
                fetch.fetch(Path('/cli'), 'medicine', 'https://www.zhihu.com/question/1')
            run.assert_not_called()

    def test_cross_cutoff_collection_keeps_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            folder = root / 'data/snapshots'
            folder.mkdir(parents=True)
            original = b'{"fetchedAt":"old","pages":[]}'
            (folder / 'medicine.json').write_bytes(original)
            stop = deadlines.cutoff('medicine')
            late = {'fetchedAt': stop.isoformat(), 'pages': []}
            with patch.object(fetch, 'ROOT', root), patch.object(fetch, 'CATEGORIES', [('medicine', '医学', '', '1', '')]), patch('deadlines.utc_now', return_value=stop-timedelta(seconds=10)), patch('fetch.fetch', return_value=late):
                self.assertEqual(fetch.sync_fetch(Path('/cli')), set())
            self.assertEqual((folder / 'medicine.json').read_bytes(), original)

    def test_frozen_review_does_not_read_or_mutate_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'data').mkdir()
            original = '{"medicine":{}}'
            (root / 'data/reviews.json').write_text(original)
            with patch.object(review, 'ROOT', root), patch.object(review, 'CATEGORIES', [('medicine', '医学', '', '1', '')]), patch('deadlines.utc_now', return_value=deadlines.cutoff('medicine')), patch('review.subprocess.run') as run:
                result = review.review_pending(Path('/cli'), retry_uncertain=True)
            run.assert_not_called()
            self.assertEqual(result['calls'], 0)
            self.assertEqual((root / 'data/reviews.json').read_text(), original)


if __name__ == '__main__':
    unittest.main()
