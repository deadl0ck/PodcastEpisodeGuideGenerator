"""RA guide generator entrypoint and orchestration."""

from __future__ import annotations

import logging
import os
import pickle

from bs4 import BeautifulSoup

from podcasts.common.guide_main_base import BaseGuideMain
from podcasts.common.runtime import configure_logging, get_test_run_settings, initialize_provider_runtime
from podcasts.ra.episode import Episode
from podcasts.ra.html_utils import HTMLUtils
from podcasts.common.page_constants import (
    DEFAULT_FONT_BOLD,
    NULL_LINK,
    TOC_FONT_SIZE,
    TOC_SPACING_DELTA,
    TOC_TEXT,
)
from podcasts.ra.page_constants import (
    COVER_IMAGE,
    EPISODE_CACHE_LOCATION,
    FULL_PDF_PATH,
    START_URL,
    TOC_FONT_COLOUR,
    ensure_cache_dirs,
)
from podcasts.ra.pdf_writer import PDFWriter
from renderers.ra_episode_renderer import RAEpisodeRenderer

configure_logging()
logger = logging.getLogger(__name__)

TEST_RUN, TEST_RUN_COUNT = get_test_run_settings()
RETRY_NUMBER = 5


class RAGuideMain(BaseGuideMain):
    """RA-specific guide orchestration built on the shared base workflow."""

    def build_context(self, episodes: list[Episode]) -> dict:
        """RA has no additional context beyond the episode list."""
        return {}

    def write_cover(self, cover_image: str) -> None:
        # RA uses a local cover image asset, so it keeps a provider-specific cover writer.
        self.writer.write_ra_cover()

    def write_toc(self, episodes: list[Episode], context: dict) -> None:
        """Write the table of contents, marking filtered episodes as removed."""
        episode_entries: list[tuple[str, str]] = []
        for episode in episodes:
            if self.writer.removal_text_present(episode.description, episode.image_url):
                episode_entries.append(("[ Episode removed ]", NULL_LINK))
            else:
                episode_entries.append((episode.title, episode.title))

        self.write_standard_toc(
            episode_entries,
            TOC_TEXT,
            DEFAULT_FONT_BOLD,
            TOC_FONT_SIZE,
            TOC_FONT_COLOUR,
            TOC_SPACING_DELTA,
        )

    def build_pages(self, episodes: list[Episode], context: dict) -> None:
        """Render all episode pages using the RA episode renderer."""
        renderer = RAEpisodeRenderer(retry_number=RETRY_NUMBER)
        renderer.render_episode_pages(self.writer, episodes)

    def write_feature_list(self, episodes: list[Episode], context: dict) -> None:
        # Retro Asylum currently has no additional feature list section.
        return


def _coerce_episode(raw_episode: object, cache_key: str) -> Episode:
    """Normalise a cached object into an Episode instance."""
    if isinstance(raw_episode, Episode):
        return raw_episode

    page_url = getattr(raw_episode, "page_url", getattr(raw_episode, "url", cache_key))
    image_url = getattr(raw_episode, "image_url", getattr(raw_episode, "cover", ""))
    title = getattr(raw_episode, "title", page_url)
    description = getattr(raw_episode, "description", "")
    audio_url = getattr(raw_episode, "audio_url", getattr(raw_episode, "mp3", ""))
    return Episode(page_url, image_url, title, description, audio_url)


def _load_episode_cache() -> dict[str, Episode]:
    """Load and coerce the RA episode cache."""
    if os.path.exists(EPISODE_CACHE_LOCATION):
        with open(EPISODE_CACHE_LOCATION, "rb") as f:
            existing = pickle.load(f)
        return {
            str(key): _coerce_episode(value, str(key))
            for key, value in dict(existing).items()
        }

    return {}


def load_episodes() -> list[Episode]:
    """Scrape and cache all RA episodes, returning them sorted newest-first."""
    ensure_cache_dirs()

    if TEST_RUN:
        logger.info("**** This is a test run - will only process %s episodes ****", TEST_RUN_COUNT)

    episode_cache = _load_episode_cache()
    existing_urls = set(episode_cache.keys())

    if TEST_RUN and len(episode_cache) >= TEST_RUN_COUNT:
        sorted_cache = dict(sorted(episode_cache.items(), key=lambda kv: kv[0], reverse=True))
        return list(sorted_cache.values())[:TEST_RUN_COUNT]

    try:
        all_pages = HTMLUtils.get_all_pages(START_URL)
    except Exception:
        if episode_cache:
            logger.warning("RA page discovery failed; using cached episodes only")
            sorted_cache = dict(sorted(episode_cache.items(), key=lambda kv: kv[0], reverse=True))
            episodes = list(sorted_cache.values())
            if TEST_RUN:
                return episodes[:TEST_RUN_COUNT]
            return episodes
        raise

    for current_page in all_pages:
        logger.info("Getting RA data for %s", current_page)
        current_html = HTMLUtils.get_html_from_url(current_page)
        soup = BeautifulSoup(current_html, "html.parser")
        episodes = HTMLUtils.get_episodes_from_page(soup, existing_urls)

        for episode_url, fallback_title in episodes:
            if episode_url in episode_cache:
                continue

            description, mp3, cover = HTMLUtils.get_details(episode_url)
            title = fallback_title
            episode = Episode(episode_url, cover, title, description, mp3)
            episode_cache[episode_url] = episode
            existing_urls.add(episode_url)

            if TEST_RUN and len(episode_cache) >= TEST_RUN_COUNT:
                break

        if TEST_RUN and len(episode_cache) >= TEST_RUN_COUNT:
            break

    sorted_cache = dict(sorted(episode_cache.items(), key=lambda kv: kv[0], reverse=True))

    with open(EPISODE_CACHE_LOCATION, "wb") as f:
        pickle.dump(sorted_cache, f)

    episodes = list(sorted_cache.values())
    if TEST_RUN:
        return episodes[:TEST_RUN_COUNT]
    return episodes


def main() -> None:
    initialize_provider_runtime()
    writer = PDFWriter()
    app = RAGuideMain(writer)
    app.create_and_save_magazine(COVER_IMAGE, load_episodes())
    logger.info('All done - PDF written to "%s"', FULL_PDF_PATH)


if __name__ == "__main__":
    main()
