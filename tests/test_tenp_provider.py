import os
import sys
import tempfile
import unittest
from unittest.mock import Mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from podcasts.tenp.episode import Episode
from podcasts.tenp.basic_ai import BasicAI
from podcasts.tenp.next_months_game_cache import NextMonthsGameCache
from podcasts.tenp.tenp_utils import TenPenceUtils


class TestTenPEpisode(unittest.TestCase):
    def test_extract_episode_number(self):
        value = Episode.extract_episode_number("Ten Pence Arcade - 210 Stuff")
        self.assertEqual(value, 210)

    def test_extract_episode_number_not_found(self):
        self.assertEqual(Episode.extract_episode_number("Special Episode"), -1)


class TestTenPUtils(unittest.TestCase):
    def test_replace_title_text(self):
        class _FakeEpisode:
            def __init__(self, title):
                self.title = title

        result = TenPenceUtils.replace_title_text([_FakeEpisode("Ten Pence Arcade - 200 Demo")])
        self.assertEqual(result, ["200 Demo"])

    def test_extract_leading_number(self):
        self.assertEqual(TenPenceUtils.extract_leading_number("210 A title"), 210)
        self.assertIsNone(TenPenceUtils.extract_leading_number("No number"))


class TestTenPNextMonthsCache(unittest.TestCase):
    def test_cache_read_write_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            cache_path = os.path.join(tmp_dir, "next_month_game_cache.pkl")
            cache = NextMonthsGameCache(cache_path)
            self.assertEqual(cache.get_next_months_game(200), NextMonthsGameCache.NO_GAME)

            cache.add_game_to_cache(200, "Ghosts 'n Goblins")
            cache.save()

            loaded = NextMonthsGameCache(cache_path)
            self.assertEqual(loaded.get_next_months_game(200), "Ghosts 'n Goblins")


class TestTenPBasicAI(unittest.TestCase):
    def test_invalid_key_error_falls_back_and_disables_for_run(self):
        ai = BasicAI()
        fake_client = Mock()
        fake_client.models.generate_content.side_effect = Exception("API_KEY_INVALID")
        ai._get_client = Mock(return_value=fake_client)

        first = ai.get_next_months_game("example")
        second = ai.get_next_months_game("example")

        self.assertEqual(first, "No Game")
        self.assertEqual(second, "No Game")
        self.assertEqual(fake_client.models.generate_content.call_count, 1)


if __name__ == "__main__":
    unittest.main()
