"""Centralized cache path helpers for all podcast providers."""

from __future__ import annotations

import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Canonical directory names.
CACHE_DIRNAME = '.cache'
IMAGE_CACHE_DIRNAME = 'images'

CACHE_ROOT = os.path.join(PROJECT_ROOT, CACHE_DIRNAME)

# Canonical provider keys.
TWIR_PROVIDER_KEY = 'TWIR'
ZTTP_PROVIDER_KEY = 'ZTTP'
RA_PROVIDER_KEY = 'RA'
TEN_P_PROVIDER_KEY = '10P'
RGDS_PROVIDER_KEY = 'RGDS'
SHARED_PROVIDER_KEY = '_SHARED'

# Canonical cache filenames used across providers.
QOW_CACHE_FILENAME = 'qow_cache.pkl'
EPISODES_JSON_FILENAME = 'episodes.json'
ZTTP_EPISODE_CACHE_FILENAME = 'episode_cache.pkl'
ZTTP_ZZAP_CACHE_FILENAME = 'zzap_cache.pkl'
ZTTP_CRAPVERTS_CACHE_FILENAME = 'crapverts_cache.pkl'
RA_EPISODE_CACHE_FILENAME = 'episodes_cache.pkl'
TEN_P_EPISODE_CACHE_FILENAME = 'episode_cache.pkl'
TEN_P_NEXT_MONTH_GAME_CACHE_FILENAME = 'next_month_game_cache.pkl'
RGDS_EPISODE_CACHE_FILENAME = 'episodes.json'
RGDS_AUTH_CACHE_FILENAME = 'auth.json'


def get_podcast_cache_root(podcast_key: str) -> str:
    """Return the provider-specific cache root directory."""
    return os.path.join(CACHE_ROOT, podcast_key.upper())


def get_podcast_image_cache_dir(podcast_key: str) -> str:
    """Return the provider-specific image cache directory."""
    return os.path.join(get_podcast_cache_root(podcast_key), IMAGE_CACHE_DIRNAME)


def get_shared_image_cache_dir() -> str:
    """Return the shared image cache directory used across all providers."""
    return get_podcast_image_cache_dir(SHARED_PROVIDER_KEY)


def get_podcast_cache_file(podcast_key: str, filename: str) -> str:
    """Return a cache file path under the provider-specific cache root."""
    return os.path.join(get_podcast_cache_root(podcast_key), filename)


# Default TWIR cache paths preserved for backward compatibility with current code.
TWIR_CACHE_ROOT = get_podcast_cache_root(TWIR_PROVIDER_KEY)
IMAGE_CACHE_DIR = get_podcast_image_cache_dir(TWIR_PROVIDER_KEY)
QOW_CACHE_FILE = get_podcast_cache_file(TWIR_PROVIDER_KEY, QOW_CACHE_FILENAME)
EPISODE_CACHE_FILE = get_podcast_cache_file(TWIR_PROVIDER_KEY, EPISODES_JSON_FILENAME)


def ensure_cache_dirs() -> None:
    """Create TWIR cache directories used by existing code paths."""
    os.makedirs(TWIR_CACHE_ROOT, exist_ok=True)
    os.makedirs(IMAGE_CACHE_DIR, exist_ok=True)


def ensure_podcast_cache_dirs(podcast_key: str) -> None:
    """Create cache directories for the given provider key."""
    cache_root = get_podcast_cache_root(podcast_key)
    image_dir = get_podcast_image_cache_dir(podcast_key)
    os.makedirs(cache_root, exist_ok=True)
    os.makedirs(image_dir, exist_ok=True)
