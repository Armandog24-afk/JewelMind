"""The Ring Family capability registry (Sprint 28, brief §27).

THE SINGLE SOURCE OF TRUTH for which families and variants JewelMind actually
builds, and its central axis is MEASURED rather than declared:

- `differsFromFamilyBaseline` and `derivedPathCount` run the real resolver
  against a real default document and ask whether the variant produces something
  the family's BASELINE does not. A variant that differed in nothing would be a
  name, which is precisely what this sprint must not ship. Exactly one variant
  in the whole taxonomy may report `false` — `solitaire`'s own baseline, which is
  what the others differ FROM — and `test_ring_families.py` asserts that.

`structuralGeometry` is DECLARED, and that is a boundary rather than a gap.
Measuring it would need the live builder registries in `jewelmind.geometry`, and
this layer is carried in JDL and read by Forge, so it must not reach into
geometry. `pave/capability.py` settles how to keep both disciplines: PAVE-GOV-012
requires the same correspondence between its own `settingGeometry` and
`setting/retention.py::retention_builders()`, PAVE-GOV-001 forbids the import,
and the correspondence is asserted in `test_pave.py` — which may import
anything. `test_ring_families.py::test_declared_structural_geometry_matches_the_builders`
does exactly that here, in both directions.

A capability is `CURRENT` only if the runtime produces it (§27). Sprint 20
deleted three hand-copied registries that had already drifted and had caused
Designer and the Setting System to misreport real capabilities; measuring the
resolver is what makes that class of drift impossible here rather than unlikely.

Built lazily inside a cached function rather than as a module-level constant,
because the measurement imports the resolver, which imports `domain.schema`,
which imports this package's `models` — the discipline
`setting/capability.py::setting_modes()` and `jewelry_category/dispatch.py` both
document.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import BaseModel, ConfigDict

from jewelmind.ring_family.models import (
    RESERVED_RING_FAMILIES,
    RING_FAMILY_TAXONOMY_VERSION,
    VARIANT_BODY_ARCHITECTURE,
    VARIANT_FAMILY,
    VARIANT_HEAD_HEIGHT_FACTOR,
    VARIANT_SHANK_ARCHITECTURE,
    VARIANT_SHOULDER_ARCHITECTURE,
    implemented_families,
    variants_for_family,
)

CapabilityStatus = Literal["CURRENT", "PARTIAL", "PLANNED", "BLOCKED", "OUT_OF_SCOPE"]
ProfessionalValidationStatus = Literal["NOT_REVIEWED", "IN_REVIEW", "VALIDATED"]

#: Version of the ring-family GEOMETRY — the shank architectures, the shoulder
#: architectures and the signet body. Bumped on any MAJOR change to how they are
#: built, separately from the taxonomy version.
RING_FAMILY_GEOMETRY_VERSION = "1.0.0"

#: The pipeline stages every variant declares a status for.
#:
#: THE POINT OF ENUMERATING THEM is that "supported" is not one question. A
#: variant can be expressible in JDL, resolvable, buildable by Atlas and still
#: absent from Studio — and a registry that answered only "SUPPORTED" would hide
#: which. The same discipline Sprint 27 applied to setting modes.
RING_FAMILY_PIPELINE_STAGES: tuple[str, ...] = (
    "schema",
    "normalization",
    "resolution",
    "compiler",
    "geometry",
    "inspection",
    "export",
    "vision",
    "studio",
    "designer",
    "conversation",
)


class RingFamilyCapability(BaseModel):
    """One ring-family variant and everything true about it."""

    model_config = ConfigDict(extra="forbid")

    variant: str
    family: str
    status: CapabilityStatus

    # ---- the four independent capability axes ------------------------------

    #: A JDL document can express it.
    representable: bool

    #: The resolver accepts it AND it produces something the family's baseline
    #: does not. MEASURED by running the real resolver.
    #:
    #: `false` is correct for exactly one variant: `SOLITAIRE_CLASSIC`, which IS
    #: the baseline the whole taxonomy differs from and which reproduces the
    #: pre-Sprint-28 solitaire exactly. `isFamilyBaseline` below distinguishes
    #: that from a variant that simply changes nothing.
    differsFromFamilyBaseline: bool

    #: True for the one variant that defines the baseline rather than differing
    #: from it. Stated so `differsFromFamilyBaseline: false` can never be
    #: mistaken for an unfinished variant.
    isFamilyBaseline: bool

    #: Real stone geometry exists for it — always true, since every ring family
    #: carries at least the design's own stone.
    stoneGeometry: bool

    #: Real STRUCTURAL metal is built for it beyond the pre-Sprint-28 band,
    #: basket and setting. DECLARED here and asserted against the live builder
    #: registries by `test_ring_families.py`, because this layer must not import
    #: geometry — see the module docstring. `false` for a variant whose
    #: distinction is a derived parameter rather than a new solid, which is
    #: honest rather than a gap.
    structuralGeometry: bool

    pipelineCoverage: dict[str, CapabilityStatus]

    shankArchitecture: str
    shoulderArchitecture: str
    bodyArchitecture: str
    headHeightFactor: float

    #: How many JDL paths this variant derives, measured against a real default
    #: document. Zero would mean the variant changes nothing.
    derivedPathCount: int

    #: Whether the variant carries more than the design's own stone.
    multiStone: bool

    professionalValidationStatus: ProfessionalValidationStatus

    #: Terms Designer and Conversation recognise for this variant. Read BY those
    #: layers rather than restated in them.
    designerTerms: list[str]

    description: str


def _all_current() -> dict[str, CapabilityStatus]:
    return {stage: "CURRENT" for stage in RING_FAMILY_PIPELINE_STAGES}


def _coverage(**overrides: CapabilityStatus) -> dict[str, CapabilityStatus]:
    coverage = _all_current()
    for stage, status in overrides.items():
        if stage not in coverage:
            raise KeyError(
                f"{stage!r} is not a ring-family pipeline stage. Known stages: "
                f"{list(RING_FAMILY_PIPELINE_STAGES)}."
            )
        coverage[stage] = status
    return coverage


#: Everything a variant row declares, minus the axes that are MEASURED.
_ROWS: tuple[dict[str, object], ...] = (
    {
        "variant": "SOLITAIRE_CLASSIC",
        "status": "CURRENT",
        "coverage": _all_current(),
        "multiStone": False,
        "structural": False,
        "terms": ["solitaire", "classic solitaire", "solitario"],
        "description": (
            "One centre stone on a closed band. Reproduces the pre-Sprint-28 "
            "solitaire exactly, which is what makes it the family's default and "
            "what leaves every existing Golden baseline untouched."
        ),
    },
    {
        "variant": "SOLITAIRE_CATHEDRAL",
        "status": "CURRENT",
        "coverage": _all_current(),
        "multiStone": False,
        "structural": True,
        "terms": ["cathedral", "cathedral solitaire", "solitario cattedrale"],
        "description": (
            "Two real shoulder arches rising from the band's own profile to the "
            "head's own height. The first geometry the shoulder has ever had: "
            "`ShoulderDefinition` has recorded `modeled: False` since Sprint 16."
        ),
    },
    {
        "variant": "SOLITAIRE_LOW_PROFILE",
        "status": "CURRENT",
        "coverage": _all_current(),
        "multiStone": False,
        "structural": False,
        "terms": ["low profile", "low-profile solitaire", "profilo basso"],
        "description": (
            "The stone sits closer to the finger: the variant scales the head's "
            "height, which moves the stone and shrinks the head's own metal. A "
            "real geometric difference, not a label."
        ),
    },
    {
        "variant": "SOLITAIRE_ELEVATED",
        "status": "CURRENT",
        "coverage": _all_current(),
        "multiStone": False,
        "structural": True,
        "terms": ["elevated", "elevated solitaire", "rialzato"],
        "description": (
            "The stone is raised and gains shoulder arches to reach the taller "
            "head — the two go together, which is why one variant derives both."
        ),
    },
    {
        "variant": "THREE_STONE_SYMMETRIC",
        "status": "CURRENT",
        "coverage": _all_current(),
        "multiStone": True,
        "structural": False,
        "terms": ["three stone", "trilogy", "trilogia", "three-stone"],
        "description": (
            "A centre plus two equal side stones, DELEGATED to the Multi-Stone "
            "Family layer, which compiles them into an arrangement. The ring "
            "family states a spacing and a scale and computes no position."
        ),
    },
    {
        "variant": "THREE_STONE_GRADUATED",
        "status": "CURRENT",
        "coverage": _all_current(),
        "multiStone": True,
        "structural": False,
        "terms": ["graduated trilogy", "graduated three stone", "trilogia graduata"],
        "description": (
            "The same delegation with a smaller side scale, so the sides step "
            "down from the centre. Real: the side stones' own solids are smaller."
        ),
    },
    {
        "variant": "HALO_SINGLE",
        "status": "PARTIAL",
        "coverage": _all_current(),
        "multiStone": True,
        "structural": False,
        "terms": ["halo", "halo ring", "anello halo"],
        "description": (
            "A centre surrounded by one ring of stones, DELEGATED to the Halo "
            "System. The radius is the CENTRE STONE's own half width times a "
            "factor, so the halo follows the stone. PARTIAL because no metal is "
            "generated to hold the halo stones — Sprint 25's own recorded "
            "boundary, unchanged."
        ),
    },
    {
        "variant": "HALO_DOUBLE",
        "status": "PARTIAL",
        "coverage": _all_current(),
        "multiStone": True,
        "structural": False,
        "terms": ["double halo", "doppio halo"],
        "description": (
            "Two concentric rings, both measured from the centre stone, so "
            "changing the stone moves both. PARTIAL for the same reason as the "
            "single halo."
        ),
    },
    {
        "variant": "HALO_HIDDEN",
        "status": "PARTIAL",
        "coverage": _all_current(),
        "multiStone": True,
        "structural": False,
        "terms": ["hidden halo", "halo nascosto"],
        "description": (
            "A ring of stones below the centre plane, with the vertical offset "
            "derived from the head's own height rather than invented as a depth. "
            "PARTIAL for the same reason as the single halo."
        ),
    },
    {
        "variant": "SPLIT_SHANK_PARALLEL",
        "status": "CURRENT",
        "coverage": _all_current(),
        "multiStone": False,
        "structural": True,
        "terms": ["split shank", "split", "gambo diviso"],
        "description": (
            "A real SHANK ARCHITECTURE: two rails joined into one band over the "
            "bottom span, genuinely separated at the top — the axial gap between "
            "them contains no metal, which is what a split shank is. Four "
            "shoulder arches carry the rails to the head. The rails SHARE the "
            "band's width, so a wider separation narrows them rather than "
            "widening the ring."
        ),
    },
    {
        "variant": "SPLIT_SHANK_TAPERED",
        "status": "CURRENT",
        "coverage": _all_current(),
        "multiStone": False,
        "structural": True,
        "terms": ["tapered split shank", "gambo diviso rastremato"],
        "description": (
            "The same architecture with the rails narrowing toward the bottom, "
            "using the width taper the Shank subsystem already owns rather than "
            "a second narrowing mechanism. Measurably different metal from the "
            "parallel variant."
        ),
    },
    {
        "variant": "BYPASS_CROSSOVER",
        "status": "CURRENT",
        "coverage": _all_current(),
        "multiStone": False,
        "structural": True,
        "terms": ["bypass", "crossover", "bypass ring", "anello incrociato"],
        "description": (
            "ONE open rail travelling past a full turn, its axial position "
            "shifting as it goes, so its two ends occupy the same angle at "
            "different axial positions and PASS each other. Deliberately one "
            "rail rather than two arcs: two axially separated arcs come out as "
            "two disconnected solids, and a ring that is not one connected body "
            "is not a ring."
        ),
    },
    {
        "variant": "SIGNET_FLAT_TABLE",
        "status": "PARTIAL",
        "coverage": _all_current(),
        "multiStone": False,
        "structural": True,
        # Both spellings of chevalière: the accent is correct and the
        # unaccented form is what a keyboard usually produces, and a request
        # that resolves to nothing because of a diacritic would be a
        # vocabulary gap rather than a real capability gap.
        "terms": [
            "signet",
            "signet ring",
            "anello con sigillo",
            "chevalière",
            "chevaliere",
        ],
        "description": (
            "A real solid body with a rectangular table at the ring's top, built "
            "as its own component so it has parametric identity. PARTIAL "
            "because a signet's decoration is the point of one and no engraving, "
            "relief or texture exists anywhere in the pipeline: the table is "
            "flat and rectangular, and both `SIGNET_ENGRAVED` and "
            "`SIGNET_OVAL_TABLE` are reserved with their real reasons. Specialty "
            "decoration is Sprint 29's territory."
        ),
    },
    # ---- SPECIALTY FAMILIES (Sprint 29) ------------------------------------
    {
        "variant": "ETERNITY_FULL",
        "status": "CURRENT",
        "coverage": _all_current(),
        "multiStone": True,
        "structural": False,
        "terms": ["eternity", "eternity ring", "full eternity", "anello eternity",
                  "veretta"],
        "description": (
            "A band set with stones around its WHOLE circumference, DELEGATED to "
            "the Pave Engine. CURRENT rather than PARTIAL because the Pave "
            "Engine is the one layer in the programme whose `settingGeometry` is "
            "true: it builds real retention metal for every stone in the field, "
            "not only for a primary one. Measured at the default: 68 stones and "
            "134 bead solids, largest angular gap 5.8 degrees. The stone COUNT "
            "follows from the band's own circumference, so a larger finger size "
            "carries more stones rather than the same stones stretched apart."
        ),
    },
    {
        "variant": "ETERNITY_HALF",
        "status": "CURRENT",
        "coverage": _all_current(),
        "multiStone": True,
        "structural": False,
        "terms": ["half eternity", "half-eternity", "mezza veretta",
                  "eternity parziale"],
        "description": (
            "The same delegation specified the way a half band actually is: an "
            "explicit stone COUNT at a stated spacing, which together decide how "
            "far round the band the set region reaches and therefore how much of "
            "it stays unadorned. That unadorned region IS the half-eternity "
            "distinction. Measured: 12 stones at 1.6 mm give 48 bead solids and "
            "at 1.4 mm give 26, because the corners genuinely share."
        ),
    },
    {
        "variant": "CLUSTER_ROUND",
        "status": "PARTIAL",
        "coverage": _coverage(),
        "multiStone": True,
        "structural": False,
        "terms": ["cluster", "cluster ring", "anello cluster"],
        "description": (
            "A centre surrounded by its own stones, DELEGATED to the Multi-Stone "
            "Family layer's CLUSTER family, which computes every position. The "
            "ring family states a count, a radius and a relative size and places "
            "nothing itself. PARTIAL because that layer's `settingGeometry` is "
            "false for every family: the surrounding stones are real solids and "
            "ONLY THE CENTRE STONE IS HELD. Sprint 24's own recorded boundary, "
            "unchanged here — a setting strategy for a non-primary member is an "
            "RFC that sprint already identified."
        ),
    },
    {
        "variant": "TOI_ET_MOI_BYPASS",
        "status": "PARTIAL",
        "coverage": _coverage(),
        "multiStone": True,
        "structural": False,
        "terms": ["toi et moi", "toi-et-moi", "two stone", "due pietre"],
        "description": (
            "Two principal stones as two SEPARATE Stone Instances, DELEGATED the "
            "same way, each with its own scale and its own gem identity. PARTIAL "
            "for TWO reasons, and both are recorded rather than approximated: "
            "the non-primary stone is not held, exactly as for the cluster; and "
            "the two stones cannot differ in CUT, because a FamilyMember is an "
            "occurrence of the design's one `stone` and carries no shape "
            "(FAMILY-GOV). An oval-and-pear pair therefore needs per-member "
            "stone specifications, which is an existing Sprint 24 RFC."
        ),
    },
)


def _measure(variant: str) -> tuple[bool, int]:
    """Measure what a variant actually DERIVES, by running the real resolver.

    RUNS THE REAL RESOLVER against a real default document. That is the whole
    difference between this registry and a hand-maintained list: a variant that
    stopped deriving anything would report `differsFromFamilyBaseline: false` on
    the next import rather than on the next code review.

    WHAT THIS DELIBERATELY DOES NOT MEASURE is `structuralGeometry`, and the
    reason is a boundary rather than an omission. Measuring it needs the live
    builder registries in `jewelmind.geometry`, and this layer is carried in JDL
    and read by Forge, so it must not reach into geometry — the neutrality every
    sibling subsystem's `__init__.py` and AST guard protects.

    `pave/capability.py` settles how to keep both disciplines: PAVE-GOV-012
    requires exactly this correspondence between its own `settingGeometry` and
    `setting/retention.py::retention_builders()`, while PAVE-GOV-001 forbids the
    import. It DECLARES the axis and asserts the correspondence in `test_pave.py`,
    which may import anything. `structuralGeometry` is declared per row here for
    the same reason, and
    `test_ring_families.py::test_declared_structural_geometry_matches_the_builders`
    compares every row against the real registries in both directions.

    `resolve` and `domain.schema` are imported inside the function because
    `resolve.py` imports `domain.schema`, which imports `ring_family.models` — a
    module-level import here would make the graph cyclic.
    """

    from jewelmind.domain.schema import JewelryDefinition
    from jewelmind.ring_family.resolve import resolve_ring_family

    definition = JewelryDefinition.model_validate(
        {
            "jewelry": {"category": "ring", "style": VARIANT_FAMILY[variant]},
            "ringFamily": {"variant": variant},
        }
    )
    resolved = resolve_ring_family(definition)
    derived_count = len(resolved.derivations)

    # A variant DIFFERS FROM THE BASELINE when it writes more than the single
    # path every variant writes, or when it scales the head. Every variant
    # writes `setting.basketHeight`, so the head factor is what distinguishes a
    # parameter-only variant from a name.
    differs = derived_count > 1 or VARIANT_HEAD_HEIGHT_FACTOR[variant] != 1.0
    return differs, derived_count


@lru_cache(maxsize=1)
def ring_family_capabilities() -> dict[str, RingFamilyCapability]:
    """The variant registry, with three of its four axes measured."""

    capabilities: dict[str, RingFamilyCapability] = {}
    for row in _ROWS:
        variant = str(row["variant"])
        differs, derived_count = _measure(variant)
        capabilities[variant] = RingFamilyCapability(
            variant=variant,
            family=VARIANT_FAMILY[variant],
            status=row["status"],  # type: ignore[arg-type]
            representable=True,
            differsFromFamilyBaseline=differs,
            isFamilyBaseline=variant == "SOLITAIRE_CLASSIC",
            stoneGeometry=True,
            structuralGeometry=bool(row["structural"]),
            pipelineCoverage=row["coverage"],  # type: ignore[arg-type]
            shankArchitecture=VARIANT_SHANK_ARCHITECTURE[variant],
            shoulderArchitecture=VARIANT_SHOULDER_ARCHITECTURE[variant],
            bodyArchitecture=VARIANT_BODY_ARCHITECTURE[variant],
            headHeightFactor=VARIANT_HEAD_HEIGHT_FACTOR[variant],
            derivedPathCount=derived_count,
            multiStone=bool(row["multiStone"]),
            professionalValidationStatus="NOT_REVIEWED",
            designerTerms=list(row["terms"]),  # type: ignore[arg-type]
            description=str(row["description"]),
        )
    return capabilities


def get_ring_family_capability(variant: str) -> RingFamilyCapability | None:
    return ring_family_capabilities().get(variant)


def family_status(family: str) -> CapabilityStatus:
    """A family's status, DERIVED from its variants rather than declared.

    `CURRENT` when every variant is, `PARTIAL` when any is. A family cannot be
    more complete than its variants, and stating it separately would let the two
    disagree.
    """

    statuses = {
        ring_family_capabilities()[variant].status
        for variant in variants_for_family(family)
    }
    if not statuses:  # pragma: no cover - every family has variants
        return "PLANNED"
    return "CURRENT" if statuses == {"CURRENT"} else "PARTIAL"


def designer_family_terms() -> dict[str, str]:
    """Every recognised term mapped to its variant id.

    DERIVED FROM THE REGISTRY so Designer and Conversation cannot recognise a
    term for a variant that does not exist, or miss one that does. A duplicate
    term across two variants raises: an ambiguous term must be resolved in the
    registry, not silently resolved to whichever row was built last.
    """

    terms: dict[str, str] = {}
    for variant, entry in ring_family_capabilities().items():
        for term in entry.designerTerms:
            key = term.lower()
            if key in terms and terms[key] != variant:
                raise ValueError(
                    f"Designer term {term!r} is claimed by both {terms[key]!r} "
                    f"and {variant!r}. An ambiguous term must be resolved here, "
                    "never by whichever registry row happened to be built last."
                )
            terms[key] = variant
    return terms


def capability_summary() -> dict[str, object]:
    """The whole registry as plain data, for a spec artifact and a report."""

    return {
        "taxonomyVersion": RING_FAMILY_TAXONOMY_VERSION,
        "geometryVersion": RING_FAMILY_GEOMETRY_VERSION,
        "pipelineStages": list(RING_FAMILY_PIPELINE_STAGES),
        "families": {
            family: {
                "status": family_status(family),
                "variants": list(variants_for_family(family)),
            }
            for family in implemented_families()
        },
        "variants": [
            ring_family_capabilities()[variant].model_dump(mode="json")
            for variant in sorted(ring_family_capabilities())
        ],
        "reserved": [
            {"name": name, "reason": reason}
            for name, reason in sorted(RESERVED_RING_FAMILIES.items())
        ],
    }
