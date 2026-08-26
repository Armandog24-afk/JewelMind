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
        ),
        shoulders=ShoulderDefinition(),
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
