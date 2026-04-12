import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import patch

from run_guides import _parse_podcast_selection


class TestRunGuidesSelection(unittest.TestCase):
    def test_single_value(self):
        self.assertEqual(_parse_podcast_selection("twir"), ["twir"])

    def test_multiple_values(self):
        self.assertEqual(_parse_podcast_selection("twir,zttp"), ["twir", "zttp"])

    def test_multiple_values_with_ra(self):
        self.assertEqual(_parse_podcast_selection("twir,ra"), ["twir", "ra"])

    def test_multiple_values_with_tenp(self):
        self.assertEqual(_parse_podcast_selection("twir,10p"), ["twir", "10p"])

    def test_all_expands(self):
        self.assertEqual(_parse_podcast_selection("all"), ["twir", "zttp", "ra", "10p"])

    def test_duplicates_removed(self):
        self.assertEqual(_parse_podcast_selection("twir,all,twir"), ["twir", "zttp", "ra", "10p"])

    def test_unknown_raises(self):
        with self.assertRaises(ValueError):
            _parse_podcast_selection("unknown")


class TestRunGuidesArgs(unittest.TestCase):
    @patch("run_guides.subprocess.run")
    def test_test_mode_env_is_set(self, mock_run):
        import run_guides

        mock_run.return_value.returncode = 0
        with patch("sys.argv", ["run_guides.py", "--podcasts", "twir", "--test", "--test-count", "3"]):
            exit_code = run_guides.main()

        self.assertEqual(exit_code, 0)
        self.assertTrue(mock_run.called)
        env = mock_run.call_args.kwargs["env"]
        self.assertEqual(env.get("GUIDE_TEST_RUN"), "true")
        self.assertEqual(env.get("GUIDE_TEST_COUNT"), "3")


if __name__ == "__main__":
    unittest.main()
