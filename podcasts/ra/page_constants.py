"""RA-specific constants and cache paths."""

from __future__ import annotations

import os

from reportlab.lib import colors

from cache_paths import (
    RA_EPISODE_CACHE_FILENAME,
    RA_PROVIDER_KEY,
    get_podcast_cache_file,
    get_podcast_cache_root,
    get_podcast_image_cache_dir,
)
from podcasts.common.page_constants import (
    PDF_LOCATION,
)

START_URL = "https://retroasylum.com/category/all-posts/podcasts/"

# Keep filtering semantics from the original RA generator, but centralize in config.
REMOVED_COVER_SUFFIX = "RA_error.png"
TEXT_TO_REMOVE = ("Paul Davies",)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RA_ASSET_DIR = os.path.join(PROJECT_ROOT, "podcasts", "ra", "assets")

CACHE_ROOT = get_podcast_cache_root(RA_PROVIDER_KEY)
IMAGE_CACHE_LOCATION = get_podcast_image_cache_dir(RA_PROVIDER_KEY)
EPISODE_CACHE_LOCATION = get_podcast_cache_file(RA_PROVIDER_KEY, RA_EPISODE_CACHE_FILENAME)

PDF_NAME = "RA Episode Guide.pdf"
FULL_PDF_PATH = f"{PDF_LOCATION}{os.sep}{PDF_NAME}"

COVER_IMAGE = os.path.join(RA_ASSET_DIR, "RACover.png")
COVER_TEXT = "RETRO ASYLUM"
COVER_LINK = "https://retroasylum.com/"
COVER_FONT_COLOUR = colors.black

TOC_BOOKMARK = "TOC"
TOC_FONT_COLOUR = colors.black
JUMP_TO_TOC_TEXT = "[Jump to TOC]"

EPISODE_FONT_SIZE = 20
EPISODE_FONT_COLOUR = colors.black
SUB_HEADINGS_LETTERS_PER_LINE = 90
EPISODE_IMAGE_HEIGHT = 500
LISTEN_IMAGE = "https://i.ibb.co/NWmMHcH/Listen-Now.jpg"

LISTEN_LABEL_Y = 29.2 - 26
DESCRIPTION_Y = 29.2 - 1
EPISODE_TITLE_Y = 29.7 - 1
EPISODE_WEB_LINK_LABEL_Y = 29.2 - 24


def ensure_cache_dirs() -> None:
    """Create RA cache directories if they do not already exist."""
    os.makedirs(CACHE_ROOT, exist_ok=True)
    os.makedirs(IMAGE_CACHE_LOCATION, exist_ok=True)
