# data_retriever.py
# Handles all external data fetching:
#   - YouTube playlist items via the YouTube Data API
#   - Podcast MP3 links and air dates via the Podbean RSS feed
from pyyoutube import Api
from podcasts.twir.twir_utils import TWIRUtils
import feedparser
import datetime


class DataRetriever:

    @staticmethod
    def get_podcast_mp3_links_and_air_dates(rss_feed_url: str) -> dict[int, tuple[str, str, str]]:
        # Returns a dict keyed by episode number: (mp3_url, formatted_date, csv_date)
        items = {}
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
    def get_youtube_playlist_items(api_key: str, playlist_id: str) -> dict[tuple[int, str], object]:
        # Paginates through the full playlist (40 items per page) and returns a dict
        # keyed by (episode_number, episode_marker_string) -> YouTube snippet.
        # Private videos are skipped.
        api = Api(api_key=api_key)
        more = True
        next_page = ""
        items = {}
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
