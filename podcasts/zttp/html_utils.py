from bs4 import BeautifulSoup
import logging

from podcasts.common.html_utils import BaseHTMLUtils


logger = logging.getLogger(__name__)


class HTMLUtils(BaseHTMLUtils):
    @staticmethod
    def get_all_pages(start_url: str) -> list:
        next_page_url = start_url
        all_pages = [start_url]

        while next_page_url != "":
            current_html = HTMLUtils.get_html_from_url(next_page_url)
            next_page_url = ""
            soup = BeautifulSoup(current_html, 'html.parser')
            my_divs = soup.find_all("div", {"class": "wp-pagenavi"})
            for div in my_divs:
                anchors = div.find_all("a")
                for anchor in anchors:
                    anchor_class = anchor.get("class") or []
                    if "nextpostslink" in anchor_class:
                        next_page_url = anchor.get("href")
                        all_pages.append(next_page_url)
                        break
                if next_page_url != "":
                    break

        return all_pages

    @staticmethod
    def get_details(url: str) -> tuple:
        description = None
        mp3 = None
        current_html = HTMLUtils.get_html_from_url(url)
        soup = BeautifulSoup(current_html, 'html.parser')

        my_divs = soup.find_all("div", {"class": "entry-content simple-grid-clearfix"})
        description = ""
        for div in my_divs:
            paragraphs = div.find_all("p")
            for p in paragraphs:
                description = p.get_text().strip()
                if description != "":
                    break

            mp3 = None
            anchors = div.find_all("a")
            for a in anchors:
                link = a.get("href")
                if link is not None and (link.endswith(".mp3") or "drive.google.com" in link):
                    mp3 = link
                    break

        if description == "":
            logger.warning('No description found for URL: %s', url)

        cover = None
        my_divs = soup.find_all("div", {"class": "wp-block-image is-style-default"})
        if len(my_divs) == 0:
            my_divs = soup.find_all("div", {"class": "wp-block-image"})
        if len(my_divs) == 0:
            my_divs = soup.find_all("div", {"class": "entry-content simple-grid-clearfix"})
        for div in my_divs:
            images = div.find_all("img")
            if len(images) > 0:
                cover = images[0].get("src")
                if cover is not None:
                    break

        if cover is None:
            logger.warning('No cover image found for URL: %s', url)

        return description, mp3, cover
