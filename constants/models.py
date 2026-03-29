from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class FeatureListKind(str, Enum):
    QOW = "qow"
    GAME_LIST = "game_list"


@dataclass(frozen=True)
class OutputConfig:
    pdf_name: str
    pdf_location: str
    csv_enabled: bool
    csv_name: Optional[str] = None


@dataclass(frozen=True)
class CoverConfig:
    image_url: str
    title_text: str
    subtitle_text: str
    title_font_size: int
    title_colour: object
    image_width: int
    link_url: str
    title_y: float
    subtitle_y: float


@dataclass(frozen=True)
class TocConfig:
    title_text: str
    font_name: str
    font_size: int
    font_colour: object
    spacing_delta: float
    bookmark_name: str
    heading_colour: Optional[object] = None
    jump_text: Optional[str] = None


@dataclass(frozen=True)
class EpisodeLayoutConfig:
    image_width: int
    title_y: float
    title_font_size: int
    title_colour: object
    heading_line_spacing: float
    description_y: float
    metadata_label_y: float
    metadata_value_y: float
    listen_label_y: float
    listen_image_url: str
    listen_image_width: int
    listen_image_y: int


@dataclass(frozen=True)
class TextConfig:
    sub_heading_font: str
    sub_heading_size: int
    sub_heading_x: int
    sub_heading_y_delta: float
    body_chars_per_line: int
    heading_chars_per_line: Optional[int]
    subtle_colour: object
    null_link: str


@dataclass(frozen=True)
class FeatureListConfig:
    list_kind: FeatureListKind
    heading_text: str
    heading_font_size: int
    heading_colour: object
    row_font_size: int
    row_colour: object
    spacing_delta: float
    bookmark_name: str


@dataclass(frozen=True)
class CacheNamespaceConfig:
    provider_key: str
    image_dir_name: str
    pickle_keys: tuple[str, ...]
    json_keys: tuple[str, ...]


@dataclass(frozen=True)
class PodcastConstants:
    provider_key: str
    display_name: str
    output: OutputConfig
    cover: CoverConfig
    toc: TocConfig
    episode_layout: EpisodeLayoutConfig
    text: TextConfig
    feature_list: Optional[FeatureListConfig]
    cache: CacheNamespaceConfig
