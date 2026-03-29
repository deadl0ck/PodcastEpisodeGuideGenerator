# podcasts/twir/episode_page_builder.py
# Builds all per-episode TWIR PDF pages and writes a companion CSV export.
import logging

from podcasts.twir.pdf_writer import PDFWriter
from renderers.twir_episode_renderer import TWIREpisodeRenderer

logger = logging.getLogger(__name__)


def build_episode_pages(writer: PDFWriter,
                        all_episodes_list: list,
                        qow_dict: dict,
                        retry_number: int) -> None:
    renderer = TWIREpisodeRenderer(qow_dict=qow_dict, retry_number=retry_number)
    renderer.render_episode_pages(writer, all_episodes_list)
