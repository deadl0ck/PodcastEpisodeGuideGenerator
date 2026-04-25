"""RA-specific PDF writer."""

from __future__ import annotations

import logging

from reportlab.lib.utils import ImageReader

from pdf_writer_base import BasePDFWriter
from podcasts.common.page_constants import (
    COVER_SUB_TEXT,
    DEFAULT_FONT_BOLD,
    LISTEN_IMAGE_WIDTH,
    LISTEN_IMAGE_Y,
    SUBTLE_TEXT_COLOUR,
    TOC_FONT_SIZE,
)
from podcasts.ra.page_constants import (
    COVER_FONT_COLOUR,
    COVER_IMAGE,
    COVER_LINK,
    FULL_PDF_PATH,
    IMAGE_CACHE_LOCATION,
    JUMP_TO_TOC_TEXT,
    LISTEN_IMAGE,
    REMOVED_COVER_SUFFIX,
    TEXT_TO_REMOVE,
    TOC_BOOKMARK,
)

logger = logging.getLogger(__name__)


class PDFWriter(BasePDFWriter):
    _toc_bookmark = TOC_BOOKMARK
    _toc_heading_colour = None
    _jump_to_toc_font = DEFAULT_FONT_BOLD

    def __init__(self):
        """Initialise the RA PDF writer with provider-local cache paths."""
        super().__init__(
            pdf_path=FULL_PDF_PATH,
            image_cache_dir=IMAGE_CACHE_LOCATION,
        )

    @staticmethod
    def removal_text_present(text: str, cover_url: str) -> bool:
        """Return True if the episode should be suppressed (error cover or filtered text)."""
        if cover_url.endswith(REMOVED_COVER_SUFFIX):
            return True

        lowered = (text or "").lower()
        for current_text in TEXT_TO_REMOVE:
            if current_text.lower() in lowered:
                return True
        return False

    def write_ra_cover(self) -> None:
        """Write the local RA cover image and branding to a new PDF page."""
        logger.info("Writing RA cover")
        cover_image = ImageReader(COVER_IMAGE)
        self.canvas.drawImage(cover_image, 30, 100, 525, 725, preserveAspectRatio=True)
        self.write_text_to_page(
            COVER_SUB_TEXT,
            DEFAULT_FONT_BOLD,
            36,
            COVER_FONT_COLOUR,
            5,
            3,
        )
        # Keep cover link behavior from existing provider pattern.
        self.canvas.linkURL(COVER_LINK, (30, 100, 555, 825), relative=0, thickness=0)
        self.new_page()

    def write_listen_badge(self, audio_url: str) -> None:
        """Write the listen-now badge linking to the episode MP3."""
        if not audio_url:
            return
        self.write_listen_image(audio_url, LISTEN_IMAGE, LISTEN_IMAGE_WIDTH, LISTEN_IMAGE_Y)

    def write_jump_to_toc_link(self) -> None:
        """Write a small jump-to-TOC hyperlink at the bottom of the current page."""
        self.write_text_with_link(
            JUMP_TO_TOC_TEXT,
            DEFAULT_FONT_BOLD,
            TOC_FONT_SIZE,
            SUBTLE_TEXT_COLOUR,
            18,
            0.3,
            TOC_BOOKMARK,
        )
