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
    "bezel": "production_metal",
    "basket_support": "production_metal",
    "stone_reference": "stone_reference",
}

PRODUCTION_ROLE: dict[str, ProductionRole] = {
    "band": "included_by_default",
    "prongs": "included_by_default",
    "bezel": "included_by_default",
    "basket_support": "included_by_default",
    "stone_reference": "excluded_by_default",
}


#: Prefix marking an additional stone instance's component,
#: `stone_reference.<instanceId>` (Sprint 22). Kept in sync with
#: `arrangement/compile.py::STONE_INSTANCE_COMPONENT_PREFIX`, which is the
#: naming authority; duplicated as a literal here only because
#: `jewelmind.geometry` must not import `jewelmind.arrangement` for a string —
#: `test_arrangement.py` asserts the two agree.
_STONE_INSTANCE_PREFIX = "stone_reference."


def geometry_role(name: str) -> GeometryRole:
    """The role a named component plays.

    An instance-suffixed stone name resolves to `stone_reference`, NOT to the
    `production_metal` default. That default is correct for an unknown metal
    part and catastrophic for a stone: it would let an additional stone be
    fused into the metal body and shipped inside a production export, breaking
    LAW-006 silently the first time a second stone was emitted. Handling the
    prefix here means the guarantee holds before any such geometry exists.
    """

    if name in GEOMETRY_ROLE:
        return GEOMETRY_ROLE[name]
    if name.startswith(_STONE_INSTANCE_PREFIX):
        return "stone_reference"
    return "production_metal"


def production_role(name: str) -> ProductionRole:
    """Whether a named component is included in a production artifact.

    Instance-suffixed stones inherit `excluded_by_default`, for the same reason
    as above: a stone is a reference, and a caller must opt in explicitly
    (`includeStoneReference: true`) to get one in a STEP/STL export.
    """

    if name in PRODUCTION_ROLE:
        return PRODUCTION_ROLE[name]
    if name.startswith(_STONE_INSTANCE_PREFIX):
        return "excluded_by_default"
    return "included_by_default"


def is_production_component(name: str) -> bool:
    return geometry_role(name) == "production_metal"


def production_component_names(all_names: list[str]) -> list[str]:
    return [n for n in all_names if is_production_component(n)]


def reference_component_names(all_names: list[str]) -> list[str]:
    return [n for n in all_names if not is_production_component(n)]
