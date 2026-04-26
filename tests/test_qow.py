"""
Unit tests for qow/question_of_the_week.py and qow/qow_cache.py

Covers:
  - QOW.__init__: episode number resolution from QUESTIONS_AND_EPISODES lookup
  - QOW episode 328 → 238 correction
  - QOWCache.__load_cache: returns empty dict when cache file doesn't exist
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import unittest.mock
import pickle
import tempfile

try:
    from podcasts.twir.qow.question_of_the_week import QOW, QUESTIONS_AND_EPISODES
except ImportError as e:
    raise unittest.SkipTest(f"Skipping test_qow: missing dependency ({e})")
from podcasts.common.page_constants import NULL_LINK


class TestQOWInit(unittest.TestCase):
    def test_explicit_episode_number_used_directly(self):
        q = QOW("Title", "Question?", 55, NULL_LINK)
        self.assertEqual(q.episode_number, 55)

    def test_none_episode_number_resolved_from_lookup(self):
        # "Is Zelda an RPG?" maps to episode 29 in QUESTIONS_AND_EPISODES
        q = QOW("Title", "Is Zelda an RPG?", None, NULL_LINK)
        self.assertEqual(q.episode_number, 29)

    def test_none_episode_number_not_in_lookup_returns_minus_one(self):
        q = QOW("Title", "A question that has no known mapping.", None, NULL_LINK)
        self.assertEqual(q.episode_number, -1)

    def test_episode_328_corrected_to_238(self):
        # Known data-entry correction: episode 328 should be 238
        q = QOW("Title", "Question?", 328, NULL_LINK)
        self.assertEqual(q.episode_number, 238)

    def test_title_and_question_and_url_stored(self):
        q = QOW("My Title", "My Question?", 10, "https://reddit.com/r/test")
        self.assertEqual(q.title, "My Title")
        self.assertEqual(q.question, "My Question?")
        self.assertEqual(q.url, "https://reddit.com/r/test")

    def test_all_lookup_questions_resolve_correctly(self):
        for question, expected_ep in QUESTIONS_AND_EPISODES.items():
            q = QOW("Title", question, None, NULL_LINK)
            self.assertEqual(
                q.episode_number, expected_ep,
                msg=f"Failed for question: {question!r}"
            )


class TestQOWCacheLoadCache(unittest.TestCase):
    def test_missing_file_returns_empty_dict(self):
        from podcasts.twir.qow.qow_cache import QOWCache
        with tempfile.TemporaryDirectory() as tmp:
            non_existent = os.path.join(tmp, "no_such_file.pkl")
            with unittest.mock.patch("podcasts.twir.qow.qow_cache.CACHE_FILE", non_existent):
                result = QOWCache._QOWCache__load_cache()
                self.assertEqual(result, {})

    def test_existing_cache_file_loaded(self):
        from podcasts.twir.qow.qow_cache import QOWCache
        q = QOW("Title", "Is Zelda an RPG?", 29, NULL_LINK)
        data = {29: q}
        with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as f:
            pickle.dump(data, f)
            tmp_path = f.name
        try:
            with unittest.mock.patch("podcasts.twir.qow.qow_cache.CACHE_FILE", tmp_path):
                result = QOWCache._QOWCache__load_cache()
                self.assertIn(29, result)
                self.assertEqual(result[29].episode_number, 29)
        finally:
            os.unlink(tmp_path)


if __name__ == "__main__":
    unittest.main()
