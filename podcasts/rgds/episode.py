from __future__ import annotations

import re

from podcasts.common.models import BasePodcastEpisode


class Episode(BasePodcastEpisode):
    """RGDS episode model normalized from Spotify episode payloads."""

    def __init__(
        self,
        spotify_id: str,
        title: str,
        link: str,
        description: str,
        published: str,
        summary: str,
        duration: str,
        mp3: str,
        html_content: str,
        episode_image: str,
    ):
        super().__init__(title, link, description, published, summary, duration, mp3, html_content, episode_image)
        self.spotify_id = spotify_id

    @property
    def bookmark(self) -> str:
        return f"rgds-{self.spotify_id}"

    @staticmethod
    def extract_episode_number(text) -> int:
        if not text:
            return -1
        match = re.search(r"(?:ep(?:isode)?\s*[-:#]?\s*)(\d+)\b", text, re.IGNORECASE)
        if match is not None:
            return int(match.group(1))

        first_number = re.search(r"\b(\d{1,4})\b", text)
        if first_number is None:
            return -1
        return int(first_number.group(1))
