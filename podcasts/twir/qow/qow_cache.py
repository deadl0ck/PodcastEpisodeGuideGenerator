# qow_cache.py
# Provides a simple pickle-based cache for Community Question of the Week data.
import pickle

from cache_paths import QOW_CACHE_FILE, ensure_cache_dirs

CACHE_FILE = QOW_CACHE_FILE


class QOWCache:
    def __init__(self):
        self.episodes_by_title = {}
        self.episodes = QOWCache.__load_cache()
        if not self.episodes:
            return

        for key in self.episodes.keys():
            title = self.episodes[key].title
            self.episodes_by_title[title] = self.episodes[key]

    @staticmethod
    def update_cache(episodes: dict) -> None:
        ensure_cache_dirs()
        with open(CACHE_FILE, 'wb') as f:
            pickle.dump(episodes, f)

    @staticmethod
    def __load_cache() -> dict:
        ensure_cache_dirs()
        try:
            with open(CACHE_FILE, 'rb') as f:
                episodes = pickle.load(f)
            return episodes
        except FileNotFoundError:
            return {}
