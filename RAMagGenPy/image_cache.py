import io
import os
import pickle
from typing import Literal, Tuple

import numpy as np
import requests
from PIL import Image
from reportlab.lib.utils import ImageReader

PICKLE_FILE = "image_cache.pkl"


class ImageCache:
    def __init__(self) -> None:
        """
        Persistent cache: URL -> raw image bytes, stored in PICKLE_FILE.
        """
        self.cache: dict[str, bytes] = {}
        if os.path.exists(PICKLE_FILE):
            with open(PICKLE_FILE, "rb") as f:
                self.cache = pickle.load(f)

    def _save_cache(self) -> None:
        with open(PICKLE_FILE, "wb") as f:
            pickle.dump(self.cache, f)

    def get_image_bytes(self, url: str) -> bytes:
        """
        Return raw bytes for URL, caching on disk keyed by URL.
        """
        if url not in self.cache:
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            self.cache[url] = resp.content
            self._save_cache()
        return self.cache[url]

    def get_imagereader_with_conversion(
        self,
        url: str,
        mode: Literal["width", "height"],
        target_size: int,
    ) -> Tuple[ImageReader, int, int]:
        """
        Load an image from URL (using persistent cache), apply conversion logic,
        resize by width or height, and return (ImageReader, width, height).
        """
        raw = self.get_image_bytes(url)
        im = Image.open(io.BytesIO(raw))

        # ---------- CONVERSION LOGIC ----------

        # Normalise mode: RGBA / CMYK -> RGB
        if im.mode in ("RGBA", "CMYK"):
            image = im.convert("RGB")
        else:
            image = im

        # If original is JPEG, do the numpy round-trip
        if (im.format or "").upper() in ("JPG", "JPEG"):
            a = np.asarray(image)
            image = Image.fromarray(a)

        # ---------- RESIZE PRESERVING ASPECT RATIO ----------

        if mode == "width":
            required_width = target_size
            width_percent = required_width / float(image.size[0])
            height_size = int(float(image.size[1]) * width_percent)
            new_size = (required_width, height_size)
        else:  # mode == "height"
            required_height = target_size
            height_percent = required_height / float(image.size[1])
            width_size = int(float(image.size[0]) * height_percent)
            new_size = (width_size, required_height)

        image = image.resize(new_size, Image.NEAREST)

        # ---------- SAVE TO BYTES AS PNG AND WRAP ----------

        buf = io.BytesIO()
        image.save(buf, format="PNG")  # always save as PNG
        buf.seek(0)

        resized_image = ImageReader(buf)
        return resized_image, image.size[0], image.size[1]
