from __future__ import annotations

import logging
import os
import pickle

import feedparser

from podcasts.common.guide_main_base import BaseGuideMain
from podcasts.common.page_constants import (
    COVER_FONT_SIZE,
    COVER_IMAGE_WIDTH,
    COVER_SUB_TEXT,
    COVER_SUB_TEXT_Y_CM,
    COVER_TEXT_Y_CM,
    DEFAULT_FONT_BOLD,
    TOC_TEXT,
)
from podcasts.common.runtime import configure_logging, get_test_run_settings
from podcasts.tenp.basic_ai import BasicAI
from podcasts.tenp.episode import Episode
from podcasts.tenp.next_months_game_cache import NextMonthsGameCache
from podcasts.tenp.page_constants import (
    COVER_FONT_COLOUR,
    COVER_IMAGE,
    COVER_LINK,
    COVER_TEXT,
    FEED_URL,
    EPISODE_CACHE_LOCATION,
    FULL_PDF_PATH,
    MIN_EPISODE_NUMBER,
    NEXT_MONTH_GAME_CACHE_LOCATION,
    NEXT_MONTHS_GAMES_OVERRIDES,
    TOC_FONT_COLOUR,
    TOC_FONT_SIZE,
    TOC_SPACING_DELTA,
    ensure_cache_dirs,
)
from podcasts.tenp.pdf_writer import PDFWriter
from podcasts.tenp.tenp_utils import TenPenceUtils
from renderers.tenp_episode_renderer import TenPEpisodeRenderer

configure_logging()
logger = logging.getLogger(__name__)

TEST_RUN, TEST_RUN_COUNT = get_test_run_settings()
RETRY_NUMBER = 5


class TenPGuideMain(BaseGuideMain):
    def __init__(self, writer):
        super().__init__(writer)
        self._ai_disabled_notice_logged = False

    def build_context(self, episodes: list[Episode]) -> dict:
        return {
            "next_month_cache": NextMonthsGameCache(NEXT_MONTH_GAME_CACHE_LOCATION),
            "next_month_ai": BasicAI(),
        }

    def write_cover(self, cover_image: str) -> None:
        self.write_standard_cover(
            cover_image,
            COVER_IMAGE_WIDTH,
            COVER_TEXT,
            COVER_TEXT_Y_CM,
            COVER_SUB_TEXT,
            COVER_SUB_TEXT_Y_CM,
            DEFAULT_FONT_BOLD,
            COVER_FONT_SIZE,
            COVER_FONT_COLOUR,
            COVER_LINK,
        )

    def write_toc(self, episodes: list[Episode], context: dict) -> None:
        cleaned_names = TenPenceUtils.replace_title_text(episodes)
        episode_names = [
            (cleaned_names[index], str(episode.episode_number))
            for index, episode in enumerate(episodes)
        ]
        self.write_standard_toc(
            episode_names,
            TOC_TEXT,
            DEFAULT_FONT_BOLD,
            TOC_FONT_SIZE,
            TOC_FONT_COLOUR,
            TOC_SPACING_DELTA,
        )

    def _get_next_month_game(self, episode: Episode, context: dict) -> tuple[str, str]:
        cache: NextMonthsGameCache = context["next_month_cache"]
        ai: BasicAI = context["next_month_ai"]

        cached = cache.get_next_months_game(episode.episode_number)
        if cached != NextMonthsGameCache.NO_GAME:
            return cached, "cache"

        if episode.episode_number in NEXT_MONTHS_GAMES_OVERRIDES:
            result = NEXT_MONTHS_GAMES_OVERRIDES[episode.episode_number]
            source = "override"
        else:
            result = ai.get_next_months_game(episode.summary)
            source = "ai"

        if ai.is_disabled_for_run and not self._ai_disabled_notice_logged:
            logger.warning(
                "TenP AI extraction has been disabled for this run due to API key/API errors; "
                "using cache, overrides, or 'No Game' fallback"
            )
            self._ai_disabled_notice_logged = True
            source = "fallback"

        cache.add_game_to_cache(episode.episode_number, result)
        cache.save()
        return result, source

    def build_pages(self, episodes: list[Episode], context: dict) -> None:
        logger.info("Resolving next-month game values for %s episode(s)", len(episodes))
        for index, episode in enumerate(episodes, start=1):
            logger.info("Resolving next-month game %s/%s for episode #%s",
                        index,
                        len(episodes),
                        episode.episode_number)
            next_game, source = self._get_next_month_game(episode, context)
            episode.next_month_game = next_game
            logger.info("Resolved next-month game for episode #%s from %s", episode.episode_number, source)
        renderer = TenPEpisodeRenderer(retry_number=RETRY_NUMBER)
        renderer.render_episode_pages(self.writer, episodes)

    def write_feature_list(self, episodes: list[Episode], context: dict) -> None:
        return


def _extract_mp3_link(entry: object) -> str:
    links = getattr(entry, "links", [])
    for link in links:
        if getattr(link, "rel", "") == "enclosure":
            href = getattr(link, "href", "")
            if href:
                return href
    if len(links) > 1:
        return getattr(links[1], "href", "")
    return ""


def _extract_html_content(entry: object) -> str:
    content_list = getattr(entry, "content", [])
    if not content_list:
        return ""
    first = content_list[0]
    if isinstance(first, dict):
        return str(first.get("value", ""))
    return str(getattr(first, "value", ""))


def load_episodes() -> list[Episode]:
    logger.info("Preparing Ten Pence cache directories")
    ensure_cache_dirs()

    if TEST_RUN:
        logger.info("**** This is a test run - will only process %s episodes ****", TEST_RUN_COUNT)

    logger.info("Fetching Ten Pence RSS feed: %s", FEED_URL)
    feed = feedparser.parse(FEED_URL)
    episodes: list[Episode] = []
    episode_cache: dict[str, Episode] = {}
    cache_hits = 0
    cache_misses = 0

    if os.path.exists(EPISODE_CACHE_LOCATION):
        with open(EPISODE_CACHE_LOCATION, "rb") as cache_handle:
            episode_cache = pickle.load(cache_handle)
        logger.info("10P episode cache loaded: %s entries", len(episode_cache))
    else:
        logger.info("10P episode cache MISS: no existing cache file")

    entries = getattr(feed, "entries", [])
    logger.info("RSS fetch complete: %s entries discovered", len(entries))

    for index, item in enumerate(entries, start=1):
        episode_number = Episode.extract_episode_number(item.title)
        if episode_number < MIN_EPISODE_NUMBER:
            logger.debug("Skipping entry %s/%s: '%s' (episode < %s)",
                         index,
                         len(entries),
                         item.title,
                         MIN_EPISODE_NUMBER)
            continue

        logger.info("Resolving episode %s/%s: #%s '%s'",
                    index,
                    len(entries),
                    episode_number,
                    item.title)
        if item.title in episode_cache:
            episodes.append(episode_cache[item.title])
            cache_hits += 1
            if TEST_RUN and len(episodes) >= TEST_RUN_COUNT:
                logger.info("Test run limit reached (%s episodes)", TEST_RUN_COUNT)
                break
            continue

        image_url, ai_generated = TenPenceUtils.get_image_url(item.link, episode_number)
        episode = Episode(
            title=item.title,
            link=item.link,
            description=TenPenceUtils.extract_description(item.description),
            published=TenPenceUtils.extract_date_time(item.published),
            summary=getattr(item, "summary", ""),
            duration=str(getattr(item, "itunes_duration", "")),
            mp3=_extract_mp3_link(item),
            html_content=_extract_html_content(item),
            episode_image=image_url,
        )
        episode.ai_generated_image = ai_generated
        episodes.append(episode)
        episode_cache[item.title] = episode
        cache_misses += 1

        if TEST_RUN and len(episodes) >= TEST_RUN_COUNT:
            logger.info("Test run limit reached (%s episodes)", TEST_RUN_COUNT)
            break

    with open(EPISODE_CACHE_LOCATION, "wb") as cache_handle:
        pickle.dump(episode_cache, cache_handle)
    logger.info(
        "10P episode cache stats: hits=%s, misses=%s, total_cached=%s",
        cache_hits,
        cache_misses,
        len(episode_cache),
    )

    episodes.sort(key=lambda ep: ep.episode_number, reverse=True)
    logger.info("Episode loading complete: %s episodes ready for rendering", len(episodes))
    return episodes


def main() -> None:
    writer = PDFWriter()
    app = TenPGuideMain(writer)
    app.create_and_save_magazine(COVER_IMAGE, load_episodes())
    logger.info('All done - PDF written to "%s"', FULL_PDF_PATH)


if __name__ == "__main__":
    main()
