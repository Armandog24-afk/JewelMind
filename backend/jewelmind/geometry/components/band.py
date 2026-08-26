"""Ring band/shank geometry — the stable public entry point.

The real construction logic lives in `jewelmind.geometry.shank` (Sprint
17's Shank subsystem: centralized profile generation, deterministic
taper interpolation, and the uniform/tapered dispatch). This module stays
as a thin, stable re-export so every existing caller
(`geometry/assemblies/solitaire.py`, `backend/tests/test_geometry.py`)
keeps working unchanged — see
docs/bible/19-shank/556-current-band-migration.md.
"""

from __future__ import annotations

from jewelmind.geometry.shank.builder import build_shank as build_ring_band

__all__ = ["build_ring_band"]
