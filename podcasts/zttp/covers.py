import os
import pickle
import re
import logging

from bs4 import BeautifulSoup

from podcasts.zttp.html_utils import HTMLUtils
from podcasts.zttp.page_constants import ZZAP_CACHE_LOCATION

BASE_COVERS_URL = "https://www.zzap64.co.uk/"
END_COVER = 90
logger = logging.getLogger(__name__)


class Covers:
    def __init__(self):
        self.cover_urls = []
        for i in range(1, END_COVER + 1):
            self.cover_urls.append(f'{BASE_COVERS_URL}/zzap{i}/zzap{i}.html')

    def get_covers(self) -> dict:
        if os.path.exists(ZZAP_CACHE_LOCATION):
            with open(ZZAP_CACHE_LOCATION, 'rb') as f:
                episode_cache = pickle.load(f)
            if Covers.__is_valid_cover_cache(episode_cache):
                return episode_cache

        cover_data = {}
        logger.info('Building ZTTP cover cache from source pages...')
        for url in self.cover_urls:
            cover_url, issue = Covers.__get_cover(url)
            if issue and cover_url:
                cover_data[issue] = cover_url
        logger.info('Collected %s ZTTP cover entries', len(cover_data))

        if Covers.__is_valid_cover_cache(cover_data):
            with open(ZZAP_CACHE_LOCATION, 'wb') as f:
                pickle.dump(cover_data, f)

        return cover_data

    @staticmethod
    def __is_valid_cover_cache(cache_data: dict) -> bool:
        if not isinstance(cache_data, dict) or not cache_data:
            return False

        for issue, url in cache_data.items():
            if not isinstance(issue, str) or not issue.strip():
                return False
            if not isinstance(url, str) or not url.startswith("http"):
                return False
        return True

    @staticmethod
    def __get_cover(url: str) -> tuple:
        cover_url = ""
        month_year = ""

        current_html = HTMLUtils.get_html_from_url(url)
        soup = BeautifulSoup(current_html, 'html.parser')

        images = soup.find_all("img")
        for image in images:
            link = image.get("src")
            if link is not None and link.startswith("../zzapcovers"):
                if link == "../zzapcovers/tni50jun89.jpg":
                    month_year = "June 1989"

                link = link.replace("tni", "i")
                link = link.replace("../", BASE_COVERS_URL)
                cover_url = link
                alt = image.get("alt")
                if alt is not None and alt.startswith("Issue"):
                    issue = re.findall(" [A-Z].+ \\d{4}", alt)
                    month_year = issue[0].strip()
                break
        return cover_url, month_year
