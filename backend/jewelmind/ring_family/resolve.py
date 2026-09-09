"""Ring Family resolution (Sprint 28).

THE SINGLE RESOLUTION POINT, the role `family/effective.py::effective_arrangement()`
plays for placement and `setting/modes.py::resolve_primary_mode()` for setting
variants. A second consumer deriving a family's blocks itself would eventually
disagree, and the disagreement would surface as geometry that does not match
what Studio displayed.

WHAT THIS MODULE DOES, AND THE THREE THINGS IT DELIBERATELY DOES NOT.

It reads a document, resolves which variant applies, and returns the
DERIVATIONS that variant makes — each one a JDL path, a value, and the
parameters it came from. That is all.

- It builds NO geometry. No field it returns holds a kernel object, and it
  imports no geometry module. The derivations are executed by the systems that
  already own them: the Shank subsystem builds the architecture, the Multi-Stone
  Family layer compiles the side stones, the Halo System composes the halo, the
  Pavé Engine populates the shoulders, and Atlas turns all of it into solids.
- It computes NO stone position. A side stone's placement comes from the stone
  family compiling into an arrangement; a halo stone's from the Halo System. A
  ring family states a SPACING and delegates — the alternative would be the
  second placement engine ARRANGE-GOV-006 forbids.
- It DERIVES nothing the document already declares. A design that states its own
  `halo` keeps it, and the family reports that it did not derive one. Silently
  replacing an author's halo would discard what they wrote; silently skipping
  the derivation while still reporting the variant would claim something not
  built. Both are refused, and `JM-RINGFAM-002` reports the conflict.

PURE AND DETERMINISTIC. One pass, fixed order, closed-form arithmetic. No
solver, no iteration to convergence, no wall-clock time, no randomness and no
runtime-generated identifier.

EVERY DERIVATION IS A MODULATION OR A RELATION, never a stored value. A halo's
radius is the centre stone's own half width times a factor; a head's height is
the document's own basket height times a factor. That is what makes changing the
stone or the size regenerate the design rather than leave it stale.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, Field

from jewelmind.ring_family.dependencies import dependencies_for, derived_paths
from jewelmind.ring_family.errors import (
    RingFamilyDerivationConflictError,
    RingFamilyUnsupportedVariantError,
    RingFamilyVariantMismatchError,
)
from jewelmind.ring_family.models import (
    VARIANT_BODY_ARCHITECTURE,
    VARIANT_HEAD_HEIGHT_FACTOR,
    VARIANT_SHANK_ARCHITECTURE,
    VARIANT_SHOULDER_ARCHITECTURE,
    RingFamilyParams,
    default_params,
    default_variant_for,
    family_for_variant,
    ring_family_fingerprint,
)

if TYPE_CHECKING:  # pragma: no cover - typing only
    from jewelmind.domain.schema import JewelryDefinition


class RingFamilyDerivation(BaseModel):
    """One JDL path a family wrote, and what it was computed from.

    THE PROVENANCE RECORD. Without it a reader can see that `setting.basketHeight`
    is 4.2 and not that the elevated variant derived it from 3.5 — which is the
    difference between a parametric system and a system that happens to have
    changed a number.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    path: str
    value: Any

    #: The parameters and fields this value was computed from, sorted.
    sourceParameters: tuple[str, ...]

    #: A one-line statement of the relation, for a report a human reads.
    relation: str


class ResolvedRingFamily(BaseModel):
    """The family a design actually uses, after resolution."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    family: str
    variant: str
    params: RingFamilyParams

    #: True when the variant was derived from `jewelry.style` alone rather than
    #: declared. Carried so a report can say which, instead of a consumer having
    #: to guess whether the document opted in.
    derived: bool

    shankArchitecture: str
    shoulderArchitecture: str
    bodyArchitecture: str

    derivations: tuple[RingFamilyDerivation, ...] = ()

    #: Paths the family WOULD have derived but did not, because the document
    #: declares them itself. Reported rather than hidden.
    skippedPaths: tuple[str, ...] = ()

    fingerprint: str

    #: Family parameters this variant does not read. INFORMATION only: the value
    #: stays in the document and has no effect, which the author deserves to be
    #: told rather than left to discover.
    unreadParameters: tuple[str, ...] = ()

    notes: tuple[str, ...] = Field(default_factory=tuple)


def resolve_ring_family(
    definition: JewelryDefinition,
) -> ResolvedRingFamily:
    """The ring family this design uses, with every derivation it makes.

    Three cases, and the first two are the compatibility path:

    1. No `ringFamily` declared -> the family's DEFAULT variant with DEFAULT
       parameters. For `solitaire` that reproduces the pre-Sprint-28 design
       exactly, which is what leaves every existing Golden baseline untouched.
    2. A `ringFamily` declared but disabled -> the same default, with the
       declared parameters DISCARDED. A disabled family contributes nothing, and
       honouring half of it would be neither state.
    3. Declared and enabled -> that variant, with its parameters.

    Raises on a family mismatch rather than choosing a winner.
    """

    family = definition.jewelry.style
    spec = definition.ringFamily

    if spec is None or not spec.enabled:
        variant = default_variant_for(family)
        params = default_params()
        derived = True
    else:
        variant = spec.variant
        declared_family = family_for_variant(variant)
        if declared_family != family:
            raise RingFamilyVariantMismatchError(
                f"ringFamily.variant '{variant}' belongs to the "
                f"'{declared_family}' family, but jewelry.style is "
                f"'{family}'. Refused rather than resolved by precedence: two "
                "authorities over one family have no determinate resolution. "
                f"Set jewelry.style to '{declared_family}', or choose a "
                f"'{family}' variant."
            )
        params = spec.params
        derived = False

    if variant not in VARIANT_SHANK_ARCHITECTURE:
        raise RingFamilyUnsupportedVariantError(
            f"ring family variant '{variant}' has no shank architecture "
            "mapping, so nothing is known about what it builds."
        )

    derivations, skipped, notes = _derive(definition, variant, params)

    return ResolvedRingFamily(
        family=family,
        variant=variant,
        params=params,
        derived=derived,
        shankArchitecture=VARIANT_SHANK_ARCHITECTURE[variant],
        shoulderArchitecture=VARIANT_SHOULDER_ARCHITECTURE[variant],
        bodyArchitecture=VARIANT_BODY_ARCHITECTURE[variant],
        derivations=tuple(derivations),
        skippedPaths=tuple(sorted(skipped)),
        fingerprint=ring_family_fingerprint(family, variant, params),
        unreadParameters=unread_parameters(variant, params),
        notes=tuple(notes),
    )


def _derive(
    definition: JewelryDefinition,
    variant: str,
    params: RingFamilyParams,
) -> tuple[list[RingFamilyDerivation], list[str], list[str]]:
    """Every derivation this variant makes, in dependency-table order."""

    from jewelmind.domain.stone_dimensions import resolved_width_mm

    derivations: list[RingFamilyDerivation] = []
    skipped: list[str] = []
    notes: list[str] = []

    def add(path: str, value: Any, sources: tuple[str, ...], relation: str) -> None:
        derivations.append(
            RingFamilyDerivation(
                path=path,
                value=value,
                sourceParameters=tuple(sorted(sources)),
                relation=relation,
            )
        )

    # ---- the head's height, derived by every family -----------------------
    #
    # TWO FACTORS, COMPOSED, and the composition is the point: the VARIANT
    # contributes its own factor (a low-profile solitaire sits the stone closer
    # to the finger, an elevated one raises it) and the AUTHOR's
    # `headHeightFactor` modulates the result. A variant that changed nothing
    # would be a name rather than a family, and an author who could not
    # modulate it would have a preset.
    #
    # Both are MODULATIONS of the document's own value, so a classic solitaire
    # multiplies by 1.0 x 1.0 and its geometry does not move.
    variant_factor = VARIANT_HEAD_HEIGHT_FACTOR[variant]
    basket = definition.setting.basketHeight * variant_factor * params.headHeightFactor
    add(
        "setting.basketHeight",
        basket,
        (
            "setting.basketHeight",
            "ringFamily.variant",
            "ringFamily.params.headHeightFactor",
        ),
        f"setting.basketHeight ({definition.setting.basketHeight}) x "
        f"variant factor ({variant_factor}) x "
        f"headHeightFactor ({params.headHeightFactor})",
    )

    # ---- the shank architecture -------------------------------------------

    architecture = VARIANT_SHANK_ARCHITECTURE[variant]
    if architecture != "UNIFORM":
        add(
            "band.architecture",
            architecture,
            ("ringFamily.variant",),
            f"the '{variant}' variant requires the {architecture} shank "
            "architecture",
        )
        if architecture == "SPLIT":
            add(
                "band.splitSeparation",
                params.splitSeparationMm,
                ("ringFamily.params.splitSeparationMm",),
                "the rails share the band's own width, so the separation "
                "narrows them rather than widening the ring",
            )
            add(
                "band.splitJoinSpan",
                params.splitJoinSpanDeg,
                ("ringFamily.params.splitJoinSpanDeg",),
                "the angular span, centred on the bottom, over which the rails "
                "are joined into one band",
            )
        else:
            add(
                "band.bypassSeparation",
                params.bypassSeparationMm,
                ("ringFamily.params.bypassSeparationMm",),
                "the clear axial distance between the rail's two ends where "
                "they pass each other",
            )
            add(
                "band.bypassOverlap",
                params.bypassOverlapDeg,
                ("ringFamily.params.bypassOverlapDeg",),
                "how far past a full turn the rail travels, which is what makes "
                "its ends pass rather than meet",
            )

    if variant == "SPLIT_SHANK_TAPERED":
        # Uses the taper the Shank subsystem already owns rather than a second
        # narrowing mechanism.
        add(
            "band.widthTaper",
            {"mode": "TOWARD_BOTTOM", "bottomRatio": 0.7},
            ("ringFamily.variant",),
            "the tapered split narrows its rails toward the bottom using the "
            "Shank subsystem's own width taper",
        )

    # ---- the stone family, DELEGATED --------------------------------------

    family = family_for_variant(variant)
    if family == "three_stone":
        if definition.family is not None:
            skipped.extend(("family.familyType", "family.params"))
            notes.append(
                "This design declares its own stone family, so the ring family "
                "derived none. The declared family is used unchanged."
            )
        elif definition.arrangement is not None:
            raise RingFamilyDerivationConflictError(
                "A 'three_stone' ring family derives a stone family, and this "
                "design already declares an explicit arrangement. A stone "
                "family and an arrangement together are refused by "
                "JM-FAMILY-001, so the derivation cannot be applied. Remove the "
                "arrangement, or choose the 'solitaire' family and place the "
                "stones yourself."
            )
        else:
            side_scale = params.sideStoneScale
            if variant == "THREE_STONE_GRADUATED":
                side_scale *= params.sideGraduationFactor
            add(
                "family.familyType",
                "THREE_STONE",
                ("ringFamily.variant",),
                "the side stones are DELEGATED to the Multi-Stone Family layer, "
                "which compiles them into an arrangement",
            )
            add(
                "family.params",
                {
                    # `kind`, not `familyType`: `FamilyDefinition.params` is a
                    # discriminated union on `kind`, and the model validator
                    # then checks the two agree. Writing the wrong key made the
                    # whole derived family unparseable.
                    "kind": "THREE_STONE",
                    "sideSpacingMm": params.sideSpacingMm,
                    "sideScale": side_scale,
                    "symmetry": params.symmetry,
                },
                (
                    "ringFamily.params.sideSpacingMm",
                    "ringFamily.params.sideStoneScale",
                    *(
                        ("ringFamily.params.sideGraduationFactor",)
                        if variant == "THREE_STONE_GRADUATED"
                        else ()
                    ),
                ),
                f"sideScale = sideStoneScale ({params.sideStoneScale})"
                + (
                    f" x sideGraduationFactor ({params.sideGraduationFactor})"
                    if variant == "THREE_STONE_GRADUATED"
                    else ""
                ),
            )

    # ---- the halo, DELEGATED ----------------------------------------------

    if family == "halo":
        if definition.halo is not None:
            skipped.extend(("halo.variant", "halo.rings"))
            notes.append(
                "This design declares its own halo, so the ring family derived "
                "none. The declared halo is used unchanged."
            )
        else:
            # THE RADIUS IS A RELATION, not a stored millimetre value: it is
            # measured from the CENTRE STONE's own half width, so changing the
            # stone moves the halo.
            girdle_half = resolved_width_mm(definition.stone) / 2.0
            radius = girdle_half * params.haloRadiusFactor
            halo_variant = {
                "HALO_SINGLE": "SINGLE",
                "HALO_DOUBLE": "DOUBLE",
                "HALO_HIDDEN": "HIDDEN",
            }[variant]
            rings: list[dict[str, Any]] = [
                {
                    "ringId": "halo0",
                    "count": params.haloStoneCount,
                    "radiusMm": radius,
                    "memberScale": params.haloStoneScale,
                }
            ]
            if halo_variant == "DOUBLE":
                rings.append(
                    {
                        "ringId": "halo1",
                        "count": params.haloStoneCount + 6,
                        "radiusMm": radius * 1.6,
                        "memberScale": params.haloStoneScale * 0.85,
                    }
                )
            if halo_variant == "HIDDEN":
                # The Halo System REQUIRES a hidden halo to sit below the centre
                # plane, so the offset is derived from the head's own height
                # rather than invented as a depth.
                rings[0]["zOffsetMm"] = -abs(basket) * 0.3
            add(
                "halo.variant",
                halo_variant,
                ("ringFamily.variant",),
                "the halo is DELEGATED to the Halo System, which owns what a "
                "halo is",
            )
            add(
                "halo.rings",
                rings,
                (
                    "ringFamily.params.haloRadiusFactor",
                    "ringFamily.params.haloStoneCount",
                    "ringFamily.params.haloStoneScale",
                    "stone.diameter",
                ),
                f"radiusMm = stone half width ({girdle_half:.4f}) x "
                f"haloRadiusFactor ({params.haloRadiusFactor})",
            )

    # ---- the signet body --------------------------------------------------

    if VARIANT_BODY_ARCHITECTURE[variant] != "NONE":
        add(
            "ringFamily.bodyArchitecture",
            VARIANT_BODY_ARCHITECTURE[variant],
            (
                "ringFamily.params.signetTableLengthMm",
                "ringFamily.params.signetTableWidthMm",
                "ringFamily.params.signetTableHeightMm",
            ),
            "a signet body is built as its own component, so it has parametric "
            "identity rather than being an unnamed lump fused to the band",
        )

    # ---- the shoulders ----------------------------------------------------

    shoulder = VARIANT_SHOULDER_ARCHITECTURE[variant]
    if shoulder != "NONE":
        add(
            "ringFamily.shoulderArchitecture",
            shoulder,
            (
                "ringFamily.params.shoulderSpanDeg",
                "ringFamily.params.shoulderTopThicknessFactor",
                "ringFamily.params.shoulderTopWidthFactor",
            ),
            f"the '{variant}' variant builds {shoulder} shoulders rising from "
            "the band to the head",
        )

    # ---- pavé shoulders, DELEGATED ----------------------------------------

    if params.paveShoulders:
        if definition.pave is not None:
            skipped.append("pave")
            notes.append(
                "This design declares its own pavé field, so the ring family "
                "derived none. The declared field is used unchanged."
            )
        else:
            add(
                "pave",
                {
                    "kind": "PAVE",
                    "host": "BAND_OUTER",
                    "spec": {
                        "kind": "PAVE",
                        "angularSpanDeg": params.paveSpanDeg,
                        "pitchMm": 1.0,
                        "rowCount": 1,
                    },
                    "stoneScale": params.paveStoneScale,
                    "label": "Family-derived pavé shoulders",
                },
                (
                    "ringFamily.params.paveShoulders",
                    "ringFamily.params.paveSpanDeg",
                    "ringFamily.params.paveStoneScale",
                ),
                "the pavé is DELEGATED to the Pavé Engine, which owns the "
                "lattice, the retention and the recess; the family names only "
                "the region and the density",
            )

    # Every derived path must appear in the dependency table, and vice versa.
    # Checked here rather than only in a test so a derivation nobody declared
    # cannot reach a document at runtime.
    declared = set(derived_paths(variant))
    written = {d.path for d in derivations}
    undeclared = sorted(written - declared)
    if undeclared:  # pragma: no cover - the test asserts this stays empty
        raise RingFamilyUnsupportedVariantError(
            f"variant '{variant}' derived paths that no dependency row "
            f"declares: {undeclared}. A derivation nobody declared is a value "
            "written by nobody's authority."
        )

    return derivations, skipped, notes


#: Which `RingFamilyParams` fields each variant actually READS.
#:
#: THE AUTHORITY FOR "IS THIS PARAMETER APPLICABLE?", consumed by
#: `JM-RINGFAM-003` so an unread value is reported to its author rather than
#: silently dropped — the mechanism `JM-SETTING-009` already uses for a setting
#: mode's unread parameters.
#:
#: `paveShoulders` and its two companions are read by EVERY variant, because any
#: family may compose a pavé onto its shoulders; `headHeightFactor` likewise,
#: because every family has a head.
_SHARED_PARAMS: tuple[str, ...] = (
    "headHeightFactor",
    "paveShoulders",
    "paveSpanDeg",
    "paveStoneScale",
)

_VARIANT_PARAMS: dict[str, tuple[str, ...]] = {
    "SOLITAIRE_CLASSIC": (),
    "SOLITAIRE_CATHEDRAL": (
        "shoulderSpanDeg",
        "shoulderTopWidthFactor",
        "shoulderTopThicknessFactor",
    ),
    "SOLITAIRE_LOW_PROFILE": (),
    "SOLITAIRE_ELEVATED": (
        "shoulderSpanDeg",
        "shoulderTopWidthFactor",
        "shoulderTopThicknessFactor",
    ),
    "THREE_STONE_SYMMETRIC": ("sideStoneScale", "sideSpacingMm", "symmetry"),
    "THREE_STONE_GRADUATED": (
        "sideStoneScale",
        "sideSpacingMm",
        "sideGraduationFactor",
        "symmetry",
    ),
    "HALO_SINGLE": ("haloStoneCount", "haloRadiusFactor", "haloStoneScale"),
    "HALO_DOUBLE": ("haloStoneCount", "haloRadiusFactor", "haloStoneScale"),
    "HALO_HIDDEN": ("haloStoneCount", "haloRadiusFactor", "haloStoneScale"),
    "SPLIT_SHANK_PARALLEL": (
        "splitSeparationMm",
        "splitJoinSpanDeg",
        "shoulderSpanDeg",
        "shoulderTopWidthFactor",
        "shoulderTopThicknessFactor",
    ),
    "SPLIT_SHANK_TAPERED": (
        "splitSeparationMm",
        "splitJoinSpanDeg",
        "shoulderSpanDeg",
        "shoulderTopWidthFactor",
        "shoulderTopThicknessFactor",
    ),
    "BYPASS_CROSSOVER": ("bypassSeparationMm", "bypassOverlapDeg"),
    "SIGNET_FLAT_TABLE": (
        "signetTableLengthMm",
        "signetTableWidthMm",
        "signetTableHeightMm",
    ),
}


def parameters_read_by(variant: str) -> tuple[str, ...]:
    """Every parameter field a variant reads, sorted."""

    return tuple(sorted({*_SHARED_PARAMS, *_VARIANT_PARAMS.get(variant, ())}))


def unread_parameters(variant: str, params: RingFamilyParams) -> tuple[str, ...]:
    """Parameters the author SET that this variant does not read.

    Compared against the model's own defaults rather than listed, so a variant
    with few parameters stays silent for a document that set none of the others.
    """

    read = set(parameters_read_by(variant))
    defaults = RingFamilyParams()
    return tuple(
        sorted(
            name
            for name in type(params).model_fields
            if name not in read and getattr(params, name) != getattr(defaults, name)
        )
    )


def resolution_summary(resolved: ResolvedRingFamily) -> dict[str, Any]:
    """A kernel-neutral summary for an API response and a report.

    Deliberately a SUMMARY: the full derivation list carries a relation string
    per entry, which is what a human reads and not what a client needs on every
    generate response.
    """

    return {
        "family": resolved.family,
        "variant": resolved.variant,
        "derived": resolved.derived,
        "fingerprint": resolved.fingerprint,
        "shankArchitecture": resolved.shankArchitecture,
        "shoulderArchitecture": resolved.shoulderArchitecture,
        "bodyArchitecture": resolved.bodyArchitecture,
        "derivedPaths": [d.path for d in resolved.derivations],
        "skippedPaths": list(resolved.skippedPaths),
        "unreadParameters": list(resolved.unreadParameters),
        "dependencyCount": len(dependencies_for(resolved.variant)),
        "notes": list(resolved.notes),
    }
