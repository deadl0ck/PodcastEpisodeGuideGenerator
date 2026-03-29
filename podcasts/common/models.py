from __future__ import annotations

import logging


logger = logging.getLogger(__name__)


class BaseGuideEpisode:
    """Shared logging helper for podcast episode models."""

    @staticmethod
    def log_fields(fields: list[tuple[str, object]]) -> None:
        for label, value in fields:
            logger.info('%-18s: %s', label, value)


class BaseEpisodeCore(BaseGuideEpisode):
    """Shared episode fields used across all podcast-specific episode models."""

    def __init__(self, title: str, description: str, episode_number: int):
        self.title = title
        self.description = description
        self.episode_number = episode_number


class BaseMediaEpisode(BaseEpisodeCore):
    """Shared media/link/date fields common to TWIR and ZTTP episodes."""

    def __init__(
        self,
        title: str,
        description: str,
        episode_number: int,
        published_display: str,
        image_url: str,
        page_url: str,
        audio_url: str,
    ):
        super().__init__(title=title, description=description, episode_number=episode_number)
        self.published_display = published_display
        self.image_url = image_url
        self.page_url = page_url
        self.audio_url = audio_url


class BasePodcastEpisode(BaseMediaEpisode):
    """Generic feed episode model shared by podcast-specific subclasses."""

    def __init__(self, title, link, description, published, summary, duration, mp3, html_content, episode_image):
        episode_number = self.extract_episode_number(title)
        super().__init__(
            title=title,
            description=description,
            episode_number=episode_number,
            published_display=published,
            image_url=episode_image,
            page_url=link,
            audio_url=mp3,
        )

        # Legacy aliases retained for backward compatibility.
        self.episode_web_page = self.page_url
        self.published = self.published_display
        self.mp3 = self.audio_url
        self.episode_image = self.image_url

        self.summary = summary
        self.duration = duration
        self.html_content = html_content

    @property
    def page_url(self) -> str:
        return getattr(self, '_page_url', getattr(self, 'episode_web_page', ''))

    @page_url.setter
    def page_url(self, value: str) -> None:
        self._page_url = value
        self.episode_web_page = value

    @property
    def audio_url(self) -> str:
        return getattr(self, '_audio_url', getattr(self, 'mp3', ''))

    @audio_url.setter
    def audio_url(self, value: str) -> None:
        self._audio_url = value
        self.mp3 = value

    @property
    def image_url(self) -> str:
        return getattr(self, '_image_url', getattr(self, 'episode_image', ''))

    @image_url.setter
    def image_url(self, value: str) -> None:
        self._image_url = value
        self.episode_image = value

    @property
    def published_display(self) -> str:
        return getattr(self, '_published_display', getattr(self, 'published', ''))

    @published_display.setter
    def published_display(self, value: str) -> None:
        self._published_display = value
        self.published = value

    def print_summary(self):
        self.log_fields([
            ('Title', self.title),
            ('Link', self.episode_web_page),
            ('Episode Image', self.episode_image),
            ('Published', self.published),
        ])

    @staticmethod
    def extract_episode_number(text) -> int:
        return -1


class BaseEpisodeImageCollection:
    """Generic heading + image list model (used by features like Crapverts)."""

    def __init__(self, heading: str, images: list):
        self.heading = heading
        self.images = images

    def print_out(self):
        logger.info(self.heading)
        for image in self.images:
            logger.info('\t%s', image)

    def get_heading(self) -> str:
        return self.heading

    def get_images(self) -> list:
        return self.images
