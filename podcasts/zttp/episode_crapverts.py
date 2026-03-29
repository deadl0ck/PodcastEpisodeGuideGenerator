from podcasts.common.models import BaseEpisodeImageCollection


class EpisodeCrapvert(BaseEpisodeImageCollection):
    def get_html(self) -> str:
        html = f'<br><center><h1>{self.heading}</center></h1><br>'
        for image in self.images:
            html += f'<img src="{image}">'
        return html
