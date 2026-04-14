from __future__ import annotations

import os

from reportlab.lib import colors

from cache_paths import (
    TEN_P_EPISODE_CACHE_FILENAME,
    TEN_P_NEXT_MONTH_GAME_CACHE_FILENAME,
    TEN_P_PROVIDER_KEY,
    ensure_podcast_cache_dirs,
    get_podcast_cache_file,
    get_podcast_cache_root,
    get_podcast_image_cache_dir,
)
from podcasts.common.page_constants import (
    PDF_LOCATION,
    TOC_FONT_SIZE,
    TOC_SPACING_DELTA,
)

FEED_URL = "https://www.tenpencearcade.com/feed.xml"

CACHE_ROOT = get_podcast_cache_root(TEN_P_PROVIDER_KEY)
IMAGE_CACHE_LOCATION = get_podcast_image_cache_dir(TEN_P_PROVIDER_KEY)
EPISODE_CACHE_LOCATION = get_podcast_cache_file(
    TEN_P_PROVIDER_KEY,
    TEN_P_EPISODE_CACHE_FILENAME,
)
NEXT_MONTH_GAME_CACHE_LOCATION = get_podcast_cache_file(
    TEN_P_PROVIDER_KEY,
    TEN_P_NEXT_MONTH_GAME_CACHE_FILENAME,
)

PDF_NAME = "Ten Pence Arcade Episode Guide.pdf"
FULL_PDF_PATH = f"{PDF_LOCATION}{os.sep}{PDF_NAME}"

DEFAULT_COVER_IMAGE = (
    "https://pbcdn1.podbean.com/imglogo/image-logo/18665248/"
    "10p_BLUPENCE_square_logo_for_Apple_1920a0b1k_300x300.jpg"
)

HI_RES_COVER_IMAGES = {
    210: "https://evercade.info/wp-content/uploads/2025/02/10P-EP210.jpg",
    209: "https://evercade.info/wp-content/uploads/2025/02/10P-EP209.jpg",
    208: "https://evercade.info/wp-content/uploads/2025/02/10P-EP208.jpg",
    207: "https://evercade.info/wp-content/uploads/2025/02/10P-EP207.jpg",
    206: "https://evercade.info/wp-content/uploads/2025/02/10P-EP206.jpg",
    205: "https://evercade.info/wp-content/uploads/2025/02/10P-EP205.jpg",
    204: "https://evercade.info/wp-content/uploads/2025/02/10P-EP204.jpg",
    203: "https://evercade.info/wp-content/uploads/2025/02/10P-EP203.jpg",
    202: DEFAULT_COVER_IMAGE,
    201: "https://evercade.info/wp-content/uploads/2025/02/10P-EP201.jpg",
    200: "https://evercade.info/wp-content/uploads/2025/02/10P-EP200.jpg",
}

COVER_IMAGE = (
    "https://pbcdn1.podbean.com/imglogo/image-logo/18665248/"
    "10p_BLUPENCE_square_logo_for_Apple_1920a0b1k.jpg"
)
COVER_TEXT = "TEN PENCE ARCADE"
COVER_LINK = "https://www.tenpencearcade.com/"

COVER_FONT_COLOUR = colors.black
TOC_FONT_COLOUR = colors.black
TOC_BOOKMARK = "TOC"

EPISODE_FONT_SIZE = 18
EPISODE_FONT_COLOUR = colors.black
EPISODE_IMAGE_WIDTH = 450
SUB_HEADINGS_LETTERS_PER_LINE = 90

NEXT_MONTHS_GAMES_OVERRIDES = {
    200: "Ghosts 'n Goblins",
    201: "Fighting Hawk",
    202: "Fighting Hawk",
    203: "Yie Ar Kung-Fu",
    205: "Demon Front",
    207: "None! There is a special interview with Olly Alpha 1",
    208: "Vapor Trail",
}

MIN_EPISODE_NUMBER = 200


def ensure_cache_dirs() -> None:
    ensure_podcast_cache_dirs(TEN_P_PROVIDER_KEY)
