from __future__ import annotations

from pdf_writer_base import BasePDFWriter
from podcasts.rgds.page_constants import (
    FULL_PDF_PATH,
    IMAGE_CACHE_LOCATION,
    JUMP_TO_TOC_FONT,
    TOC_BOOKMARK,
)


class PDFWriter(BasePDFWriter):
    _toc_bookmark = TOC_BOOKMARK
    _toc_heading_colour = None
    _jump_to_toc_font = JUMP_TO_TOC_FONT

    def __init__(self):
        super().__init__(
            pdf_path=FULL_PDF_PATH,
            image_cache_dir=IMAGE_CACHE_LOCATION,
        )
