"""
Shared constants for all podcasts.
Defines common PDF layout, colors, fonts, and standard values.
Each podcast-specific page_constants.py imports from here and adds
podcast-specific values (cover images, branding, cache paths, etc.).
"""
from reportlab.lib import colors
from reportlab.lib.units import cm
import os

# ================================================================
# Common PDF Layout & Design Constants
# ================================================================

# Standard fonts used across all podcasts
DEFAULT_FONT_BOLD = "Helvetica-Bold"
DEFAULT_FONT = "Helvetica"

# Standard colors
DEFAULT_FONT_COLOUR = colors.black
HEADING_FONT_COLOUR = colors.blue
SUBTLE_TEXT_COLOUR = colors.slategrey
NULL_LINK = "#null"

# Desktop PDF output paths (podcasts override PDF_NAME and FULL_PDF_PATH)
PDF_LOCATION = f"{os.path.expanduser('~')}{os.sep}Desktop"

# Standard font sizes for major sections
TOC_FONT_SIZE = 10
EPISODE_FONT_SIZE = 18
SUB_HEADING_FONT_SIZE = 12

# Standard text and spacing
TOC_TEXT = "Table Of Contents"
TOC_SPACING_DELTA = 0.5
TOC_BOOKMARK = "Table of Contents"

# Sub-heading layout (used for titles within episodes)
SUB_HEADING_FONT = "Helvetica-Bold"
SUB_HEADING_X = 15
SUB_HEADING_Y_DELTA = 0.5

# Image sizing
EPISODE_IMAGE_WIDTH = 400
LISTEN_IMAGE_WIDTH = 140
LISTEN_IMAGE_Y = 5

# Text rendering dimensions for link rectangles
DEFAULT_FONT_WIDTH = .182  # approximate char width in cm
DEFAULT_FONT_HEIGHT = 0.3   # link rect height in cm

# Cover page layout (Y positions in cm)
COVER_FONT_SIZE = 30
COVER_IMAGE_WIDTH = 525
COVER_TEXT_Y_CM = 27 * cm
COVER_SUB_TEXT_Y_CM = 2 * cm
COVER_SUB_TEXT = "Episode Guide".upper()

# Episode page layout (Y positions relative to A4 page)
EPISODE_TEXT_Y_CM = 28 * cm
EPISODE_HEADING_LINE_SPACING = 0.6 * cm
EPISODE_DESCRIPTION_Y = 29.2 * cm - 2.5 * cm
EPISODE_YOUTUBE_LABEL_Y = 29.2 * cm - 22 * cm
EPISODE_AIRDATE_Y = 29.2 * cm - 23 * cm
EPISODE_LISTEN_LABEL_Y = 29.2 * cm - 27 * cm

# Text wrapping dimensions
HEADING_LETTERS_PER_LINE = 60
DEFAULT_LETTERS_PER_LINE = 92

# Standard listen image (same for both podcasts)
LISTEN_IMAGE = "https://i.ibb.co/NWmMHcH/Listen-Now.jpg"
