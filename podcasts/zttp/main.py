"""ZTTP guide generator entrypoint and orchestration."""

from __future__ import annotations

import os
import pickle
import logging

import feedparser

from podcasts.common.guide_main_base import BaseGuideMain
from podcasts.common.runtime import configure_logging, get_test_run_settings
from podcasts.zttp.covers import Covers
from podcasts.zttp.crapverts import Crapverts
from podcasts.zttp.episode import Episode
from podcasts.zttp.page_constants import (
    COVER_FONT_COLOUR,
    COVER_FONT_SIZE,
    COVER_IMAGE,
    COVER_IMAGE_WIDTH,
    COVER_LINK,
    COVER_SUB_TEXT,
    COVER_SUB_TEXT_Y_CM,
    COVER_TEXT,
    COVER_TEXT_Y_CM,
    DEFAULT_FONT_BOLD,
    EPISODE_CACHE_LOCATION,
    FEED_URL,
    GAME_LIST_FONT_COLOUR,
    GAME_LIST_FONT_SIZE,
    GAME_LIST_SPACING_DELTA,
    GAME_LIST_TEXT,
    PDF_LOCATION,
    PDF_NAME,
    TOC_FONT_COLOUR,
    TOC_FONT_SIZE,
    TOC_SPACING_DELTA,
    TOC_TEXT,
    ensure_cache_dirs,
)
from podcasts.zttp.pdf_writer import PDFWriter
from podcasts.zttp.zzap_utils import ZzapUtils
from renderers.toc_renderer import ZTTPTocRenderer
from renderers.zttp_episode_renderer import ZTTPEpisodeRenderer

configure_logging()
logger = logging.getLogger(__name__)

TEST_RUN, TEST_RUN_COUNT = get_test_run_settings()


class ZTTPGuideMain(BaseGuideMain):
    """ZTTP-specific guide orchestration built on the shared base workflow."""

    def build_context(self, episodes: list[Episode]) -> dict[str, dict]:
        logger.info('Writing games list....')
        crapverts = Crapverts.get_all_crapverts()
        covers = Covers().get_covers()
        return {
            "crapverts": crapverts,
            "covers": covers,
        }

    def write_toc(self, episodes: list[Episode], context: dict[str, dict]) -> None:
        renderer = ZTTPTocRenderer()
        episode_names = renderer.build_entries(
            episodes,
            formatter=ZzapUtils.replace_title_text,
            crapverts=context["crapverts"],
        )
        self.write_standard_toc(
            episode_names,
            TOC_TEXT,
            DEFAULT_FONT_BOLD,
            TOC_FONT_SIZE,
            TOC_FONT_COLOUR,
            TOC_SPACING_DELTA,
        )

    def build_pages(self, episodes: list[Episode], context: dict[str, dict]) -> None:
        logger.info("Getting original Zzap64! cover data....")
        renderer = ZTTPEpisodeRenderer(
            crapverts=context["crapverts"],
            cover_data=context["covers"],
            retry_number=5,
        )
        renderer.render_episode_pages(self.writer, episodes)

    def write_feature_list(self, episodes: list[Episode], context: dict[str, dict]) -> None:
        self.writer.write_games_list(
            episodes,
            GAME_LIST_TEXT,
            DEFAULT_FONT_BOLD,
            GAME_LIST_FONT_SIZE,
            GAME_LIST_FONT_COLOUR,
            GAME_LIST_SPACING_DELTA,
        )

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


def format_duration(duration_str: str) -> str:
    """Convert a raw duration string in seconds to HH:MM format."""
    if not duration_str:
        return "00:00"

    seconds = int(duration_str.strip("'\""))
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours:02d}:{minutes:02d}"


def load_episodes() -> list[Episode]:
    """Load and cache ZTTP feed episodes enriched with parsed game metadata."""
    ensure_cache_dirs()

    if TEST_RUN:
        logger.info('**** This is a test run - will only process %s episodes ****', TEST_RUN_COUNT)

    feed = feedparser.parse(FEED_URL)
    content = feed.entries
    episodes = []
    test_run_count = 0
    episode_cache = {}

    if os.path.exists(EPISODE_CACHE_LOCATION):
        with open(EPISODE_CACHE_LOCATION, 'rb') as f:
            episode_cache = pickle.load(f)

    for ep in content:
        logger.info('Getting base data for %s', ep.title)
        if ep.title in episode_cache:
            logger.info('Using cached data for %s', ep.title)
            episodes.append(episode_cache[ep.title])
        else:
            html = ep.content[0].value
            game_list_text = ZzapUtils.extract_game_award_text(html)
            game_list = ZzapUtils.extract_games_info(html)
            episodes.append(Episode(
                ep.title,
                ep.link,
                ep.description,
                ZzapUtils.extract_date_time(ep.published),
                ep.summary,
                format_duration(ep.itunes_duration),
                ep.links[1].href,
                html,
                ZzapUtils.get_image_url(ep.link),
                game_list_text,
                game_list,
            ))

        test_run_count += 1
        if test_run_count >= TEST_RUN_COUNT and TEST_RUN:
            break

    episode_cache.clear()
    for episode in episodes:
        episode_cache[episode.title] = episode
    with open(EPISODE_CACHE_LOCATION, 'wb') as f:
        pickle.dump(episode_cache, f)

    return episodes


def main() -> None:
    """Run the ZTTP guide generation flow."""
    writer = PDFWriter()
    app = ZTTPGuideMain(writer)
    app.create_and_save_magazine(COVER_IMAGE, load_episodes())
    logger.info('All done - PDF written to "%s%s%s"', PDF_LOCATION, os.path.sep, PDF_NAME)


if __name__ == "__main__":
    main()
