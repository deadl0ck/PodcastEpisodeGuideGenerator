"""Tests for RA episode filtering logic in PDFWriter."""

import unittest


class TestRemovalTextPresent(unittest.TestCase):
    """PDFWriter.removal_text_present identifies episodes that should be suppressed."""

    def _get_writer(self):
        from podcasts.ra.pdf_writer import PDFWriter
        writer = PDFWriter.__new__(PDFWriter)
        return writer

    def test_error_cover_suffix_triggers_removal(self):
        writer = self._get_writer()
        self.assertTrue(writer.removal_text_present("Some description", "https://example.com/RA_error.png"))

    def test_normal_cover_not_removed(self):
        writer = self._get_writer()
        self.assertFalse(writer.removal_text_present("Normal episode", "https://example.com/cover.jpg"))

    def test_filtered_text_in_description_triggers_removal(self):
        # "Paul Davies" is in TEXT_TO_REMOVE
        writer = self._get_writer()
        self.assertTrue(writer.removal_text_present("Guest: Paul Davies talks retro games", "https://example.com/cover.jpg"))

    def test_filtered_text_is_case_insensitive(self):
        writer = self._get_writer()
        self.assertTrue(writer.removal_text_present("PAUL DAVIES was the host", "https://example.com/cover.jpg"))

    def test_empty_description_not_removed(self):
        writer = self._get_writer()
        self.assertFalse(writer.removal_text_present("", "https://example.com/cover.jpg"))

    def test_none_description_not_removed(self):
        writer = self._get_writer()
        self.assertFalse(writer.removal_text_present(None, "https://example.com/cover.jpg"))

    def test_cover_url_without_suffix_not_removed(self):
        writer = self._get_writer()
        self.assertFalse(writer.removal_text_present("Great episode", "https://example.com/RA_error_extra.png"))


if __name__ == "__main__":
    unittest.main()
