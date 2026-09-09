"""The JDL -> RingDefinition v2 compatibility adapter (brief section 20:
prefer "existing JDL -> compatibility adapter -> internal model" over a
breaking JDL migration). Every field is copied from a real
`JewelryDefinition`, never invented — see
docs/bible/18-ring-architecture/533-solitaire-migration-model.md for the
full field-by-field mapping table this function implements.
"""

from __future__ import annotations

from jewelmind.domain.schema import JewelryDefinition
from jewelmind.jewelry_category.errors import CategoryAdapterFailedError
from jewelmind.ring.models import (
    RingDefinition,
    RingHeadDefinition,
    RingSizing,
    SettingAttachmentDefinition,
    ShankDefinition,
    ShoulderDefinition,
    StoneArrangementDefinition,
)


def ring_definition_from_jdl(definition: JewelryDefinition) -> RingDefinition:
    category = definition.jewelry.category
    if category != "ring":
        raise CategoryAdapterFailedError(
            f"ring_definition_from_jdl() requires jewelry.category == 'ring', got '{category}'."
        )

    return RingDefinition(
        family=definition.jewelry.style,
        sizing=RingSizing(
            sizeSystem=definition.ring.sizeSystem,
            size=definition.ring.size,
            innerDiameter=definition.ring.innerDiameter,
        ),
        shank=ShankDefinition(
            profile=definition.band.profile,
            widthMm=definition.band.width,
            thicknessMm=definition.band.thickness,
            widthTaper=definition.band.widthTaper.model_copy(),
            thicknessTaper=definition.band.thicknessTaper.model_copy(),
            architecture=definition.band.architecture,
            splitSeparationMm=definition.band.splitSeparation,
            splitJoinSpanDeg=definition.band.splitJoinSpan,
            bypassSeparationMm=definition.band.bypassSeparation,
            bypassOverlapDeg=definition.band.bypassOverlap,
        ),
        shoulders=_shoulders_from_jdl(definition),
        head=RingHeadDefinition(basketHeightMm=definition.setting.basketHeight),
        stoneArrangement=StoneArrangementDefinition(
            arrangement="SINGLE_CENTER",
            stone=definition.stone.model_copy(),
        ),
        setting=SettingAttachmentDefinition(
            settingType=definition.setting.type,
            prongCount=definition.setting.prongCount,
            prongDiameterMm=definition.setting.prongDiameter,
            prongHeightMm=definition.setting.prongHeight,
        ),
    )


def _shoulders_from_jdl(definition: JewelryDefinition) -> ShoulderDefinition:
    """The shoulder contract, read from the RESOLVED ring family (Sprint 28).

    Resolved rather than inferred from `jewelry.style`, because the architecture
    belongs to the VARIANT: a classic solitaire has no shoulders and a cathedral
    one has two arches, and both are `solitaire`. Reading the resolver is what
    keeps this from disagreeing with the component the assembly actually built —
    the single-resolution-point discipline `effective_arrangement()` established.

    A document the resolver refuses reports NO shoulder rather than raising: this
    adapter's job is to describe a design, and `JM-RINGFAM-001` is what reports
    the refusal.
    """

    from jewelmind.ring_family.errors import RingFamilyError
    from jewelmind.ring_family.resolve import resolve_ring_family

    try:
        architecture = resolve_ring_family(definition).shoulderArchitecture
    except RingFamilyError:
        return ShoulderDefinition()

    if architecture == "NONE":
        return ShoulderDefinition()
    return ShoulderDefinition(modeled=True, architecture=architecture)
