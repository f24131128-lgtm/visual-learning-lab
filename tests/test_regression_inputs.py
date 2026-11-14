"""Checkout portability keeps exact historical hashes and rejects mutations."""
import hashlib
import unittest
from tools.prepare_regression_inputs import exact_bytes, prepare


class FrozenInputTests(unittest.TestCase):
    def test_checkout_newlines_restore_only_the_exact_frozen_bytes(self):
        frozen = b'first\r\nsecond\r\n'
        expected = hashlib.sha256(frozen).hexdigest()
        self.assertEqual(exact_bytes(b'first\nsecond\n', expected), frozen)
        self.assertEqual(exact_bytes(frozen, expected), frozen)

    def test_changed_content_cannot_be_normalized_into_approval(self):
        expected = hashlib.sha256(b'approved\n').hexdigest()
        with self.assertRaises(ValueError):
            exact_bytes(b'changed\r\n', expected)

    def test_all_real_archives_and_frozen_hashes_are_available(self):
        self.assertEqual(prepare(), 0)
