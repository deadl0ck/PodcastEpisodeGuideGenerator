# podcasts/twir/pdf_writer.py
# TWIR-specific PDF writer — extends BasePDFWriter with QoW page support.
import os
from typing import Any

from reportlab.lib import colors
from reportlab.pdfgen.canvas import Canvas  # Backward-compatible test patch target.

from cache_paths import IMAGE_CACHE_DIR, LEGACY_TWIR_IMAGE_CACHE_DIR, ensure_cache_dirs
from podcasts.twir.page_constants import (
    DEFAULT_FONT_BOLD,
    DEFAULT_LETTERS_PER_LINE,
    FULL_PDF_PATH,
    QOW_FONT,
    QOW_FONT_COLOUR,
    QOW_LIST_BOOKMARK,
    QOW_LIST_FONT_SIZE,
    QOW_LIST_HEADING_FONT_COLOUR,
    TOC_BOOKMARK,
    TOC_HEADING_FONT_COLOUR,
)
from pdf_writer_base import BasePDFWriter, PAGE_HEIGHT


class PDFWriter(BasePDFWriter):
    # TWIR-specific provider settings
    _toc_bookmark = TOC_BOOKMARK
    _toc_heading_colour = TOC_HEADING_FONT_COLOUR
    _jump_to_toc_font = QOW_FONT

    def __init__(self):
        ensure_cache_dirs()
        super().__init__(
            pdf_path=FULL_PDF_PATH,
            image_cache_dir=IMAGE_CACHE_DIR,
            legacy_image_cache_dir=os.path.join(os.path.dirname(__file__), "..", "..", "image_cache"),
            legacy_namespaced_image_cache_dir=LEGACY_TWIR_IMAGE_CACHE_DIR,
        )

    @staticmethod
    def split_into_multiline(text: str, letters_per_line: int = DEFAULT_LETTERS_PER_LINE) -> list[str]:
        return BasePDFWriter.split_into_multiline(text, letters_per_line)

    def write_qow(self, text: str, x: float, y: float, url: str) -> None:
        multiline_text = PDFWriter.split_into_multiline(text)
        self.write_text_to_page(
            'Community Question of the Week:',
            QOW_FONT,
            QOW_LIST_FONT_SIZE,
            colors.black,
            1,
            y,
        )
        y -= 0.5

        for current_line in multiline_text:
            self.write_text_with_link(
                current_line,
                QOW_FONT,
                QOW_LIST_FONT_SIZE,
                QOW_FONT_COLOUR,
                x,
                y,
                url,
            )
            y -= 0.5

        self.write_text_to_page(
            '(Click the question to go to the Reddit post!)',
            QOW_FONT,
            QOW_LIST_FONT_SIZE,
            colors.slategrey,
            1,
            y,
        )

    def write_qow_list(
        self,
        qow_dict: dict,
        qow_text: str,
        qow_font: str,
        qow_font_size: int,
        qow_font_colour: Any,
        qow_spacing_delta: float,
    ) -> None:
        x = 1
        current_y = PAGE_HEIGHT - 1

        self.canvas.bookmarkPage(QOW_LIST_BOOKMARK)
        self.write_text_to_page(
            qow_text,
            qow_font,
            qow_font_size + 4,
            QOW_LIST_HEADING_FONT_COLOUR,
            5,
            current_y,
        )
        current_y -= qow_spacing_delta

        qow_list = []
        for qow in qow_dict.keys():
            qow_list.append((
                qow_dict[qow].episode_number,
                PDFWriter.split_into_multiline(
                    f'[Episode {qow_dict[qow].episode_number}] {qow_dict[qow].question}'
                ),
            ))

        for qow_tuples in qow_list:
            episode_num = qow_tuples[0]
            question_text = qow_tuples[1]
            question_text.append("")
            for qow in question_text:
                if current_y == 0:
                    current_y = PAGE_HEIGHT - 1
                    self.new_page()

                self.write_text_with_link(
                    f'{qow}',
                    qow_font,
                    qow_font_size,
                    qow_font_colour,
                    x,
                    current_y,
                    qow_dict[episode_num].url,
                )

                current_y -= qow_spacing_delta

        self.new_page()
