"""Small, dependency-free validation helpers for uploaded filenames."""
from typing import Set


def has_allowed_extension(filename: str, allowed_extensions: Set[str]) -> bool:
    """Return True when a filename has an explicitly allowed extension."""
    if not filename or "." not in filename:
        return False
    extension = filename.rsplit(".", 1)[1].lower()
    return bool(extension and extension in allowed_extensions)
