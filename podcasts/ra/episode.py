"""Retro Asylum episode model."""

from __future__ import annotations

import re

from podcasts.common.models import BaseMediaEpisode


class Episode(BaseMediaEpisode):
    """Concrete RA episode with source URL identity for cache ordering."""

    def __init__(self, url: str, cover: str, title: str, description: str, mp3: str):
        super().__init__(
            title=title,
            description=description,
            episode_number=self.extract_episode_number(title),
            published_display="",
            image_url=cover,
            page_url=url,
            audio_url=mp3,
        )
        self.source_url = url

    @staticmethod
    def extract_episode_number(text: str) -> int:
        """Parse the episode number from a title, returning -1 if not found."""
        match = re.search(r"(?:episode|bytesize\s+episode)\s+(\d+)", text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return -1

    def print_out(self) -> None:
        self.log_fields([
            ("Title", self.title),
            ("Episode Number", self.episode_number),
            ("Page URL", self.page_url),
            ("Cover", self.image_url),
            ("MP3", self.audio_url),
        ])
