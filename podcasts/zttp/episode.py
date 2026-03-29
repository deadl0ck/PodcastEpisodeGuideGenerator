import re

from podcasts.common.models import BasePodcastEpisode


class Episode(BasePodcastEpisode):
    def __init__(self, title, link, description, published, summary, duration, mp3, html_content, episode_image,
                 games_summary_text, games_list):
        super().__init__(title, link, description, published, summary, duration, mp3, html_content, episode_image)
        self.games_summary_text = games_summary_text
        self.games_list = games_list

    def print_out(self):
        self.log_fields([
            ('Title', self.title),
            ('Link', self.episode_web_page),
            ('Description', self.description),
            ('Published', self.published),
            ('Summary', self.summary),
            ('Duration', self.duration),
            ('MP3', self.mp3),
            ('Episode Num', self.episode_number),
            ('Episode Image', self.episode_image),
            ('Games Summary Text', self.games_summary_text),
            ('Games List', self.games_list),
        ])

    # Backward-compatible alias.
    def print(self):
        self.print_out()

    @staticmethod
    def extract_episode_number(text) -> int:
        match = re.search("Episode \\d+ ", text)
        if match is not None:
            return int(match.group(0).split()[1].strip())
        return -1
