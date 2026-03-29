from bs4 import BeautifulSoup
import requests
import re

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
    @staticmethod
    def replace_title_text(episodes: list, crapverts: dict) -> list:
        episode_names = []
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
        return BasePodcastUtils.strip_time_suffix(data)

    @staticmethod
    def extract_games_info(content_html: str) -> list:
        games_this_episode = []
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
    def extract_game_award_text(text: str) -> str:
        for value in GAME_AWARD_TEXT:
            if value in text:
                return value
        return ""
