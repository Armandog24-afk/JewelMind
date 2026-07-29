"""EU ring size <-> inner diameter conversion.

Convention used (French/EU civil ring sizing):

    size = (pi * inner_diameter_mm) - 40

Equivalently:

    inner_diameter_mm = (size + 40) / pi

This is the common "EU/French" convention where the size roughly equals the
internal circumference (in millimeters) minus 40. It is *not* the German
convention (where the size equals the circumference directly), nor the US/UK
systems. Because sizing conventions vary by region and manufacturer, JewelMind
never silently rewrites one field from the other (see rule JM-RING-003) — this
utility only reports how consistent the two fields are.
"""

from __future__ import annotations

import math

# Consistency thresholds, in millimeters of inner-diameter discrepancy
# between the stored innerDiameter and the diameter implied by `size`.
_INFO_THRESHOLD_MM = 0.15
_WARNING_THRESHOLD_MM = 0.5


def eu_size_to_inner_diameter(size: float) -> float:
    """Convert an EU/French ring size to the implied inner diameter (mm)."""

    return (size + 40.0) / math.pi


def inner_diameter_to_eu_size(inner_diameter_mm: float) -> float:
    """Convert an inner diameter (mm) to the implied EU/French ring size."""

    return (math.pi * inner_diameter_mm) - 40.0


def sizing_consistency(size: float, inner_diameter_mm: float) -> str | None:
    """Classify how consistent `size` and `inner_diameter_mm` are.

    Returns None when consistent, "information" for a small discrepancy, or
    "warning" for a larger one that likely indicates a data entry mistake or a
    non-EU sizing convention being used for one of the two fields.
    """

    implied_diameter = eu_size_to_inner_diameter(size)
    delta = abs(implied_diameter - inner_diameter_mm)

    if delta <= _INFO_THRESHOLD_MM:
        return None
    if delta <= _WARNING_THRESHOLD_MM:
        return "information"
    return "warning"
