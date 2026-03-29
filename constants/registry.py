from __future__ import annotations

from constants.models import PodcastConstants
from constants.twir_constants import build_twir_constants
from constants.zttp_constants import build_zttp_constants


def get_provider_constants(provider_key: str) -> PodcastConstants:
    normalized = provider_key.strip().upper()
    if normalized == "TWIR":
        return build_twir_constants()
    if normalized == "ZTTP":
        return build_zttp_constants()
    raise ValueError(f"Unknown provider key: {provider_key}")
