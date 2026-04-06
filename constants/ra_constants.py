"""PodcastConstants factory for the Retro Asylum provider."""

from __future__ import annotations

from cache_paths import IMAGE_CACHE_DIRNAME, RA_PROVIDER_KEY
from constants.base_constants import BaseConstants
from constants.models import (
    CacheNamespaceConfig,
    CoverConfig,
    EpisodeLayoutConfig,
    OutputConfig,
    PodcastConstants,
    TextConfig,
    TocConfig,
)
from podcasts.common.page_constants import (
    DEFAULT_FONT_BOLD,
    LISTEN_IMAGE_WIDTH,
    LISTEN_IMAGE_Y,
    NULL_LINK,
    PDF_LOCATION,
    SUB_HEADING_FONT,
    SUB_HEADING_FONT_SIZE,
    SUB_HEADING_X,
    SUB_HEADING_Y_DELTA,
    SUBTLE_TEXT_COLOUR,
    TOC_FONT_SIZE,
    TOC_SPACING_DELTA,
    TOC_TEXT,
)
from podcasts.ra.page_constants import (
    COVER_FONT_COLOUR,
    COVER_IMAGE,
    COVER_LINK,
    COVER_TEXT,
    EPISODE_FONT_COLOUR,
    EPISODE_FONT_SIZE,
    EPISODE_IMAGE_HEIGHT,
    LISTEN_IMAGE,
    PDF_NAME,
    SUB_HEADINGS_LETTERS_PER_LINE,
    TOC_BOOKMARK,
    TOC_FONT_COLOUR,
)

_BASE = BaseConstants()


def build_ra_constants() -> PodcastConstants:
    """Build and return the PodcastConstants configuration for the RA provider."""
    return PodcastConstants(
        provider_key=RA_PROVIDER_KEY,
        display_name="Retro Asylum",
        output=OutputConfig(
            pdf_name=PDF_NAME,
            pdf_location=PDF_LOCATION,
            csv_enabled=False,
            csv_name=None,
        ),
        cover=CoverConfig(
            image_url=COVER_IMAGE,
            title_text=COVER_TEXT,
            subtitle_text="EPISODE GUIDE",
            title_font_size=_BASE.cover_font_size,
            title_colour=COVER_FONT_COLOUR,
            image_width=_BASE.cover_image_width,
            link_url=COVER_LINK,
            title_y=_BASE.cover_title_y,
            subtitle_y=_BASE.cover_subtitle_y,
        ),
        toc=TocConfig(
            title_text=TOC_TEXT,
            font_name=DEFAULT_FONT_BOLD,
            font_size=TOC_FONT_SIZE,
            font_colour=TOC_FONT_COLOUR,
            spacing_delta=TOC_SPACING_DELTA,
            bookmark_name=TOC_BOOKMARK,
            heading_colour=None,
            jump_text="[Jump to TOC]",
        ),
        episode_layout=EpisodeLayoutConfig(
            image_width=EPISODE_IMAGE_HEIGHT,
            title_y=29.7 - 1,
            title_font_size=EPISODE_FONT_SIZE,
            title_colour=EPISODE_FONT_COLOUR,
            heading_line_spacing=0.6,
            description_y=29.2 - 1,
            metadata_label_y=29.2 - 24,
            metadata_value_y=29.2 - 25,
            listen_label_y=29.2 - 26,
            listen_image_url=LISTEN_IMAGE,
            listen_image_width=LISTEN_IMAGE_WIDTH,
            listen_image_y=LISTEN_IMAGE_Y,
        ),
        text=TextConfig(
            sub_heading_font=SUB_HEADING_FONT,
            sub_heading_size=SUB_HEADING_FONT_SIZE,
            sub_heading_x=SUB_HEADING_X,
            sub_heading_y_delta=SUB_HEADING_Y_DELTA,
            body_chars_per_line=SUB_HEADINGS_LETTERS_PER_LINE,
            heading_chars_per_line=None,
            subtle_colour=SUBTLE_TEXT_COLOUR,
            null_link=NULL_LINK,
        ),
        feature_list=None,
        cache=CacheNamespaceConfig(
            provider_key=RA_PROVIDER_KEY,
            image_dir_name=IMAGE_CACHE_DIRNAME,
            pickle_keys=("episodes_cache",),
            json_keys=(),
        ),
    )
