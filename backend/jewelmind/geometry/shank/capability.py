"""The real Shank capability registry (SHANK-GOV-015, brief section 56) —
distinguishes CURRENT from PLANNED, and JDL-exposed/internal-only from
generatable/inspectable, so documentation, Designer, and Studio can never
advertise a capability the code doesn't actually have. Mirrored, not
hand-duplicated, at specs/shank/v1/capability-registry.json.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

CapabilityStatus = Literal["current", "planned"]


class ShankCapability(BaseModel):
    model_config = ConfigDict(extra="forbid")

    capability: str
    status: CapabilityStatus
    jdlExposed: bool
    generatable: bool
    inspectable: bool
    description: str


SHANK_CAPABILITIES: dict[str, ShankCapability] = {
    entry.capability: entry
    for entry in [
        ShankCapability(
            capability="uniform_shank",
            status="current",
            jdlExposed=True,
            generatable=True,
            inspectable=True,
            description="Constant width/thickness all the way around — the pre-Sprint-17 default.",
        ),
        ShankCapability(
            capability="flat_profile",
            status="current",
            jdlExposed=True,
            generatable=True,
            inspectable=True,
            description="Rectangular cross-section, optional outer-rim fillet (uniform shank only).",
        ),
        ShankCapability(
            capability="comfort_fit_profile",
            status="current",
            jdlExposed=True,
            generatable=True,
            inspectable=True,
            description="Shallow outward-bulging inner edge; optional outer-rim fillet (uniform shank only).",
        ),
        ShankCapability(
            capability="width_taper_toward_bottom",
            status="current",
            jdlExposed=True,
            generatable=True,
            inspectable=True,
            description="Full base width at the head, linearly tapering to bottomRatio*base at the bottom.",
        ),
        ShankCapability(
            capability="thickness_taper_toward_bottom",
            status="current",
            jdlExposed=True,
            generatable=True,
            inspectable=True,
            description=(
                "Full base thickness at the head, linearly tapering to bottomRatio*base at the bottom."
            ),
        ),
        ShankCapability(
            capability="combined_width_and_thickness_taper",
            status="current",
            jdlExposed=True,
            generatable=True,
            inspectable=True,
            description="Width and thickness taper applied together, independently controlled.",
        ),
        ShankCapability(
            capability="outer_rim_fillet_on_tapered_shank",
            status="planned",
            jdlExposed=False,
            generatable=False,
            inspectable=False,
            description=(
                "No single 'circle at radius X' exists once the radius varies by angle; not yet implemented."
            ),
        ),
        ShankCapability(
            capability="taper_toward_head",
            status="planned",
            jdlExposed=False,
            generatable=False,
            inspectable=False,
            description=(
                "Would move the connection-interface anchor away from u=0; deliberately out of v1 scope."
            ),
        ),
        ShankCapability(
            capability="designer_taper_proposal",
            status="planned",
            jdlExposed=False,
            generatable=False,
            inspectable=False,
            description=(
                "Designer may not propose widthTaper/thicknessTaper this Sprint "
                "(not in KNOWN_JDL_FIELD_PATHS)."
            ),
        ),
        ShankCapability(
            capability="studio_taper_editor",
            status="planned",
            jdlExposed=False,
            generatable=False,
            inspectable=False,
            description="No Studio UI control for taper this Sprint — JDL/API-only.",
        ),
        ShankCapability(
            capability="split_shank",
            status="current",
            jdlExposed=True,
            generatable=True,
            inspectable=True,
            description=(
                "Sprint 28. TWO rails sharing the band's width, joined into one "
                "band over the bottom span and genuinely separated at the top — "
                "the axial gap between them contains no metal. Built by "
                "`shank/architecture.py::build_split_shank()`, selected by "
                "`band.architecture = 'SPLIT'`, and reported by the "
                "SHANK_RAIL_COUNT and SHANK_SEPARATED_AT_HEAD inspection facts. "
                "A wider separation NARROWS the rails rather than widening the "
                "ring, and `JM-RINGFAM-004` refuses a separation that leaves no "
                "rail at all."
            ),
        ),
        ShankCapability(
            capability="bypass_shank",
            status="current",
            jdlExposed=True,
            generatable=True,
            inspectable=True,
            description=(
                "Sprint 28. ONE open rail travelling past a full turn with its "
                "axial position shifting as it goes, so its two ends occupy the "
                "same angles at different axial positions and PASS each other. "
                "Deliberately one rail rather than two arcs: two axially "
                "separated arcs come out as two disconnected solids, and a ring "
                "that is not one connected body is not a ring. Built by "
                "`shank/architecture.py::build_bypass_shank()`, selected by "
                "`band.architecture = 'BYPASS'`."
            ),
        ),
        ShankCapability(
            capability="cathedral_shank",
            status="current",
            jdlExposed=True,
            generatable=True,
            inspectable=True,
            description=(
                "Sprint 28. Still not a profile type — it belongs to "
                "shoulder/head integration, exactly as this entry has said since "
                "Sprint 17 — and that integration now exists: "
                "`geometry/shoulder.py` builds two real arches for "
                "SOLITAIRE_CATHEDRAL and four for a split shank, each lofted "
                "from the band's OWN profile wire up to the head's OWN height. "
                "Selected by the ring-family variant rather than by a band "
                "field, because a cathedral is a family variant and not a "
                "section shape."
            ),
        ),
        ShankCapability(
            capability="knife_edge_profile",
            status="planned",
            jdlExposed=False,
            generatable=False,
            inspectable=False,
            description="A third section-profile type; not implemented.",
        ),
        ShankCapability(
            capability="euro_shank",
            status="planned",
            jdlExposed=False,
            generatable=False,
            inspectable=False,
            description="A modified centerline path; the current path is circular only.",
        ),
        ShankCapability(
            capability="twisted_shank",
            status="planned",
            jdlExposed=False,
            generatable=False,
            inspectable=False,
            description="Not implemented.",
        ),
        ShankCapability(
            capability="multi_rail_shank",
            status="planned",
            jdlExposed=False,
            generatable=False,
            inspectable=False,
            description=(
                "MORE THAN TWO rails. `split_shank` became real in Sprint 28 and "
                "builds exactly two; the general case is still not built, and it "
                "is not a loop over the two-rail builder — three rails sharing "
                "one band width need their own axial layout and their own bridge."
            ),
        ),
        ShankCapability(
            capability="sculpted_shank",
            status="planned",
            jdlExposed=False,
            generatable=False,
            inspectable=False,
            description=(
                "Local, non-parametric sculpting; not implemented. It needs a "
                "verified swept solid along a 3D spline, which is the same "
                "prerequisite `SPLIT_SHANK_SCULPTED`, `SOLITAIRE_TRELLIS` and "
                "`BYPASS_TWIST` all wait on — see "
                "docs/bible/30-ring-families/coverage-review.md."
            ),
        ),
    ]
}


def get_shank_capability(capability: str) -> ShankCapability | None:
    return SHANK_CAPABILITIES.get(capability)
