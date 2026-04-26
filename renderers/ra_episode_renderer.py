"""Episode renderer for the Retro Asylum provider."""

from __future__ import annotations

import logging
from typing import Any

from reportlab.lib.units import cm

from podcasts.common.page_constants import (
    SUB_HEADING_FONT,
    SUB_HEADING_FONT_SIZE,
    SUBTLE_TEXT_COLOUR,
)
from podcasts.ra.page_constants import (
    DESCRIPTION_Y,
    EPISODE_FONT_COLOUR,
    EPISODE_FONT_SIZE,
    EPISODE_IMAGE_HEIGHT,
    EPISODE_TITLE_Y,
    EPISODE_WEB_LINK_LABEL_Y,
    LISTEN_LABEL_Y,
)
from renderers.episode_renderer_base import BaseEpisodeRenderer

logger = logging.getLogger(__name__)


class RAEpisodeRenderer(BaseEpisodeRenderer):
    """Renders individual Retro Asylum episode pages into the PDF."""

    def __init__(self, retry_number: int):
        super().__init__(retry_number=retry_number)

    def _render_single_episode_page(self, writer: Any, episode: Any) -> None:
        """Render one RA episode page: cover image, title, listen badge, and description."""
        if writer.removal_text_present(episode.description, episode.image_url):
            logger.info("Skipping filtered RA episode: %s", episode.title)
            return

        writer.create_bookmark(episode.title)
        writer.insert_image_from_url_centred(episode.image_url, EPISODE_IMAGE_HEIGHT, episode.page_url)
        writer.write_text_to_page_centered_x(
            "(Click image above to jump to episode webpage)",
            EPISODE_WEB_LINK_LABEL_Y * cm,
            SUB_HEADING_FONT,
            SUB_HEADING_FONT_SIZE,
            SUBTLE_TEXT_COLOUR,
        )
        writer.write_text_to_page_centered_x(
            episode.title,
            EPISODE_TITLE_Y * cm,
            SUB_HEADING_FONT,
            EPISODE_FONT_SIZE,
            EPISODE_FONT_COLOUR,
        )
        writer.write_text_to_page_centered_x(
            "(Click image below to jump to episode MP3)",
            LISTEN_LABEL_Y * cm,
            SUB_HEADING_FONT,
            SUB_HEADING_FONT_SIZE,
            SUBTLE_TEXT_COLOUR,
        )
        writer.write_listen_badge(episode.audio_url)
        writer.write_sub_heading_to_page(episode.description, DESCRIPTION_Y * cm)
        writer.insert_jump_to_toc_link()
        writer.new_page()

    def render_episode_pages(self, writer: Any, episodes: list[Any]) -> None:
        """Render all RA episode pages, skipping any that exhaust retry attempts."""
        for episode in episodes:
            logger.info(self._EPISODE_SEPARATOR)
            episode.print_out()
            try:
                self._run_with_retry(
                    lambda current=episode: self._render_single_episode_page(writer, current),
                    episode.title,
                    (Exception,),
                )
            except RuntimeError:
                logger.warning("Skipping RA episode after retries: %s", episode.title)
