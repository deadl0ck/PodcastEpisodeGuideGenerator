from __future__ import annotations

import re

from podcasts.common.models import BasePodcastEpisode


class Episode(BasePodcastEpisode):
    """Ten Pence Arcade episode model."""

    def __init__(self, title, link, description, published, summary, duration, mp3, html_content, episode_image):
        super().__init__(title, link, description, published, summary, duration, mp3, html_content, episode_image)
        self.ai_generated_image = False

    @staticmethod
    def extract_episode_number(text) -> int:
        match = re.search(r"Ten Pence Arcade\s*-\s*(\d+)\b", text)
        if match is None:
            return -1
        return int(match.group(1))
