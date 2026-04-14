import os
import tempfile
import unittest

from podcasts.rgds.episode import Episode
from podcasts.rgds.episode_cache import RGDSEpisodeCache


class TestRGDSEpisodeCache(unittest.TestCase):
    def test_save_and_load_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = os.path.join(tmp_dir, "episodes.json")
            expected = Episode(
                spotify_id="abc123",
                title="RGDS Episode 1",
                link="https://open.spotify.com/episode/abc123",
                description="Description",
                published="2026-01-01",
                summary="Summary",
                duration="01:02:03",
                mp3="https://open.spotify.com/episode/abc123",
                html_content="",
                episode_image="https://example.com/image.jpg",
            )

            RGDSEpisodeCache.save(path, {expected.spotify_id: expected})
            loaded = RGDSEpisodeCache.load(path)

            self.assertIn("abc123", loaded)
            self.assertEqual(loaded["abc123"].title, expected.title)
            self.assertEqual(loaded["abc123"].duration, expected.duration)


if __name__ == "__main__":
    unittest.main()
