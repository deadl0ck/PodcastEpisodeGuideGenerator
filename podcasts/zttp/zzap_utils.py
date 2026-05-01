"""ZTTP-specific parsing helpers for titles, dates, games, and cover images."""

from __future__ import annotations

from typing import Any

from bs4 import BeautifulSoup

import requests

from podcasts.common.podcast_utils import BasePodcastUtils
from podcasts.zttp.page_constants import COVER_IMAGE

GAME_AWARD_TEXT = [
    "Games covered in this episode:",
    "The running order of the awards",
    "Games covered in the episode:",
    "Game covered in this episode:",
    "Awards in this episode:",
    "Games reviewed in this special:",
]

TITLE_TEXT_START_REPLACEMENTS = [
    ("Zapped to the Past Presents - ", ""),
    ("Zapped to the Past  - ", ""),
    ("Zapped to the Past meet", "Meet"),
    ("Zapped to the Past - ", ""),
    ("Zapped to the Past", ""),
]


class ZzapUtils(BasePodcastUtils):
    """Utility methods for parsing ZTTP feed and web page data."""

    @staticmethod
    def replace_title_text(episodes: list[Any], crapverts: dict[int, Any]) -> list[tuple[str, str]]:
        """Return TOC-ready episode titles with ZTTP-specific title cleanup."""
        episode_names: list[tuple[str, str]] = []
        for curr_episode in episodes:
            title = curr_episode.title
            for replacement in TITLE_TEXT_START_REPLACEMENTS:
                if title.startswith(replacement[0]):
                    title = title.replace(replacement[0], replacement[1])
            extra = ''
            if curr_episode.episode_number in crapverts:
                extra = ' (With Crapverts!!)'

            episode_names.append((title.strip() + extra, curr_episode.title))
        return episode_names

    @staticmethod
    def extract_date_time(data: str) -> str:
        """Strip the time suffix from a published-date string."""
        return BasePodcastUtils.strip_time_suffix(data)

    @staticmethod
    def extract_games_info(content_html: str) -> list[str]:
        """Extract the list of game titles reviewed in an episode."""
        games_this_episode: list[str] = []
        soup = BeautifulSoup(content_html, "lxml")
        data = soup.find_all("li")
        if len(data) > 0:
            for item in data:
                if item.text.startswith("http"):
                    continue
                games_this_episode.append(item.text.replace("\xa0", ""))
        return games_this_episode

    @staticmethod
    def get_image_url(url: str) -> str:
        """Return the primary episode image URL from a ZTTP episode page."""
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            html_content = response.text
        else:
            return "!!! NO IMAGE FOUND !!!"
        soup = BeautifulSoup(html_content, "lxml")
        images = soup.find_all("img")
        if len(images) > 0:
            for image in images:
                img_src = image.get('src')
                if not img_src.endswith("1920x500.png") and \
                        not img_src.endswith("ZTTP_ORANGE_2k.png") and \
                        not img_src.endswith("iphone-app.png") and \
                        not img_src.endswith("android-app-sm.png"):
                    return img_src
        return COVER_IMAGE

    @staticmethod
    def format_duration(duration_str: str) -> str:
        """Convert a raw duration string in seconds to HH:MM format."""
        if not duration_str:
            return "00:00"
        seconds = int(duration_str.strip("'\""))
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours:02d}:{minutes:02d}"

    @staticmethod
    def extract_game_award_text(text: str) -> str:
        """Return the matching award/games heading text from HTML content."""
        for value in GAME_AWARD_TEXT:
            if value in text:
                return value
        return ""
