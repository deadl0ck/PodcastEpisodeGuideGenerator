import unittest

from podcasts.rgds.episode import Episode
from podcasts.rgds.text_utils import RGDSTextUtils


class TestRGDSEpisode(unittest.TestCase):
    def test_extract_episode_number_with_episode_prefix(self):
        value = Episode.extract_episode_number("RGDS Episode 263 - Pac-Man")
        self.assertEqual(value, 263)

    def test_extract_episode_number_with_fallback_number(self):
        value = Episode.extract_episode_number("RGDS 271 Retro News")
        self.assertEqual(value, 271)

    def test_extract_episode_number_without_number(self):
        value = Episode.extract_episode_number("RGDS Special")
        self.assertEqual(value, -1)


class TestRGDSTextUtils(unittest.TestCase):
    def test_normalize_title_replaces_non_breaking_hyphen(self):
        value = RGDSTextUtils.normalize_title("Tolkien's Games of Middle\u2011Earth Special")
        self.assertEqual(value, "Tolkien's Games of Middle-Earth Special")

    def test_normalize_title_falls_back_for_empty(self):
        value = RGDSTextUtils.normalize_title("")
        self.assertEqual(value, "Untitled Episode")


if __name__ == "__main__":
    unittest.main()
