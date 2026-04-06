"""
TWIR-specific constants — cover, branding, and features.
Inherits common PDF layout constants from podcasts.common.page_constants.
"""
import os
from reportlab.lib import colors

from podcasts.common.page_constants import (
    DEFAULT_FONT_BOLD,
    DEFAULT_FONT_HEIGHT,
    DEFAULT_FONT_WIDTH,
    HEADING_FONT_COLOUR,
    PDF_LOCATION,
    TOC_FONT_SIZE,
    TOC_SPACING_DELTA,
)

# TWIR-specific PDF file name and path
PDF_NAME = "TWiR Episode Guide.pdf"
FULL_PDF_PATH = f'{PDF_LOCATION}{os.sep}{PDF_NAME}'
CSV_LOCATION = f"{os.path.expanduser('~')}{os.sep}Desktop{os.sep}TWiR_Data.csv"

# TWIR branding
COVER_IMAGE = "https://i.ibb.co/ccL0XZPJ/TWIR-Reddit-logo.jpg"
COVER_TEXT = "This Week in Retro".upper()
COVER_LINK = "https://www.youtube.com/@ThisWeekinRetro/videos"

# TWIR-specific colors (using common default colors for most)
COVER_FONT_COLOUR = colors.black
TOC_FONT_COLOUR = colors.black
TOC_HEADING_FONT_COLOUR = HEADING_FONT_COLOUR  # colors.blue
EPISODE_FONT_COLOUR = colors.black
EPISODE_HEADING_FONT_COLOUR = HEADING_FONT_COLOUR  # colors.blue

# Community Question of the Week feature (TWIR-specific)
QOW_LIST_BOOKMARK = "QOW List"
QOW_LIST_FONT_SIZE = TOC_FONT_SIZE  # 10
QOW_LIST_FONT_COLOUR = colors.black
QOW_LIST_TEXT = "Community Question of the Week List"
QOW_LIST_HEADING_FONT_COLOUR = HEADING_FONT_COLOUR  # colors.blue
QOW_LIST_SPACING_DELTA = TOC_SPACING_DELTA  # 0.5
QOW_FONT_WIDTH = DEFAULT_FONT_WIDTH  # .182
QOW_FONT_HEIGHT = DEFAULT_FONT_HEIGHT  # 0.3
QOW_FONT = DEFAULT_FONT_BOLD  # "Helvetica-Bold"
QOW_FONT_COLOUR = colors.black

# Deprecated: Legacy Y coordinate (kept for compatibility)
EPISODE_QOW_Y = 29.2 - 24
SUB_HEADING_FONT_COLOUR = colors.black
