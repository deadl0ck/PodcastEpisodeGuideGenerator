"""Tests for the RA episode model, focusing on episode number extraction."""

import unittest

from podcasts.ra.episode import Episode


class TestExtractEpisodeNumber(unittest.TestCase):
    """Episode.extract_episode_number parses numbers from title strings."""

    def test_standard_episode_format(self):
        self.assertEqual(Episode.extract_episode_number("Retro Asylum Episode 123 - Games"), 123)

    def test_bytesize_episode_format(self):
        self.assertEqual(Episode.extract_episode_number("Bytesize Episode 7 - Spectrum"), 7)

    def test_bytesize_with_extra_whitespace(self):
        self.assertEqual(Episode.extract_episode_number("Bytesize  Episode 42"), 42)

    def test_case_insensitive_episode(self):
        self.assertEqual(Episode.extract_episode_number("EPISODE 99"), 99)

    def test_no_episode_number_returns_minus_one(self):
        self.assertEqual(Episode.extract_episode_number("A random title with no number"), -1)

    def test_bare_number_not_matched(self):
        # Numbers not preceded by "episode" should not match.
        self.assertEqual(Episode.extract_episode_number("Show 5 - Retro gaming"), -1)

    def test_large_episode_number(self):
        self.assertEqual(Episode.extract_episode_number("Episode 366 - Final episode"), 366)


class TestEpisodeConstruction(unittest.TestCase):
    """Episode fields are mapped correctly from constructor arguments."""

    def setUp(self):
        self.ep = Episode(
            url="https://retroasylum.com/episode-1/",
            cover="https://example.com/cover.jpg",
            title="Episode 1 - Test",
            description="A test episode.",
            mp3="https://example.com/audio.mp3",
        )

    def test_page_url(self):
        self.assertEqual(self.ep.page_url, "https://retroasylum.com/episode-1/")

    def test_image_url(self):
        self.assertEqual(self.ep.image_url, "https://example.com/cover.jpg")

    def test_audio_url(self):
        self.assertEqual(self.ep.audio_url, "https://example.com/audio.mp3")

    def test_title(self):
        self.assertEqual(self.ep.title, "Episode 1 - Test")

    def test_description(self):
        self.assertEqual(self.ep.description, "A test episode.")

    def test_episode_number_parsed_from_title(self):
        self.assertEqual(self.ep.episode_number, 1)

    def test_source_url_matches_page_url(self):
        self.assertEqual(self.ep.source_url, "https://retroasylum.com/episode-1/")


if __name__ == "__main__":
    unittest.main()
