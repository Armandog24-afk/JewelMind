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
            status="planned",
            jdlExposed=False,
            generatable=False,
            inspectable=False,
            description="Multiple rails — architecture reserves the concept, v1 builds exactly one rail.",
        ),
        ShankCapability(
            capability="cathedral_shank",
            status="planned",
            jdlExposed=False,
            generatable=False,
            inspectable=False,
            description="Belongs primarily to shoulder/head integration, not a profile type.",
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
            description="See split_shank — the general case of more than one rail.",
        ),
        ShankCapability(
            capability="sculpted_shank",
            status="planned",
            jdlExposed=False,
            generatable=False,
            inspectable=False,
            description="Local, non-parametric sculpting; not implemented.",
        ),
    ]
}


def get_shank_capability(capability: str) -> ShankCapability | None:
    return SHANK_CAPABILITIES.get(capability)
