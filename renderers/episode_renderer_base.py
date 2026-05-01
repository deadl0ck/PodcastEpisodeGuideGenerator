from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Callable

logger = logging.getLogger(__name__)


class BaseEpisodeRenderer(ABC):
    """Common retry and rendering contract for provider-specific episode renderers."""

    _EPISODE_SEPARATOR = "[ ---------- Building Episode ---------- ]"

    def __init__(self, retry_number: int):
        self.retry_number = retry_number

    def _run_with_retry(self,
                        fn: Callable[[], None],
                        episode_title: str,
                        exception_types: tuple[type[BaseException], ...]) -> None:
        """Execute an episode render function with bounded retries."""
        retry_count = 0
        while True:
            try:
                if retry_count > 0:
                    logger.warning('Retry %s for %s', retry_count, episode_title)
                fn()
                return
            except exception_types:
                logger.error('Exception thrown processing episode: %s', episode_title)
                logger.exception('Exception details')
                retry_count += 1
                if retry_count > self.retry_number:
                    raise RuntimeError(f'Failed to build episode: {episode_title}')

    @abstractmethod
    def render_episode_pages(self, writer: Any, episodes: list[Any]) -> None:
        """Render all episode pages for a provider."""
        raise NotImplementedError
