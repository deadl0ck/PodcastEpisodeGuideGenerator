from __future__ import annotations

from dataclasses import dataclass

from reportlab.lib import colors
from reportlab.lib.units import cm


@dataclass(frozen=True)
class BaseConstants:
    default_font_bold: str = "Helvetica-Bold"

    cover_font_size: int = 30
    cover_font_colour: object = colors.black
    cover_image_width: int = 525
    cover_title_y: float = 27 * cm
    cover_subtitle_y: float = 2 * cm

    toc_font_size: int = 10
    toc_font_colour: object = colors.black
    toc_text: str = "Table Of Contents"
    toc_spacing_delta: float = 0.5

    sub_heading_font: str = "Helvetica-Bold"
    sub_heading_font_size: int = 12
    sub_heading_x: int = 15
    sub_heading_y_delta: float = 0.5
    sub_heading_font_colour: object = colors.black

    episode_title_y: float = 28 * cm
    episode_title_font_size: int = 18
    episode_title_font_colour: object = colors.black

    listen_image_url: str = "https://i.ibb.co/NWmMHcH/Listen-Now.jpg"
    listen_image_width: int = 140
    listen_image_y: int = 5

    subtle_text_colour: object = colors.slategrey
    null_link: str = "#null"
