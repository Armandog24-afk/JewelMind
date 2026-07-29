"""Filename sanitization shared by every export endpoint."""

from __future__ import annotations

import re

_UNSAFE_CHARS = re.compile(r"[^A-Za-z0-9._-]+")
_MAX_LENGTH = 120


def sanitize_filename(name: str, *, default: str = "jewelmind-export") -> str:
    """Return a filesystem- and header-safe filename derived from `name`.

    Collapses whitespace and any character outside [A-Za-z0-9._-] into a
    single underscore, strips leading dots/dashes (to avoid hidden files or
    option-like names), and falls back to `default` if nothing usable
    remains.
    """

    collapsed = _UNSAFE_CHARS.sub("_", name.strip())
    collapsed = collapsed.strip("._-")
    if not collapsed:
        collapsed = default
    return collapsed[:_MAX_LENGTH]
