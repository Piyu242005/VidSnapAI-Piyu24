import unittest

from security_utils import has_allowed_extension


class UploadValidationTests(unittest.TestCase):
    def test_accepts_allowed_extension_case_insensitively(self):
        self.assertTrue(has_allowed_extension("photo.JPG", {"jpg", "jpeg", "png"}))

    def test_rejects_missing_or_disallowed_extensions(self):
        allowed = {"jpg", "jpeg", "png"}
        for filename in ("", "photo", "photo.exe", ".env", None):
            with self.subTest(filename=filename):
                self.assertFalse(has_allowed_extension(filename, allowed))


if __name__ == "__main__":
    unittest.main()
