from __future__ import annotations

import logging
from typing import Any

import requests
from reportlab.lib.units import cm

from podcasts.common.page_constants import (
    DEFAULT_FONT_BOLD,
    LISTEN_IMAGE,
    LISTEN_IMAGE_WIDTH,
    LISTEN_IMAGE_Y,
    SUBTLE_TEXT_COLOUR,
)
from podcasts.tenp.page_constants import EPISODE_FONT_COLOUR, EPISODE_FONT_SIZE, EPISODE_IMAGE_WIDTH
from renderers.episode_renderer_base import BaseEpisodeRenderer

logger = logging.getLogger(__name__)


class TenPEpisodeRenderer(BaseEpisodeRenderer):
    def __init__(self, retry_number: int):
        super().__init__(retry_number=retry_number)
        self._logged_listen_badge_hint = False

    def render_episode_pages(self, writer: Any, episodes: list[Any]) -> None:
        for episode in episodes:
            logger.info(self._EPISODE_SEPARATOR)
            logger.info("[PAGE] %s", episode.title)
            writer.create_bookmark(str(episode.episode_number))
            episode.print_summary()
            self._run_with_retry(
                lambda current=episode: self._render_single_episode_page(writer, current),
                episode.title,
                (Exception,),
            )

    def _render_single_episode_page(self, writer: Any, episode: Any) -> None:
        writer.insert_image_from_url_centred(episode.image_url, EPISODE_IMAGE_WIDTH, episode.page_url)
        writer.write_text_to_page_centered_x(
            episode.title,
            28 * cm,
            DEFAULT_FONT_BOLD,
            EPISODE_FONT_SIZE,
            EPISODE_FONT_COLOUR,
        )
        writer.write_sub_heading_to_page(episode.description, 29.2 * cm - 2 * cm)

        writer.write_text_to_page_centered_x(
            "Click image above to go to the episode page",
            23 * cm,
            DEFAULT_FONT_BOLD,
            12,
            SUBTLE_TEXT_COLOUR,
        )

        writer.write_sub_heading_to_page(f"Episode Duration: {episode.duration}", 30 * cm - 25 * cm)
        writer.write_sub_heading_to_page(f"Aired on: {episode.published_display}", 30 * cm - 25.5 * cm)

        next_month = getattr(episode, "next_month_game", "No Game")
        writer.write_sub_heading_to_page(f"Next Month's Game: {next_month}", 30 * cm - 26.5 * cm)

        writer.write_text_to_page_centered_x(
            "Click listen image below to go to episode MP3",
            2.2 * cm,
            DEFAULT_FONT_BOLD,
            12,
            SUBTLE_TEXT_COLOUR,
        )
        try:
            writer.write_listen_image(episode.audio_url, LISTEN_IMAGE, LISTEN_IMAGE_WIDTH, LISTEN_IMAGE_Y)
        except requests.RequestException:
            logger.warning("Listen badge download failed for %s", episode.title)
            if not self._logged_listen_badge_hint:
                cache_path = writer._get_cached_image_path(LISTEN_IMAGE)
                cache_name = cache_path.rsplit("/", 1)[-1]
                logger.warning(
                    "Pull image from %s and rename it to %s and put it in %s to fix this error",
                    LISTEN_IMAGE,
                    cache_name,
                    writer.image_cache_dir,
                )
                self._logged_listen_badge_hint = True
        if not self._logged_listen_badge_hint:
            cache_path = writer._get_cached_image_path(LISTEN_IMAGE)
            cache_name = cache_path.rsplit("/", 1)[-1]
            logger.info(
                "Listen badge cache candidate name: %s (provider cache: %s)",
                cache_name,
                writer.image_cache_dir,
            )
            self._logged_listen_badge_hint = True
        writer.insert_jump_to_toc_link()
        writer.new_page()
