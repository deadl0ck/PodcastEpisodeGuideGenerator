from bs4 import BeautifulSoup
import os
import pickle
import re
import sys
import logging

from podcasts.zttp.episode_crapverts import EpisodeCrapvert
from podcasts.zttp.html_utils import HTMLUtils
from podcasts.zttp.page_constants import CRAPVERTS_CACHE_LOCATION


logger = logging.getLogger(__name__)


class Crapverts:
    BASE_URL = "https://zappedtothepast.com/classic-crapverts/"

    @staticmethod
    def __extract_episode_number(episode_text: str) -> int:
        match = re.search(r'\d+', episode_text)
        if match:
            return int(match.group())
        return -1

    @staticmethod
    def get_all_crapverts() -> dict:
        if os.path.exists(CRAPVERTS_CACHE_LOCATION):
            with open(CRAPVERTS_CACHE_LOCATION, 'rb') as f:
                return pickle.load(f)

        current_html = HTMLUtils.get_html_from_url(Crapverts.BASE_URL)
        soup = BeautifulSoup(current_html, 'html.parser')

        headings = []
        episode_crapverts = {}

        all_headings = soup.find_all("h2", {"class": "wp-block-heading"})
        for heading in all_headings:
            headings.append(heading.text)

        all_image_objects = soup.find_all("div", {"class": "wp-block-jetpack-slideshow aligncenter"})

        if len(all_headings) != len(all_image_objects):
            logger.error("Array lengths for crapverts do not match - aborting")
            sys.exit(1)

        for i in range(len(all_image_objects)):
            heading = headings[i]
            current_image_object = all_image_objects[i]
            images = []
            unordered_lists = current_image_object.find_all("ul", {
                "class": "wp-block-jetpack-slideshow_swiper-wrapper"})
            for unordered_list in unordered_lists:
                list_items = unordered_list.find_all("li", {"class": "wp-block-jetpack-slideshow_slide"})
                for list_item in list_items:
                    current_crapvert_images = list_item.find_all("img")
                    for current_crapvert_image in current_crapvert_images:
                        images.append(current_crapvert_image.get("src"))

            episode_crapverts[Crapverts.__extract_episode_number(heading)] = EpisodeCrapvert(heading, images)

        with open(CRAPVERTS_CACHE_LOCATION, 'wb') as f:
            pickle.dump(episode_crapverts, f)

        return episode_crapverts
