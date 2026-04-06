from __future__ import annotations

import re
import logging
from typing import Any

from reportlab.lib.units import cm

from podcasts.common.page_constants import (
    DEFAULT_FONT_BOLD,
    EPISODE_TEXT_Y_CM,
    LISTEN_IMAGE,
    LISTEN_IMAGE_WIDTH,
    LISTEN_IMAGE_Y,
    SUB_HEADING_FONT_SIZE,
    SUBTLE_TEXT_COLOUR,
)
from podcasts.zttp.page_constants import (
    EPISODE_FONT_COLOUR,
    EPISODE_FONT_SIZE,
    EPISODE_IMAGE_WIDTH,
    ZZAP_COVER_WIDTH,
)
from renderers.episode_renderer_base import BaseEpisodeRenderer

CRAPVERTS_BASE_URL = "https://zappedtothepast.com/classic-crapverts/"
logger = logging.getLogger(__name__)


class ZTTPEpisodeRenderer(BaseEpisodeRenderer):
    def __init__(self, crapverts: dict, cover_data: dict, retry_number: int):
        super().__init__(retry_number=retry_number)
        self.crapverts = crapverts
        self.cover_data = cover_data
        self._current_cover_month = ""

    @staticmethod
    def _extract_month_year(episode_title: str) -> str:
        my = re.findall("[J,F,M,A,S,O,N,D].+ \\d{4}", episode_title)
        if not my:
            return ""

        month_year = my[0].strip()
        if month_year == "November & December 1991":
            return "December 1991"
        return month_year

    def _render_cover_if_needed(self, writer: Any, episode: Any) -> None:
        month_year = self._extract_month_year(episode.title)
        if not month_year:
            logger.info('No original cover data for episode "%s"', episode.title)
            return

        if month_year not in self.cover_data:
            logger.info('No cover URL found for month/year "%s"', month_year)
            return

        if self._current_cover_month == month_year:
            return

        self._current_cover_month = month_year
        logger.info('Cover URL for %s is %s', episode.title, self.cover_data[month_year])
        writer.insert_image_from_url_centred(self.cover_data[month_year], ZZAP_COVER_WIDTH, episode.page_url)
        writer.new_page()

    def _render_single_episode_page(self, writer: Any, episode: Any) -> None:
        writer.insert_image_from_url_centred(episode.image_url, EPISODE_IMAGE_WIDTH, episode.page_url)
        writer.write_text_to_page_centered_x(episode.title,
                                             EPISODE_TEXT_Y_CM,
                                             DEFAULT_FONT_BOLD,
                                             EPISODE_FONT_SIZE,
                                             EPISODE_FONT_COLOUR)
        writer.write_sub_heading_to_page(episode.description, 29.2 * cm - 2 * cm)

        writer.write_text_to_page_centered_x('(Click image above to go to the Podbean episode page)',
                                             29.2 * cm - 21 * cm,
                                             DEFAULT_FONT_BOLD,
                                             SUB_HEADING_FONT_SIZE,
                                             SUBTLE_TEXT_COLOUR)
        writer.write_sub_heading_to_page(f'Episode Duration: {episode.duration}', 29.2 * cm - 22 * cm)
        writer.write_sub_heading_to_page(f'Aired on: {episode.published_display}', 29.2 * cm - 22.5 * cm)

        if episode.games_list:
            extra_info = f'{episode.games_summary_text} {", ".join(episode.games_list)}'
            writer.write_sub_heading_to_page(extra_info, 29.2 * cm - 23.5 * cm)

        writer.write_text_to_page_centered_x('(Click listen image below to go to episode MP3)',
                                             (LISTEN_IMAGE_Y - 2.8) * cm,
                                             DEFAULT_FONT_BOLD,
                                             SUB_HEADING_FONT_SIZE,
                                             SUBTLE_TEXT_COLOUR)
        writer.write_listen_image(episode.audio_url,
                                  LISTEN_IMAGE,
                                  LISTEN_IMAGE_WIDTH,
                                  LISTEN_IMAGE_Y)
        writer.insert_jump_to_toc_link()
        writer.new_page()

    def _render_crapverts(self, writer: Any, episode: Any) -> None:
        if episode.episode_number not in self.crapverts:
            return

        crapvert = self.crapverts[episode.episode_number]
        heading = crapvert.get_heading()
        images = crapvert.get_images()
        if not images:
            return

        writer.write_text_to_page_centered_x(f'{heading} (1/{len(images)})',
                                             EPISODE_TEXT_Y_CM,
                                             DEFAULT_FONT_BOLD,
                                             EPISODE_FONT_SIZE,
                                             EPISODE_FONT_COLOUR)
        writer.insert_image_from_url_centred(images[0], 650, CRAPVERTS_BASE_URL)
        writer.new_page()
        for i in range(1, len(images)):
            writer.write_text_to_page_centered_x(f'{heading} ({i + 1}/{len(images)})',
                                                 EPISODE_TEXT_Y_CM,
                                                 DEFAULT_FONT_BOLD,
                                                 EPISODE_FONT_SIZE,
                                                 EPISODE_FONT_COLOUR)
            writer.insert_image_from_url_centred(images[i], 650, CRAPVERTS_BASE_URL)
            writer.new_page()

    def render_episode_pages(self, writer: Any, episodes: list[Any]) -> None:
        for episode in episodes:
            logger.info('[ ---------- Building Episode ---------- ]')
            logger.info('[PAGE] %s', episode.title)
            writer.create_bookmark(episode.title)
            episode.print_summary()

            self._render_cover_if_needed(writer, episode)

            try:
                self._run_with_retry(
                    lambda current=episode: self._render_single_episode_page(writer, current),
                    episode.title,
                    (Exception,),
                )
            except RuntimeError:
                logger.warning('Skipping episode after retries: %s', episode.title)
                continue

            self._render_crapverts(writer, episode)
