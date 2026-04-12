from __future__ import annotations

from cache_paths import RA_PROVIDER_KEY, TENP_PROVIDER_KEY, TWIR_PROVIDER_KEY, ZTTP_PROVIDER_KEY
from constants.models import PodcastConstants
from constants.ra_constants import build_ra_constants
from constants.tenp_constants import build_tenp_constants
from constants.twir_constants import build_twir_constants
from constants.zttp_constants import build_zttp_constants


def get_provider_constants(provider_key: str) -> PodcastConstants:
    normalized = provider_key.strip().upper()
    if normalized == TWIR_PROVIDER_KEY:
        return build_twir_constants()
    if normalized == ZTTP_PROVIDER_KEY:
        return build_zttp_constants()
    if normalized == RA_PROVIDER_KEY:
        return build_ra_constants()
    if normalized == TENP_PROVIDER_KEY:
        return build_tenp_constants()
    raise ValueError(f"Unknown provider key: {provider_key}")
