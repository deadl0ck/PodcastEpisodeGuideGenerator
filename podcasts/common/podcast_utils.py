from __future__ import annotations

import re


class BasePodcastUtils:
    """Shared helpers for podcast-specific utility classes."""

    @staticmethod
    def extract_first_number(text: str) -> int:
        match = re.search(r"\d+", text)
        if match is None:
            return -1
        return int(match.group())

    @staticmethod
    def strip_known_prefixes(text: str, replacements: list[tuple[str, str]]) -> str:
        value = text
        for old, new in replacements:
            if value.startswith(old):
                value = value.replace(old, new)
        return value.strip()

    @staticmethod
    def strip_time_suffix(data: str) -> str:
        result = re.search(r"\d\d:", data)
        if result is None:
            return data
        return data[:result.regs[0][0]].strip()
