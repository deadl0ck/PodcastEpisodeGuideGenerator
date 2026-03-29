import logging

from podcasts.common.models import BaseMediaEpisode


logger = logging.getLogger(__name__)


class Episode(BaseMediaEpisode):
    def __init__(self,
                 title: str,
                 description: str,
                 episode_number: int,
                 publish_date: str,
                 image_url: str,
                 video_url: str,
                 mp3_url: str,
                 sortable_date: str):
        super().__init__(
            title=title,
            description=description,
            episode_number=episode_number,
            published_display=publish_date,
            image_url=image_url,
            page_url=video_url,
            audio_url=mp3_url,
        )

        # Legacy aliases retained for compatibility with existing callers.
        self.publish_date = self.published_display
        self.video_url = self.page_url
        self.mp3_url = self.audio_url

        self.sortable_date = sortable_date

    def print_out(self) -> None:
        self.log_fields([
            ('Title', self.title),
            ('Description', self.description),
            ('Episode Number', self.episode_number),
            ('Publish Date', self.publish_date),
            ('Image URL', self.image_url),
            ('Video URL', self.video_url),
            ('MP3 URL', self.mp3_url),
        ])
