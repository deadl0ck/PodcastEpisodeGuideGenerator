from __future__ import annotations

import re

from podcasts.rgds.desc_text import TEXT_TO_REMOVE, TEXT_TO_STOP_AT


_DASH_TRANSLATION_TABLE = str.maketrans(
    {
        "\u2010": "-",  # hyphen
        "\u2011": "-",  # non-breaking hyphen
        "\u2012": "-",  # figure dash
        "\u2013": "-",  # en dash
        "\u2014": "-",  # em dash
        "\u2015": "-",  # horizontal bar
    }
)


class RGDSTextUtils:
    """Text cleanup utilities for RGDS episode descriptions."""

    @staticmethod
    def normalize_title(title: str | None) -> str:
        if not title:
            return "Untitled Episode"

        cleaned = str(title).translate(_DASH_TRANSLATION_TABLE)
        cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
        return cleaned or "Untitled Episode"

    @staticmethod
    def format_duration_ms(duration_ms: int | None) -> str:
        if duration_ms is None:
            return "00:00:00"
        total_seconds = int(duration_ms) // 1000
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    @staticmethod
    def trim_description(description: str | None) -> str:
        if description is None:
            return ""

        cleaned = re.sub(r"[^\x00-\x7F]", " ", description)
        cleaned = re.sub(r"\. {2,}", ". ", cleaned)
        cleaned = re.sub(r" {2,}", " ", cleaned)
        cleaned = re.sub(r'"(.*?)"', lambda m: f'"{m.group(1).strip()}"', cleaned)

        for text in TEXT_TO_REMOVE:
            if text in cleaned:
                cleaned = cleaned.replace(text, "").strip()

        for text in TEXT_TO_STOP_AT:
            position = cleaned.find(text)
            if position != -1:
                cleaned = cleaned[:position].strip()

        if cleaned and not cleaned.endswith("."):
            cleaned += "."

        return cleaned
