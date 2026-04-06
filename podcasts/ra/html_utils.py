"""Retro Asylum HTML scraping helpers."""

from __future__ import annotations

import logging

from bs4 import BeautifulSoup

from podcasts.common.html_utils import BaseHTMLUtils

logger = logging.getLogger(__name__)


class HTMLUtils(BaseHTMLUtils):
    """Scraping helpers for the Retro Asylum WordPress site."""

    @staticmethod
    def get_all_pages(start_url: str) -> list[str]:
        """Follow WordPress pagination to collect all episode listing page URLs."""
        next_page_url = start_url
        all_pages = [start_url]

        while next_page_url:
            current_html = HTMLUtils.get_html_from_url(next_page_url)
            next_page_url = ""
            soup = BeautifulSoup(current_html, "html.parser")
            for div in soup.find_all("div", {"class": "wp-pagenavi"}):
                for anchor in div.find_all("a"):
                    anchor_class = anchor.get("class") or []
                    if "nextpostslink" in anchor_class:
                        next_page_url = anchor.get("href") or ""
                        if next_page_url and next_page_url not in all_pages:
                            all_pages.append(next_page_url)
                        break
                if next_page_url:
                    break

        return all_pages

    @staticmethod
    def get_episodes_from_page(soup: BeautifulSoup, episode_urls: set[str]) -> list[tuple[str, str]]:
        """Extract (url, title) pairs from a listing page, stopping at already-cached URLs."""
        all_episodes: list[tuple[str, str]] = []
        blocks = soup.find_all(
            "div",
            {"class": "simple-grid-grid-post-thumbnail simple-grid-grid-post-block"},
        )

        for div in blocks:
            anchors = div.find_all("a")
            if not anchors:
                continue

            main_page = anchors[0].get("href")
            if not main_page:
                continue

            if main_page in episode_urls:
                # Pages are newest-first; once cached URL is encountered, older entries follow.
                return all_episodes

            title = ""
            images = div.find_all("img")
            if images:
                title = images[0].get("title") or ""

            if not title:
                logger.warning("Skipping RA tile with missing title: %s", main_page)
                continue

            all_episodes.append((main_page, title))

        return all_episodes

    @staticmethod
    def get_details(url: str) -> tuple[str, str, str]:
        """Fetch an episode detail page and return (description, mp3_url, cover_url)."""
        description = ""
        mp3 = ""
        current_html = HTMLUtils.get_html_from_url(url)
        soup = BeautifulSoup(current_html, "html.parser")

        content_divs = soup.find_all("div", {"class": "entry-content simple-grid-clearfix"})
        for div in content_divs:
            for paragraph in div.find_all("p"):
                description = paragraph.get_text().strip()
                if description:
                    break

            for anchor in div.find_all("a"):
                link = anchor.get("href")
                if link and (link.endswith(".mp3") or "drive.google.com" in link):
                    mp3 = link
                    break

            if description and mp3:
                break

        cover = ""
        cover_divs = soup.find_all("div", {"class": "wp-block-image is-style-default"})
        if not cover_divs:
            cover_divs = soup.find_all("div", {"class": "wp-block-image"})
        if not cover_divs:
            cover_divs = content_divs

        for div in cover_divs:
            images = div.find_all("img")
            if images:
                cover = images[0].get("src") or ""
                if cover:
                    break

        if not cover:
            logger.warning("No RA cover image found for URL: %s", url)
        if not description:
            logger.warning("No RA description found for URL: %s", url)

        return description, mp3, cover
