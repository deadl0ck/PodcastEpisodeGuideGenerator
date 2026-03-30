import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest

from renderers.toc_renderer import TWIRTocRenderer, ZTTPTocRenderer


class _Episode:
    def __init__(self, episode_number: int, title: str):
        self.episode_number = episode_number
        self.title = title


class TestTWIRTocRenderer(unittest.TestCase):
    def test_build_entries_prepends_qow_link(self):
        renderer = TWIRTocRenderer("QOW List")
        episodes = [_Episode(2, "Episode Two"), _Episode(1, "Episode One")]

        entries = renderer.build_entries(episodes)

        self.assertEqual(entries[0], ("Jump to Question of the Week List", "QOW List"))
        self.assertEqual(entries[1], ("2 - Episode Two", 2))
        self.assertEqual(entries[2], ("1 - Episode One", 1))


class TestZTTPTocRenderer(unittest.TestCase):
    def test_build_entries_prepends_game_list_link(self):
        renderer = ZTTPTocRenderer("GAMES_LIST")
        episodes = [_Episode(3, "Three")]

        def formatter(input_episodes, input_crapverts):
            return [("formatted", "bookmark")]

        entries = renderer.build_entries(episodes, formatter=formatter, crapverts={})

        self.assertEqual(entries[0], ("Jump to Game Review List", "GAMES_LIST"))
        self.assertEqual(entries[1], ("formatted", "bookmark"))

    def test_build_entries_delegates_to_formatter(self):
        renderer = ZTTPTocRenderer("GAMES_LIST")
        episodes = [_Episode(3, "Three")]

        called = {"count": 0}

        def formatter(input_episodes, input_crapverts):
            called["count"] += 1
            self.assertIs(input_episodes, episodes)
            self.assertEqual(input_crapverts, {3: "x"})
            return [("formatted", "bookmark")]

        entries = renderer.build_entries(episodes, formatter=formatter, crapverts={3: "x"})

        self.assertEqual(called["count"], 1)
        self.assertEqual(entries[0], ("Jump to Game Review List", "GAMES_LIST"))
        self.assertEqual(entries[1], ("formatted", "bookmark"))

    def test_build_entries_requires_callable_formatter(self):
        renderer = ZTTPTocRenderer("GAMES_LIST")
        with self.assertRaises(ValueError):
            renderer.build_entries([], formatter=None, crapverts={})


if __name__ == "__main__":
    unittest.main()
