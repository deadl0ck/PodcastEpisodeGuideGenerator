"""TWIR guide generator entrypoint and orchestration."""

from __future__ import annotations

import logging

from data_retriever import DataRetriever
from cache_paths import EPISODE_CACHE_FILE, ensure_cache_dirs
from env_var_utils import (
    ENV_VAR_NAMES,
    EnvVarUtils,
    PODBEAN_RSS_FEED,
    YOUTUBE_API_KEY,
    YOUTUBE_PLAYLIST_ID,
)
from podcasts.common.runtime import configure_logging, get_test_run_settings, initialize_provider_runtime
from renderers.twir_episode_renderer import TWIREpisodeRenderer
from podcasts.common.guide_main_base import BaseGuideMain
from podcasts.twir.episode_cache import TWIREpisodeCache
from podcasts.twir.episode import Episode
from podcasts.common.page_constants import (
    COVER_FONT_SIZE,
    COVER_IMAGE_WIDTH,
    COVER_SUB_TEXT,
    COVER_SUB_TEXT_Y_CM,
    COVER_TEXT_Y_CM,
    TOC_TEXT,
)
from podcasts.twir.page_constants import (
    COVER_FONT_COLOUR,
    COVER_IMAGE,
    COVER_LINK,
    COVER_TEXT,
    DEFAULT_FONT_BOLD,
    FULL_PDF_PATH,
    QOW_LIST_BOOKMARK,
    QOW_LIST_FONT_COLOUR,
    QOW_LIST_FONT_SIZE,
    QOW_LIST_SPACING_DELTA,
    QOW_LIST_TEXT,
    TOC_FONT_COLOUR,
    TOC_FONT_SIZE,
    TOC_SPACING_DELTA,
)
from podcasts.twir.twir_utils import TWIRUtils
from podcasts.twir.pdf_writer import PDFWriter
from podcasts.twir.qow.qow_processor import QuestionOfTheWeekProcessor
from renderers.toc_renderer import TWIRTocRenderer

configure_logging()
logger = logging.getLogger(__name__)

TEST_RUN, TEST_RUN_COUNT = get_test_run_settings()
RETRY_NUMBER = 1
YOUTUBE_WATCH_PREFIX = "https://www.youtube.com/watch?v="


class TWIRGuideMain(BaseGuideMain):
    """TWIR-specific guide orchestration built on the shared base workflow."""

    def __init__(self, writer, qow_dict: dict[int, object]):
        super().__init__(writer)
        self.qow_dict = qow_dict

    def build_context(self, episodes: list[Episode]) -> dict[str, dict[int, object]]:
        return {"qow": self.qow_dict}

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

    def write_toc(self, episodes: list[Episode], context: dict[str, dict[int, object]]) -> None:
        renderer = TWIRTocRenderer(QOW_LIST_BOOKMARK)
        episode_names = renderer.build_entries(episodes)

        self.write_standard_toc(
            episode_names,
            TOC_TEXT,
            DEFAULT_FONT_BOLD,
            TOC_FONT_SIZE,
            TOC_FONT_COLOUR,
            TOC_SPACING_DELTA,
        )

    def build_pages(self, episodes: list[Episode], context: dict[str, dict[int, object]]) -> None:
        renderer = TWIREpisodeRenderer(qow_dict=context["qow"], retry_number=RETRY_NUMBER)
        renderer.render_episode_pages(self.writer, episodes)

    def write_feature_list(self, episodes: list[Episode], context: dict[str, dict[int, object]]) -> None:
        self.writer.write_qow_list(
            context["qow"],
            QOW_LIST_TEXT,
            DEFAULT_FONT_BOLD,
            QOW_LIST_FONT_SIZE,
            QOW_LIST_FONT_COLOUR,
            QOW_LIST_SPACING_DELTA,
        )


def load_episodes() -> list[Episode]:
    """Load and normalize TWIR episode data from YouTube and Podbean."""
    ensure_cache_dirs()

    cached_episodes = TWIREpisodeCache.load(EPISODE_CACHE_FILE)
    if cached_episodes:
        logger.info("TWIR episode cache available: %s entries", len(cached_episodes))
    else:
        logger.info("TWIR episode cache empty")

    logger.info("Refreshing TWIR episodes from remote sources")

    try:
        youtube_items = DataRetriever.get_youtube_playlist_items(
            EnvVarUtils.get_env_var(YOUTUBE_API_KEY),
            EnvVarUtils.get_env_var(YOUTUBE_PLAYLIST_ID),
        )
        podcast_items = DataRetriever.get_podcast_mp3_links_and_air_dates(
            EnvVarUtils.get_env_var(PODBEAN_RSS_FEED)
        )
    except Exception as exc:  # pragma: no cover - defensive network fallback
        if cached_episodes:
            logger.warning("TWIR refresh failed, using cached episodes: %s", exc)
            cached_episodes.sort(key=lambda x: x.episode_number, reverse=True)
            if TEST_RUN:
                del cached_episodes[TEST_RUN_COUNT:]
            return cached_episodes
        raise

    if TEST_RUN:
        logger.info('**** This is a test run - will only process %s episodes ****', TEST_RUN_COUNT)

    all_episodes = []
    for key in youtube_items.keys():
        episode_number = TWIRUtils.extract_episode_number(youtube_items[key].title)[0]

        if episode_number < 0:
            logger.warning(
                'Skipping YouTube item with unrecognized TWIR episode pattern: "%s"',
                youtube_items[key].title,
            )
            continue

        if episode_number not in podcast_items:
            logger.warning(
                "Skipping episode %s - no matching Podbean RSS item found yet",
                episode_number,
            )
            continue

        all_episodes.append(Episode(
            f'{TWIRUtils.tidy_up_title(youtube_items[key].title)}',
            TWIRUtils.extract_description(youtube_items[key].description),
            episode_number,
            podcast_items[episode_number][1],
            youtube_items[key].thumbnails.high.url,
            YOUTUBE_WATCH_PREFIX + youtube_items[key].resourceId.videoId,
            podcast_items[episode_number][0],
            podcast_items[episode_number][2],
        ))

    if not all_episodes and cached_episodes:
        logger.warning("TWIR refresh returned 0 episodes; keeping cached episode set")
        cached_episodes.sort(key=lambda x: x.episode_number, reverse=True)
        if TEST_RUN:
            del cached_episodes[TEST_RUN_COUNT:]
        return cached_episodes

    all_episodes.sort(key=lambda x: x.episode_number, reverse=True)
    TWIREpisodeCache.save(EPISODE_CACHE_FILE, all_episodes)
    logger.info("TWIR episode cache updated: %s entries", len(all_episodes))
    if TEST_RUN:
        del all_episodes[TEST_RUN_COUNT:]

    return all_episodes


def main() -> None:
    """Run the TWIR guide generation flow."""
    initialize_provider_runtime(required_env_vars=ENV_VAR_NAMES)
    writer = PDFWriter()
    qow_processor = QuestionOfTheWeekProcessor()
    qow_processor.process_qow()

    app = TWIRGuideMain(writer, qow_processor.episodes_and_questions)
    app.create_and_save_magazine(COVER_IMAGE, load_episodes())

    logger.info('All done - magazine written to "%s"', FULL_PDF_PATH)


if __name__ == "__main__":
    main()
