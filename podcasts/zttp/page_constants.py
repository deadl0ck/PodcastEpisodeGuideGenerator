"""
ZTTP-specific constants — feed, cache paths, cover, branding, and game features.
Inherits common PDF layout constants from podcasts.common.page_constants.
"""
import os
from reportlab.lib import colors

from podcasts.common.page_constants import (
    PDF_LOCATION,
    TOC_FONT_SIZE,
    TOC_SPACING_DELTA,
)

# ZTTP-specific RSS feed
FEED_URL = 'https://feed.podbean.com/zappedtothepast/feed.xml'

# ZTTP cache directory structure
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CACHE_ROOT = os.path.join(PROJECT_ROOT, '.cache', 'ZTTP')
IMAGE_CACHE_LOCATION = os.path.join(CACHE_ROOT, 'images')
EPISODE_CACHE_LOCATION = os.path.join(CACHE_ROOT, 'episode_cache.pkl')
ZZAP_CACHE_LOCATION = os.path.join(CACHE_ROOT, 'zzap_cache.pkl')
CRAPVERTS_CACHE_LOCATION = os.path.join(CACHE_ROOT, 'crapverts_cache.pkl')

# ZTTP-specific PDF file name and path
PDF_NAME = "ZTTP Episode Guide.pdf"
FULL_PDF_PATH = f'{PDF_LOCATION}{os.sep}{PDF_NAME}'

# ZTTP branding
COVER_IMAGE = "https://pbcdn1.podbean.com/imglogo/image-logo/10864927/ZTTP_ORANGE_2k.png"
COVER_TEXT = "Zapped to The past".upper()
COVER_LINK = "https://zappedtothepast.com/"

# ZTTP-specific colors (using common defaults for most)
COVER_FONT_COLOUR = colors.black
TOC_FONT_COLOUR = colors.black
EPISODE_FONT_SIZE = 18
EPISODE_FONT_COLOUR = colors.black

# ZTTP-specific TOC enhancements
JUMP_TO_TOC_FONT = "Helvetica"
JUMP_TO_TOC_TEXT = "[Jump to TOC]"
GAME_LIST_BOOKMARK = "GAMES_LIST"
TOC_BOOKMARK = "TOC"  # ZTTP uses short form

# Game Review List feature (ZTTP-specific)
GAME_LIST_FONT_SIZE = TOC_FONT_SIZE  # 10
GAME_LIST_FONT_COLOUR = colors.black
GAME_LIST_TEXT = "Game Review List"
GAME_LIST_SPACING_DELTA = TOC_SPACING_DELTA  # 0.5

# ZTTP-specific layout
EPISODE_IMAGE_WIDTH = 350  # Smaller than TWIR for game list space
ZZAP_COVER_WIDTH = 780
SUB_HEADINGS_LETTERS_PER_LINE = 90  # ZTTP-specific text wrapping

# Re-export inherited values for backward compatibility
SUB_HEADING_FONT_COLOUR = colors.black


def ensure_cache_dirs() -> None:
    """Create ZTTP cache directories if they don't exist."""
    os.makedirs(CACHE_ROOT, exist_ok=True)
    os.makedirs(IMAGE_CACHE_LOCATION, exist_ok=True)

