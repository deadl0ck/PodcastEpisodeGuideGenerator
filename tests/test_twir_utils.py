"""
Unit tests for twir_utils.py

Covers the three pure, side-effect-free utility methods:
  - TWIRUtils.extract_episode_number
  - TWIRUtils.tidy_up_title
  - TWIRUtils.extract_description
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from podcasts.twir.twir_utils import TWIRUtils


class TestExtractEpisodeNumber(unittest.TestCase):
    def test_standard_twir_podcast_format(self):
        num, marker = TWIRUtils.extract_episode_number("This Week in Retro Podcast 123 - Some Title")
        self.assertEqual(num, 123)

    def test_twir_ep_format(self):
        num, marker = TWIRUtils.extract_episode_number("TWiR Ep 42 | A Title")
        self.assertEqual(num, 42)

    def test_twir_episode_format(self):
        num, marker = TWIRUtils.extract_episode_number("TWiR Episode 7 - Retro Stuff")
        self.assertEqual(num, 7)

    def test_twir_podcast_abbreviated(self):
        num, marker = TWIRUtils.extract_episode_number("TWiR Podcast 200 - Anniversary Special")
        self.assertEqual(num, 200)

    def test_no_match_returns_minus_one(self):
        num, marker = TWIRUtils.extract_episode_number("Some Random YouTube Video")
        self.assertEqual(num, -1)
        self.assertEqual(marker, "")

    def test_returns_tuple(self):
        result = TWIRUtils.extract_episode_number("TWiR Ep 10 | Title")
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

    def test_episode_number_is_int(self):
        num, _ = TWIRUtils.extract_episode_number("TWiR Ep 99 | Title")
        self.assertIsInstance(num, int)


class TestTidyUpTitle(unittest.TestCase):
    def test_strips_episode_marker_with_pipe(self):
        title = "TWiR Ep 42 | Some Great Title"
        result = TWIRUtils.tidy_up_title(title)
        self.assertEqual(result, "Some Great Title")

    def test_strips_episode_marker_with_dash(self):
        title = "This Week in Retro Podcast 10 - A Retro Show"
        result = TWIRUtils.tidy_up_title(title)
        self.assertEqual(result, "A Retro Show")

    def test_strips_leading_pipe(self):
        # Some titles have the marker at the end and a leading pipe after stripping
        title = "Great Title | TWiR Ep 5"
        result = TWIRUtils.tidy_up_title(title)
        self.assertEqual(result, "Great Title")

    def test_no_marker_returns_original(self):
        title = "Some Random Title With No Marker"
        result = TWIRUtils.tidy_up_title(title)
        self.assertEqual(result, title)

    def test_returns_string(self):
        result = TWIRUtils.tidy_up_title("TWiR Ep 1 | Title")
        self.assertIsInstance(result, str)


class TestExtractDescription(unittest.TestCase):
    def test_returns_first_meaningful_line(self):
        desc = "This is the show description.\n\nSome sponsor info."
        result = TWIRUtils.extract_description(desc)
        self.assertEqual(result, "This is the show description.")

    def test_strips_ignored_lines(self):
        desc = "Yellow On Blue!\nActual description here."
        result = TWIRUtils.extract_description(desc)
        self.assertEqual(result, "Actual description here.")

    def test_skips_ad_marker_line(self):
        # Lines starting with 🛠 are ad markers; next line should be used instead
        desc = "🛠 Some sponsor content\nActual description here."
        result = TWIRUtils.extract_description(desc)
        self.assertEqual(result, "Actual description here.")

    def test_empty_first_line_returns_placeholder(self):
        result = TWIRUtils.extract_description("   \n\n   ")
        self.assertEqual(result, "[No detailed show notes for this episode]")

    def test_trophy_line_returns_placeholder(self):
        result = TWIRUtils.extract_description("🏆 Some trophy content")
        self.assertEqual(result, "[No detailed show notes for this episode]")

    def test_strips_whitespace_from_result(self):
        result = TWIRUtils.extract_description("  Trimmed description.  ")
        self.assertEqual(result, "Trimmed description.")

    def test_returns_string(self):
        result = TWIRUtils.extract_description("Some description.")
        self.assertIsInstance(result, str)


if __name__ == "__main__":
    unittest.main()
