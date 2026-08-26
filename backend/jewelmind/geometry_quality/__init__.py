"""Geometry Quality & Golden Models — software regression, not professional
approval (QUALITY-GOV-001). See docs/bible/17-geometry-quality/README.md.

Public entry points only; internal modules stay unexported so callers use
the same real pipeline this subsystem itself uses.
"""

from jewelmind.geometry_quality.harness import (
    generate_candidate_baseline,
    verify_all_goldens,
    verify_golden,
)
from jewelmind.geometry_quality.snapshot import generate_snapshot

__all__ = [
    "generate_candidate_baseline",
    "generate_snapshot",
    "verify_all_goldens",
    "verify_golden",
]
