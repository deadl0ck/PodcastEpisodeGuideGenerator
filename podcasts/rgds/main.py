from __future__ import annotations

import logging

from env_var_utils import (
    EnvVarUtils,
    RGDS_CLIENT_ID,
    RGDS_CLIENT_SECRET,
    RGDS_REDIRECT_URI,
    RGDS_REFRESH_TOKEN,
    RGDS_SHOW_ID,
)
from podcasts.common.guide_main_base import BaseGuideMain
from podcasts.common.page_constants import (
    COVER_FONT_SIZE,
    COVER_IMAGE_WIDTH,
    COVER_SUB_TEXT,
    COVER_SUB_TEXT_Y_CM,
    COVER_TEXT_Y_CM,
    DEFAULT_FONT_BOLD,
    TOC_TEXT,
)
from podcasts.common.runtime import configure_logging, get_test_run_settings, initialize_provider_runtime
from podcasts.rgds.episode import Episode
from podcasts.rgds.episode_cache import RGDSEpisodeCache
from podcasts.rgds.page_constants import (
    COVER_FONT_COLOUR,
    COVER_LINK,
    COVER_TEXT,
    DEFAULT_SHOW_ID,
    EPISODE_CACHE_LOCATION,
    TOC_FONT_COLOUR,
    TOC_FONT_SIZE,
    TOC_SPACING_DELTA,
    ensure_cache_dirs,
)
from podcasts.rgds.pdf_writer import PDFWriter
from podcasts.rgds.spotify_client import RGDSSpotifyClient, SpotifyAuthConfig
from podcasts.rgds.text_utils import RGDSTextUtils
from renderers.rgds_episode_renderer import RGDSEpisodeRenderer

configure_logging()
logger = logging.getLogger(__name__)

TEST_RUN, TEST_RUN_COUNT = get_test_run_settings()
RETRY_NUMBER = 5


class RGDSGuideMain(BaseGuideMain):
    """RGDS-specific guide orchestration built on the shared base workflow."""

    def build_context(self, episodes: list[Episode]) -> dict:
        return {}

    def write_cover(self, cover_image: str) -> None:
        self.write_standard_cover(
            cover_image,
            COVER_IMAGE_WIDTH,
            COVER_TEXT,
            COVER_TEXT_Y_CM,
            COVER_SUB_TEXT,
            COVER_SUB_TEXT_Y_CM,
            DEFAULT_FONT_BOLD,
            COVER_FONT_SIZE,
            COVER_FONT_COLOUR,
            COVER_LINK,
        )

    def write_toc(self, episodes: list[Episode], context: dict) -> None:
        entries = []
        for episode in episodes:
            title = episode.title
            if episode.episode_number > 0:
                title = f"{episode.episode_number} - {title}"
            entries.append((title, episode.bookmark))

        self.write_standard_toc(
            entries,
            TOC_TEXT,
            DEFAULT_FONT_BOLD,
            TOC_FONT_SIZE,
            TOC_FONT_COLOUR,
            TOC_SPACING_DELTA,
        )

    def build_pages(self, episodes: list[Episode], context: dict) -> None:
        renderer = RGDSEpisodeRenderer(retry_number=RETRY_NUMBER)
        renderer.render_episode_pages(self.writer, episodes)

    def write_feature_list(self, episodes: list[Episode], context: dict) -> None:
        return


def _format_duration_ms(duration_ms: int | None) -> str:
    if duration_ms is None:
        return "00:00:00"
    total_seconds = int(duration_ms) // 1000
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"


def _build_episode(item: dict) -> Episode:
    images = item.get("images") or []
    image_url = images[0]["url"] if images else ""
    external_urls = item.get("external_urls") or {}
    page_url = external_urls.get("spotify", "")
    published = item.get("release_date", "")
    title = RGDSTextUtils.normalize_title(item.get("name"))

    return Episode(
        spotify_id=str(item.get("id", "")),
        title=title,
        link=page_url,
        description=RGDSTextUtils.trim_description(item.get("description", "")),
        published=published,
        summary=item.get("description", ""),
        duration=_format_duration_ms(item.get("duration_ms")),
        mp3=page_url,
        html_content="",
        episode_image=image_url,
    )


def _sort_key(episode: Episode) -> tuple[str, int]:
    return episode.published_display, episode.episode_number


def load_show_data() -> tuple[str, list[Episode]]:
    ensure_cache_dirs()

    show_id = EnvVarUtils.get_env_var(RGDS_SHOW_ID) or DEFAULT_SHOW_ID
    auth_config = SpotifyAuthConfig(
        client_id=EnvVarUtils.get_env_var(RGDS_CLIENT_ID) or "",
        client_secret=EnvVarUtils.get_env_var(RGDS_CLIENT_SECRET) or "",
        redirect_uri=EnvVarUtils.get_env_var(RGDS_REDIRECT_URI) or "",
        show_id=show_id,
        refresh_token=EnvVarUtils.get_env_var(RGDS_REFRESH_TOKEN),
    )
    client = RGDSSpotifyClient(auth_config)

    cached_by_id = RGDSEpisodeCache.load(EPISODE_CACHE_LOCATION)
    if cached_by_id:
        logger.info("RGDS episode cache loaded: %s entries", len(cached_by_id))

    show_info = client.get_show_info()
    show_cover = ((show_info.get("images") or [{}])[0]).get("url", "")
    entries = client.get_episodes()

    episodes_by_id = dict(cached_by_id)
    cache_hits = 0
    cache_misses = 0
    for item in entries:
        if item is None:
            continue
        spotify_id = str(item.get("id", ""))
        if spotify_id and spotify_id in episodes_by_id:
            cache_hits += 1
            continue

        episode = _build_episode(item)
        if episode.spotify_id:
            episodes_by_id[episode.spotify_id] = episode
            cache_misses += 1

    RGDSEpisodeCache.save(EPISODE_CACHE_LOCATION, episodes_by_id)
    logger.info(
        "RGDS episode cache stats: hits=%s, misses=%s, total_cached=%s",
        cache_hits,
        cache_misses,
        len(episodes_by_id),
    )

    for episode in episodes_by_id.values():
        episode.title = RGDSTextUtils.normalize_title(episode.title)

    episodes = sorted(episodes_by_id.values(), key=_sort_key, reverse=True)
    if TEST_RUN:
        logger.info("**** This is a test run - will only process %s episodes ****", TEST_RUN_COUNT)
        episodes = episodes[:TEST_RUN_COUNT]

    return show_cover, episodes


def main() -> None:
    initialize_provider_runtime(
        required_env_vars=[
            RGDS_CLIENT_ID,
            RGDS_CLIENT_SECRET,
            RGDS_REDIRECT_URI,
        ]
    )
    writer = PDFWriter()
    app = RGDSGuideMain(writer)
    cover_image, episodes = load_show_data()
    app.create_and_save_magazine(cover_image, episodes)
    logger.info("All done - RGDS guide generated")


if __name__ == "__main__":
    main()
