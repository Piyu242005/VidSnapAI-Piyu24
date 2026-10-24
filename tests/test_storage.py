import tempfile
import unittest
from pathlib import Path

from production.storage import LocalStorage


class LocalStorageTests(unittest.TestCase):
    def test_put_get_exists_delete(self):
        with tempfile.TemporaryDirectory() as root:
            storage = LocalStorage(root)
            source = Path(root) / "source.txt"
            target = Path(root) / "nested" / "copy.txt"
            source.write_text("test", encoding="utf-8")
            storage.put_file("inputs/test.txt", str(source))
            self.assertTrue(storage.exists("inputs/test.txt"))
            storage.get_file("inputs/test.txt", str(target))
            self.assertEqual(target.read_text(encoding="utf-8"), "test")
            storage.delete("inputs/test.txt")
            self.assertFalse(storage.exists("inputs/test.txt"))

    def test_rejects_traversal(self):
        with tempfile.TemporaryDirectory() as root:
            storage = LocalStorage(root)
            for key in ("../outside", "/absolute", "a/../../outside", "a\\..\\outside"):
                with self.subTest(key=key):
                    with self.assertRaises(ValueError):
                        storage.exists(key)


if __name__ == "__main__":
    unittest.main()
