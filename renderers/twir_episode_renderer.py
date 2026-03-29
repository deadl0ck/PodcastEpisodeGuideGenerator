from __future__ import annotations

import csv
import logging
from typing import Any

import requests

from podcasts.twir.page_constants import (
    CSV_LOCATION,
    DEFAULT_FONT_BOLD,
    EPISODE_AIRDATE_Y,
    EPISODE_DESCRIPTION_Y,
    EPISODE_FONT_COLOUR,
    EPISODE_FONT_SIZE,
    EPISODE_HEADING_FONT_COLOUR,
    EPISODE_HEADING_LINE_SPACING,
    EPISODE_IMAGE_WIDTH,
    EPISODE_LISTEN_LABEL_Y,
    EPISODE_QOW_Y,
    EPISODE_TEXT_Y_CM,
    EPISODE_YOUTUBE_LABEL_Y,
    HEADING_LETTERS_PER_LINE,
    LISTEN_IMAGE,
    LISTEN_IMAGE_WIDTH,
    LISTEN_IMAGE_Y,
    SUB_HEADING_FONT,
    SUB_HEADING_FONT_SIZE,
    SUBTLE_TEXT_COLOUR,
)
from podcasts.twir.qow.qow_constants import VALID_MISSING_QOW
from renderers.episode_renderer_base import BaseEpisodeRenderer

logger = logging.getLogger(__name__)


class TWIREpisodeRenderer(BaseEpisodeRenderer):
    def __init__(self, qow_dict: dict, retry_number: int):
        super().__init__(retry_number=retry_number)
        self.qow_dict = qow_dict

    def _get_qow_values(self, episode_number: int) -> tuple[str, str]:
        if episode_number in VALID_MISSING_QOW or episode_number < 25:
            return "", ""

        qow = self.qow_dict.get(episode_number)
        if qow is None:
            logger.warning('No QoW found for episode %s; leaving question fields blank', episode_number)
            return "", ""

        return qow.question, qow.url

    def _render_single_episode_page(self, writer: Any, episode: Any) -> None:
        episode_url = episode.page_url
        episode_title = episode.title
        episode_cover = episode.image_url
        listen_url = episode.audio_url

        writer.insert_jump_to_toc_link()
        writer.insert_image_from_url_centred(episode_cover, EPISODE_IMAGE_WIDTH, episode_url)

        heading = f'{episode.episode_number} - {episode_title}'
        writer.create_bookmark(f'{episode.episode_number}')
        multiline_heading = writer.split_into_multiline(heading, HEADING_LETTERS_PER_LINE)
        current_y = EPISODE_TEXT_Y_CM
        for line in multiline_heading:
            writer.write_text_to_page_centered_x(line,
                                                 current_y,
                                                 DEFAULT_FONT_BOLD,
                                                 EPISODE_FONT_SIZE,
                                                 EPISODE_HEADING_FONT_COLOUR)
            current_y -= EPISODE_HEADING_LINE_SPACING

        writer.write_sub_heading_to_page(episode.description, EPISODE_DESCRIPTION_Y)

        question_text, question_url = self._get_qow_values(episode.episode_number)

        writer.write_text_to_page_centered_x('(Click image above to watch on YouTube)',
                                             EPISODE_YOUTUBE_LABEL_Y,
                                             SUB_HEADING_FONT,
                                             SUB_HEADING_FONT_SIZE,
                                             SUBTLE_TEXT_COLOUR)
        writer.write_text_to_page_centered_x(f'Aired on: {episode.published_display}',
                                             EPISODE_AIRDATE_Y,
                                             SUB_HEADING_FONT,
                                             SUB_HEADING_FONT_SIZE,
                                             EPISODE_FONT_COLOUR)

        if question_text:
            writer.write_qow(question_text,
                             1,
                             EPISODE_QOW_Y,
                             question_url)

        writer.write_text_to_page_centered_x('(Click image below to listen on Podbean)',
                                             EPISODE_LISTEN_LABEL_Y,
                                             SUB_HEADING_FONT,
                                             SUB_HEADING_FONT_SIZE,
                                             SUBTLE_TEXT_COLOUR)

        writer.write_listen_image(listen_url,
                                  LISTEN_IMAGE,
                                  LISTEN_IMAGE_WIDTH,
                                  LISTEN_IMAGE_Y)
        writer.new_page()

    def render_episode_pages(self, writer: Any, episodes: list[Any]) -> None:
        with open(CSV_LOCATION, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['Episode #', 'Published', 'Title', 'CQOtW', 'CQOtW URL'])

            for episode in episodes:
                logger.info('[ ---------- Building Episode ---------- ]')
                episode.print_out()

                self._run_with_retry(
                    lambda current=episode: self._render_single_episode_page(writer, current),
                    episode.title,
                    (requests.RequestException, OSError, KeyError, ValueError, RuntimeError),
                )

                question_text, question_url = self._get_qow_values(episode.episode_number)
                csv_writer.writerow([
                    episode.episode_number,
                    episode.sortable_date,
                    episode.title,
                    question_text,
                    question_url,
                ])
