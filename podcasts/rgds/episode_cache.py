from __future__ import annotations

import json
import os

from podcasts.rgds.episode import Episode


class RGDSEpisodeCache:
    """JSON-backed cache for RGDS episode metadata."""

    @staticmethod
    def load(cache_path: str) -> dict[str, Episode]:
        if not os.path.exists(cache_path):
            return {}

        with open(cache_path, "r", encoding="utf-8") as handle:
            raw_items = json.load(handle)

        episodes_by_id: dict[str, Episode] = {}
        for item in raw_items:
            episode = Episode(
                spotify_id=item["spotify_id"],
                title=item["title"],
                link=item["link"],
                description=item["description"],
                published=item["published"],
                summary=item["summary"],
                duration=item["duration"],
                mp3=item["mp3"],
                html_content=item.get("html_content", ""),
                episode_image=item["episode_image"],
            )
            episodes_by_id[episode.spotify_id] = episode

        return episodes_by_id

    @staticmethod
    def save(cache_path: str, episodes: dict[str, Episode]) -> None:
        payload = []
        for spotify_id, episode in episodes.items():
            payload.append(
                {
                    "spotify_id": spotify_id,
                    "title": episode.title,
                    "link": episode.page_url,
                    "description": episode.description,
                    "published": episode.published_display,
                    "summary": episode.summary,
                    "duration": episode.duration,
                    "mp3": episode.audio_url,
                    "html_content": episode.html_content,
                    "episode_image": episode.image_url,
                }
            )

        with open(cache_path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=True)
