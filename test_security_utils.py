import unittest

from security_utils import has_allowed_extension, is_valid_upload_id, parse_bounded_number


class UploadValidationTests(unittest.TestCase):
    def test_accepts_allowed_extension_case_insensitively(self):
        self.assertTrue(has_allowed_extension("photo.JPG", {"jpg", "jpeg", "png"}))

    def test_rejects_missing_or_disallowed_extensions(self):
        allowed = {"jpg", "jpeg", "png"}
        for filename in ("", "photo", "photo.exe", ".env", None):
            with self.subTest(filename=filename):
                self.assertFalse(has_allowed_extension(filename, allowed))

    def test_uuid_validation_rejects_path_traversal_and_noncanonical_ids(self):
        self.assertTrue(is_valid_upload_id("2f9f82f4-2c21-11f0-a12f-ad551e1c593a"))
        for value in ("", "../etc/passwd", "temp_test", None):
            with self.subTest(value=value):
                self.assertFalse(is_valid_upload_id(value))

    def test_bounded_number_validation(self):
        self.assertEqual(parse_bounded_number("1.5", 0.5, 2.0, "speed"), 1.5)
        for value in ("nan", "inf", "-1", "not-a-number", None):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    parse_bounded_number(value, 0.5, 2.0, "speed")


if __name__ == "__main__":
    unittest.main()
