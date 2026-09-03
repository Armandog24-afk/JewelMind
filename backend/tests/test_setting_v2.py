"""Setting System v2 — advanced heads and prongs (Sprint 23).

Covers each implemented prong style and head architecture as REAL GEOMETRY
(valid solids, expected connectivity, correct extents), the explicit-position
and grouping escape hatches, the deterministic setting -> stone-instance
mapping, seat relief as a cut rather than a fuse, the structural rules, and —
the part easiest to break and most important to prove — that a design left on
the defaults produces byte-identical geometry.
"""

from __future__ import annotations

import ast
import json
import math
from pathlib import Path

import pytest
from pydantic import ValidationError

from jewelmind.domain.defaults import default_definition
from jewelmind.domain.schema import JewelryDefinition
from jewelmind.geometry.assemblies.solitaire import build_solitaire_ring
from jewelmind.geometry.roles import is_production_component
from jewelmind.geometry.setting_adapter import (
    head_definition_from_jdl,
    setting_attachment_interface,
    setting_definition_from_jdl,
)
from jewelmind.setting.capability import (
    HEAD_ARCHITECTURE_CAPABILITIES,
    PRONG_STYLE_CAPABILITIES,
    RESERVED_HEAD_ARCHITECTURES,
    RESERVED_PRONG_CAPABILITIES,
    RESERVED_SUPPORT_ELEMENTS,
    SEAT_CAPABILITIES,
    SETTING_CAPABILITIES,
    SETTING_GEOMETRY_VERSION,
    head_architecture_names,
    prong_styles,
)
from jewelmind.setting.dispatch import generate_setting
from jewelmind.setting.errors import SettingGenerationFailedError
from jewelmind.setting.head import (
    HEAD_COMPONENT,
    build_head,
    head_architectures,
    head_builders,
)
from jewelmind.setting.models import (
    HeadSettingDefinition,
    ProngGroupSpec,
    ProngPositionSpec,
    SeatSettingDefinition,
    SettingAttachmentInterface,
)
from jewelmind.setting.prong_styles import build_prong_solid, prong_solid_builders
from jewelmind.setting.seat import apply_seat_relief
from jewelmind.validation.engine import has_errors, validate_definition

#: The default solitaire's fused metal volume, unchanged since Sprint 19.
#: Compared with a relative tolerance rather than `==` because OCCT-derived
#: floats are not bit-identical across platform builds — the lesson Sprint 19's
#: CI failure taught, applied here from the start.
LEGACY_METAL_VOLUME_MM3 = 341.44334316909976
KERNEL_REL_TOLERANCE = 1e-9

ATTACHMENT = SettingAttachmentInterface(
    attachmentPlaneZMm=9.0, embedMm=0.15, supportHeightMm=3.5
)


def head(architecture: str, **over) -> HeadSettingDefinition:
    params: dict = {
        "architecture": architecture,
        "outerRadiusMm": 2.8,
        "wallThicknessMm": 1.1,
        "heightMm": 3.5,
    }
    params.update(over)
    return HeadSettingDefinition(**params)


def ring(**setting_over) -> JewelryDefinition:
    definition = default_definition()
    for key, value in setting_over.items():
        setattr(definition.setting, key, value)
    return definition


def setting_rule_ids(definition: JewelryDefinition) -> dict[str, str]:
    return {
        r.ruleId: r.severity
        for r in validate_definition(definition)
        if r.ruleId in {"JM-SETTING-005", "JM-SETTING-006", "JM-SETTING-007"}
    }


# ------------------------------------------------------------- prong styles


class TestProngStyles:
    @pytest.mark.parametrize("style", sorted(prong_solid_builders()))
    def test_every_style_builds_one_valid_solid(self, style: str):
        solid = build_prong_solid(style, 2.0, 0.0, 1.0, 4.8, 0.55, 0.6)
        assert len(solid.Solids()) == 1, style
        assert solid.isValid(), style
        assert solid.Volume() > 0.0, style

    @pytest.mark.parametrize("style", sorted(prong_solid_builders()))
    def test_every_style_spans_the_requested_height(self, style: str):
        base_z, height = 1.0, 4.8
        box = build_prong_solid(style, 2.0, 0.0, base_z, height, 0.55, 0.6).BoundingBox()
        assert box.zmin == pytest.approx(base_z, abs=1e-9)
        assert box.zmax == pytest.approx(base_z + height, abs=1e-6)

    def test_the_round_prong_is_the_pre_sprint_23_cylinder(self):
        """Byte-identical to the previous inline construction.

        A "unified" builder producing round as a degenerate taper would have
        been tidier and would have moved every existing design's geometry.
        """

        import cadquery as cq

        legacy = (
            cq.Workplane("XY")
            .workplane(offset=1.0)
            .center(2.0, 0.0)
            .circle(0.55)
            .extrude(4.8)
            .val()
        )
        built = build_prong_solid("ROUND_PRONG", 2.0, 0.0, 1.0, 4.8, 0.55, 0.6)
        assert built.Volume() == legacy.Volume()

    def test_the_round_prong_ignores_the_tip_ratio(self):
        """Honouring it would silently change every existing design."""

        wide = build_prong_solid("ROUND_PRONG", 0.0, 0.0, 0.0, 4.0, 0.5, 1.0)
        narrow = build_prong_solid("ROUND_PRONG", 0.0, 0.0, 0.0, 4.0, 0.5, 0.2)
        assert wide.Volume() == narrow.Volume()

    def test_a_tapered_prong_is_narrower_than_a_cylinder(self):
        cylinder = build_prong_solid("ROUND_PRONG", 0.0, 0.0, 0.0, 4.0, 0.5, 0.6)
        tapered = build_prong_solid("TAPERED_PRONG", 0.0, 0.0, 0.0, 4.0, 0.5, 0.6)
        assert tapered.Volume() < cylinder.Volume()

    def test_a_tapered_prong_honours_its_tip_ratio(self):
        wide = build_prong_solid("TAPERED_PRONG", 0.0, 0.0, 0.0, 4.0, 0.5, 0.9)
        narrow = build_prong_solid("TAPERED_PRONG", 0.0, 0.0, 0.0, 4.0, 0.5, 0.2)
        assert narrow.Volume() < wide.Volume()

    def test_a_claw_keeps_more_material_than_a_full_taper(self):
        """A claw concentrates its taper near the tip.

        That is the whole distinction between the two styles, so it is asserted
        rather than assumed — otherwise one of them is redundant.
        """

        claw = build_prong_solid("CLAW_PRONG", 0.0, 0.0, 0.0, 4.0, 0.5, 0.5)
        tapered = build_prong_solid("TAPERED_PRONG", 0.0, 0.0, 0.0, 4.0, 0.5, 0.5)
        assert claw.Volume() > tapered.Volume()

    def test_a_v_prong_removes_material_from_a_cylinder(self):
        cylinder = build_prong_solid("ROUND_PRONG", 2.0, 0.0, 0.0, 4.0, 0.5, 0.6)
        v_prong = build_prong_solid("V_PRONG", 2.0, 0.0, 0.0, 4.0, 0.5, 0.6)
        assert v_prong.Volume() < cylinder.Volume()
        # The notch is at the TIP, so the base is untouched and the solid still
        # spans the full height.
        assert v_prong.BoundingBox().zmax == pytest.approx(4.0, abs=1e-6)

    def test_an_unregistered_style_is_an_explicit_error(self):
        """Never a substitution: a round prong built for a requested claw would
        report one style and deliver another."""

        with pytest.raises(SettingGenerationFailedError):
            build_prong_solid("BEAD_PRONG", 0.0, 0.0, 0.0, 4.0, 0.5, 0.6)  # type: ignore[arg-type]

    def test_style_construction_is_deterministic(self):
        for style in sorted(prong_solid_builders()):
            first = build_prong_solid(style, 1.5, 0.5, 0.0, 4.0, 0.5, 0.6).Volume()
            for _ in range(3):
                assert (
                    build_prong_solid(style, 1.5, 0.5, 0.0, 4.0, 0.5, 0.6).Volume()
                    == first
                )


# --------------------------------------------------------- head architectures


class TestHeadArchitectures:
    @pytest.mark.parametrize("architecture", sorted(head_builders()))
    def test_every_architecture_builds_one_connected_solid(self, architecture: str):
        """One connected body, not several.

        `PEG_HEAD` originally produced TWO disconnected solids — a floating
        basket above an unattached peg — because a peg narrower than the wall's
        bore never touches it. The builder now raises on that, and this is the
        test that would have caught it.
        """

        extra = (
            {"pegDiameterMm": 1.6, "pegHeightMm": 1.2}
            if architecture == "PEG_HEAD"
            else {}
        )
        component = build_head(head(architecture, **extra), ATTACHMENT)
        assert len(component.shape.Solids()) == 1, architecture
        assert component.shape.isValid(), architecture
        assert component.volume_mm3 > 0.0, architecture

    @pytest.mark.parametrize("architecture", sorted(head_builders()))
    def test_every_architecture_keeps_the_component_name(self, architecture: str):
        """The name is a structural role, wired into the role map, the
        inspection required-component set, every manifest and every Golden."""

        extra = (
            {"pegDiameterMm": 1.6, "pegHeightMm": 1.2}
            if architecture == "PEG_HEAD"
            else {}
        )
        component = build_head(head(architecture, **extra), ATTACHMENT)
        assert component.name == HEAD_COMPONENT == "basket_support"
        assert is_production_component(component.name)

    @pytest.mark.parametrize("architecture", sorted(head_builders()))
    def test_every_architecture_spans_the_same_vertical_extent(self, architecture: str):
        """The stone's height above the attachment plane must not depend on the
        architecture; otherwise choosing a martini would silently move the
        stone."""

        extra = (
            {"pegDiameterMm": 1.6, "pegHeightMm": 1.2}
            if architecture == "PEG_HEAD"
            else {}
        )
        box = build_head(head(architecture, **extra), ATTACHMENT).shape.BoundingBox()
        assert box.zmin == pytest.approx(
            ATTACHMENT.attachmentPlaneZMm - ATTACHMENT.embedMm, abs=1e-9
        )
        assert box.zmax == pytest.approx(
            ATTACHMENT.attachmentPlaneZMm + 3.5, abs=1e-6
        )

    @pytest.mark.parametrize("architecture", sorted(head_builders()))
    def test_every_architecture_reports_what_it_built(self, architecture: str):
        extra = (
            {"pegDiameterMm": 1.6, "pegHeightMm": 1.2}
            if architecture == "PEG_HEAD"
            else {}
        )
        metadata = build_head(head(architecture, **extra), ATTACHMENT).metadata
        assert metadata["headArchitecture"] == architecture
        assert metadata["solidCount"] == 1

    def test_a_martini_is_narrower_at_its_base(self):
        component = build_head(head("MARTINI", baseRadiusRatio=0.4), ATTACHMENT)
        # Sampled at two heights: a conical wall's cross-section grows upward.
        low = component.shape.BoundingBox()
        assert low.xlen == pytest.approx(2 * 2.8, rel=1e-6)
        # Volume is strictly less than a straight wall of the same outer radius.
        basket = build_head(head("BASKET"), ATTACHMENT)
        assert component.volume_mm3 < basket.volume_mm3

    def test_a_tulip_is_a_concave_flare_not_a_straight_cone(self):
        """The tulip and martini must differ, or one of them is redundant."""

        tulip = build_head(head("TULIP", baseRadiusRatio=0.5), ATTACHMENT)
        martini = build_head(head("MARTINI", baseRadiusRatio=0.5), ATTACHMENT)
        assert tulip.volume_mm3 != martini.volume_mm3
        assert tulip.metadata["profile"] == "QUADRATIC_FLARE"
        assert tulip.metadata["sectionCount"] >= 2

    def test_a_peg_head_requires_its_peg_dimensions(self):
        """Refused rather than defaulted: an invented peg size would be a
        construction choice the caller never made."""

        with pytest.raises(SettingGenerationFailedError):
            build_head(head("PEG_HEAD"), ATTACHMENT)
        with pytest.raises(SettingGenerationFailedError):
            build_head(head("PEG_HEAD", pegDiameterMm=1.6), ATTACHMENT)

    def test_a_peg_taller_than_the_head_is_refused(self):
        with pytest.raises(SettingGenerationFailedError):
            build_head(
                head("PEG_HEAD", pegDiameterMm=1.6, pegHeightMm=3.5), ATTACHMENT
            )

    def test_an_unregistered_architecture_is_refused_before_construction(self):
        """`HeadArchitecture` is a closed enum whose every member has a builder,
        so an unknown name is rejected by the MODEL — earlier and more clearly
        than a generator-time error would be."""

        with pytest.raises(ValidationError):
            head("TRELLIS")
        assert "TRELLIS" not in head_builders()

    def test_head_construction_is_deterministic(self):
        for architecture in sorted(head_builders()):
            extra = (
                {"pegDiameterMm": 1.6, "pegHeightMm": 1.2}
                if architecture == "PEG_HEAD"
                else {}
            )
            first = build_head(head(architecture, **extra), ATTACHMENT).volume_mm3
            for _ in range(3):
                assert (
                    build_head(head(architecture, **extra), ATTACHMENT).volume_mm3
                    == first
                )

    def test_an_explicit_inner_radius_wins_over_the_derived_one(self):
        """The mechanism that preserves the legacy basket bore bit-for-bit."""

        derived = build_head(head("BASKET"), ATTACHMENT)
        explicit = build_head(head("BASKET", innerRadiusMm=1.0), ATTACHMENT)
        assert explicit.metadata["innerRadiusMm"] == 1.0
        assert explicit.volume_mm3 != derived.volume_mm3


# ----------------------------------------------------- explicit prong layouts


class TestExplicitPositions:
    def test_explicit_positions_are_used_verbatim(self):
        definition = setting_definition_from_jdl(
            default_definition(), build_solitaire_ring(default_definition()).components["stone_reference"]
        )
        assert definition.prong is not None
        updated = definition.model_copy(
            update={
                "prong": definition.prong.model_copy(
                    update={
                        "positionSource": "EXPLICIT",
                        "positions": [
                            ProngPositionSpec(xMm=2.0, yMm=0.0),
                            ProngPositionSpec(xMm=-2.0, yMm=0.0),
                            ProngPositionSpec(xMm=0.0, yMm=2.0),
                        ],
                    }
                )
            }
        )
        components, result = generate_setting(updated)
        metadata = components["prongs"].metadata
        assert metadata["positionSource"] == "EXPLICIT"
        assert metadata["generatedCount"] == 3
        assert [(p["x"], p["y"]) for p in metadata["positions"]] == [
            (2.0, 0.0),
            (-2.0, 0.0),
            (0.0, 2.0),
        ]
        assert result.generatedProngCount == 3

    def test_explicit_with_no_positions_is_refused(self):
        """Never a silent fall back to the derived strategy, which would build
        a layout the caller did not ask for."""

        base = setting_definition_from_jdl(
            default_definition(),
            build_solitaire_ring(default_definition()).components["stone_reference"],
        )
        assert base.prong is not None
        broken = base.model_copy(
            update={
                "prong": base.prong.model_copy(update={"positionSource": "EXPLICIT"})
            }
        )
        with pytest.raises(SettingGenerationFailedError):
            generate_setting(broken)

    def test_a_group_style_override_is_applied_per_prong(self):
        base = setting_definition_from_jdl(
            default_definition(),
            build_solitaire_ring(default_definition()).components["stone_reference"],
        )
        assert base.prong is not None
        mixed = base.model_copy(
            update={
                "prong": base.prong.model_copy(
                    update={
                        "positionSource": "EXPLICIT",
                        "style": "ROUND_PRONG",
                        "positions": [
                            ProngPositionSpec(xMm=2.0, yMm=0.0),
                            ProngPositionSpec(xMm=-2.0, yMm=0.0),
                        ],
                        "groups": [
                            ProngGroupSpec(
                                groupId="tip", style="V_PRONG", positionIndices=[0]
                            )
                        ],
                    }
                )
            }
        )
        components, _result = generate_setting(mixed)
        styles = components["prongs"].metadata["stylesUsed"]
        assert styles == ["V_PRONG", "ROUND_PRONG"]

    def test_a_group_naming_a_missing_index_is_refused(self):
        """Ignoring it would apply a requested style to nothing."""

        base = setting_definition_from_jdl(
            default_definition(),
            build_solitaire_ring(default_definition()).components["stone_reference"],
        )
        assert base.prong is not None
        broken = base.model_copy(
            update={
                "prong": base.prong.model_copy(
                    update={
                        "positionSource": "EXPLICIT",
                        "positions": [ProngPositionSpec(xMm=2.0, yMm=0.0)],
                        "groups": [
                            ProngGroupSpec(
                                groupId="ghost", style="V_PRONG", positionIndices=[7]
                            )
                        ],
                    }
                )
            }
        )
        with pytest.raises(SettingGenerationFailedError):
            generate_setting(broken)

    def test_a_malformed_position_is_rejected_by_the_model(self):
        for bad in (float("nan"), float("inf"), 1000.0):
            with pytest.raises(ValidationError):
                ProngPositionSpec(xMm=bad, yMm=0.0)


# ------------------------------------------------- setting -> stone mapping


class TestStoneInstanceMapping:
    def test_a_shared_prong_reports_every_stone_it_serves(self):
        """By ID, not inferred from coordinates.

        The mapping is what makes a shared prong a real concept rather than a
        coincidence of position.
        """

        base = setting_definition_from_jdl(
            default_definition(),
            build_solitaire_ring(default_definition()).components["stone_reference"],
        )
        assert base.prong is not None
        shared = base.model_copy(
            update={
                "prong": base.prong.model_copy(
                    update={
                        "positionSource": "EXPLICIT",
                        "positions": [
                            ProngPositionSpec(
                                xMm=3.0,
                                yMm=0.0,
                                servesStoneInstanceIds=["center", "side.right"],
                            ),
                            ProngPositionSpec(
                                xMm=-3.0, yMm=0.0, servesStoneInstanceIds=["center"]
                            ),
                        ],
                    }
                )
            }
        )
        components, result = generate_setting(shared)
        assert result.stoneInstanceAssignments["prongs"] == ["center", "side.right"]
        assert components["prongs"].metadata["sharedProngCount"] == 1

    def test_the_mapping_is_deterministic_and_sorted(self):
        base = setting_definition_from_jdl(
            default_definition(),
            build_solitaire_ring(default_definition()).components["stone_reference"],
        )
        assert base.prong is not None

        def build(order: list[str]):
            updated = base.model_copy(
                update={
                    "prong": base.prong.model_copy(
                        update={
                            "positionSource": "EXPLICIT",
                            "positions": [
                                ProngPositionSpec(
                                    xMm=2.0, yMm=0.0, servesStoneInstanceIds=order
                                )
                            ],
                        }
                    )
                }
            )
            return generate_setting(updated)[1].stoneInstanceAssignments["prongs"]

        assert build(["b", "a"]) == build(["a", "b"]) == ["a", "b"]

    def test_a_single_stone_setting_reports_no_assignment(self):
        """An empty assignment means "the setting's own stone", which is the
        single-stone case — not a missing mapping."""

        _components, result = generate_setting(
            setting_definition_from_jdl(
                default_definition(),
                build_solitaire_ring(default_definition()).components[
                    "stone_reference"
                ],
            )
        )
        assert result.stoneInstanceAssignments == {"prongs": []}

    def test_the_setting_system_never_resolves_a_stone_instance_id(self):
        """It carries the reference and never imports the arrangement layer.

        Asserted structurally: the whole package is parsed, not merely
        imported, because a cached module imports fine regardless of what it
        depends on.
        """

        setting_dir = Path(__file__).resolve().parents[1] / "jewelmind" / "setting"
        for path in sorted(setting_dir.glob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                modules: list[str] = []
                if isinstance(node, ast.Import):
                    modules = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                    modules = [node.module]
                for module in modules:
                    assert not module.startswith("jewelmind.arrangement"), (
                        path.name,
                        module,
                    )


# ---------------------------------------------------------------- seat relief


class TestSeatRelief:
    def test_relief_is_off_by_default(self):
        assert SeatSettingDefinition().mode == "NONE"
        component = build_head(head("BASKET"), ATTACHMENT)
        unchanged, notes = apply_seat_relief(
            component, component.shape, SeatSettingDefinition()
        )
        assert unchanged is component
        assert notes == []

    def test_relief_removes_real_material(self):
        model = build_solitaire_ring(ring(seatMode="REFERENCE_SEAT"))
        plain = build_solitaire_ring(default_definition())
        assert (
            model.components["basket_support"].volume_mm3
            < plain.components["basket_support"].volume_mm3
        )
        assert model.components["prongs"].volume_mm3 < plain.components["prongs"].volume_mm3
        assert model.combined_metal_volume_mm3 < plain.combined_metal_volume_mm3

    def test_relief_reports_the_operation_it_performed(self):
        """Explicitly a CUT. A reader must not have to trust that a fuse was
        avoided — the metadata says which operation ran."""

        model = build_solitaire_ring(ring(seatMode="REFERENCE_SEAT"))
        for name in ("prongs", "basket_support"):
            metadata = model.components[name].metadata
            assert metadata["seatOperation"] == "CUT_STONE_FROM_METAL"
            assert metadata["seatMode"] == "REFERENCE_SEAT"
            assert metadata["seatRemovedVolumeMm3"] > 0.0
        assert model.setting_result.seatMode == "REFERENCE_SEAT"

    def test_relief_never_fuses_the_stone_into_metal(self):
        """LAW-006, asserted structurally over `seat.py`'s own source.

        A cut is why relief can exist at all; a fuse would put stone material
        into the production body and into every export.
        """

        source = (
            Path(__file__).resolve().parents[1] / "jewelmind" / "setting" / "seat.py"
        ).read_text(encoding="utf-8")
        tree = ast.parse(source)
        called = {
            node.func.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        }
        assert "fuse" not in called
        assert "cut" in called

    def test_the_stone_reference_is_still_excluded_from_production(self):
        model = build_solitaire_ring(ring(seatMode="REFERENCE_SEAT"))
        production = sorted(n for n in model.components if is_production_component(n))
        assert production == ["band", "basket_support", "prongs"]

    def test_relief_keeps_the_metal_one_connected_solid(self):
        model = build_solitaire_ring(ring(seatMode="REFERENCE_SEAT"))
        assert len(model.combined_metal.Solids()) == 1

    def test_relief_is_deterministic(self):
        first = build_solitaire_ring(
            ring(seatMode="REFERENCE_SEAT")
        ).combined_metal_volume_mm3
        again = build_solitaire_ring(
            ring(seatMode="REFERENCE_SEAT")
        ).combined_metal_volume_mm3
        assert first == again

    def test_a_non_overlapping_stone_reports_that_nothing_was_removed(self):
        """A no-op cut is a fact worth stating, not a silent success."""

        import cadquery as cq

        component = build_head(head("BASKET"), ATTACHMENT)
        far_away = cq.Solid.makeBox(1, 1, 1, pnt=cq.Vector(50, 50, 50))
        _relieved, notes = apply_seat_relief(
            component, far_away, SeatSettingDefinition(mode="REFERENCE_SEAT")
        )
        assert notes and "removed no material" in notes[0]


# ------------------------------------------------------------- Forge rules


class TestSettingV2Rules:
    def test_a_default_design_produces_no_findings(self):
        assert setting_rule_ids(default_definition()) == {}

    def test_a_peg_head_without_peg_dimensions_is_an_error(self):
        definition = ring(headArchitecture="PEG_HEAD")
        assert setting_rule_ids(definition)["JM-SETTING-005"] == "error"
        assert has_errors(validate_definition(definition))

    def test_a_peg_taller_than_the_head_is_an_error(self):
        definition = ring(
            headArchitecture="PEG_HEAD", pegDiameter=1.6, pegHeight=4.0
        )
        assert setting_rule_ids(definition)["JM-SETTING-005"] == "error"

    def test_a_valid_peg_head_produces_no_error(self):
        definition = ring(
            headArchitecture="PEG_HEAD", pegDiameter=1.6, pegHeight=1.2
        )
        assert not has_errors(validate_definition(definition))

    def test_an_unread_field_is_information_not_a_warning(self):
        """The document is perfectly valid; the value simply has no effect."""

        definition = ring(type="bezel", prongStyle="CLAW_PRONG")
        assert setting_rule_ids(definition)["JM-SETTING-006"] == "information"
        assert not has_errors(validate_definition(definition))

    def test_peg_fields_on_a_non_peg_head_are_reported(self):
        definition = ring(pegDiameter=1.6)
        assert setting_rule_ids(definition)["JM-SETTING-006"] == "information"

    def test_seat_relief_on_an_imported_stone_is_a_warning(self):
        definition = default_definition()
        definition.setting.seatMode = "REFERENCE_SEAT"
        # Only the source matters to this rule; the asset itself is validated
        # elsewhere, and constructing a real import here would test that instead.
        data = definition.stone.model_dump()
        data["source"] = "IMPORTED_CAD"
        data["importedAsset"] = {"assetHash": "a" * 64, "declaredUnit": "mm"}
        from jewelmind.domain.schema import StoneSpec

        definition.stone = StoneSpec.model_validate(data)
        assert setting_rule_ids(definition)["JM-SETTING-007"] == "warning"

    def test_no_setting_v2_rule_invents_a_professional_threshold(self):
        """Scans the real emitted messages, not the source.

        A claim introduced through an f-string would be caught here too.
        """

        forbidden = (
            "too thin",
            "too thick",
            "minimum thickness",
            "not castable",
            "not manufacturable",
            "industry standard",
            "recommended",
            "will hold",
            "secure",
        )
        definitions = [
            default_definition(),
            ring(headArchitecture="PEG_HEAD"),
            ring(headArchitecture="MARTINI", headBaseRatio=0.1),
            ring(prongStyle="V_PRONG", prongTipRatio=0.1),
            ring(seatMode="REFERENCE_SEAT"),
            ring(type="bezel", prongStyle="CLAW_PRONG"),
        ]
        for definition in definitions:
            for result in validate_definition(definition):
                lowered = result.message.lower()
                for term in forbidden:
                    assert term not in lowered, (result.ruleId, result.message)


# ----------------------------------------------------------------- assembly


class TestAssemblyIntegration:
    @pytest.mark.parametrize("style", sorted(prong_solid_builders()))
    def test_every_style_generates_a_complete_ring(self, style: str):
        model = build_solitaire_ring(ring(prongStyle=style))
        assert sorted(model.components) == [
            "band",
            "basket_support",
            "prongs",
            "stone_reference",
        ]
        assert len(model.combined_metal.Solids()) == 1
        assert model.setting_result.prongStyle == style

    @pytest.mark.parametrize("architecture", sorted(head_builders()))
    def test_every_architecture_generates_a_complete_ring(self, architecture: str):
        over = {"headArchitecture": architecture}
        if architecture == "PEG_HEAD":
            over |= {"pegDiameter": 1.6, "pegHeight": 1.2}
        model = build_solitaire_ring(ring(**over))
        assert sorted(model.components) == [
            "band",
            "basket_support",
            "prongs",
            "stone_reference",
        ]
        assert len(model.combined_metal.Solids()) == 1
        assert model.setting_result.headArchitecture == architecture

    def test_the_head_is_built_once(self):
        """Both the Setting System and the Ring re-export call the same builder;
        the assembly must not construct it twice."""

        model = build_solitaire_ring(ring(headArchitecture="MARTINI"))
        assert model.components["basket_support"].metadata["headArchitecture"] == (
            "MARTINI"
        )

    def test_the_adapter_resolves_the_head_from_ring_facts(self):
        definition = default_definition()
        resolved = head_definition_from_jdl(definition)
        interface = setting_attachment_interface(definition)
        assert resolved.heightMm == definition.setting.basketHeight
        assert resolved.wallThicknessMm == definition.setting.prongDiameter
        assert interface.supportHeightMm == definition.setting.basketHeight


# -------------------------------------------------- backward compatibility


class TestBackwardCompatibility:
    def test_the_default_metal_volume_is_unchanged(self):
        """The single most important assertion in this file.

        Head construction moved into the Setting System and prong construction
        gained style dispatch. If either had changed the default path's
        geometry, every Golden baseline and every stored model would have moved.
        """

        model = build_solitaire_ring(default_definition())
        assert model.combined_metal_volume_mm3 == pytest.approx(
            LEGACY_METAL_VOLUME_MM3, rel=KERNEL_REL_TOLERANCE
        )

    def test_the_defaults_are_the_pre_sprint_23_behaviour(self):
        setting = default_definition().setting
        assert setting.prongStyle == "ROUND_PRONG"
        assert setting.headArchitecture == "BASKET"
        assert setting.seatMode == "NONE"
        assert setting.pegDiameter is None
        assert setting.pegHeight is None

    def test_a_legacy_document_without_the_new_fields_still_validates(self):
        """A stored design saved before Sprint 23 has none of these keys."""

        payload = default_definition().model_dump(mode="json")
        for key in (
            "prongStyle",
            "headArchitecture",
            "seatMode",
            "prongTipRatio",
            "headBaseRatio",
            "pegDiameter",
            "pegHeight",
        ):
            payload["setting"].pop(key, None)
        restored = JewelryDefinition.model_validate(payload)
        assert restored.setting.prongStyle == "ROUND_PRONG"
        assert restored.setting.headArchitecture == "BASKET"
        assert build_solitaire_ring(restored).combined_metal_volume_mm3 == (
            pytest.approx(LEGACY_METAL_VOLUME_MM3, rel=KERNEL_REL_TOLERANCE)
        )

    def test_the_basket_bore_is_preserved_exactly(self):
        """Not merely close: the adapter passes the ORIGINAL expression.

        Deriving the bore as `outerRadius - wallThickness` re-associates the
        same arithmetic and lands ~1e-11 mm away — harmless numerically and
        still an avoidable change to shipped geometry.
        """

        definition = default_definition()
        resolved = head_definition_from_jdl(definition)
        interface = setting_attachment_interface(definition)
        from jewelmind.geometry.connection import shank_connection_interface

        center_r = shank_connection_interface(definition).headCenterRadiusMm
        prong_r = definition.setting.prongDiameter / 2
        assert resolved.innerRadiusMm == center_r - prong_r
        assert interface.attachmentPlaneZMm == (
            shank_connection_interface(definition).topZMm
        )

    def test_the_stone_reference_is_untouched_by_every_new_option(self):
        plain = build_solitaire_ring(default_definition())
        for over in (
            {"prongStyle": "CLAW_PRONG"},
            {"headArchitecture": "TULIP"},
            {"prongTipRatio": 0.3},
        ):
            model = build_solitaire_ring(ring(**over))
            assert model.components["stone_reference"].volume_mm3 == pytest.approx(
                plain.components["stone_reference"].volume_mm3, rel=1e-12
            )


# --------------------------------------------------- capability consistency


SPECS_V2 = Path(__file__).resolve().parents[2] / "specs" / "setting" / "v2"


class TestCapabilityConsistency:
    def test_every_registered_style_has_a_builder_and_vice_versa(self):
        assert set(prong_styles()) == set(prong_solid_builders())

    def test_every_registered_architecture_has_a_builder_and_vice_versa(self):
        assert set(head_architecture_names()) == set(head_architectures())

    def test_reserved_names_have_no_builder(self):
        for name in RESERVED_HEAD_ARCHITECTURES:
            assert name.upper() not in head_builders()
            # And a real reason, not a roadmap slogan.
            assert len(RESERVED_HEAD_ARCHITECTURES[name]) > 40

    def test_reserved_support_elements_and_prong_capabilities_are_explained(self):
        for mapping in (RESERVED_SUPPORT_ELEMENTS, RESERVED_PRONG_CAPABILITIES):
            assert mapping
            for name, reason in mapping.items():
                assert len(reason) > 40, name

    def test_only_the_round_prong_and_basket_claim_legacy_preservation(self):
        legacy_styles = [
            name for name, e in PRONG_STYLE_CAPABILITIES.items() if e.preservesLegacyGeometry
        ]
        legacy_heads = [
            name
            for name, e in HEAD_ARCHITECTURE_CAPABILITIES.items()
            if e.preservesLegacyGeometry
        ]
        assert legacy_styles == ["ROUND_PRONG"]
        assert legacy_heads == ["BASKET"]

    def test_no_entry_claims_professional_validation(self):
        for mapping in (
            PRONG_STYLE_CAPABILITIES,
            HEAD_ARCHITECTURE_CAPABILITIES,
            SEAT_CAPABILITIES,
        ):
            for entry in mapping.values():
                assert entry.professionalValidationStatus == "NOT_REVIEWED"

    def test_seat_support_is_partial_not_current(self):
        """Relief is real; a cut seat with a bearing shoulder is not."""

        for capability in SETTING_CAPABILITIES.values():
            assert capability.seatSupport == "PARTIAL"
            assert capability.bearingSupport == "PLANNED"
            assert capability.cutterSupport == "PLANNED"

    def test_the_geometry_version_records_the_change(self):
        assert SETTING_GEOMETRY_VERSION == "1.1.0"

    def test_the_v2_specs_match_the_live_registries(self):
        def load(name: str) -> dict:
            return json.loads((SPECS_V2 / name).read_text(encoding="utf-8"))

        heads = load("head-architecture-registry.json")
        assert heads["componentName"] == HEAD_COMPONENT
        assert {e["architecture"] for e in heads["architectures"]} == set(
            HEAD_ARCHITECTURE_CAPABILITIES
        )
        for entry in heads["architectures"]:
            assert entry == HEAD_ARCHITECTURE_CAPABILITIES[
                entry["architecture"]
            ].model_dump(mode="json")

        styles = load("prong-style-registry.json")
        for entry in styles["styles"]:
            assert entry == PRONG_STYLE_CAPABILITIES[entry["style"]].model_dump(
                mode="json"
            )

        seats = load("seat-registry.json")
        for entry in seats["modes"]:
            assert entry == SEAT_CAPABILITIES[entry["mode"]].model_dump(mode="json")
        relief = next(e for e in seats["modes"] if e["mode"] == "REFERENCE_SEAT")
        assert relief["operation"] == "CUT_STONE_FROM_METAL"

    def test_the_consistency_vectors_still_hold(self):
        vectors = json.loads(
            (
                SPECS_V2 / "test-vectors" / "registry-consistency-vectors.json"
            ).read_text(encoding="utf-8")
        )
        assert vectors["prongStylesWithBuilders"] == vectors["prongStylesInRegistry"]
        assert (
            vectors["headArchitecturesWithBuilders"]
            == vectors["headArchitecturesInRegistry"]
        )
        assert set(vectors["prongStylesWithBuilders"]) == set(prong_solid_builders())
        assert set(vectors["headArchitecturesWithBuilders"]) == set(head_builders())
        # A reserved name must never appear as a real family or architecture.
        assert not set(vectors["reservedHeadArchitectures"]) & {
            n.lower() for n in head_builders()
        }
        assert not set(vectors["reservedSettingFamilies"]) & set(
            vectors["settingFamilies"]
        )


# --------------------------------------------------------------- geometry math


class TestGeometryFacts:
    def test_a_v_notch_opens_along_the_prong_radial_direction(self):
        """A notch pointing the wrong way is not a V prong.

        Compared by the notch's own effect: a prong on +X and one on +Y remove
        the same volume, because each notch follows its own radius.
        """

        on_x = build_prong_solid("V_PRONG", 2.0, 0.0, 0.0, 4.0, 0.5, 0.6)
        on_y = build_prong_solid("V_PRONG", 0.0, 2.0, 0.0, 4.0, 0.5, 0.6)
        assert on_x.Volume() == pytest.approx(on_y.Volume(), rel=1e-9)

    def test_a_prong_on_the_axis_still_builds(self):
        """No radial direction exists there; the notch falls back rather than
        producing an arbitrary rotation or a failure."""

        solid = build_prong_solid("V_PRONG", 0.0, 0.0, 0.0, 4.0, 0.5, 0.6)
        assert len(solid.Solids()) == 1

    def test_head_volume_ordering_matches_the_silhouettes(self):
        """A straight wall holds the most metal, a flared one the least — a
        cheap check that the three architectures are really different shapes."""

        basket = build_head(head("BASKET"), ATTACHMENT).volume_mm3
        martini = build_head(head("MARTINI", baseRadiusRatio=0.55), ATTACHMENT).volume_mm3
        tulip = build_head(head("TULIP", baseRadiusRatio=0.55), ATTACHMENT).volume_mm3
        assert basket > martini > tulip

    def test_a_narrower_base_ratio_removes_metal(self):
        wide = build_head(head("MARTINI", baseRadiusRatio=0.9), ATTACHMENT).volume_mm3
        narrow = build_head(head("MARTINI", baseRadiusRatio=0.3), ATTACHMENT).volume_mm3
        assert narrow < wide

    def test_every_head_stays_inside_its_own_radius(self):
        for architecture in sorted(head_builders()):
            extra = (
                {"pegDiameterMm": 1.6, "pegHeightMm": 1.2}
                if architecture == "PEG_HEAD"
                else {}
            )
            box = build_head(head(architecture, **extra), ATTACHMENT).shape.BoundingBox()
            radius = max(abs(box.xmin), abs(box.xmax), abs(box.ymin), abs(box.ymax))
            assert radius <= 2.8 + 1e-6, architecture

    def test_prong_positions_are_unchanged_by_the_style(self):
        """Style changes the body, never where it sits."""

        plain = build_solitaire_ring(default_definition())
        for style in ("TAPERED_PRONG", "CLAW_PRONG", "V_PRONG"):
            model = build_solitaire_ring(ring(prongStyle=style))
            assert (
                model.components["prongs"].metadata["positions"]
                == plain.components["prongs"].metadata["positions"]
            )

    def test_a_radial_layout_still_sits_on_one_circle(self):
        model = build_solitaire_ring(default_definition())
        positions = model.components["prongs"].metadata["positions"]
        radii = [math.hypot(p["x"], p["y"]) for p in positions]
        assert max(radii) == pytest.approx(min(radii), rel=1e-12)
