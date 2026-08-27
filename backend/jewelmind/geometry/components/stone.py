"""Thin re-export — the real Stone System builder lives in
`jewelmind.geometry.stone` (Sprint 18). Kept for import-path stability;
see docs/bible/20-stone/576-current-round-migration.md.
"""

from __future__ import annotations

from jewelmind.geometry.stone.builder import build_stone as build_stone_reference

__all__ = ["build_stone_reference"]
