"""The parametric dependency model (Sprint 28, brief §6).

WHY THIS IS DATA AND NOT CODE. A parametric CAD system's value is that changing
one input regenerates everything downstream of it without the author rebuilding
the model. For that to be trustworthy, the system has to be able to SAY what
depends on what — otherwise "parametric" is a claim about the implementation
that nobody can check.

So the dependency graph is stated as INSPECTABLE DATA, the same discipline
`family/models.py::FAMILY_ROLE_RULES` follows so Forge can report a failure
without compiling. `resolve.py` consumes this table and nothing else decides
which fields a variant derives:

- a derived path that appears in no dependency row would be written by nobody's
  authority;
- a dependency row whose path is never written would be a promise nothing keeps.

`test_ring_families.py` asserts both directions.

THE GRAPH'S SHAPE. Two kinds of edge, and keeping them apart is what makes the
graph honest:

- A **DERIVATION** edge says a family parameter WRITES a JDL path. Those are the
  edges `resolve.py` executes.
- An **INFLUENCE** edge says an existing JDL field is READ while deriving
  something else — `ring.size` and `stone.diameter` are the two that matter, and
  neither is written by any family. Recording them is what lets the system
  answer "what does changing the finger size affect?", which is the question §29
  asks the propagation tests to prove.

NOTHING HERE IS A PROFESSIONAL RELATION. An edge records that one value is
computed from another; it never asserts that the result is correct for
manufacture.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from jewelmind.ring_family.models import VARIANT_FAMILY

#: What kind of edge this is. See the module docstring for why the two are kept
#: apart rather than merged into one "depends on".
DependencyKind = Literal["DERIVATION", "INFLUENCE"]


class RingFamilyDependency(BaseModel):
    """One edge of the parametric graph."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    kind: DependencyKind

    #: The variant this edge applies to. `None` means every variant.
    variant: str | None

    #: The parameter or JDL field the edge starts from.
    source: str

    #: The JDL paths this edge writes (`DERIVATION`) or contributes to
    #: (`INFLUENCE`).
    targets: tuple[str, ...]

    #: Why the edge exists. A sentence, because a graph nobody can read is a
    #: graph nobody can check.
    reason: str


def _every(kind: DependencyKind, source: str, targets: tuple[str, ...], reason: str):
    return RingFamilyDependency(
        kind=kind, variant=None, source=source, targets=targets, reason=reason
    )


def _for(
    variant: str, source: str, targets: tuple[str, ...], reason: str
) -> RingFamilyDependency:
    return RingFamilyDependency(
        kind="DERIVATION", variant=variant, source=source, targets=targets, reason=reason
    )


#: The INFLUENCE edges: existing JDL fields that are read while a family
#: derives, and that no family ever writes.
#:
#: These are the edges that make the system parametric in the sense a designer
#: cares about. `ring.size` is the clearest case: it is not a family parameter,
#: no family writes it, and changing it moves the band's radius, the head's
#: attachment plane, the stone's position, the shoulders' base and every
#: pavé stone on the shank — because every one of those is derived from the
#: band's own geometry, which is derived from the size.
_INFLUENCES: tuple[RingFamilyDependency, ...] = (
    _every(
        "INFLUENCE",
        "ring.size",
        (
            "ring.innerDiameter",
            "band",
            "setting",
            "stone",
        ),
        "The finger size sets the ring's inner diameter, which sets the band's "
        "outer radius, which is the assembly's anchor point: the head attaches "
        "there, the stone sits above it, and a shoulder or a pavé field is "
        "measured from it. Nothing in a ring family writes the size; everything "
        "structural reads it.",
    ),
    _every(
        "INFLUENCE",
        "band.thickness",
        ("setting", "stone"),
        "The band's thickness sets its outer radius and therefore the height "
        "the head attaches at, so it moves the stone even though no stone field "
        "changed.",
    ),
    _every(
        "INFLUENCE",
        "stone.diameter",
        ("halo.rings", "family.params", "setting"),
        "The centre stone's own size is what a halo radius and a side-stone "
        "spacing are measured against, so a derived halo or side stone follows "
        "the stone rather than a stored millimetre value.",
    ),
    _every(
        "INFLUENCE",
        "band.width",
        ("band.architecture",),
        "A split or bypass shank's rails SHARE the band's width, so widening "
        "the band widens the rails rather than moving them apart.",
    ),
)


#: The DERIVATION edges: what each variant actually writes.
_DERIVATIONS: tuple[RingFamilyDependency, ...] = (
    # ---- SOLITAIRE ---------------------------------------------------------
    _for(
        "SOLITAIRE_CATHEDRAL",
        "ringFamily.params.shoulderSpanDeg",
        ("ringFamily.shoulderArchitecture",),
        "A cathedral solitaire builds real shoulder arches rising from the band "
        "to the head. The span is where each arch meets the band.",
    ),
    _for(
        "SOLITAIRE_LOW_PROFILE",
        "ringFamily.params.headHeightFactor",
        ("setting.basketHeight",),
        "A low-profile solitaire sits the stone closer to the finger. It "
        "MODULATES the document's own basket height rather than replacing it, so "
        "the author's scale still applies.",
    ),
    _for(
        "SOLITAIRE_ELEVATED",
        "ringFamily.params.headHeightFactor",
        ("setting.basketHeight", "ringFamily.shoulderArchitecture"),
        "An elevated solitaire raises the stone and gains shoulder arches to "
        "support the taller head — the two go together, which is why one variant "
        "derives both.",
    ),
    # ---- THREE_STONE -------------------------------------------------------
    _for(
        "THREE_STONE_SYMMETRIC",
        "ringFamily.params.sideSpacingMm",
        ("family.familyType", "family.params"),
        "The ring family DELEGATES the side stones to the Multi-Stone Family "
        "layer, which compiles them into an arrangement. Nothing here computes a "
        "stone position.",
    ),
    _for(
        "THREE_STONE_GRADUATED",
        "ringFamily.params.sideGraduationFactor",
        ("family.familyType", "family.params"),
        "A graduated trilogy's sides are smaller than a symmetric one's by the "
        "graduation factor. The same delegation, with a different scale.",
    ),
    # ---- HALO --------------------------------------------------------------
    _for(
        "HALO_SINGLE",
        "ringFamily.params.haloStoneCount",
        ("halo.variant", "halo.rings"),
        "The ring family DELEGATES the halo to the Halo System, which owns what "
        "a halo IS. The radius is derived from the CENTRE STONE's own half "
        "width times `haloRadiusFactor`, so the halo follows the stone.",
    ),
    _for(
        "HALO_DOUBLE",
        "ringFamily.params.haloRadiusFactor",
        ("halo.variant", "halo.rings"),
        "A double halo derives two rings whose radii are both measured from the "
        "centre stone, so changing the stone moves both.",
    ),
    _for(
        "HALO_HIDDEN",
        "ringFamily.params.haloRadiusFactor",
        ("halo.variant", "halo.rings"),
        "A hidden halo sits BELOW the centre plane, and the Halo System already "
        "requires a negative vertical offset for one — the family derives an "
        "offset from the head's own height rather than inventing a depth.",
    ),
    # ---- SPLIT_SHANK -------------------------------------------------------
    _for(
        "SPLIT_SHANK_PARALLEL",
        "ringFamily.params.splitSeparationMm",
        ("band.architecture", "band.splitSeparation", "band.splitJoinSpan",
         "ringFamily.shoulderArchitecture"),
        "A split shank is a real SHANK ARCHITECTURE: two rails joined into one "
        "band over the bottom span. The band's own width is shared between the "
        "rails, so the separation narrows them rather than widening the ring.",
    ),
    _for(
        "SPLIT_SHANK_TAPERED",
        "ringFamily.params.splitJoinSpanDeg",
        ("band.architecture", "band.splitSeparation", "band.splitJoinSpan",
         "band.widthTaper", "ringFamily.shoulderArchitecture"),
        "The tapered split additionally derives a width taper, so the rails "
        "narrow toward the bottom — using the taper the Shank subsystem already "
        "owns rather than a second narrowing mechanism.",
    ),
    # ---- BYPASS ------------------------------------------------------------
    _for(
        "BYPASS_CROSSOVER",
        "ringFamily.params.bypassOverlapDeg",
        ("band.architecture", "band.bypassSeparation", "band.bypassOverlap"),
        "A bypass is one open rail travelling past a full turn, so its two ends "
        "occupy the same angle at different axial positions. The overlap is what "
        "makes them PASS rather than meet.",
    ),
    # ---- SIGNET ------------------------------------------------------------
    _for(
        "SIGNET_FLAT_TABLE",
        "ringFamily.params.signetTableLengthMm",
        ("ringFamily.bodyArchitecture",),
        "A signet ring's defining feature is a solid body with a table at the "
        "ring's top, built as its own component so it has parametric identity "
        "rather than being an unnamed lump fused to the band.",
    ),
    # ---- shared across families -------------------------------------------
    _every(
        "DERIVATION",
        "ringFamily.params.paveShoulders",
        ("pave",),
        "Any family may compose a pavé field onto its shoulders. The Pavé Engine "
        "does every piece of it — the family only names the region and the "
        "density, and a field is derived only when the document declares no pavé "
        "of its own.",
    ),
    _every(
        "DERIVATION",
        "ringFamily.params.headHeightFactor",
        ("setting.basketHeight",),
        "Every family modulates the head's height, because every family has a "
        "head. A factor of 1.0 writes the document's own value back unchanged, "
        "which is why a classic solitaire's geometry does not move.",
    ),
)

RING_FAMILY_DEPENDENCIES: tuple[RingFamilyDependency, ...] = (
    *_INFLUENCES,
    *_DERIVATIONS,
)


def dependencies_for(variant: str) -> tuple[RingFamilyDependency, ...]:
    """Every edge that applies to one variant, in declaration order.

    Declaration order, not sorted: the order the edges are written in is the
    order `resolve.py` applies them, and a derivation that depends on an
    earlier one would silently change meaning if this were re-sorted.
    """

    return tuple(
        edge
        for edge in RING_FAMILY_DEPENDENCIES
        if edge.variant is None or edge.variant == variant
    )


def derived_paths(variant: str) -> tuple[str, ...]:
    """Every JDL path a variant may write, sorted and de-duplicated."""

    paths: set[str] = set()
    for edge in dependencies_for(variant):
        if edge.kind == "DERIVATION":
            paths.update(edge.targets)
    return tuple(sorted(paths))


def influenced_paths(source: str) -> tuple[str, ...]:
    """What changing an existing JDL field affects.

    THE QUESTION A DESIGNER ACTUALLY ASKS — "if I change the finger size, what
    moves?" — answered from the graph rather than from a comment.
    """

    targets: set[str] = set()
    for edge in RING_FAMILY_DEPENDENCIES:
        if edge.source == source:
            targets.update(edge.targets)
    return tuple(sorted(targets))


def dependency_graph() -> dict[str, dict[str, list[str]]]:
    """The whole graph, keyed by variant, for a machine-readable spec artifact.

    Generated rather than hand-maintained, so `specs/ring-family/v1/` cannot
    drift from the table above.
    """

    graph: dict[str, dict[str, list[str]]] = {}
    for variant in sorted(VARIANT_FAMILY):
        edges = dependencies_for(variant)
        graph[variant] = {
            "derives": sorted(derived_paths(variant)),
            "influencedBy": sorted(
                {edge.source for edge in edges if edge.kind == "INFLUENCE"}
            ),
            "parameters": sorted(
                {
                    edge.source
                    for edge in edges
                    if edge.kind == "DERIVATION"
                    and edge.source.startswith("ringFamily.params.")
                }
            ),
        }
    return graph
