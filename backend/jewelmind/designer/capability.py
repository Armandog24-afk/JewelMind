"""Capability awareness — what Designer is allowed to propose.

Every value here is derived from real code, never hand-invented, so
Designer can never describe unsupported geometry as though it were
supported (see docs/bible/12-designer/296-capability-awareness.md).
`BandProfile`/`StoneShape`/`SettingType`/`MetalType`/`ManufacturingMethod`
come directly from the schema's own `Literal` type arguments;
`prongCount`'s allowed set is not a schema `Literal` (see
domain/schema.py's comment on `SettingSpec.prongCount`) so it is read from
the Forge rule that actually enforces it, `JM-PRONG-001` in
validation/rules.py, rather than re-declared here.
"""

from __future__ import annotations

from typing import Any, get_args

from jewelmind.domain import schema as S

# The Forge rule (validation/engine.py::_prong_rules) hardcodes this as
# `(4, 6)`; kept as a literal tuple here too since the rule module doesn't
# expose it as an importable constant. If that rule's allowed set ever
# changes, this must change with it in the same commit.
SUPPORTED_PRONG_COUNTS = (4, 6)

# Concepts that are common natural-language jewelry requests but do not
# exist anywhere in the current schema/geometry. Used as a deterministic
# backstop for unsupported-feature detection, independent of whether the
# provider itself flagged the request — see 301-unsupported-request-handling.md.
KNOWN_UNSUPPORTED_CONCEPTS: dict[str, str] = {
    "oval": "Only round stones are currently supported (stone.shape).",
    "emerald_cut": "Only round stones are currently supported (stone.shape).",
    "princess_cut": "Only round stones are currently supported (stone.shape).",
    "pear": "Only round stones are currently supported (stone.shape).",
    "marquise": "Only round stones are currently supported (stone.shape).",
    "cushion": "Only round stones are currently supported (stone.shape).",
    "halo": "Halo settings are not currently supported; only a single prong setting exists.",
    "pave": "Pave bands are not currently supported.",
    "pavé": "Pave bands are not currently supported.",
    "trilogy": "Only a single-stone solitaire is currently supported.",
    "three_stone": "Only a single-stone solitaire is currently supported.",
    "multi_stone": "Only a single-stone solitaire is currently supported.",
    "bezel": "Only a prong setting is currently supported (setting.type).",
    "tension": "Only a prong setting is currently supported (setting.type).",
    "channel": "Only a prong setting is currently supported (setting.type).",
    "necklace": "Only rings are currently supported (jewelry.category).",
    "bracelet": "Only rings are currently supported (jewelry.category).",
    "earring": "Only rings are currently supported (jewelry.category).",
    "pendant": "Only rings are currently supported (jewelry.category).",
}


def current_capabilities() -> dict[str, Any]:
    """The real, current set of values Designer may ever propose."""

    return {
        "jewelryCategory": list(get_args(S.JewelryCategory)),
        "jewelryStyle": list(get_args(S.JewelryStyle)),
        "stoneShape": list(get_args(S.StoneShape)),
        "settingType": list(get_args(S.SettingType)),
        "bandProfile": list(get_args(S.BandProfile)),
        "metal": list(get_args(S.MetalType)),
        "manufacturingMethod": list(get_args(S.ManufacturingMethod)),
        "ringSizeSystem": list(get_args(S.RingSizeSystem)),
        "prongCount": list(SUPPORTED_PRONG_COUNTS),
    }


# Maps a JDL dotted field path to the capability-set key that constrains it,
# for enum-valued fields only. Numeric fields (widths, diameters, heights)
# have no enum capability set — their bounds are Forge's job, not
# capability-awareness's job.
_ENUM_FIELD_CAPABILITY_KEY: dict[str, str] = {
    "jewelry.category": "jewelryCategory",
    "jewelry.style": "jewelryStyle",
    "stone.shape": "stoneShape",
    "setting.type": "settingType",
    "setting.prongCount": "prongCount",
    "band.profile": "bandProfile",
    "material.metal": "metal",
    "manufacturing.method": "manufacturingMethod",
    "ring.sizeSystem": "ringSizeSystem",
}

# Fields Designer is allowed to propose at all. Anything outside this set
# is rejected before it can reach a candidate JDL, regardless of what a
# provider returns — see DESIGNER-GOV-004.
KNOWN_JDL_FIELD_PATHS: frozenset[str] = frozenset(
    {
        "project.name",
        "ring.size",
        "ring.innerDiameter",
        "band.width",
        "band.thickness",
        "band.profile",
        "stone.diameter",
        "stone.depth",
        "stone.shape",
        "setting.prongCount",
        "setting.prongDiameter",
        "setting.prongHeight",
        "setting.basketHeight",
        "setting.type",
        "material.metal",
        "manufacturing.method",
        "jewelry.category",
        "jewelry.style",
        "ring.sizeSystem",
    }
)


def is_known_field(path: str) -> bool:
    return path in KNOWN_JDL_FIELD_PATHS


def enum_capability_key(path: str) -> str | None:
    """The capability-set key for an enum field, or None if `path` isn't one."""

    return _ENUM_FIELD_CAPABILITY_KEY.get(path)


def is_supported_enum_value(path: str, value: Any, capabilities: dict[str, Any]) -> bool:
    key = enum_capability_key(path)
    if key is None:
        # Not an enum field (e.g. a numeric dimension) — capability-awareness
        # has nothing to say about it; Forge validates its range instead.
        return True
    return value in capabilities.get(key, [])
