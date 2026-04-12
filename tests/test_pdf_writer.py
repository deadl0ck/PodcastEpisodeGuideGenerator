"""
Unit tests for pdf_writer_v2.py (cache and text-splitting utilities)

Covers the static/instance methods that have no network or PDF-canvas side effects:
  - PDFWriter._sanitize_cache_name
  - PDFWriter._get_cached_image_path
  - PDFWriter.split_into_multiline
"""
import sys
import os
import tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import patch


class TestSanitizeCacheName(unittest.TestCase):
    def _sanitize(self, value: str) -> str:
        # Import lazily so ReportLab canvas creation doesn't run at import time
        from podcasts.twir.pdf_writer import PDFWriter
        return PDFWriter._sanitize_cache_name(value)

    def test_plain_name_unchanged(self):
        self.assertEqual(self._sanitize("hqdefault.jpg"), "hqdefault.jpg")

    def test_dots_and_hyphens_preserved(self):
        self.assertEqual(self._sanitize("i-ytimg-com-abc-hqdefault.jpg"), "i-ytimg-com-abc-hqdefault.jpg")

    def test_special_chars_replaced_with_hyphen(self):
        result = self._sanitize("host/path/file.jpg")
        self.assertNotIn("/", result)

    def test_empty_string_returns_default(self):
        self.assertEqual(self._sanitize(""), "cached_image")

    def test_only_separators_returns_default(self):
        self.assertEqual(self._sanitize("---"), "cached_image")

    def test_spaces_replaced(self):
        result = self._sanitize("some file name.jpg")
        self.assertNotIn(" ", result)

    def test_returns_string(self):
        self.assertIsInstance(self._sanitize("test.jpg"), str)


class TestGetCachedImagePath(unittest.TestCase):
    def setUp(self):
        # Use a temp dir so the real image_cache directory is not touched
        self.tmp_dir = tempfile.mkdtemp()

    def _make_writer(self):
        from podcasts.twir.pdf_writer import PDFWriter
        with patch("pdf_writer_base.Canvas"), patch("reportlab.pdfgen.canvas.Canvas"):
            writer = PDFWriter.__new__(PDFWriter)
            writer.listen_image = None
            writer.image_cache_dir = self.tmp_dir
            return writer

    def test_youtube_thumbnail_includes_video_id(self):
        writer = self._make_writer()
        url = "https://i.ytimg.com/vi/kE8c463aibw/hqdefault.jpg"
        path = writer._get_cached_image_path(url)
        filename = os.path.basename(path)
        self.assertIn("kE8c463aibw", filename)
        self.assertIn("hqdefault", filename)

    def test_different_video_ids_produce_different_keys(self):
        writer = self._make_writer()
        url1 = "https://i.ytimg.com/vi/AAAAAAAAAA/hqdefault.jpg"
        url2 = "https://i.ytimg.com/vi/BBBBBBBBBB/hqdefault.jpg"
        self.assertNotEqual(
            writer._get_cached_image_path(url1),
            writer._get_cached_image_path(url2),
        )

    def test_same_url_produces_same_key(self):
        writer = self._make_writer()
        url = "https://i.ytimg.com/vi/kE8c463aibw/hqdefault.jpg"
        self.assertEqual(
            writer._get_cached_image_path(url),
            writer._get_cached_image_path(url),
        )

    def test_cache_path_is_inside_cache_dir(self):
        writer = self._make_writer()
        url = "https://i.ytimg.com/vi/kE8c463aibw/hqdefault.jpg"
        path = writer._get_cached_image_path(url)
        self.assertTrue(path.startswith(self.tmp_dir))

    def test_host_included_in_filename(self):
        writer = self._make_writer()
        url = "https://i.ibb.co/ccL0XZPJ/TWIR-Reddit-logo.jpg"
        path = writer._get_cached_image_path(url)
        filename = os.path.basename(path)
        self.assertIn("i-ibb-co", filename)


class TestSplitIntoMultiline(unittest.TestCase):
    def _split(self, text, letters_per_line=None):
        from podcasts.twir.pdf_writer import PDFWriter
        if letters_per_line is not None:
            return PDFWriter.split_into_multiline(text, letters_per_line)
        return PDFWriter.split_into_multiline(text)

    def test_short_text_stays_single_line(self):
        result = self._split("Short text.", 50)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "Short text.")

    def test_long_text_splits_on_word_boundary(self):
        text = "word " * 30  # 150 chars
        result = self._split(text, 50)
        self.assertGreater(len(result), 1)
        for line in result:
            self.assertLessEqual(len(line), 50)

    def test_no_word_boundaries_splits_at_limit(self):
        text = "a" * 100
        result = self._split(text, 50)
        self.assertGreater(len(result), 1)

    def test_empty_string_returns_empty_list(self):
        result = self._split("")
        self.assertEqual(result, [])

    def test_returns_list_of_strings(self):
        result = self._split("Some text here.", 50)
        self.assertIsInstance(result, list)
        for item in result:
            self.assertIsInstance(item, str)

    def test_rejoined_matches_original(self):
        text = "The quick brown fox jumps over the lazy dog and keeps on running."
        result = self._split(text, 20)
        rejoined = " ".join(line.strip() for line in result)
        # All words should be preserved
        for word in text.split():
            self.assertIn(word, rejoined)


class TestSharedImageCacheReuse(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.cache_root = os.path.join(self.tmp_dir, ".cache")
        self.twir_images = os.path.join(self.cache_root, "TWIR", "images")
        self.tenp_images = os.path.join(self.cache_root, "10P", "images")
        self.shared_images = os.path.join(self.cache_root, "_SHARED", "images")
        os.makedirs(self.twir_images, exist_ok=True)
        os.makedirs(self.tenp_images, exist_ok=True)
        os.makedirs(self.shared_images, exist_ok=True)

    def _make_writer(self):
        from podcasts.twir.pdf_writer import PDFWriter

        with patch("pdf_writer_base.Canvas"), patch("reportlab.pdfgen.canvas.Canvas"):
            writer = PDFWriter.__new__(PDFWriter)
            writer.listen_image = None
            writer.image_cache_dir = self.tenp_images
            writer.shared_image_cache_dir = self.shared_images
            return writer

    def test_reuses_image_from_other_provider_cache(self):
        writer = self._make_writer()
        url = "https://i.ibb.co/NWmMHcH/Listen-Now.jpg"
        filename = os.path.basename(writer._get_cached_image_path(url))
        source_path = os.path.join(self.twir_images, filename)
        with open(source_path, "wb") as handle:
            handle.write(b"shared-bytes")

        with patch("pdf_writer_base.requests.get") as mock_get:
            data = writer._get_or_download_image_bytes(url)

        self.assertEqual(data, b"shared-bytes")
        self.assertFalse(mock_get.called)
        self.assertTrue(os.path.exists(os.path.join(self.tenp_images, filename)))
        self.assertTrue(os.path.exists(os.path.join(self.shared_images, filename)))

    def test_reuses_image_from_shared_cache(self):
        writer = self._make_writer()
        url = "https://i.ibb.co/NWmMHcH/Listen-Now.jpg"
        filename = os.path.basename(writer._get_cached_image_path(url))
        shared_path = os.path.join(self.shared_images, filename)
        with open(shared_path, "wb") as handle:
            handle.write(b"shared-cache-bytes")

        with patch("pdf_writer_base.requests.get") as mock_get:
            data = writer._get_or_download_image_bytes(url)

        self.assertEqual(data, b"shared-cache-bytes")
        self.assertFalse(mock_get.called)
        self.assertTrue(os.path.exists(os.path.join(self.tenp_images, filename)))


if __name__ == "__main__":
    unittest.main()
