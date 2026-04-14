import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest

from constants import get_provider_constants


class TestConstantsRegistry(unittest.TestCase):
    def test_twir_constants(self):
        constants = get_provider_constants("TWIR")
        self.assertEqual(constants.provider_key, "TWIR")
        self.assertTrue(constants.output.csv_enabled)
        self.assertEqual(constants.feature_list.list_kind.value, "qow")

    def test_zttp_constants(self):
        constants = get_provider_constants("ZTTP")
        self.assertEqual(constants.provider_key, "ZTTP")
        self.assertFalse(constants.output.csv_enabled)
        self.assertEqual(constants.feature_list.list_kind.value, "game_list")

    def test_ra_constants(self):
        constants = get_provider_constants("RA")
        self.assertEqual(constants.provider_key, "RA")
        self.assertFalse(constants.output.csv_enabled)
        self.assertIsNone(constants.feature_list)

    def test_tenp_constants(self):
        constants = get_provider_constants("10P")
        self.assertEqual(constants.provider_key, "10P")
        self.assertFalse(constants.output.csv_enabled)
        self.assertIsNone(constants.feature_list)

    def test_rgds_constants(self):
        constants = get_provider_constants("RGDS")
        self.assertEqual(constants.provider_key, "RGDS")
        self.assertFalse(constants.output.csv_enabled)
        self.assertIsNone(constants.feature_list)

    def test_key_is_case_insensitive(self):
        constants = get_provider_constants("twir")
        self.assertEqual(constants.provider_key, "TWIR")

    def test_tenp_key_is_case_insensitive(self):
        constants = get_provider_constants("10p")
        self.assertEqual(constants.provider_key, "10P")

    def test_rgds_key_is_case_insensitive(self):
        constants = get_provider_constants("rgds")
        self.assertEqual(constants.provider_key, "RGDS")

    def test_unknown_provider_raises(self):
        with self.assertRaises(ValueError):
            get_provider_constants("UNKNOWN")


if __name__ == "__main__":
    unittest.main()
