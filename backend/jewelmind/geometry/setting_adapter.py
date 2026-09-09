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
    BarSettingDefinition,
    BezelSettingDefinition,
    ChannelSettingDefinition,
    FlushSettingDefinition,
    HeadSettingDefinition,
    ProngSettingDefinition,
    ProngStyle,
    SeatSettingDefinition,
    SettingAttachmentInterface,
    SettingDefinition,
    TensionSettingDefinition,
)
from jewelmind.setting.modes import (
    prong_style_for_mode,
    resolve_primary_mode,
    setting_mode_fingerprint,
)
from jewelmind.setting.placement import resolve_strategy
from jewelmind.setting.stone_interface import build_stone_setting_reference

#: Mirrors `setting/head.py::_MIN_INNER_RADIUS_MM`. Applied here so the value
#: handed across the boundary is already the one the old basket used, rather
#: than relying on the head builder's own clamp to reproduce it.
_MIN_BASKET_INNER_RADIUS_MM = 0.2


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

    # THE RESOLVED PRIMARY MODE, resolved ONCE, here (Sprint 27).
    #
    # `resolve_primary_mode()` is the single resolution point, the role
    # `effective_arrangement()` plays for placement. Every family block below
    # reads its parameters from the SAME resolved mode, so a channel's wall
    # height and the mode id reported in the result can never come from
    # different readings of the document.
    resolved_mode = resolve_primary_mode(
        definition.setting.type,
        definition.setting.prongStyle,
        definition.setting.mode,
    )
    parameters = resolved_mode.parameters
    instance_ids = resolved_mode.arrangementInstanceIds

    prong: ProngSettingDefinition | None = None
    bezel: BezelSettingDefinition | None = None
    channel: ChannelSettingDefinition | None = None
    bar: BarSettingDefinition | None = None
    flush: FlushSettingDefinition | None = None
    tension: TensionSettingDefinition | None = None

    if definition.setting.type == "prong":
        prong = ProngSettingDefinition(
            prongCount=definition.setting.prongCount,
            prongDiameterMm=definition.setting.prongDiameter,
            prongHeightMm=definition.setting.prongHeight,
            # Resolved from the stone's real symmetry, not requested via JDL.
            placementStrategy=resolve_strategy(stone_reference),
            # The BODY STYLE comes from the resolved mode, which for a document
            # with no mode block is exactly `setting.prongStyle` — so this is
            # the same value it always was, read through the one resolution
            # point instead of twice.
            style=_prong_style_for(resolved_mode, definition.setting.prongStyle),
            tipRatio=definition.setting.prongTipRatio,
        )
    elif definition.setting.type == "bezel":
        bezel = BezelSettingDefinition(
            wallThicknessMm=definition.setting.bezelWallThickness,
            wallHeightMm=definition.setting.bezelWallHeight,
            variant="PARTIAL" if resolved_mode.modeId == "BEZEL_PARTIAL" else "FULL",
            openingCount=parameters.openingCount,
            openingSweepDeg=parameters.openingSweepDeg,
            openingStartAngleDeg=parameters.openingStartAngleDeg,
        )
    elif definition.setting.type == "channel":
        channel = ChannelSettingDefinition(
            axisDeg=parameters.axisDeg,
            spanMm=parameters.spanMm,
            innerWidthMm=parameters.innerWidthMm,
            wallThicknessMm=parameters.wallThicknessMm,
            wallHeightMm=parameters.wallHeightMm,
            termination=parameters.termination,
            symmetry=parameters.symmetry,
            offsetXMm=parameters.offsetXMm,
            offsetYMm=parameters.offsetYMm,
            offsetZMm=parameters.offsetZMm,
            stoneInstanceIds=instance_ids,
        )
    elif definition.setting.type == "bar":
        bar = BarSettingDefinition(
            axisDeg=parameters.axisDeg,
            barCount=parameters.barCount,
            barSpacingMm=parameters.barSpacingMm,
            barWidthMm=parameters.wallThicknessMm,
            barLengthMm=parameters.barLengthMm,
            barHeightMm=parameters.barHeightMm,
            symmetry=parameters.symmetry,
            offsetXMm=parameters.offsetXMm,
            offsetYMm=parameters.offsetYMm,
            offsetZMm=parameters.offsetZMm,
            stoneInstanceIds=instance_ids,
        )
    elif definition.setting.type == "flush":
        flush = FlushSettingDefinition(
            collarWidthMm=parameters.collarWidthMm,
            rimHeightMm=parameters.rimHeightMm,
            offsetXMm=parameters.offsetXMm,
            offsetYMm=parameters.offsetYMm,
            offsetZMm=parameters.offsetZMm,
        )
    else:
        tension = TensionSettingDefinition(
            gripAxisDeg=parameters.gripAxisDeg,
            padWidthMm=parameters.padWidthMm,
            padThicknessMm=parameters.padThicknessMm,
            padDepthMm=parameters.padDepthMm,
            gripHeightMm=parameters.gripHeightMm,
            offsetXMm=parameters.offsetXMm,
            offsetYMm=parameters.offsetYMm,
            offsetZMm=parameters.offsetZMm,
        )

    return SettingDefinition(
        settingId=setting_id,
        settingType=definition.setting.type,
        stone=stone_reference,
        attachment=attachment,
        prong=prong,
        bezel=bezel,
        channel=channel,
        bar=bar,
        flush=flush,
        tension=tension,
        head=head_definition_from_jdl(definition),
        seat=SeatSettingDefinition(mode=definition.setting.seatMode),
        settingModeId=resolved_mode.modeId,
        settingModeFingerprint=setting_mode_fingerprint(resolved_mode),
    )


def _prong_style_for(resolved_mode, declared_style: ProngStyle) -> ProngStyle:
    """The prong body style a resolved mode names.

    `PRONG_SHARED` maps to the round body, so it cannot itself express a style;
    for that one mode the declared `setting.prongStyle` still applies, which is
    what makes "a shared CLAW prong" expressible. Every other prong mode names
    exactly one body.
    """

    if resolved_mode.modeId == "PRONG_SHARED":
        return declared_style
    style = prong_style_for_mode(resolved_mode.modeId)
    return style if style is not None else declared_style  # type: ignore[return-value]


def head_definition_from_jdl(definition: JewelryDefinition) -> HeadSettingDefinition:
    """Map the ring's head fields onto the category-neutral head contract.

    THE RADIAL DIMENSIONS COME FROM THE RING, RESOLVED HERE. `outerRadiusMm`
    and `wallThicknessMm` reproduce exactly what the pre-Sprint-23 basket
    computed from `prong_center_radius()` and the prong diameter — outer radius
    was `centre + prongR` and the wall spanned down to `centre - prongR`, i.e.
    a thickness of the full prong diameter. Restating it as those two numbers is
    what lets the Setting System build the head without ever learning that a
    band exists (SETTING-GOV-014), while keeping the BASKET solid identical.
    """

    interface = shank_connection_interface(definition)
    prong_r = definition.setting.prongDiameter / 2
    center_r = interface.headCenterRadiusMm

    return HeadSettingDefinition(
        architecture=definition.setting.headArchitecture,
        outerRadiusMm=center_r + prong_r,
        wallThicknessMm=prong_r * 2,
        # The ORIGINAL expression, not a re-derivation. See
        # `HeadSettingDefinition.innerRadiusMm`.
        innerRadiusMm=max(center_r - prong_r, _MIN_BASKET_INNER_RADIUS_MM),
        heightMm=definition.setting.basketHeight,
        baseRadiusRatio=definition.setting.headBaseRatio,
        pegDiameterMm=definition.setting.pegDiameter,
        pegHeightMm=definition.setting.pegHeight,
        windowCount=definition.setting.galleryWindowCount,
        windowSweepDeg=definition.setting.galleryWindowSweep,
        windowHeightFraction=definition.setting.galleryWindowHeightFraction,
    )
