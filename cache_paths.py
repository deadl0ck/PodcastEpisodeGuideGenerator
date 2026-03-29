# cache_paths.py
# Centralized cache locations for all runtime-generated cache artifacts.
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE_ROOT = os.path.join(PROJECT_ROOT, '.cache')


def get_podcast_cache_root(podcast_key: str) -> str:
    return os.path.join(CACHE_ROOT, podcast_key.upper())


def get_podcast_image_cache_dir(podcast_key: str) -> str:
    return os.path.join(get_podcast_cache_root(podcast_key), 'images')


# Default TWIR cache paths preserved for backward compatibility with current code.
TWIR_CACHE_ROOT = get_podcast_cache_root('TWIR')
IMAGE_CACHE_DIR = get_podcast_image_cache_dir('TWIR')
QOW_CACHE_FILE = os.path.join(TWIR_CACHE_ROOT, 'qow_cache.pkl')
EPISODE_CACHE_FILE = os.path.join(TWIR_CACHE_ROOT, 'episodes.json')

# Legacy lower-case path from previous versions, used as read fallback during migration.
LEGACY_TWIR_CACHE_ROOT = os.path.join(CACHE_ROOT, 'twir')
LEGACY_TWIR_IMAGE_CACHE_DIR = os.path.join(LEGACY_TWIR_CACHE_ROOT, 'images')


def ensure_cache_dirs() -> None:
    os.makedirs(TWIR_CACHE_ROOT, exist_ok=True)
    os.makedirs(IMAGE_CACHE_DIR, exist_ok=True)


def ensure_podcast_cache_dirs(podcast_key: str) -> None:
    cache_root = get_podcast_cache_root(podcast_key)
    image_dir = get_podcast_image_cache_dir(podcast_key)
    os.makedirs(cache_root, exist_ok=True)
    os.makedirs(image_dir, exist_ok=True)
