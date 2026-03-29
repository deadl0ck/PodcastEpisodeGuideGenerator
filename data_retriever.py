"""External data retrieval helpers for TWIR feeds and YouTube data."""

from __future__ import annotations

import datetime
from typing import Any

import feedparser
from pyyoutube import Api

from podcasts.twir.twir_utils import TWIRUtils


class DataRetriever:
    """Fetch and normalize remote data sources used by the TWIR generator."""

    @staticmethod
    def get_podcast_mp3_links_and_air_dates(rss_feed_url: str) -> dict[int, tuple[str, str, str]]:
        """Return a mapping of episode number to audio URL and formatted dates."""
        items: dict[int, tuple[str, str, str]] = {}
        feed = feedparser.parse(rss_feed_url)
        content = feed.entries
        for episode in content:
            parsed_date = datetime.datetime.strptime(episode.published[:-6], '%a, %d %b %Y %H:%M:%S')
            formatted_date = parsed_date.strftime('%a, %d %b %Y %H:%M')
            csv_formatted_date = parsed_date.strftime('%Y-%m-%d')
            items[TWIRUtils.extract_episode_number(episode.title)[0]] = \
                episode.links[1].href, formatted_date, csv_formatted_date
        return items

    @staticmethod
    def get_youtube_playlist_items(api_key: str, playlist_id: str) -> dict[tuple[int, str], Any]:
        """Return YouTube playlist items keyed by extracted episode marker tuple."""
        api = Api(api_key=api_key)
        more = True
        next_page = ""
        items: dict[tuple[int, str], Any] = {}
        while more:
            playlist_item_by_playlist = api.get_playlist_items(playlist_id=playlist_id, count=40, page_token=next_page)
            for vid in playlist_item_by_playlist.items:
                if vid.snippet.title == "Private video":
                    continue
                items[TWIRUtils.extract_episode_number(vid.snippet.title)] = vid.snippet
            next_page = playlist_item_by_playlist.nextPageToken
            if next_page is None:
                more = False
        return items
