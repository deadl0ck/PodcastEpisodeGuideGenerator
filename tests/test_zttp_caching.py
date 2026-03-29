import os
import pickle
import tempfile
import unittest
from unittest.mock import patch


class TestZTTPCRapvertsCaching(unittest.TestCase):
    def test_uses_cache_when_present(self):
        try:
            from podcasts.zttp.crapverts import Crapverts
            from podcasts.zttp.episode_crapverts import EpisodeCrapvert
        except ModuleNotFoundError as exc:
            if exc.name == "bs4":
                self.skipTest("BeautifulSoup dependency is not installed in this test environment")
            raise

        with tempfile.TemporaryDirectory() as tmp_dir:
            cache_file = os.path.join(tmp_dir, "crapverts_cache.pkl")
            cached_data = {12: EpisodeCrapvert("Episode 12", ["https://example.com/a.jpg"])}
            with open(cache_file, "wb") as f:
                pickle.dump(cached_data, f)

            with patch("podcasts.zttp.crapverts.CRAPVERTS_CACHE_LOCATION", cache_file), \
                    patch("podcasts.zttp.crapverts.HTMLUtils.get_html_from_url") as mock_fetch:
                loaded = Crapverts.get_all_crapverts()

            self.assertIn(12, loaded)
            self.assertEqual(loaded[12].get_heading(), "Episode 12")
            mock_fetch.assert_not_called()


if __name__ == "__main__":
    unittest.main()
