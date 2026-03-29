from __future__ import annotations

from abc import ABC, abstractmethod


class BaseGuideMain(ABC):
    """Shared orchestration for guide generation entrypoints."""

    def __init__(self, writer):
        self.writer = writer

    def create_magazine(self, cover_image: str, episodes: list):
        self.write_cover(cover_image)
        context = self.build_context(episodes)
        self.write_toc(episodes, context)
        self.build_pages(episodes, context)
        self.write_feature_list(episodes, context)

    def create_and_save_magazine(self, cover_image: str, episodes: list) -> None:
        """Shared end-to-end flow used by provider main() entrypoints."""
        self.create_magazine(cover_image, episodes)
        self.writer.save_and_close_pdf()

    def write_standard_cover(
        self,
        cover_image: str,
        cover_image_width: int,
        cover_text: str,
        cover_text_y_cm,
        cover_sub_text: str,
        cover_sub_text_y_cm,
        default_font_bold: str,
        cover_font_size: int,
        cover_font_colour,
        cover_link: str,
    ) -> None:
        """Shared cover writer used by podcast-specific guide mains."""
        self.writer.write_cover(
            cover_image,
            cover_image_width,
            cover_text,
            cover_text_y_cm,
            cover_sub_text,
            cover_sub_text_y_cm,
            default_font_bold,
            cover_font_size,
            cover_font_colour,
            cover_link,
        )

    def write_standard_toc(
        self,
        episode_names: list,
        toc_text: str,
        default_font_bold: str,
        toc_font_size: int,
        toc_font_colour,
        toc_spacing_delta: float,
    ) -> None:
        """Shared TOC writer used by podcast-specific guide mains."""
        self.writer.write_toc(
            episode_names,
            toc_text,
            default_font_bold,
            toc_font_size,
            toc_font_colour,
            toc_spacing_delta,
        )

    @abstractmethod
    def write_cover(self, cover_image: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def build_context(self, episodes: list) -> dict:
        raise NotImplementedError

    @abstractmethod
    def write_toc(self, episodes: list, context: dict) -> None:
        raise NotImplementedError

    @abstractmethod
    def build_pages(self, episodes: list, context: dict) -> None:
        raise NotImplementedError

    @abstractmethod
    def write_feature_list(self, episodes: list, context: dict) -> None:
        raise NotImplementedError
