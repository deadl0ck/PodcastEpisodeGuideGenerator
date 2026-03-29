from __future__ import annotations

import requests


class BaseHTMLUtils:
    @staticmethod
    def get_html_from_url(url: str) -> str:
        return requests.get(url, timeout=30).text
