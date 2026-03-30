"""Table-of-contents renderers shared by provider guide generators."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable


class BaseTocRenderer(ABC):
    """Builds TOC entry tuples consumed by PDF writer implementations."""

    @abstractmethod
    def build_entries(self, episodes: list[Any], **kwargs: Any) -> list[tuple[str, Any]]:
        """Return a list of (title, target) entries for TOC rendering."""


class TWIRTocRenderer(BaseTocRenderer):
    """Build TOC entries for TWIR episode pages plus the QoW section."""

    def __init__(self, qow_bookmark: str):
        """Store the bookmark target for the Question of the Week list."""
        self.qow_bookmark = qow_bookmark

    def build_entries(self, episodes: list[Any], **kwargs: Any) -> list[tuple[str, Any]]:
        """Return TWIR TOC entries prefixed with the QoW jump target."""
        entries: list[tuple[str, Any]] = [
            ("Jump to Question of the Week List", self.qow_bookmark),
        ]
        entries.extend((f"{episode.episode_number} - {episode.title}", episode.episode_number) for episode in episodes)
        return entries


class ZTTPTocRenderer(BaseTocRenderer):
    """Build TOC entries for ZTTP using provider-specific title formatting."""

    def __init__(self, game_list_bookmark: str):
        """Store the bookmark target for the Game Review List."""
        self.game_list_bookmark = game_list_bookmark

    def build_entries(self,
                      episodes: list[Any],
                      **kwargs: Any) -> list[tuple[str, Any]]:
        """Return ZTTP TOC entries prefixed with the Game Review List jump target."""
        formatter = kwargs.get("formatter")
        crapverts = kwargs.get("crapverts")
        if not callable(formatter):
            raise ValueError("ZTTPTocRenderer requires a callable 'formatter' keyword argument")

        entries: list[tuple[str, Any]] = [
            ("Jump to Game Review List", self.game_list_bookmark),
        ]
        entries.extend(formatter(episodes, crapverts))
        return entries
