from __future__ import annotations

import logging
import re

import requests
from bs4 import BeautifulSoup

from podcasts.tenp.page_constants import COVER_IMAGE, HI_RES_COVER_IMAGES

logger = logging.getLogger(__name__)

_TITLE_PREFIX = "Ten Pence Arcade - "
_DESCRIPTION_STOP_MARKERS = [
    "Discussed In This Episode:The Duke of Lancaster",
    "NEXT SHOW'S GAME",
    "NEXT SHOW’S GAME",
    "LINKS:",
    "SEND US YOUR GAME ROOM PICS!",
]
_DISCUSSION_PREFIXES = [
    "DISCUSSED IN THIS SHOW:",
    "DISCUSSED IN THIS SHOW",
    "DISCUSSED IN THIS EPISODE.",
    "DISCUSSED IN THIS EPISODE:",
    "DISCUSSED IN THIS EPISODE",
    "Discussed in this month's episode:",
]


class TenPenceUtils:
    @staticmethod
    def replace_title_text(episodes: list) -> list[str]:
        cleaned = []
        for episode in episodes:
            title = episode.title
            if title.startswith(_TITLE_PREFIX):
                title = title.replace(_TITLE_PREFIX, "", 1)
            cleaned.append(title.strip())
        return cleaned

    @staticmethod
    def extract_date_time(data: str) -> str:
        result = re.search(r"\d\d:", data)
        if result is None:
            return data
        return data[: result.regs[0][0]].strip()

    @staticmethod
    def get_image_url(url: str, episode_number: int) -> tuple[str, bool]:
        logger.info("Fetching episode page for image resolution: #%s", episode_number)
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
        except requests.RequestException:
            logger.warning("Image resolution fallback to default cover for episode #%s", episode_number)
            return COVER_IMAGE, False

        soup = BeautifulSoup(response.text, "lxml")
        images = soup.find_all("img")
        if episode_number in HI_RES_COVER_IMAGES:
            logger.info("Using hi-res mapped cover for episode #%s", episode_number)
            return HI_RES_COVER_IMAGES[episode_number], True

        for image in images:
            img_src = image.get("src")
            if img_src:
                logger.info("Using first image from episode page for episode #%s", episode_number)
                return img_src, False
        logger.warning("No image found on episode page; using default cover for episode #%s", episode_number)
        return COVER_IMAGE, False

    @staticmethod
    def extract_description(text: str) -> str:
        return TenPenceUtils.tidy_up_description(text)

    @staticmethod
    def tidy_up_description(text: str) -> str:
        desc = TenPenceUtils.extract_description_from_text(text).strip()
        for remove_text in _DISCUSSION_PREFIXES:
            desc = desc.replace(remove_text, "")

        if desc and not desc.endswith((".", "!", "?")):
            desc += "."

        desc = re.sub(r"(\.)(\w)", r"\1 \2", desc)
        desc = re.sub(r"([a-z])([A-Z])", r"\1. \2", desc)
        desc = re.sub(r"(!|:|\?)([A-Z])", r"\1 \2", desc)
        return desc.strip()

    @staticmethod
    def extract_leading_number(value: str) -> int | None:
        match = re.match(r"^(\d+)", value.strip())
        return int(match.group(1)) if match else None

    @staticmethod
    def extract_description_from_text(text: str) -> str:
        lines = text.splitlines()
        return_data = ""

        for line in lines:
            current = line.strip()
            if not current:
                continue

            if "Who is David Gunn" in text:
                return (
                    "Who is David Gunn? The van is dead. Massive cartridge in the sea. "
                    "OI, IVY! GET OFF MY BRICKS! Pickups from the cat litter tray. "
                    "200,000 Biscuits. Ecco And The Machine Guns. Not many woods left "
                    "around Alex's house."
                )
            if "Dangling baked beans" in text:
                return (
                    "Dangling baked beans from your eye brows. Being born a Mekon. "
                    "GET TO THE FISH MISSION! Easy on the eye, easier on both eyes."
                )

            for stop_text in _DESCRIPTION_STOP_MARKERS:
                if stop_text in current:
                    pos = current.find(stop_text)
                    return_data += current[:pos]
                    return return_data

            if return_data and not return_data.endswith(":"):
                return_data += ". "
            return_data += current

        return return_data
