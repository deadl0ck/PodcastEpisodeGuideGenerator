from __future__ import annotations

import os
import logging
from typing import Any
from urllib.parse import unquote, urlparse


from pdf_writer_base import BasePDFWriter, PAGE_HEIGHT
from podcasts.common.page_constants import DEFAULT_FONT_BOLD, SUBTLE_TEXT_COLOUR
from podcasts.zttp.page_constants import (
    PDF_LOCATION,
    PDF_NAME,
    IMAGE_CACHE_LOCATION,
    GAME_LIST_BOOKMARK,
    JUMP_TO_TOC_FONT,
    JUMP_TO_TOC_TEXT,
    TOC_BOOKMARK,
    TOC_FONT_SIZE,
)


logger = logging.getLogger(__name__)


class PDFWriter(BasePDFWriter):
    # ZTTP-specific provider settings
    _toc_bookmark = TOC_BOOKMARK
    _toc_heading_colour = None
    _jump_to_toc_font = JUMP_TO_TOC_FONT

    def __init__(self):
        pdf_path = f'{PDF_LOCATION}/{PDF_NAME}'
        super().__init__(
            pdf_path=pdf_path,
            image_cache_dir=IMAGE_CACHE_LOCATION,
        )

    def _get_or_download_image_bytes(self, image_url: str) -> bytes:
        # ZTTP historically keyed cache entries by bare filename; preserve that path
        # so pre-seeded files like Listen-Now.jpg are used without network access.
        parsed = urlparse(image_url)
        file_name = os.path.basename(parsed.path) or "cached_image"
        file_name = unquote(file_name)
        zttp_filename_cache = os.path.join(IMAGE_CACHE_LOCATION, file_name)
        if os.path.exists(zttp_filename_cache):
            logger.info("Image cache HIT (ZTTP filename): %s", os.path.basename(zttp_filename_cache))
            with open(zttp_filename_cache, "rb") as f:
                return f.read()
        logger.info("Image cache MISS (ZTTP filename): %s", file_name)
        return super()._get_or_download_image_bytes(image_url)

    # Backward-compatible aliases during migration.
    def insert_image_from_ulr_centred(self, url: str, required_height: int, link_url: str | None = None):
        return self.insert_image_from_url_centred(url, required_height, link_url)

    def insert_image_from_ulr_with_link(self, image_url: str, required_width: int, image_x: int, image_y: int,
                                        link_url: str | None = None, show_boundary: bool = True):
        return self.insert_image_from_url_with_link(
            image_url, required_width, image_x, image_y, link_url, show_boundary
        )

    def write_games_list(
        self,
        episodes: list,
        heading: str,
        game_list_font: str,
        game_list_font_size: int,
        game_list_font_colour: Any,
        game_list_spacing_delta: float,
    ):
        x = 1
        current_y = PAGE_HEIGHT - 1
        self.create_bookmark(GAME_LIST_BOOKMARK)

        total_games = 0
        for ep in episodes:
            total_games += len(ep.games_list)
        heading += f' (Total Games Reviewed: {total_games})'

        self.write_text_to_page(heading, game_list_font, game_list_font_size + 4, game_list_font_colour, 4.5, current_y)
        current_y -= game_list_spacing_delta

        for episode in episodes:
            logger.info('Episode: %s', episode.title)
            if len(episode.games_list) == 0 or "Award" in episode.title:
                logger.info('\tSkipping above episode')
                logger.info('\tEpisode Number: %s', episode.episode_number)
                logger.info('\tGames List Length: %s', len(episode.games_list))
                if "Award" in episode.title:
                    logger.info('\tEpisode Title: "%s" contains "Award"', episode.title)
                continue

            episode_and_games = [episode.title] + episode.games_list
            episode_name_written = False
            for game in episode_and_games:
                if current_y == 0:
                    current_y = PAGE_HEIGHT - 1
                    self.new_page()

                data = f'        - {game}'
                if not episode_name_written:
                    number_to_use = episode.episode_number if episode.episode_number != -1 else "Special"
                    data = f'({number_to_use}) {game}'
                    self.write_text_with_link(
                        data,
                        game_list_font,
                        game_list_font_size,
                        game_list_font_colour,
                        x,
                        current_y,
                        f'{episode.title}',
                    )
                else:
                    total_games += 1
                    self.write_text_to_page(
                        data,
                        game_list_font,
                        game_list_font_size,
                        game_list_font_colour,
                        x,
                        current_y,
                    )
                current_y -= game_list_spacing_delta
                episode_name_written = True
                self.write_text_with_link(
                    JUMP_TO_TOC_TEXT,
                    DEFAULT_FONT_BOLD,
                    TOC_FONT_SIZE,
                    SUBTLE_TEXT_COLOUR,
                    18,
                    0.3,
                    TOC_BOOKMARK,
                )

        self.new_page()
