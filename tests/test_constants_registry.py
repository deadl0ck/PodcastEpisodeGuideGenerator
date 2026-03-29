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

    def test_key_is_case_insensitive(self):
        constants = get_provider_constants("twir")
        self.assertEqual(constants.provider_key, "TWIR")

    def test_unknown_provider_raises(self):
        with self.assertRaises(ValueError):
            get_provider_constants("UNKNOWN")


if __name__ == "__main__":
    unittest.main()
