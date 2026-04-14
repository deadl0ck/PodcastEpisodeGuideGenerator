from __future__ import annotations

import os
from urllib.parse import urlparse

from reportlab.lib import colors
from reportlab.lib.units import cm

from cache_paths import (
    RGDS_AUTH_CACHE_FILENAME,
    RGDS_EPISODE_CACHE_FILENAME,
    RGDS_PROVIDER_KEY,
    ensure_podcast_cache_dirs,
    get_podcast_cache_file,
    get_podcast_cache_root,
    get_podcast_image_cache_dir,
)
from podcasts.common.page_constants import (
    COVER_SUB_TEXT,
    DEFAULT_FONT_BOLD,
    LISTEN_IMAGE,
    PDF_LOCATION,
    SUB_HEADING_FONT,
    SUB_HEADING_FONT_SIZE,
    SUBTLE_TEXT_COLOUR,
    TOC_BOOKMARK,
    TOC_FONT_SIZE,
    TOC_SPACING_DELTA,
    TOC_TEXT,
)

CACHE_ROOT = get_podcast_cache_root(RGDS_PROVIDER_KEY)
IMAGE_CACHE_LOCATION = get_podcast_image_cache_dir(RGDS_PROVIDER_KEY)
EPISODE_CACHE_LOCATION = get_podcast_cache_file(RGDS_PROVIDER_KEY, RGDS_EPISODE_CACHE_FILENAME)
AUTH_CACHE_LOCATION = get_podcast_cache_file(RGDS_PROVIDER_KEY, RGDS_AUTH_CACHE_FILENAME)

PDF_NAME = "RGDS Episode Guide.pdf"
FULL_PDF_PATH = f"{PDF_LOCATION}{os.sep}{PDF_NAME}"

DEFAULT_SHOW_ID = "00sL9tgDezr0PRSzd3C7H6"
OAUTH_SCOPE = "user-read-playback-position"

COVER_TEXT = "Retro Game Discussion Show".upper()
COVER_LINK = "https://open.spotify.com/show/00sL9tgDezr0PRSzd3C7H6"
COVER_FONT_COLOUR = colors.black

TOC_FONT_COLOUR = colors.black

EPISODE_FONT_SIZE = 18
EPISODE_FONT_COLOUR = colors.black
EPISODE_IMAGE_WIDTH = 530
SUB_HEADINGS_LETTERS_PER_LINE = 90

RELEASED_TEXT_Y_CM = 2.75 * cm
RELEASED_FONT_SIZE = 12
RELEASED_FONT_COLOUR = colors.black
RELEASED_HEADING_FONT = DEFAULT_FONT_BOLD
DESCRIPTION_Y = 29.2 * cm - 1.5 * cm
EPISODE_INFO_Y = 29.2 * cm - 24.5 * cm

JUMP_TO_TOC_FONT = DEFAULT_FONT_BOLD
JUMP_TO_TOC_TEXT = "[Jump to TOC]"


def redirect_port(redirect_uri: str) -> int:
    parsed = urlparse(redirect_uri)
    if parsed.port is not None:
        return int(parsed.port)
    return 443 if parsed.scheme == "https" else 80


def ensure_cache_dirs() -> None:
    ensure_podcast_cache_dirs(RGDS_PROVIDER_KEY)
