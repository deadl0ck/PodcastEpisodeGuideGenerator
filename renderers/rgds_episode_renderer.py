from __future__ import annotations

import logging
from typing import Any

from reportlab.lib.units import cm

from podcasts.common.page_constants import (
    DEFAULT_FONT_BOLD,
    LISTEN_IMAGE,
    LISTEN_IMAGE_WIDTH,
    LISTEN_IMAGE_Y,
    SUB_HEADING_FONT,
    SUB_HEADING_FONT_SIZE,
    SUBTLE_TEXT_COLOUR,
)
from podcasts.rgds.page_constants import (
    DESCRIPTION_Y,
    EPISODE_FONT_COLOUR,
    EPISODE_FONT_SIZE,
    EPISODE_IMAGE_WIDTH,
    EPISODE_INFO_Y,
    RELEASED_FONT_COLOUR,
    RELEASED_FONT_SIZE,
    RELEASED_HEADING_FONT,
    RELEASED_TEXT_Y_CM,
)
from renderers.episode_renderer_base import BaseEpisodeRenderer

logger = logging.getLogger(__name__)


class RGDSEpisodeRenderer(BaseEpisodeRenderer):
    """Render RGDS Spotify episodes into the guide PDF."""

    def __init__(self, retry_number: int):
        super().__init__(retry_number=retry_number)

    def _render_single_episode_page(self, writer: Any, episode: Any) -> None:
        writer.insert_image_from_url_centred(episode.image_url, EPISODE_IMAGE_WIDTH, episode.page_url)
        writer.write_text_to_page_centered_x(
            "(Click image above to jump to episode on Spotify)",
            EPISODE_INFO_Y,
            SUB_HEADING_FONT,
            SUB_HEADING_FONT_SIZE,
            SUBTLE_TEXT_COLOUR,
        )

        writer.write_text_to_page_centered_x(
            episode.title,
            28.5 * cm,
            DEFAULT_FONT_BOLD,
            EPISODE_FONT_SIZE,
            EPISODE_FONT_COLOUR,
        )

        writer.write_text_to_page_centered_x(
            f"Released: {episode.published_display} - Duration: {episode.duration}",
            RELEASED_TEXT_Y_CM,
            RELEASED_HEADING_FONT,
            RELEASED_FONT_SIZE,
            RELEASED_FONT_COLOUR,
        )

        writer.write_sub_heading_to_page(episode.description, DESCRIPTION_Y)
        writer.write_listen_image(episode.audio_url, LISTEN_IMAGE, LISTEN_IMAGE_WIDTH, LISTEN_IMAGE_Y)
        writer.insert_jump_to_toc_link()
        writer.new_page()

    def render_episode_pages(self, writer: Any, episodes: list[Any]) -> None:
        for episode in episodes:
            logger.info(self._EPISODE_SEPARATOR)
            logger.info("[PAGE] %s", episode.title)
            writer.create_bookmark(episode.bookmark)
            self._run_with_retry(
                lambda current=episode: self._render_single_episode_page(writer, current),
                episode.title,
                (Exception,),
            )
