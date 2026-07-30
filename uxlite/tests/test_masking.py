from django.test import TestCase

from uxlite import settings_defaults
from uxlite.masking import mask_payload


class MaskPayloadTests(TestCase):
    def test_masks_sensitive_top_level_keys(self):
        data = {"email": "a@b.com", "name": "Alice"}
        masked = mask_payload(data)

        self.assertEqual(masked["email"], settings_defaults.MASK_VALUE)
        self.assertEqual(masked["name"], "Alice")

    def test_masks_nested_dicts_and_lists(self):
        data = {"user": {"password": "secret"}, "items": [{"token": "abc"}]}
        masked = mask_payload(data)

        self.assertNotEqual(masked["user"]["password"], "secret")
        self.assertNotEqual(masked["items"][0]["token"], "abc")

    def test_does_not_mutate_input(self):
        data = {"password": "secret"}
        mask_payload(data)
        self.assertEqual(data["password"], "secret")

    def test_does_not_mask_unrelated_substring_matches(self):
        # "ip" is not a sensitive field, but naive substring matching could
        # wrongly flag keys like "zip_code" or "receipt_id".
        data = {"zip_code": "12345", "receipt_id": "r-1"}
        masked = mask_payload(data)

        self.assertEqual(masked["zip_code"], "12345")
        self.assertEqual(masked["receipt_id"], "r-1")

    def test_masks_camel_case_and_snake_case_variants(self):
        data = {"cardNumber": "4111", "card_number": "4111"}
        masked = mask_payload(data)

        self.assertEqual(masked["cardNumber"], settings_defaults.MASK_VALUE)
        self.assertEqual(masked["card_number"], settings_defaults.MASK_VALUE)
