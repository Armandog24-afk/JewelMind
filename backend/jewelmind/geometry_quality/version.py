"""Software-regression comparison tolerances (QUALITY-GOV-006).

These are comparison tools for this subsystem only — never manufacturing
or jewelry tolerances. Determined empirically, not invented:

- Repeating real generation+inspection for the SOL-001 default solitaire
  3 times on the same machine/kernel build produced bit-identical
  GeometrySnapshot values every time (see
  backend/tests/test_geometry_quality_harness.py::TestRepeatability) —
  JewelMind's own determinism guarantee (ATLAS-GOV-003) holds locally.
- The only real observed numeric drift is cross-platform: Sprint 14's CI
  run measured a ~1.3e-5 relative divergence between Windows and Linux
  OCCT builds on the smallest, most near-tangent pairwise intersection
  volume (band<->prongs). See
  docs/bible/16-geometry-inspection/486-inspection-determinism.md.

RELATIVE_COMPARISON_TOLERANCE is set two orders of magnitude above that
measured bound, so it absorbs real cross-platform kernel noise while
still catching an actual regression (which changes geometry by orders of
magnitude more, not a rounding-level amount).
"""

from __future__ import annotations

QUALITY_VERSION = "1.0.0"

ABSOLUTE_COMPARISON_TOLERANCE_MM = 1e-4
RELATIVE_COMPARISON_TOLERANCE = 1e-3
