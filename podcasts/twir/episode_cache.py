from __future__ import annotations

import json
import os

from podcasts.twir.episode import Episode


class TWIREpisodeCache:
    """Simple JSON-backed episode cache for TWIR metadata."""

    @staticmethod
    def load(cache_path: str) -> list[Episode]:
        if not os.path.exists(cache_path):
            return []

        with open(cache_path, "r", encoding="utf-8") as handle:
            raw_items = json.load(handle)

        episodes: list[Episode] = []
        for item in raw_items:
            episodes.append(
                Episode(
                    title=item["title"],
                    description=item["description"],
                    episode_number=int(item["episode_number"]),
                    publish_date=item["publish_date"],
                    image_url=item["image_url"],
                    video_url=item["video_url"],
                    mp3_url=item["mp3_url"],
                    sortable_date=item["sortable_date"],
                )
            )
        return episodes

    @staticmethod
    def save(cache_path: str, episodes: list[Episode]) -> None:
        payload = []
        for episode in episodes:
            payload.append(
                {
                    "title": episode.title,
                    "description": episode.description,
                    "episode_number": episode.episode_number,
                    "publish_date": episode.publish_date,
                    "image_url": episode.image_url,
                    "video_url": episode.video_url,
                    "mp3_url": episode.mp3_url,
                    "sortable_date": episode.sortable_date,
                }
            )

        with open(cache_path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=True)
