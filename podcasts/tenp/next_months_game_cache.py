from __future__ import annotations

import os
import pickle


class NextMonthsGameCache:
    NO_GAME = "NOT FOUND"

    def __init__(self, cache_file: str):
        self.game_dict: dict[int, str] = {}
        self.cache_file = cache_file
        self._read_cache_pickle_file(cache_file)

    def get_next_months_game(self, episode_number: int) -> str:
        return self.game_dict.get(episode_number, NextMonthsGameCache.NO_GAME)

    def add_game_to_cache(self, episode_number: int, game_title: str) -> None:
        self.game_dict[episode_number] = game_title

    def _read_cache_pickle_file(self, cache_file: str) -> None:
        if not os.path.exists(cache_file):
            return
        try:
            with open(cache_file, "rb") as cache_handle:
                self.game_dict = pickle.load(cache_handle)
        except (pickle.PickleError, EOFError):
            self.game_dict = {}

    def save(self) -> None:
        with open(self.cache_file, "wb") as cache_handle:
            pickle.dump(self.game_dict, cache_handle)

    def delete_entry(self, episode_number: int) -> None:
        self.game_dict.pop(episode_number, None)
        self.save()
