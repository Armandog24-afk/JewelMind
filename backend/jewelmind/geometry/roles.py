"""The single source of truth for which named component plays which role.

Previously duplicated as a private mapping inside `preview/mesh.py`
(Sprint 8/Vision) — extracted here during Sprint 14 (Geometry Inspection
v2) so `jewelmind.geometry.inspection` can determine production-vs-
reference status without a second, drifting copy of the same mapping.
Adding a new component name requires updating this file plus
docs/bible/07-atlas/130-component-contract.md.
"""

from __future__ import annotations

from typing import Literal

GeometryRole = Literal["production_metal", "stone_reference", "support", "preview_only"]
ProductionRole = Literal["included_by_default", "excluded_by_default", "never_included"]

GEOMETRY_ROLE: dict[str, GeometryRole] = {
    "band": "production_metal",
    "prongs": "production_metal",
    "basket_support": "production_metal",
    "stone_reference": "stone_reference",
}

PRODUCTION_ROLE: dict[str, ProductionRole] = {
    "band": "included_by_default",
    "prongs": "included_by_default",
    "basket_support": "included_by_default",
    "stone_reference": "excluded_by_default",
}


def is_production_component(name: str) -> bool:
    return GEOMETRY_ROLE.get(name, "production_metal") == "production_metal"


def production_component_names(all_names: list[str]) -> list[str]:
    return [n for n in all_names if is_production_component(n)]


def reference_component_names(all_names: list[str]) -> list[str]:
    return [n for n in all_names if not is_production_component(n)]
