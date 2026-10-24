"""Dependency-free request validation helpers used by VidSnapAI."""
import math
import uuid
from typing import Iterable, Optional


def has_allowed_extension(filename: Optional[str], allowed_extensions: Iterable[str]) -> bool:
    """Return True only when a filename ends with an explicitly allowed extension."""
    if not isinstance(filename, str) or not filename or "." not in filename:
        return False
    extension = filename.rsplit(".", 1)[1].lower()
    return bool(extension and extension in {item.lower().lstrip(".") for item in allowed_extensions})


def is_valid_upload_id(value: Optional[str]) -> bool:
    """Accept canonical UUID identifiers only; used to constrain storage paths."""
    if not isinstance(value, str) or not value:
        return False
    try:
        parsed = uuid.UUID(value)
    except (ValueError, AttributeError, TypeError):
        return False
    return str(parsed) == value.lower()


def parse_bounded_number(value, minimum: float, maximum: float, field_name: str) -> float:
    """Parse a finite number within inclusive bounds, raising a safe validation error."""
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        raise ValueError("Invalid {}.".format(field_name))
    if not math.isfinite(parsed) or not minimum <= parsed <= maximum:
        raise ValueError("{} must be between {} and {}.".format(field_name.capitalize(), minimum, maximum))
    return parsed
