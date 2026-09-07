"""What Multi-Stone Families v1 can actually do (Sprint 24).

THE SINGLE SOURCE OF TRUTH for CURRENT vs PARTIAL vs PLANNED, mirrored — never
hand-copied — into `specs/family/v1/family-registry.json` and
`specs/capabilities/jewelmind-capabilities.json`.

FOUR INDEPENDENT AXES, and a family may sit anywhere in the grid:

    representable  - the model expresses it, and it round-trips through JDL
    compilable     - `compile.py` turns it into a real arrangement
    stoneGeometry  - Atlas builds a stone solid for every member
    settingGeometry- the Setting System builds a setting for every member

The fourth is the one that separates this sprint's honest claim from an
overstated one. Every implemented family compiles AND builds real stone
geometry for each member; NONE of them builds a setting for a non-primary
member, because a setting strategy for accent stones does not exist and
inventing one would mean inventing setter geometry. Reporting these families as
fully supported would be exactly the overstatement the brief forbids.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

CapabilityStatus = Literal["CURRENT", "PARTIAL", "PLANNED"]

#: Bumped whenever family COMPILATION changes — which arrangement primitives a
#: family emits, or the arithmetic behind a derived placement. A purely
#: additive capability entry does not bump it.
FAMILY_COMPILER_VERSION = "1.0.0"

FAMILY_REGISTRY_VERSION = "1.0.0"

#: Family types named for architectural completeness but with NO compiler and
#: NO membership in `FamilyType`. The mapped value is the real reason, not a
#: roadmap slogan.
#:
#: `halo` was reserved here in Sprint 24 and is no longer, because Sprint 25
#: established that a halo is not a family at all — it is a COMPOSABLE
#: structure that adds rings to whatever placement a design declares
#: (`jewelmind.halo`). Sprint 24's stated concern was that a fifth family type
#: would create two ways to say one thing; that concern is honoured rather than
#: overturned, since `FamilyType` still gains no member. See
#: `docs/bible/27-halo/halo-rfc.md`.
RESERVED_FAMILY_TYPES: dict[str, str] = {
    "pave": (
        "Pave is a surface treatment covering a region, not a set of "
        "individually placed stones. It needs a region-fill capability the "
        "arrangement engine does not have, and approximating it as a dense "
        "radial pattern would misrepresent both the design and its stone count."
    ),
    "eternity": (
        "An eternity band places stones around the shank's own path, so it "
        "requires placement along a category-specific curve. That is Shank "
        "territory, and this layer is category-neutral."
    ),
    "bypass": (
        "A bypass design is defined by how the SHANK splits and crosses, not by "
        "how its stones relate. The stones can already be expressed as a "
        "toi-et-moi; the bypass itself is a shank capability."
    ),
    "channel_row": (
        "A row of stones held between two rails needs the rail geometry Sprint "
        "23 recorded as PLANNED, and a channel setting family that does not "
        "exist."
    ),
}


class FamilyCapabilityEntry(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    family: str
    status: CapabilityStatus

    #: Can the model express it and JDL carry it?
    representable: bool

    #: Does `compile.py` produce a real arrangement for it?
    compilable: bool

    #: Does Atlas build a stone solid for every member?
    stoneGeometry: bool

    #: Does the Setting System build a setting for every member? `False`
    #: everywhere: only the primary stone gets one today.
    settingGeometry: bool

    #: Roles the family accepts, and the required count where fixed.
    roles: dict[str, int | None]

    note: str


def _entry(
    family: str,
    status: CapabilityStatus,
    roles: dict[str, int | None],
    note: str,
    *,
    representable: bool = True,
    compilable: bool = True,
    stone_geometry: bool = True,
    setting_geometry: bool = False,
) -> FamilyCapabilityEntry:
    return FamilyCapabilityEntry(
        family=family,
        status=status,
        representable=representable,
        compilable=compilable,
        stoneGeometry=stone_geometry,
        settingGeometry=setting_geometry,
        roles=roles,
        note=note,
    )


FAMILY_CAPABILITIES: dict[str, FamilyCapabilityEntry] = {
    entry.family: entry
    for entry in (
        _entry(
            "THREE_STONE",
            "PARTIAL",
            {"CENTER": 1, "SIDE": 2},
            "A centre with two flanking stones. Compiles to a centre instance "
            "plus a MIRROR pattern when symmetric, or two explicit side "
            "instances when not. Real stone geometry for all three; only the "
            "primary stone receives a setting.",
        ),
        _entry(
            "TOI_ET_MOI",
            "PARTIAL",
            {"SIDE": 2},
            "Two stones as a deliberate pair, straddling the design axis along "
            "a settable angle. Symmetric compiles to a mirror, which also flips "
            "a chiral stone's own orientation. Real stone geometry for both; "
            "only the primary stone receives a setting.",
        ),
        _entry(
            "CLUSTER",
            "PARTIAL",
            {"CENTER": None, "ACCENT": None},
            "Stones grouped around an optional centre. Not necessarily circular "
            "(radiusYMm makes it elliptical) and not necessarily centred. Real "
            "stone geometry for every member; only the primary stone receives a "
            "setting.",
        ),
        _entry(
            "CENTER_WITH_ACCENTS",
            "PARTIAL",
            {"CENTER": 1, "ACCENT": None},
            "The general centre-plus-accents family, for designs that are "
            "neither a strict three-stone nor a cluster. Real stone geometry for "
            "every member; only the primary stone receives a setting.",
        ),
    )
}


#: Cross-family capabilities, kept beside the families so a reader sees the
#: whole picture rather than inferring it from four notes.
FAMILY_FEATURE_CAPABILITIES: dict[str, FamilyCapabilityEntry] = {
    entry.family: entry
    for entry in (
        _entry(
            "mixed_gem_identities",
            "CURRENT",
            {},
            "Each member may carry its own GemIdentity, resolved through the "
            "real Sprint 21 registry. Semantic only, exactly as for a single "
            "stone: it never affects geometry.",
            setting_geometry=False,
        ),
        _entry(
            "mixed_member_scale",
            "CURRENT",
            {},
            "A member's `scale` (or the family's default) is applied to the "
            "stone's real resolved dimensions when its solid is built, so a "
            "smaller side stone is genuinely smaller geometry.",
        ),
        _entry(
            "member_orientation",
            "CURRENT",
            {},
            "A member's `orientationDeg` rotates its stone about its own "
            "vertical axis, which is what lets a toi-et-moi's two pears point "
            "in opposite directions.",
        ),
        _entry(
            "asymmetric_layout",
            "CURRENT",
            {},
            "`symmetry='ASYMMETRIC'` places each member from its own values "
            "instead of mirroring, so a deliberately unbalanced design is "
            "expressible rather than approximated.",
        ),
        _entry(
            "explicit_member_placement",
            "CURRENT",
            {},
            "`placementOverride` carries an arrangement `InstanceTransform` "
            "verbatim — the escape hatch for a position no family parameter "
            "derives. It reuses the arrangement's own transform model rather "
            "than declaring a second one.",
        ),
        _entry(
            "mixed_stone_specifications",
            "PARTIAL",
            {},
            "A member's `stoneRef` may name a stone specification other than "
            "'primary', and that reference is preserved and reported. It does "
            "not resolve, because JDL carries exactly one `stone` — so such a "
            "member produces no geometry and says so (JM-FAMILY-004).",
            stone_geometry=False,
        ),
        _entry(
            "per_member_setting",
            "PLANNED",
            {},
            "A member's `settingRef` is carried and reported, but only the "
            "primary stone receives a setting. A setting strategy for accent "
            "stones does not exist, and inventing one would mean inventing "
            "setter geometry.",
            stone_geometry=False,
        ),
        _entry(
            "family_aware_head",
            "PLANNED",
            {},
            "A single head spanning several stones (a three-stone gallery, a "
            "cluster basket) needs multi-stone head geometry, which Sprint 23 "
            "recorded as one head per setting.",
            stone_geometry=False,
        ),
        _entry(
            "professional_family_rules",
            "PLANNED",
            {},
            "Proportion rules between a centre and its accents, minimum "
            "spacing, or whether a cluster is settable. Each needs sourced "
            "professional evidence this project does not have, so none exists.",
            representable=False,
            compilable=False,
            stone_geometry=False,
        ),
    )
}


def get_family_capability(family: str) -> FamilyCapabilityEntry | None:
    return FAMILY_CAPABILITIES.get(family)


def current_families() -> tuple[str, ...]:
    """Families with a real compiler. Derived from the registry, never restated."""

    return tuple(
        sorted(name for name, entry in FAMILY_CAPABILITIES.items() if entry.compilable)
    )


def families_with_stone_geometry() -> tuple[str, ...]:
    return tuple(
        sorted(
            name for name, entry in FAMILY_CAPABILITIES.items() if entry.stoneGeometry
        )
    )


def families_with_setting_geometry() -> tuple[str, ...]:
    """Empty today, and that is the honest answer.

    A family whose accents get no setting is PARTIAL, and this function exists
    so the fact is queryable rather than buried in prose.
    """

    return tuple(
        sorted(
            name
            for name, entry in FAMILY_CAPABILITIES.items()
            if entry.settingGeometry
        )
    )
