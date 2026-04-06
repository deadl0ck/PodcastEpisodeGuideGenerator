"""
Base PDF writer — shared canvas, image cache, and layout utilities.

DESIGN PATTERN:
- BasePDFWriter defines core layout constants as class attributes
  (matching values in podcasts/common/page_constants.py)
- TWIR (pdf_writer_v2.py) and ZTTP (podcasts/zttp/pdf_writer.py)
  extend this class and add only podcast-specific methods
- page_constants.py files import the same layout constants from
  podcasts/common/page_constants.py for use in non-PDF modules

This ensures layout consistency while keeping podcast-specific logic
(QoW pages, Zzap games list, etc.) in subclasses.
"""
from __future__ import annotations

import io
import os
import tempfile
import logging
from typing import Any
from urllib.parse import unquote, urlparse

import numpy as np
import requests
from PIL import Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas

PAGE_HEIGHT = 30
_NULL_LINK = "#null"

logger = logging.getLogger(__name__)


class BasePDFWriter:
    # YouTube serves many different videos under identical filenames (e.g. hqdefault.jpg),
    # so cache keys are always derived from the full URL rather than bare filenames.

    # Layout constants — identical values in both TWIR and ZTTP page_constants.
    # Subclasses can override these class attributes if values ever diverge.
    _FONT_HEIGHT: float = 0.3        # link rect height (cm)
    _FONT_WIDTH: float = 0.182       # approximate char width for link rect (cm)
    _SUB_HEADING_X: float = 15
    _SUB_HEADING_FONT: str = "Helvetica-Bold"
    _SUB_HEADING_FONT_SIZE: int = 12
    _SUB_HEADING_FONT_COLOUR: Any = colors.black
    _SUB_HEADING_Y_DELTA: float = 0.5

    # Provider-specific overrides — subclasses set these as class attributes.
    _toc_bookmark: str = "TOC"
    _toc_heading_colour: Any = None  # None → falls back to toc_font_colour param
    _jump_to_toc_font: str = "Helvetica"

    def __init__(
        self,
        pdf_path: str,
        image_cache_dir: str,
    ) -> None:
        self.canvas = Canvas(pdf_path, pagesize=A4)
        self.listen_image = None
        self.image_cache_dir = image_cache_dir
        os.makedirs(image_cache_dir, exist_ok=True)

    # ------------------------------------------------------------------ #
    # Image cache infrastructure                                           #
    # ------------------------------------------------------------------ #

    def _get_cached_image_path(self, image_url: str) -> str:
        """Build a unique, filesystem-safe cache filename from the URL.
        Format: <host>-<parent_path_segment>-<filename>
        Example: https://i.ytimg.com/vi/kE8c463aibw/hqdefault.jpg
              -> i-ytimg-com-kE8c463aibw-hqdefault.jpg
        """
        parsed = urlparse(image_url)
        path_parts = [unquote(part) for part in parsed.path.split("/") if part]
        file_name = path_parts[-1] if path_parts else "cached_image"
        if len(path_parts) >= 2:
            file_name = f"{path_parts[-2]}-{file_name}"
        host_prefix = parsed.netloc.replace(".", "-")
        file_name = f"{host_prefix}-{file_name}" if host_prefix else file_name
        return os.path.join(self.image_cache_dir, self._sanitize_cache_name(file_name))

    @staticmethod
    def _sanitize_cache_name(value: str) -> str:
        sanitized = "".join(c if c.isalnum() or c in "-_." else "-" for c in value)
        sanitized = sanitized.strip("-_.")
        return sanitized or "cached_image"

    def _get_or_download_image_bytes(self, image_url: str) -> bytes:
        """Load image bytes from canonical cache, otherwise download and cache."""
        cache_path = self._get_cached_image_path(image_url)
        if os.path.exists(cache_path):
            logger.info("Image cache HIT: %s", os.path.basename(cache_path))
            with open(cache_path, "rb") as f:
                return f.read()

        logger.info("Image cache MISS: %s - downloading", os.path.basename(cache_path))
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            image_bytes = response.content
        except requests.RequestException:
            logger.error("Image download FAILED for URL: %s", image_url)
            raise

        with open(cache_path, "wb") as f:
            f.write(image_bytes)
        return image_bytes

    # ------------------------------------------------------------------ #
    # Canvas operations                                                    #
    # ------------------------------------------------------------------ #

    def new_page(self) -> None:
        self.canvas.showPage()

    def save_and_close_pdf(self) -> None:
        self.canvas.save()

    def create_bookmark(self, bookmark_name: str) -> None:
        logger.info("Creating bookmark: %s", bookmark_name)
        self.canvas.bookmarkPage(bookmark_name)

    # ------------------------------------------------------------------ #
    # Text drawing                                                         #
    # ------------------------------------------------------------------ #

    def write_text_to_page(
        self,
        text: str,
        font_name: str,
        font_size: int,
        font_colour: Any,
        x_cm: float,
        y_cm: float,
    ) -> None:
        canvas_text = self.canvas.beginText(x_cm * cm, y_cm * cm)
        canvas_text.setFont(font_name, font_size)
        canvas_text.setFillColor(font_colour)
        canvas_text.textLine(text)
        self.canvas.drawText(canvas_text)

    def write_text_to_page_centered_x(
        self,
        text: str,
        y_cm: float,
        font: str,
        font_size: int,
        font_colour: Any,
    ) -> None:
        text_width = self.canvas.stringWidth(text, font, font_size)
        page_width, _ = A4
        text_x = (page_width - text_width) / 2
        canvas_text = self.canvas.beginText(text_x, y_cm)
        canvas_text.setFont(font, font_size)
        canvas_text.setFillColor(font_colour)
        canvas_text.textLine(text)
        self.canvas.drawText(canvas_text)

    def write_text_with_link(
        self,
        text: str,
        font_name: str,
        font_size: int,
        font_colour: Any,
        x_cm: float,
        y_cm: float,
        url: str,
    ) -> None:
        self.write_text_to_page(text, font_name, font_size, font_colour, x_cm, y_cm)
        if not text.strip() or url == _NULL_LINK:
            return
        link_rect = BasePDFWriter._get_text_rect([text], x_cm, y_cm, y_cm + self._FONT_HEIGHT)
        if url.startswith("http"):
            self.canvas.linkURL(url, link_rect, relative=0, thickness=0)
        else:
            self.canvas.linkRect("Click to jump to episode", url, link_rect, relative=0, thickness=0)

    @staticmethod
    def _get_text_rect(
        text_list: list[str], x_pos: float, start_y: float, end_y: float
    ) -> tuple:
        x1 = x_pos * cm
        y1 = start_y * cm
        max_line_length = max((len(line) for line in text_list), default=0)
        x2 = x1 + (max_line_length * 0.182) * cm
        y2 = end_y * cm
        return x1, y1, x2, y2

    def write_sub_heading_to_page(self, text: str, y_cm: float) -> None:
        for line in BasePDFWriter.split_into_multiline(text):
            canvas_text = self.canvas.beginText(self._SUB_HEADING_X, y_cm)
            canvas_text.setFont(self._SUB_HEADING_FONT, self._SUB_HEADING_FONT_SIZE)
            canvas_text.setFillColor(self._SUB_HEADING_FONT_COLOUR)
            canvas_text.textLine(line)
            self.canvas.drawText(canvas_text)
            y_cm -= self._SUB_HEADING_Y_DELTA * cm

    def insert_jump_to_toc_link(self) -> None:
        self.write_text_with_link(
            "[Jump to TOC]",
            self._jump_to_toc_font,
            10,  # TOC_FONT_SIZE — identical in both providers
            colors.slategrey,
            18,
            0.3,
            self._toc_bookmark,
        )

    @staticmethod
    def split_into_multiline(text: str, letters_per_line: int = 90) -> list[str]:
        current_text = text
        lines = []
        while current_text:
            if len(current_text) >= letters_per_line:
                if " " in current_text[:letters_per_line]:
                    last_space = current_text[:letters_per_line].rindex(" ")
                else:
                    last_space = letters_per_line
                lines.append(current_text[:last_space])
                current_text = current_text[last_space:].strip()
            else:
                lines.append(current_text)
                break
        return lines

    # ------------------------------------------------------------------ #
    # Image drawing                                                        #
    # ------------------------------------------------------------------ #

    def write_listen_image(
        self,
        link_url: str,
        listen_image_url: str,
        listen_image_width: int,
        listen_image_y: int,
    ) -> None:
        page_width, _ = A4
        image_x = (page_width - listen_image_width) / 2
        self.insert_image_from_url_with_link(
            listen_image_url, listen_image_width, image_x, listen_image_y,
            link_url, show_boundary=False,
        )

    def write_cover(
        self,
        image_url: str,
        image_width: int,
        text: str,
        text_y_cm: int,
        sub_text: str,
        sub_text_y_cm: int,
        font: str,
        font_size: int,
        font_colour: Any,
        link_url: str | None = None,
    ) -> None:
        logger.info("Writing main cover")
        self.insert_image_from_url_centred(image_url, image_width, link_url)
        self.write_text_to_page_centered_x(text, text_y_cm, font, font_size, font_colour)
        self.write_text_to_page_centered_x(sub_text, sub_text_y_cm, font, font_size, font_colour)
        self.new_page()

    def insert_image_from_url_with_link(
        self,
        image_url: str,
        required_width: int,
        image_x: int,
        image_y: int,
        link_url: str | None = None,
        show_boundary: bool = True,
    ) -> None:
        # The listen/Podbean button image is the same on every page; load once
        # and reuse via self.listen_image to avoid redundant file reads.
        if self.listen_image is None:
            image_bytes = self._get_or_download_image_bytes(image_url)
            logger.debug("Loaded listen image")
            image = Image.open(io.BytesIO(image_bytes))
            self.listen_image = image
        else:
            image = self.listen_image

        # ReportLab cannot write JPEG data directly; convert to PNG via numpy.
        image_format = image_url[image_url.rindex(".") + 1:].lower()
        if image_format in ("jpg", "jpeg"):
            a = np.asarray(image)
            image = Image.fromarray(a)
            image_format = "png"

        width_percent = required_width / float(image.size[0])
        height_size = int(float(image.size[1]) * width_percent)
        image = image.resize((required_width, height_size), Image.NEAREST)

        tmp = tempfile.NamedTemporaryFile()
        image.save(tmp.name, format=image_format)
        resized_image = ImageReader(tmp)

        self.canvas.drawImage(
            resized_image, image_x, image_y, required_width, height_size,
            preserveAspectRatio=True, showBoundary=show_boundary,
        )
        if image_url and image_url.strip():
            link_rect = (int(image_x), int(image_y), int(image_x) + required_width, int(image_y) + height_size)
            self.canvas.linkURL(link_url, link_rect, relative=0, thickness=0)

    def insert_image_from_url_centred(
        self, url: str, required_height: int, link_url: str | None = None
    ) -> None:
        """Download (or load from cache) an image, scale it to required_height
        preserving aspect ratio, then centre it horizontally on the current page."""
        logger.debug("Image URL is %s", url)
        image_bytes = self._get_or_download_image_bytes(url)
        im = Image.open(io.BytesIO(image_bytes))

        if im.mode in ("RGBA", "CMYK"):
            image = im.convert("RGB")
        else:
            image = im
        image_format = im.format
        # Copy JPEG data through numpy to avoid artefacts from Pillow's JPEG encoder.
        if image.format == "JPEG":
            image_format = image.format
            a = np.asarray(image)
            image = Image.fromarray(a)

        height_percent = required_height / float(image.size[1])
        width_size = int(float(image.size[0]) * height_percent)
        image = image.resize((width_size, required_height), Image.NEAREST)
        image.format = image_format

        tmp = tempfile.NamedTemporaryFile()
        tmp_name = tmp.name + "." + image.format
        image.save(tmp_name, format=image.format)
        resized_image = ImageReader(tmp_name)

        page_width, page_height = A4
        image_x = (page_width - width_size) / 2
        image_y = (page_height - required_height) / 2
        self.canvas.drawImage(
            resized_image, image_x, image_y, width_size, required_height,
            preserveAspectRatio=True, showBoundary=False,
        )
        if url and url.strip():
            link_rect = (int(image_x), int(image_y), int(image_x) + width_size, int(image_y) + required_height)
            self.canvas.linkURL(link_url, link_rect, relative=0, thickness=0)

    # ------------------------------------------------------------------ #
    # Table of contents                                                    #
    # ------------------------------------------------------------------ #

    def write_toc(
        self,
        episodes: list[tuple],
        toc_text: str,
        toc_font: str,
        toc_font_size: int,
        toc_font_colour: Any,
        toc_spacing_delta: float,
    ) -> None:
        x = 1
        current_y = PAGE_HEIGHT - 1
        self.canvas.bookmarkPage(self._toc_bookmark)

        heading_colour = (
            self._toc_heading_colour if self._toc_heading_colour is not None else toc_font_colour
        )
        self.write_text_to_page(toc_text, toc_font, toc_font_size + 4, heading_colour, 8, current_y)
        current_y -= toc_spacing_delta

        for episode in episodes:
            if current_y == 0:
                current_y = PAGE_HEIGHT - 1
                self.new_page()

            toc_title = episode[0]
            episode_ref = f"{episode[1]}"
            if toc_title:
                self.write_text_with_link(
                    toc_title, toc_font, toc_font_size, toc_font_colour, x, current_y, episode_ref
                )
            else:
                self.write_text_to_page(
                    toc_title, toc_font, toc_font_size, toc_font_colour, x, current_y
                )
            current_y -= toc_spacing_delta

        self.new_page()
