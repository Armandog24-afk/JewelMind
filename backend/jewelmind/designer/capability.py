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
from jewelmind.gem.models import GemOrigin, GemTreatmentType
from jewelmind.jewelry_category.registry import get_capability
from jewelmind.pave.models import (
    PaveContainmentPolicy,
    PaveHost,
    PaveKind,
    PavePattern,
    PaveRetentionStrategy,
)
from jewelmind.stone.capability import (
    RESERVED_STONE_SHAPES as _RESERVED_STONE_SHAPES,
)
from jewelmind.stone.models import StoneReferenceProfile

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
    # Sprint 26: `pave` and `pavé` were REMOVED from this map. A pavé is now a
    # real, generating field with real retention metal, and Designer can
    # propose its parameters directly — reporting it as unsupported would have
    # made Designer actively misreport a real capability, the same mistake
    # Sprints 18 and 20 each had to correct.
    #
    # `halo` was also removed, for a different reason: the capability is real
    # (Sprint 25) but Designer cannot compose a nested halo, so it belongs in
    # `PRODUCT_SUPPORTED_NOT_PROPOSABLE` below rather than being described as
    # absent from the product.
    "trilogy": "Only a single-stone solitaire is currently supported.",
    "three_stone": "Only a single-stone solitaire is currently supported.",
    "multi_stone": "Only a single-stone solitaire is currently supported.",
    # Sprint 19: `bezel` was removed from this map — it is now a real,
    # generatable setting family. The remaining entries are genuinely
    # unimplemented reserved families.
    "tension": "Only prong and bezel settings are currently supported (setting.type).",
    "channel": "Only prong and bezel settings are currently supported (setting.type).",
    "flush": "Only prong and bezel settings are currently supported (setting.type).",
    "bar": "Only prong and bezel settings are currently supported (setting.type).",
    # Sprint 20: heart, radiant, asscher, trillion, baguette, tapered baguette,
    # triangle, trapezoid, lozenge, hexagon, kite, shield, half moon, pearl and
    # cabochon were REMOVED from this map — every one is now a real, generating
    # shape or profile. Reporting them as unsupported would have made Designer
    # actively misreport a real capability, which is the same mistake Sprint 18
    # had to correct for the six shapes it added.
    #
    # The entries below are the stone shapes JewelMind genuinely does not build.
    # Sourced from `jewelmind/stone/capability.py::RESERVED_STONE_SHAPES` rather
    # than hand-written here, so the two can never disagree.
}

for _shape, _reason in _RESERVED_STONE_SHAPES.items():
    KNOWN_UNSUPPORTED_CONCEPTS[_shape] = (
        f"The {_shape.replace('_', ' ')} cut is not currently supported "
        f"(stone.shape). {_reason} A stone with no built-in cut can still be "
        "modelled today by supplying a custom outline."
    )


def _stone_source_capabilities() -> dict[str, str]:
    """The real, current stone source modes and their status.

    Read from the Stone System registry so Designer can never advertise a source
    the backend cannot resolve.
    """

    from jewelmind.stone.capability import STONE_SOURCE_CAPABILITIES

    return {mode: entry.status for mode, entry in STONE_SOURCE_CAPABILITIES.items()}


def _current_gem_ids() -> list[str]:
    """Gem IDs a design may reference, from the real registry.

    DEPRECATED entries are excluded — Designer must not propose one — while
    remaining resolvable for a saved design that already references it
    (brief section 29).
    """

    from jewelmind.gem.registry import current_gem_ids

    return current_gem_ids()


def _category_unsupported_message(category: str) -> str:
    """Sourced from the real jewelry category capability registry
    (Sprint 16), never a second hand-maintained roadmap string — see
    docs/bible/18-ring-architecture/520-jewelry-category-architecture.md."""

    capability = get_capability(category)
    if capability is not None:
        return f"{capability.message} (jewelry.category)."
    return "Only rings are currently supported (jewelry.category)."


for _category in ("necklace", "bracelet", "earring", "pendant"):
    KNOWN_UNSUPPORTED_CONCEPTS[_category] = _category_unsupported_message(_category)


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
        # Sprint 20: the two independent Stone v2 axes. Exposed so Designer's
        # capability report describes what a stone can actually be, rather than
        # implying every stone is a named parametric cut.
        "stoneSourceMode": list(_stone_source_capabilities()),
        "stoneReferenceProfile": list(get_args(StoneReferenceProfile)),
        # Sprint 21: gem identity is a THIRD axis, independent of both of the
        # above. Read from the live registry rather than restated, so a gem
        # added to `jewelmind/gem/registry.py` is offered here in the same
        # change — the drift Sprint 20 had to fix three times.
        "gemId": _current_gem_ids(),
        "gemOrigin": list(get_args(GemOrigin)),
        "gemTreatment": list(get_args(GemTreatmentType)),
        # Sprint 26: read from the live pavé model, so a reserved host or a
        # reserved retention strategy can never be offered — the model's
        # `Literal` members ARE the set with a real builder.
        "paveKind": list(get_args(PaveKind)),
        "paveHost": list(get_args(PaveHost)),
        "pavePattern": list(get_args(PavePattern)),
        "paveRetentionStrategy": list(get_args(PaveRetentionStrategy)),
        "paveSeatMode": ["NONE", "REFERENCE_RECESS"],
        "paveContainment": list(get_args(PaveContainmentPolicy)),
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
    "stone.gem.gemId": "gemId",
    "stone.gem.origin": "gemOrigin",
    # Sprint 26.
    "pave.kind": "paveKind",
    "pave.host": "paveHost",
    "pave.spec.pattern": "pavePattern",
    "pave.retention.strategy": "paveRetentionStrategy",
    "pave.seat.mode": "paveSeatMode",
    "pave.containment": "paveContainment",
}

# Concepts the PRODUCT supports but Designer cannot PROPOSE (Sprint 26).
#
# A different statement from `KNOWN_UNSUPPORTED_CONCEPTS`, and the distinction
# matters: telling a user a halo is unsupported when the product builds one is
# a misreport, while telling them Designer cannot compose one is the truth.
# Designer proposes flat dotted scalar paths, and a family or a halo is a
# nested structure whose fields could not be diffed one by one or shown with
# real per-field provenance.
PRODUCT_SUPPORTED_NOT_PROPOSABLE: dict[str, str] = {
    "halo": (
        "Halos are supported and generate real geometry, but they are "
        "configured in the workspace rather than proposed from a description: "
        "a halo is a nested structure and every proposed field must carry its "
        "own provenance."
    ),
    "three_stone": (
        "Multi-stone families are supported and generate real geometry, but "
        "they are configured in the workspace rather than proposed from a "
        "description, for the same reason."
    ),
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
        "stone.length",
        "stone.width",
        "stone.depth",
        "stone.orientation",
        "stone.shape",
        "setting.prongCount",
        "setting.prongDiameter",
        "setting.prongHeight",
        "setting.basketHeight",
        "setting.bezelWallThickness",
        "setting.bezelWallHeight",
        "setting.type",
        "material.metal",
        "manufacturing.method",
        "jewelry.category",
        "jewelry.style",
        "ring.sizeSystem",
        # Sprint 21. Deliberately NOT the whole gem identity: `visualProfileId`
        # is a Vision presentation choice rather than design intent, and
        # `treatments` is a list a dotted-path patch cannot express. Both are
        # set through the Studio UI and the API, not proposed by Designer.
        "stone.gem.gemId",
        "stone.gem.origin",
        "stone.gem.customName",
        "stone.gem.note",
        # Sprint 26. The pavé block's geometrically meaningful fields are flat
        # scalars by design, so Designer can propose them one at a time with
        # real per-field provenance. Deliberately NOT the whole field:
        # `spec` is a discriminated union and `explicitPlacements` is a list,
        # neither of which a dotted-path patch can express — both are set
        # through the workspace and the API.
        "pave.enabled",
        "pave.kind",
        "pave.host",
        "pave.stoneScale",
        "pave.stoneOrientationDeg",
        "pave.retention.strategy",
        "pave.retention.beadRadiusMm",
        "pave.seat.mode",
        "pave.containment",
        "pave.spec.pattern",
        # `rowCount` is the ONE numeric field both specs share, so a dotted
        # patch can set it whichever kind the field is.
        "pave.spec.rowCount",
        #
        # The metric spacings are deliberately ABSENT. `pitchMm` belongs to a
        # PaveSpec and `stoneSpacingMm` to a MicrosettingSpec, so a flat patch
        # naming one could land on a spec that has no such field — and a
        # request for "denser stones" names a relative density, not a
        # millimetre value. Turning one into the other would require knowing
        # what pitch is appropriate, which is exactly the professional judgment
        # this project has no evidence for (see
        # `normalizer.PAVE_DENSITY_TERMS`, recognized so such a request becomes
        # a question rather than an invented number).
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
