"""What Halo System v1 can actually do (Sprint 25).

THE SINGLE SOURCE OF TRUTH for CURRENT vs PARTIAL vs PLANNED, mirrored — never
hand-copied — into `specs/halo/v1/halo-registry.json` and
`specs/capabilities/jewelmind-capabilities.json`.

FOUR INDEPENDENT AXES, carried over from Sprint 24 because the same distinction
decides the same question, and a halo may sit anywhere in the grid:

    representable  - the model expresses it, and it round-trips through JDL
    composable     - `compile.py` adds it to a real arrangement
    stoneGeometry  - Atlas builds a stone solid for every halo stone
    settingGeometry- the Setting System builds metal that holds those stones

The fourth is what separates this sprint's honest claim from an overstated one.
Every implemented variant composes AND builds real, individually placed, scaled
and offset stone geometry for every halo stone. NONE of them builds the metal
that would hold those stones, because a halo setting — a shared bezel rail, a
row of shared prongs, a cut-down bead setting — is real setter geometry, and
inventing it would mean inventing setter geometry. A halo whose stones exist and
whose metal does not is PARTIAL, and saying otherwise would be the overstatement
these axes exist to prevent.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

CapabilityStatus = Literal["CURRENT", "PARTIAL", "PLANNED"]

#: Bumped whenever halo COMPOSITION changes — which arrangement primitives a
#: halo emits, how a ring's positions are derived, or how the centre is
#: anchored. A purely additive capability entry does not bump it.
HALO_COMPILER_VERSION = "1.0.0"

HALO_REGISTRY_VERSION = "1.0.0"

#: Halo variants named for architectural completeness but with NO compiler and
#: NO membership in `HaloVariant`. The mapped value is the real reason, not a
#: roadmap slogan.
RESERVED_HALO_VARIANTS: dict[str, str] = {
    "cushion_halo": (
        "A halo following a cushion or emerald outline rather than an ellipse "
        "needs stones distributed along the CENTRE STONE'S OWN girdle outline, "
        "which means an outline-offset walk the arrangement engine does not "
        "have. `radiusYMm` gives an ellipse, and calling an ellipse a cushion "
        "halo would misdescribe where every corner stone sits."
    ),
    "floral_halo": (
        "A floral or petal halo groups halo stones into clusters at intervals "
        "rather than distributing them evenly. It is a nested arrangement — a "
        "ring of clusters — and the arrangement engine expands one pattern per "
        "source, not a pattern of patterns."
    ),
    "compass_halo": (
        "A compass halo alternates stone SHAPES around the ring (round with "
        "marquise or baguette at the cardinals). That requires more than one "
        "stone specification in a document, which JDL does not yet carry: "
        "`stoneRef` other than 'primary' is preserved and reported unresolved."
    ),
    "triple_halo": (
        "Three concentric rings are expressible in every respect except the "
        "software bound (MAX_HALO_RINGS = 2), which is deliberately set to what "
        "is tested rather than to what the arithmetic would tolerate. Raising it "
        "is a bound change plus a Golden case, not a redesign."
    ),
    "pave_halo": (
        "A pave halo is a surface treatment covering the halo region rather "
        "than a set of individually placed stones. It needs the region-fill "
        "capability Sprint 24 recorded as absent, and approximating it as a "
        "dense ring would misrepresent both the design and its stone count."
    ),
}


#: How a halo may be anchored, per family it composes with.
#:
#: REPORTING, NEVER THE GATE. The authoritative check is derived: a named centre
#: must exist in the arrangement the halo composes onto, which
#: `compile.py::_anchor_transform` verifies against the real compiled
#: instances. This table exists so an unsupported combination can be EXPLAINED
#: rather than merely refused, and
#: `test_halo.py::TestCompositionSupport::test_the_support_table_matches_the_real_compiler`
#: re-derives every row by actually composing, so it cannot drift into fiction.
HALO_COMPOSITION: dict[str, dict[str, object]] = {
    "THREE_STONE": {
        "namedCenter": True,
        "originAnchor": True,
        "note": (
            "A three-stone family derives a CENTER member, so a halo may "
            "surround it by name. Anchoring on the origin instead encircles the "
            "whole trio."
        ),
    },
    "TOI_ET_MOI": {
        "namedCenter": False,
        "originAnchor": True,
        "note": (
            "A toi-et-moi has no CENTER member — the pair IS the design — so a "
            "halo cannot name one and is refused if it tries. It is supported "
            "with centerMemberId=null, which encircles the pair: the two stones "
            "straddle the design origin, so an origin-anchored ring surrounds "
            "both rather than one."
        ),
    },
    "CLUSTER": {
        "namedCenter": True,
        "originAnchor": True,
        "note": (
            "A cluster derives a CENTER member when includeCenter is true. A "
            "cluster declared without one has no centre to name, and the halo "
            "must anchor on the origin."
        ),
    },
    "CENTER_WITH_ACCENTS": {
        "namedCenter": True,
        "originAnchor": True,
        "note": (
            "The centre-plus-accents family always derives a CENTER member, so "
            "centre + accents + halo composes directly."
        ),
    },
}


class HaloCapabilityEntry(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    capability: str
    status: CapabilityStatus

    #: Can the model express it and JDL carry it?
    representable: bool

    #: Does `compile.py` add it to a real arrangement?
    composable: bool

    #: Does Atlas build a stone solid for every halo stone?
    stoneGeometry: bool

    #: Does the Setting System build metal that holds them? `False` everywhere:
    #: only the primary stone receives a setting.
    settingGeometry: bool

    #: How many concentric rings the variant describes, where fixed.
    rings: int | None

    note: str


def _entry(
    capability: str,
    status: CapabilityStatus,
    rings: int | None,
    note: str,
    *,
    representable: bool = True,
    composable: bool = True,
    stone_geometry: bool = True,
    setting_geometry: bool = False,
) -> HaloCapabilityEntry:
    return HaloCapabilityEntry(
        capability=capability,
        status=status,
        representable=representable,
        composable=composable,
        stoneGeometry=stone_geometry,
        settingGeometry=setting_geometry,
        rings=rings,
        note=note,
    )


HALO_CAPABILITIES: dict[str, HaloCapabilityEntry] = {
    entry.capability: entry
    for entry in (
        _entry(
            "SINGLE",
            "PARTIAL",
            1,
            "One ring of stones around a centre, level with it. Every stone is "
            "an individually identifiable instance with real placed, scaled and "
            "oriented geometry. No metal holds them: only the primary stone "
            "receives a setting.",
        ),
        _entry(
            "DOUBLE",
            "PARTIAL",
            2,
            "Two concentric rings, each with its own count, radius, start angle "
            "and scale — which is why a halo is not a CENTER_WITH_ACCENTS "
            "family, whose single accent parameter set cannot carry two rings. "
            "Real stone geometry for every stone in both rings; no halo metal.",
        ),
        _entry(
            "HIDDEN",
            "PARTIAL",
            1,
            "One ring below the centre stone's girdle plane, which is what "
            "'hidden' means structurally. The vertical offset reaches the solid "
            "through the arrangement's own transform, so the stones are "
            "genuinely lower — verified by measuring the built geometry's "
            "bounding box, not by trusting the field. No halo metal.",
        ),
    )
}


#: Cross-variant capabilities, kept beside the variants so a reader sees the
#: whole picture rather than inferring it from three notes.
HALO_FEATURE_CAPABILITIES: dict[str, HaloCapabilityEntry] = {
    entry.capability: entry
    for entry in (
        _entry(
            "halo_over_family",
            "PARTIAL",
            None,
            "A halo composes onto a compiled family rather than replacing it, so "
            "centre + halo, centre + accents + halo, and three-stone + halo are "
            "one design each. The centre is resolved by id against the real "
            "compiled instances; an unresolvable centre is refused, never "
            "re-anchored. Halo stones get geometry; halo metal does not exist.",
        ),
        _entry(
            "halo_over_arrangement",
            "PARTIAL",
            None,
            "A halo composes onto an explicit arrangement the same way it "
            "composes onto a family, so a hand-placed multi-stone centre can "
            "carry one. Same stone-geometry and metal boundary.",
        ),
        _entry(
            "halo_around_multi_stone_center",
            "PARTIAL",
            None,
            "centerMemberId=null anchors the halo on the design origin, which "
            "encircles a multi-stone centre (a toi-et-moi pair, a cluster) "
            "rather than one of its stones. What does NOT exist is a halo whose "
            "radius follows the combined outline of that centre: the ring is a "
            "circle or an ellipse, and no group-outline offset capability "
            "exists to make it hug an arbitrary group.",
        ),
        _entry(
            "elliptical_halo",
            "CURRENT",
            None,
            "radiusYMm gives a second semi-axis, so a halo around an oval or "
            "marquise centre is an ellipse rather than a circle. A geometric "
            "parameter, not a claim that the result suits any particular centre "
            "stone.",
        ),
        _entry(
            "partial_halo",
            "CURRENT",
            None,
            "sweepDeg under 360 lays a ring on an arc, with both endpoints "
            "included — the same closed-form distinction the arrangement "
            "resolver applies to a RADIAL pattern, from the same shared "
            "function.",
        ),
        _entry(
            "mixed_halo_stone_identities",
            "CURRENT",
            None,
            "A ring may carry its own GemIdentity and an individual stone may "
            "override it, resolved through the real Sprint 21 registry. "
            "Semantic only, exactly as for a single stone: it never affects "
            "geometry.",
        ),
        _entry(
            "per_stone_halo_override",
            "CURRENT",
            None,
            "A ring's `members` list overrides individual stones' scale, "
            "orientation, gem and placement. Members are matched to positions "
            "by sorted id, never by array order, so reordering the list cannot "
            "move a stone. It reuses the family's own FamilyMember model rather "
            "than declaring a parallel one.",
        ),
        _entry(
            "mixed_halo_stone_shapes",
            "PARTIAL",
            None,
            "A halo stone's `stoneRef` may name a stone specification other "
            "than 'primary', and that reference is preserved and reported. It "
            "does not resolve, because JDL carries exactly one `stone` — so "
            "such a stone produces no geometry and says so (JM-HALO-004). A "
            "compass halo alternating shapes therefore cannot be built yet.",
            stone_geometry=False,
        ),
        _entry(
            "halo_setting_metal",
            "PLANNED",
            None,
            "The metal that holds a halo — a shared bezel rail, a row of shared "
            "prongs, cut-down bead setting — does not exist. A ring's "
            "`settingRef` is carried and reported, and only the primary stone "
            "receives a setting. Sprint 23 built the contract a future strategy "
            "will use (explicit prong positions carrying "
            "servesStoneInstanceIds); SETTING-GOV requires an RFC before a halo "
            "setting family is added, and this sprint did not bypass it.",
            stone_geometry=False,
        ),
        _entry(
            "outline_following_halo",
            "PLANNED",
            None,
            "A halo whose stones follow the centre stone's own girdle outline "
            "(a cushion or emerald halo) needs an outline-offset walk that does "
            "not exist. An ellipse is offered and is honestly an ellipse.",
            representable=False,
            composable=False,
            stone_geometry=False,
        ),
        _entry(
            "designer_halo_language",
            "PLANNED",
            None,
            "Designer proposes flat scalar JDL paths only; neither `family` nor "
            "`halo` is in its allow-list, because a provider proposing a nested "
            "structure could not be diffed field by field or shown with real "
            "provenance. Adding halo alone would advertise a capability "
            "families do not have.",
            representable=False,
            composable=False,
            stone_geometry=False,
        ),
        _entry(
            "professional_halo_rules",
            "PLANNED",
            None,
            "Minimum halo stone spacing, a centre-to-halo proportion, a "
            "settable radius, or whether a hidden halo clears the centre's "
            "pavilion. Each needs sourced professional evidence this project "
            "does not have, so none exists. Whether two placed stones overlap "
            "is a GEOMETRIC fact for Geometry Inspection.",
            representable=False,
            composable=False,
            stone_geometry=False,
        ),
    )
}


def get_halo_capability(capability: str) -> HaloCapabilityEntry | None:
    return HALO_CAPABILITIES.get(capability)


def current_halo_variants() -> tuple[str, ...]:
    """Variants with a real compiler. Derived from the registry, never restated."""

    return tuple(
        sorted(
            name for name, entry in HALO_CAPABILITIES.items() if entry.composable
        )
    )


def halo_variants_with_stone_geometry() -> tuple[str, ...]:
    return tuple(
        sorted(
            name for name, entry in HALO_CAPABILITIES.items() if entry.stoneGeometry
        )
    )


def halo_variants_with_setting_geometry() -> tuple[str, ...]:
    """Empty today, and that is the honest answer.

    A halo whose stones have no metal holding them is PARTIAL, and this function
    exists so the fact is queryable rather than buried in prose.
    """

    return tuple(
        sorted(
            name for name, entry in HALO_CAPABILITIES.items() if entry.settingGeometry
        )
    )
