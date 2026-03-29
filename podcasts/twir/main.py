"""TWIR guide generator entrypoint and orchestration."""

from __future__ import annotations

import logging

from data_retriever import DataRetriever
from env_var_utils import EnvVarUtils, GOOGLE_API_KEY, PODBEAN_RSS_FEED, YOUTUBE_PLAYLIST_ID
from podcasts.common.runtime import configure_logging, get_test_run_settings
from podcasts.twir.episode_page_builder import build_episode_pages
from podcasts.common.guide_main_base import BaseGuideMain
from podcasts.twir.episode import Episode
from podcasts.twir.page_constants import (
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
    FULL_PDF_PATH,
    QOW_LIST_BOOKMARK,
    QOW_LIST_FONT_COLOUR,
    QOW_LIST_FONT_SIZE,
    QOW_LIST_SPACING_DELTA,
    QOW_LIST_TEXT,
    TOC_FONT_COLOUR,
    TOC_FONT_SIZE,
    TOC_SPACING_DELTA,
    TOC_TEXT,
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
        build_episode_pages(self.writer, episodes, context["qow"], RETRY_NUMBER)

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
    EnvVarUtils.init()

    youtube_items = DataRetriever.get_youtube_playlist_items(
        EnvVarUtils.get_env_var(GOOGLE_API_KEY),
        EnvVarUtils.get_env_var(YOUTUBE_PLAYLIST_ID),
    )
    podcast_items = DataRetriever.get_podcast_mp3_links_and_air_dates(
        EnvVarUtils.get_env_var(PODBEAN_RSS_FEED)
    )

    if TEST_RUN:
        logger.info('**** This is a test run - will only process %s episodes ****', TEST_RUN_COUNT)

    all_episodes = []
    for key in youtube_items.keys():
        episode_number = TWIRUtils.extract_episode_number(youtube_items[key].title)[0]
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

    all_episodes.sort(key=lambda x: x.episode_number, reverse=True)
    if TEST_RUN:
        del all_episodes[TEST_RUN_COUNT:]

    return all_episodes


def main() -> None:
    """Run the TWIR guide generation flow."""
    writer = PDFWriter()
    qow_processor = QuestionOfTheWeekProcessor()
    qow_processor.process_qow()

    app = TWIRGuideMain(writer, qow_processor.episodes_and_questions)
    app.create_and_save_magazine(COVER_IMAGE, load_episodes())

    logger.info('All done - magazine written to "%s"', FULL_PDF_PATH)


if __name__ == "__main__":
    main()
