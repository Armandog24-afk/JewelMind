"""Ring-side adapter: `JewelryDefinition` -> Setting System inputs.

This module is the **only** place ring-shaped facts are turned into the
category-neutral contracts the Setting System consumes. It lives on the
Ring/Atlas side of the boundary on purpose: the dependency arrow is

    Ring/assembly  ->  setting_adapter  ->  jewelmind.setting  ->  Stone contracts

and never the reverse. `jewelmind.setting` has no idea a band or a ring
size exists (SETTING-GOV-001/014); it receives an
`attachmentPlaneZMm`/`embedMm`/`supportHeightMm` triple and works from that.

It is deliberately NOT inside `jewelmind/setting/` — putting it there would
require importing `JewelryDefinition` (which carries `ring`, `band`, and
`setting` fields) into the Setting core, exactly the leak
`test_setting_system_no_ring_dependency.py` exists to prevent.
"""

from __future__ import annotations

from jewelmind.domain.schema import JewelryDefinition
from jewelmind.geometry.connection import shank_connection_interface
from jewelmind.geometry.model import GeneratedComponent
from jewelmind.setting.models import (
    BezelSettingDefinition,
    ProngSettingDefinition,
    SettingAttachmentInterface,
    SettingDefinition,
)
from jewelmind.setting.placement import resolve_strategy
from jewelmind.setting.stone_interface import build_stone_setting_reference


def setting_attachment_interface(definition: JewelryDefinition) -> SettingAttachmentInterface:
    """Build the generic attachment contract from the ring's own head geometry.

    `attachmentPlaneZMm` is the top of the band and `supportHeightMm` is the
    basket height — both real ring facts, resolved here so the Setting never
    reads them itself.
    """

    interface = shank_connection_interface(definition)
    return SettingAttachmentInterface(
        attachmentPlaneZMm=interface.topZMm,
        embedMm=interface.embedMm,
        supportHeightMm=definition.setting.basketHeight,
    )


def setting_definition_from_jdl(
    definition: JewelryDefinition,
    stone_component: GeneratedComponent,
    setting_id: str = "primary",
) -> SettingDefinition:
    """Map the public JDL `setting` block onto the discriminated Setting model.

    This is the compatibility adapter referenced in brief section 30: the
    flat JDL `SettingSpec` stays backward compatible while the Setting
    System works with per-family typed models.
    """

    stone_reference = build_stone_setting_reference(definition.stone, stone_component)
    attachment = setting_attachment_interface(definition)

    prong: ProngSettingDefinition | None = None
    bezel: BezelSettingDefinition | None = None

    if definition.setting.type == "prong":
        prong = ProngSettingDefinition(
            prongCount=definition.setting.prongCount,
            prongDiameterMm=definition.setting.prongDiameter,
            prongHeightMm=definition.setting.prongHeight,
            # Resolved from the stone's real symmetry, not requested via JDL.
            placementStrategy=resolve_strategy(stone_reference),
        )
    else:
        bezel = BezelSettingDefinition(
            wallThicknessMm=definition.setting.bezelWallThickness,
            wallHeightMm=definition.setting.bezelWallHeight,
        )

    return SettingDefinition(
        settingId=setting_id,
        settingType=definition.setting.type,
        stone=stone_reference,
        attachment=attachment,
        prong=prong,
        bezel=bezel,
    )
