"""EXTENDED SETTING MODES v1 (Sprint 27).

The test matrix the brief asks for, in the order it asks for it: registry,
schema, domain, compiler, geometry, inspection, Forge, export, and the
architectural audit.

TWO PRINCIPLES RUN THROUGH EVERY TEST HERE.

1. **A capability claim is checked against the thing that would have to exist
   for it to be true.** Not against a restated list — against
   `setting_generators()`, `head_builders()`, `retention_builders()` and, for
   geometry, against a real built solid. That is why the registry tests import
   the live dispatch registries rather than a copy.

2. **Nothing asserts a professional judgment, and several tests assert that
   nothing does.** `TestNoInventedThresholds` reads this sprint's own source
   files and refuses a phrase that would turn a construction parameter into a
   recommendation.
"""

from __future__ import annotations

import ast
import json
import math
from pathlib import Path
from typing import get_args

import pytest

from jewelmind.domain.defaults import default_definition
from jewelmind.domain.schema import JewelryDefinition, SettingSpec, SettingType
from jewelmind.geometry.assemblies.solitaire import build_solitaire_ring
from jewelmind.geometry.inspection.inspector import inspect_model
from jewelmind.geometry.roles import GEOMETRY_ROLE, PRODUCTION_ROLE, geometry_role
from jewelmind.geometry.setting_adapter import setting_definition_from_jdl
from jewelmind.setting.bar import BAR_COMPONENT
from jewelmind.setting.capability import (
    PROFESSIONAL_REVIEW_REQUIRED,
    RESERVED_SETTING_FAMILIES,
    SETTING_GEOMETRY_VERSION,
    SETTING_MODE_PIPELINE_STAGES,
    designer_mode_terms,
    get_setting_mode,
    setting_mode_ids,
    setting_modes,
)
from jewelmind.setting.channel import CHANNEL_COMPONENT
from jewelmind.setting.dispatch import setting_generators
from jewelmind.setting.errors import SettingGenerationFailedError
from jewelmind.setting.flush import FLUSH_COMPONENT
from jewelmind.setting.frame import (
    axis_direction,
    crown_height_mm,
    oriented_prism,
    stone_extent_along,
)
from jewelmind.setting.head import head_builders
from jewelmind.setting.models import SettingFamily
from jewelmind.setting.modes import (
    MODE_PARAMETER_FIELDS,
    PRIMARY_FAMILY_SETTING_TYPE,
    RESERVED_SETTING_MODES,
    SETTING_MODE_TAXONOMY_VERSION,
    SettingModeId,
    SettingModeParameters,
    SettingModeSpec,
    default_primary_mode,
    mode_axis,
    mode_family,
    resolve_primary_mode,
    setting_mode_fingerprint,
)
from jewelmind.setting.prong_styles import prong_solid_builders
from jewelmind.setting.retention import retention_builders
from jewelmind.setting.tension import TENSION_COMPONENT
from jewelmind.validation.engine import validate_definition

REPO_ROOT = Path(__file__).resolve().parents[2]
SETTING_ROOT = REPO_ROOT / "backend" / "jewelmind" / "setting"

#: Kernel-derived floats are not bit-identical across OpenCascade builds, so
#: every geometric comparison here is relative. Sprint 5's CI proved two OCCT
#: builds produce different volumes for one design; this tolerance is a SOFTWARE
#: comparison tool and never a manufacturing tolerance (QUALITY-GOV-006).
KERNEL_REL = 1e-9

#: The component each family produces, stated once.
FAMILY_COMPONENT = {
    "prong": "prongs",
    "bezel": "bezel",
    "channel": CHANNEL_COMPONENT,
    "bar": BAR_COMPONENT,
    "flush": FLUSH_COMPONENT,
    "tension": TENSION_COMPONENT,
}


def definition_for(setting_type: str, **setting: object) -> JewelryDefinition:
    """A default design with one setting family selected.

    `flush` gets seat relief automatically: the recess is half its geometry and
    the generator refuses without it, so a fixture that omitted it would be
    testing the refusal rather than the family.
    """

    payload: dict[str, object] = {"type": setting_type, **setting}
    if setting_type == "flush":
        payload.setdefault("seatMode", "REFERENCE_SEAT")
    definition = default_definition()
    definition.setting = SettingSpec.model_validate(payload)
    return definition


def build(setting_type: str, **setting: object):
    return build_solitaire_ring(definition_for(setting_type, **setting))


# =========================================================================
# A. REGISTRY
# =========================================================================


class TestModeRegistry:
    def test_every_mode_id_has_a_registry_entry(self):
        assert set(setting_modes()) == set(get_args(SettingModeId))

    def test_every_mode_is_on_exactly_one_axis(self):
        for mode_id in setting_modes():
            axis = mode_axis(mode_id)
            assert axis in {"PRIMARY", "HEAD", "RETENTION"}
            on_axis = [a for a in ("PRIMARY", "HEAD", "RETENTION") if mode_id in setting_mode_ids(a)]
            assert on_axis == [axis]

    def test_no_duplicate_ids_and_no_reserved_id_is_implemented(self):
        ids = list(setting_modes())
        assert len(ids) == len(set(ids))
        assert not set(ids) & set(RESERVED_SETTING_MODES)

    def test_every_reserved_mode_states_a_real_reason(self):
        """A reason, not a roadmap slogan.

        The threshold is deliberately crude — a length and the absence of the
        word "planned" on its own — because the point is that a reader can tell
        what would have to exist first, and a one-word status cannot say that.
        """

        for mode_id, reason in RESERVED_SETTING_MODES.items():
            assert len(reason) > 60, mode_id
            assert reason.strip().lower() not in {"planned", "not implemented"}

    def test_geometry_is_claimed_only_where_a_builder_exists(self):
        """THE ANTI-DRIFT ASSERTION, checked in both directions.

        `settingGeometry` is DERIVED inside `setting_modes()` from the live
        builder registries rather than declared per row, so this test also
        asserts that the derivation actually ran.
        """

        for mode_id, entry in setting_modes().items():
            assert entry.settingGeometry is True, mode_id

        # Every builder is named by exactly one mode.
        assert {
            entry.settingType
            for entry in setting_modes().values()
            if entry.axis == "PRIMARY"
        } == set(setting_generators())

        head_modes = {
            mode_id for mode_id in setting_mode_ids("HEAD")
        }
        assert len(head_modes) == len(head_builders())

        retention_modes = set(setting_mode_ids("RETENTION"))
        assert len(retention_modes) == len(retention_builders())

    def test_every_prong_mode_names_a_real_body_builder(self):
        from jewelmind.setting.modes import prong_style_for_mode

        for mode_id in setting_mode_ids("PRIMARY"):
            style = prong_style_for_mode(mode_id)
            if style is None:
                continue
            assert style in prong_solid_builders(), mode_id

    def test_every_row_declares_every_pipeline_stage(self):
        for mode_id, entry in setting_modes().items():
            assert set(entry.pipelineCoverage) == set(
                SETTING_MODE_PIPELINE_STAGES
            ), mode_id

    def test_a_partial_mode_says_what_is_missing(self):
        """PARTIAL is not a place to park an unfinished mode.

        A PARTIAL mode must either declare an incomplete pipeline stage or
        require professional review — otherwise "PARTIAL" would carry no
        information at all.
        """

        for mode_id, entry in setting_modes().items():
            if entry.status == "CURRENT":
                continue
            incomplete = {
                stage
                for stage, status in entry.pipelineCoverage.items()
                if status != "CURRENT"
            }
            assert (
                incomplete or entry.professionalReviewRequirement == "REQUIRED"
            ), mode_id

    def test_no_mode_claims_professional_validation(self):
        for entry in setting_modes().values():
            assert entry.professionalValidationStatus == "NOT_REVIEWED"

    def test_professional_review_requirement_matches_the_family_table(self):
        """The mode-level and family-level records of the same fact must agree."""

        required_families = {
            entry.settingType
            for entry in setting_modes().values()
            if entry.professionalReviewRequirement == "REQUIRED"
        }
        assert required_families == set(PROFESSIONAL_REVIEW_REQUIRED)

    def test_designer_terms_are_unambiguous_and_cover_every_mode(self):
        terms = designer_mode_terms()
        assert set(terms.values()) == set(setting_modes())
        for entry in setting_modes().values():
            assert entry.designerTerms, entry.settingModeId

    def test_the_taxonomy_and_geometry_versions_are_recorded(self):
        assert SETTING_MODE_TAXONOMY_VERSION == "1.0.0"
        assert SETTING_GEOMETRY_VERSION == "1.2.0"


# =========================================================================
# B. SCHEMA
# =========================================================================


class TestSchema:
    def test_the_public_setting_type_matches_the_generator_registry(self):
        """A public type with no generator is a promise the pipeline cannot
        keep; a generator with no public type is unreachable."""

        assert set(get_args(SettingType)) == set(setting_generators())
        assert set(get_args(SettingType)) == set(get_args(SettingFamily))

    def test_every_primary_family_is_selectable_by_a_public_type(self):
        for family, setting_type in PRIMARY_FAMILY_SETTING_TYPE.items():
            assert setting_type in get_args(SettingType), family
            assert mode_family(default_primary_mode(setting_type)) == family

    def test_a_reserved_family_is_not_a_public_setting_type(self):
        for family in RESERVED_SETTING_FAMILIES:
            assert family not in get_args(SettingType)

    @pytest.mark.parametrize("setting_type", list(get_args(SettingType)))
    def test_every_setting_type_validates_with_no_other_field(self, setting_type):
        spec = SettingSpec.model_validate({"type": setting_type})
        assert spec.type == setting_type
        assert spec.mode is None

    def test_a_mode_block_round_trips(self):
        spec = SettingSpec.model_validate(
            {
                "type": "channel",
                "mode": {
                    "modeId": "CHANNEL_LINEAR",
                    "parameters": {"wallHeightMm": 1.1, "spanMm": 9.0},
                },
            }
        )
        assert spec.mode is not None
        assert spec.mode.parameters.wallHeightMm == 1.1
        assert spec.mode.parameters.spanMm == 9.0

    def test_an_unknown_mode_id_is_rejected(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            SettingSpec.model_validate(
                {"type": "channel", "mode": {"modeId": "CHANNEL_SHARED_WALL"}}
            )

    def test_openings_that_would_remove_the_whole_wall_are_refused(self):
        """REFUSED, not clamped: a wall the author never described is worse."""

        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            SettingModeParameters(openingCount=6, openingSweepDeg=60.0)

    @pytest.mark.parametrize(
        "payload",
        [
            {"collarWidthMm": 0.0},
            {"collarWidthMm": -1.0},
            {"rimHeightMm": float("nan")},
            {"rimHeightMm": float("inf")},
            {"barCount": 0},
            {"barCount": 10_000},
            {"padWidthMm": float("-inf")},
            {"wallThicknessMm": 0.0},
            {"axisDeg": 5_000.0},
            {"symmetry": "SOMETIMES"},
            {"termination": "WELDED"},
        ],
    )
    def test_hostile_parameter_values_are_rejected(self, payload):
        """SECURITY/ROBUSTNESS (brief §37).

        Zero, negative, NaN, Infinity, an out-of-range angle, an enormous count
        and an unknown enum member are each refused at the schema layer, before
        the kernel is ever asked for a solid. The bounds are SOFTWARE SAFETY
        LIMITS and say so in the model.
        """

        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            SettingModeParameters(**payload)

    def test_no_parameter_is_read_by_nothing(self):
        """A field nothing reads is the silently ignored parameter
        ARRANGE-GOV-011 forbids.

        This is why the open gallery's window parameters live on `SettingSpec`
        beside the other head fields rather than inside `mode.parameters`: the
        head is a different axis, and a mode that never reads a field must not
        carry one.
        """

        read = {
            name
            for fields in MODE_PARAMETER_FIELDS.values()
            for name in fields
        }
        assert read == set(SettingModeParameters.model_fields)

    def test_every_mode_has_a_parameter_field_list(self):
        assert set(MODE_PARAMETER_FIELDS) == set(setting_modes())


# =========================================================================
# C. DOMAIN — resolution and identity
# =========================================================================


class TestModeResolution:
    def test_a_document_with_no_mode_resolves_to_its_existing_meaning(self):
        """THE COMPATIBILITY GUARANTEE. A pre-Sprint-27 document's `type` and
        `prongStyle` already carried the variant, and resolution must reproduce
        exactly that."""

        for style, expected in (
            ("ROUND_PRONG", "PRONG_ROUND"),
            ("CLAW_PRONG", "PRONG_CLAW"),
            ("V_PRONG", "PRONG_V"),
            ("TAPERED_PRONG", "PRONG_TAPERED"),
        ):
            resolved = resolve_primary_mode("prong", style)
            assert resolved.modeId == expected
            assert resolved.derived is True

        assert resolve_primary_mode("bezel").modeId == "BEZEL_FULL"

    def test_a_family_mismatch_is_refused_rather_than_resolved(self):
        with pytest.raises(ValueError, match="determinate resolution"):
            resolve_primary_mode(
                "prong", "ROUND_PRONG", SettingModeSpec(modeId="BEZEL_PARTIAL")
            )

    def test_a_head_or_retention_mode_cannot_be_declared_as_primary(self):
        for mode_id in ("HEAD_MARTINI", "RETENTION_SHARED_BEAD"):
            with pytest.raises(ValueError, match="not a PRIMARY"):
                resolve_primary_mode(
                    "prong", "ROUND_PRONG", SettingModeSpec(modeId=mode_id)
                )

    def test_a_disabled_mode_falls_back_and_discards_its_parameters(self):
        resolved = resolve_primary_mode(
            "bezel",
            "ROUND_PRONG",
            SettingModeSpec(
                modeId="BEZEL_PARTIAL",
                enabled=False,
                parameters=SettingModeParameters(openingCount=5),
            ),
        )
        assert resolved.modeId == "BEZEL_FULL"
        assert resolved.derived is True
        assert resolved.parameters.openingCount == SettingModeParameters().openingCount

    def test_every_public_setting_type_has_a_default_mode(self):
        for setting_type in get_args(SettingType):
            assert default_primary_mode(setting_type) in setting_modes()


class TestModeIdentity:
    def test_the_fingerprint_is_deterministic(self):
        resolved = resolve_primary_mode("channel")
        assert setting_mode_fingerprint(resolved) == setting_mode_fingerprint(
            resolve_primary_mode("channel")
        )

    def test_a_changed_geometry_parameter_changes_the_fingerprint(self):
        base = resolve_primary_mode(
            "channel", "ROUND_PRONG", SettingModeSpec(modeId="CHANNEL_LINEAR")
        )
        changed = resolve_primary_mode(
            "channel",
            "ROUND_PRONG",
            SettingModeSpec(
                modeId="CHANNEL_LINEAR",
                parameters=SettingModeParameters(wallHeightMm=1.4),
            ),
        )
        assert setting_mode_fingerprint(base) != setting_mode_fingerprint(changed)

    def test_a_changed_mode_changes_the_fingerprint(self):
        full = resolve_primary_mode("bezel")
        partial = resolve_primary_mode(
            "bezel", "ROUND_PRONG", SettingModeSpec(modeId="BEZEL_PARTIAL")
        )
        assert setting_mode_fingerprint(full) != setting_mode_fingerprint(partial)

    def test_how_the_mode_was_reached_does_not_change_its_identity(self):
        """A document that declares `PRONG_ROUND` explicitly and one that
        reaches it through `prongStyle` describe the same setting.

        `derived` is therefore excluded from the fingerprint: including it would
        encode how the author typed the document rather than what they meant.
        """

        derived = resolve_primary_mode("prong", "ROUND_PRONG")
        declared = resolve_primary_mode(
            "prong", "ROUND_PRONG", SettingModeSpec(modeId="PRONG_ROUND")
        )
        assert derived.derived is not declared.derived
        assert setting_mode_fingerprint(derived) == setting_mode_fingerprint(declared)

    def test_instance_id_order_does_not_change_the_identity(self):
        one = resolve_primary_mode(
            "channel",
            "ROUND_PRONG",
            SettingModeSpec(
                modeId="CHANNEL_LINEAR", arrangementInstanceIds=["a", "b", "c"]
            ),
        )
        other = resolve_primary_mode(
            "channel",
            "ROUND_PRONG",
            SettingModeSpec(
                modeId="CHANNEL_LINEAR", arrangementInstanceIds=["c", "a", "b"]
            ),
        )
        assert setting_mode_fingerprint(one) == setting_mode_fingerprint(other)

    def test_the_fingerprint_carries_no_wall_clock_or_random_value(self):
        """ARRANGE-GOV-004's discipline, checked as CODE rather than as text.

        A text scan is the wrong instrument here: the module's own docstring
        documents the rule by naming the forbidden sources, so scanning for the
        words flags the documentation. What matters is whether the module
        IMPORTS or CALLS any of them, which is an AST question.
        """

        tree = ast.parse((SETTING_ROOT / "modes.py").read_text(encoding="utf-8"))
        forbidden_modules = {"time", "datetime", "uuid", "random", "os", "secrets"}
        assert not (_imported_modules(SETTING_ROOT / "modes.py") & forbidden_modules)

        forbidden_calls = {"id", "hash"}
        called = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        assert not called & forbidden_calls, sorted(called & forbidden_calls)


class TestGeometryIdentitySeparation:
    """HASHING / NORMALIZATION (brief §25)."""

    def test_changing_the_setting_mode_changes_the_geometry_identity(self):
        from jewelmind.utils.hashing import geometry_hash

        base = definition_for("bezel")
        partial = definition_for(
            "bezel", mode={"modeId": "BEZEL_PARTIAL"}
        )
        assert geometry_hash(base) != geometry_hash(partial)

    def test_changing_a_geometry_parameter_changes_the_geometry_identity(self):
        from jewelmind.utils.hashing import geometry_hash

        one = definition_for(
            "channel",
            mode={"modeId": "CHANNEL_LINEAR", "parameters": {"wallHeightMm": 0.8}},
        )
        other = definition_for(
            "channel",
            mode={"modeId": "CHANNEL_LINEAR", "parameters": {"wallHeightMm": 1.4}},
        )
        assert geometry_hash(one) != geometry_hash(other)

    def test_a_non_geometric_edit_leaves_the_geometry_identity_alone(self):
        """The gem separation Sprint 21 established still holds for the new
        families: a setting mode does not change what excludes what."""

        from jewelmind.utils.hashing import definition_hash, geometry_hash

        base = definition_for("channel")
        relabelled = definition_for(
            "channel", mode={"modeId": "CHANNEL_LINEAR", "label": "shank channel"}
        )
        recoloured = base.model_copy(deep=True)
        recoloured.material.metal = "platinum"

        assert geometry_hash(base) == geometry_hash(recoloured)
        assert definition_hash(base) != definition_hash(recoloured)
        # A label is carried in the document, so it DOES change both identities:
        # `geometryHash` excludes only the paths empirically proven not to drive
        # geometry, and `setting.mode` as a whole drives it.
        assert definition_hash(base) != definition_hash(relabelled)

    def test_the_label_does_not_change_the_mode_fingerprint(self):
        """The mode's OWN identity excludes the label, which is what makes
        renaming a mode free at the geometry layer even though the document
        changed."""

        plain = resolve_primary_mode(
            "channel", "ROUND_PRONG", SettingModeSpec(modeId="CHANNEL_LINEAR")
        )
        labelled = resolve_primary_mode(
            "channel",
            "ROUND_PRONG",
            SettingModeSpec(modeId="CHANNEL_LINEAR", label="shank channel"),
        )
        assert setting_mode_fingerprint(plain) == setting_mode_fingerprint(labelled)


# =========================================================================
# D. COMPILER — the adapter
# =========================================================================


class TestCompilerIntegration:
    @pytest.mark.parametrize("setting_type", list(get_args(SettingType)))
    def test_the_adapter_populates_exactly_its_own_family_block(self, setting_type):
        definition = definition_for(setting_type)
        model = build_solitaire_ring(definition)
        setting_def = setting_definition_from_jdl(
            definition, model.components["stone_reference"]
        )
        blocks = {
            "prong": setting_def.prong,
            "bezel": setting_def.bezel,
            "channel": setting_def.channel,
            "bar": setting_def.bar,
            "flush": setting_def.flush,
            "tension": setting_def.tension,
        }
        assert blocks[setting_type] is not None
        for name, block in blocks.items():
            if name != setting_type:
                assert block is None, name

    def test_the_adapter_carries_the_resolved_mode_and_its_identity(self):
        definition = definition_for("bar")
        model = build_solitaire_ring(definition)
        setting_def = setting_definition_from_jdl(
            definition, model.components["stone_reference"]
        )
        assert setting_def.settingModeId == "BAR_TRANSVERSE"
        assert setting_def.settingModeFingerprint == setting_mode_fingerprint(
            resolve_primary_mode("bar")
        )

    def test_there_is_exactly_one_compilation_path(self):
        """No second dispatch: every family is reached through
        `generate_setting()`, which is also where the head and seat steps run."""

        source = (SETTING_ROOT / "dispatch.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        entry_points = [
            node.name
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name == "generate_setting"
        ]
        assert entry_points == ["generate_setting"]

    def test_an_unsupported_mode_is_refused_before_geometry(self):
        """A mode/type mismatch produces a Forge ERROR, so the caller learns
        about it from validation rather than from a kernel exception."""

        definition = definition_for("prong", mode={"modeId": "FLUSH_GYPSY"})
        errors = [
            r
            for r in validate_definition(definition)
            if r.ruleId == "JM-SETTING-008" and r.severity == "error"
        ]
        assert errors


# =========================================================================
# E. GEOMETRY — real solids
# =========================================================================


class TestGeometry:
    @pytest.mark.parametrize("setting_type", list(get_args(SettingType)))
    def test_every_family_builds_a_real_measurable_solid(self, setting_type):
        model = build(setting_type)
        component = model.components[FAMILY_COMPONENT[setting_type]]
        assert component.shape.Solids()
        assert component.volume_mm3 > 0
        box = component.bounding_box
        assert box.xmax > box.xmin and box.ymax > box.ymin and box.zmax > box.zmin

    @pytest.mark.parametrize("setting_type", list(get_args(SettingType)))
    def test_every_family_is_reproducible(self, setting_type):
        """NUMERICAL REPEATABILITY (brief §35). Same input, same engine, same
        geometry — measured rather than assumed."""

        first = build(setting_type)
        second = build(setting_type)
        assert first.combined_metal_volume_mm3 == pytest.approx(
            second.combined_metal_volume_mm3, rel=KERNEL_REL
        )
        assert first.component_volumes() == pytest.approx(
            second.component_volumes(), rel=KERNEL_REL
        )
        assert first.bounding_box.as_dict() == pytest.approx(
            second.bounding_box.as_dict(), rel=KERNEL_REL
        )

    def test_the_default_prong_solitaire_is_byte_identical(self):
        """THE REGRESSION GUARANTEE. A design that declares no mode must
        generate exactly what it did before this sprint.

        The pinned volume is the same one SETTING-GOV-017 pins, carried forward
        unchanged since Sprint 19.
        """

        model = build_solitaire_ring(default_definition())
        assert model.combined_metal_volume_mm3 == pytest.approx(
            341.44334316909976, rel=KERNEL_REL
        )

    def test_a_partial_bezel_is_the_full_bezel_minus_its_openings(self):
        full = build("bezel").components["bezel"]
        partial = build("bezel", mode={"modeId": "BEZEL_PARTIAL"}).components["bezel"]
        assert partial.volume_mm3 < full.volume_mm3
        # n openings leave n arcs. Reported, never repaired.
        assert len(partial.shape.Solids()) == 2
        assert partial.metadata["openingCount"] == 2

    def test_more_openings_remove_more_metal(self):
        two = build(
            "bezel",
            mode={"modeId": "BEZEL_PARTIAL", "parameters": {"openingCount": 2}},
        ).components["bezel"]
        four = build(
            "bezel",
            mode={
                "modeId": "BEZEL_PARTIAL",
                "parameters": {"openingCount": 4, "openingSweepDeg": 30.0},
            },
        ).components["bezel"]
        assert four.volume_mm3 < two.volume_mm3
        assert len(four.shape.Solids()) == 4

    def test_an_open_gallery_is_one_connected_solid_with_less_metal(self):
        basket = build("prong").components["basket_support"]
        gallery = build("prong", headArchitecture="OPEN_GALLERY").components[
            "basket_support"
        ]
        assert gallery.volume_mm3 < basket.volume_mm3
        # SETTINGV2-GOV-006: a head that is not one connected body is not a head.
        assert len(gallery.shape.Solids()) == 1
        assert gallery.metadata["windowCount"] == 4

    def test_the_gallery_wall_stays_connected_at_the_schema_boundary(self):
        """THE GUARANTEE THAT ACTUALLY HOLDS, measured rather than assumed.

        `windowHeightFraction < 1.0` is a construction correctness bound: it
        leaves a rim at the top and the bottom, and those rims are what keep the
        pierced wall one connected body (SETTINGV2-GOV-006). Pushed to the
        extreme the rims become very thin, and the wall must still be ONE solid
        — so the boundary is enforced by the schema, and the builder's own
        solid-count check is the backstop for a future change that removed it.
        """

        component = build(
            "prong",
            headArchitecture="OPEN_GALLERY",
            galleryWindowHeightFraction=0.99,
            galleryWindowCount=8,
            galleryWindowSweep=40.0,
        ).components["basket_support"]
        assert len(component.shape.Solids()) == 1

    def test_a_full_height_window_is_refused_by_the_schema(self):
        """Where the real boundary is: a fraction of 1.0 would sever the wall,
        and it is unreachable rather than caught late."""

        from pydantic import ValidationError

        for fraction in (1.0, 1.5):
            with pytest.raises(ValidationError):
                SettingSpec.model_validate(
                    {
                        "type": "prong",
                        "headArchitecture": "OPEN_GALLERY",
                        "galleryWindowHeightFraction": fraction,
                    }
                )

    def test_a_channel_builds_two_walls_and_end_caps_add_metal(self):
        open_ended = build("channel").components[CHANNEL_COMPONENT]
        assert open_ended.metadata["wallCount"] == 2
        assert open_ended.metadata["endCapCount"] == 0

        closed = build(
            "channel",
            mode={"modeId": "CHANNEL_LINEAR", "parameters": {"termination": "CLOSED_ENDS"}},
        ).components[CHANNEL_COMPONENT]
        assert closed.metadata["endCapCount"] == 2
        assert closed.volume_mm3 > open_ended.volume_mm3

    def test_a_channels_clear_width_is_the_width_it_was_asked_for(self):
        """The document states the CLEAR distance between the walls, not a
        centre-to-centre distance. Measured from the real solids."""

        component = build(
            "channel",
            mode={
                "modeId": "CHANNEL_LINEAR",
                "parameters": {
                    "innerWidthMm": 4.0,
                    "wallThicknessMm": 0.7,
                    "axisDeg": 0.0,
                },
            },
        ).components[CHANNEL_COMPONENT]
        box = component.bounding_box
        # Outer width across the run = clear width + two wall thicknesses.
        assert box.ymax - box.ymin == pytest.approx(4.0 + 2 * 0.7, rel=1e-6)

    def test_a_channel_defaults_to_the_stones_own_measured_extent(self):
        component = build("channel").components[CHANNEL_COMPONENT]
        assert component.metadata["spanSource"] == "STONE_EXTENT"
        assert component.metadata["innerWidthSource"] == "STONE_EXTENT"

    def test_bar_count_is_honoured_and_reported(self):
        for count in (2, 3, 5):
            model = build(
                "bar", mode={"modeId": "BAR_TRANSVERSE", "parameters": {"barCount": count}}
            )
            component = model.components[BAR_COMPONENT]
            assert component.metadata["requestedBarCount"] == count
            assert component.metadata["generatedBarCount"] == count
            assert len(component.metadata["barOffsetsMm"]) == count
            assert model.setting_result.generatedBarCount == count

    def test_symmetric_and_asymmetric_bar_rows_are_genuinely_different(self):
        symmetric = build(
            "bar",
            mode={
                "modeId": "BAR_TRANSVERSE",
                "parameters": {"barCount": 3, "symmetry": "SYMMETRIC"},
            },
        ).components[BAR_COMPONENT]
        asymmetric = build(
            "bar",
            mode={
                "modeId": "BAR_TRANSVERSE",
                "parameters": {"barCount": 3, "symmetry": "ASYMMETRIC"},
            },
        ).components[BAR_COMPONENT]
        assert symmetric.metadata["barOffsetsMm"] != asymmetric.metadata["barOffsetsMm"]
        assert symmetric.bounding_box.as_dict() != asymmetric.bounding_box.as_dict()

    def test_a_flush_collar_has_the_stone_cut_out_of_it(self):
        """The recess is real: the collar's volume is measurably less than the
        solid plate it started as."""

        component = build("flush").components[FLUSH_COMPONENT]
        stone = build("flush").components["stone_reference"]
        box = component.bounding_box
        plate = math.pi * ((box.xmax - box.xmin) / 2.0) ** 2 * (box.zmax - box.zmin)
        assert component.volume_mm3 < plate
        assert component.metadata["recessOperation"] == "CUT_STONE_FROM_METAL"
        assert stone.volume_mm3 > 0

    def test_a_flush_setting_without_relief_refuses_rather_than_burying_the_stone(self):
        definition = default_definition()
        definition.setting = SettingSpec.model_validate(
            {"type": "flush", "seatMode": "NONE"}
        )
        with pytest.raises(SettingGenerationFailedError, match="requires seat relief"):
            build_solitaire_ring(definition)

    def test_a_flush_rim_above_the_crown_is_refused(self):
        definition = definition_for(
            "flush", mode={"modeId": "FLUSH_GYPSY", "parameters": {"rimHeightMm": 3.0}}
        )
        with pytest.raises(SettingGenerationFailedError, match="crown height"):
            build_solitaire_ring(definition)

    def test_tension_builds_two_opposing_supports(self):
        component = build("tension").components[TENSION_COMPONENT]
        assert component.metadata["supportCount"] == 2
        assert component.metadata["structuralBehaviourModelled"] is False
        assert component.metadata["professionalReviewRequirement"] == "REQUIRED"

    def test_tension_supports_that_would_meet_through_the_stone_are_refused(self):
        definition = definition_for(
            "tension",
            mode={"modeId": "TENSION_OPPOSED", "parameters": {"padDepthMm": 9.0}},
        )
        with pytest.raises(SettingGenerationFailedError, match="grip axis"):
            build_solitaire_ring(definition)

    def test_the_grip_axis_actually_rotates_the_supports(self):
        along_x = build("tension").components[TENSION_COMPONENT].bounding_box
        along_y = build(
            "tension",
            mode={"modeId": "TENSION_OPPOSED", "parameters": {"gripAxisDeg": 90.0}},
        ).components[TENSION_COMPONENT].bounding_box
        assert along_x.xmax - along_x.xmin == pytest.approx(
            along_y.ymax - along_y.ymin, rel=1e-6
        )
        assert along_x.xmax - along_x.xmin != pytest.approx(
            along_y.xmax - along_y.xmin, rel=1e-6
        )

    def test_an_offset_moves_the_setting_and_nothing_else(self):
        base = build("channel").components[CHANNEL_COMPONENT].bounding_box
        moved = build(
            "channel",
            mode={"modeId": "CHANNEL_LINEAR", "parameters": {"offsetXMm": 1.5}},
        ).components[CHANNEL_COMPONENT].bounding_box
        assert moved.xmin == pytest.approx(base.xmin + 1.5, rel=1e-6)
        assert moved.zmin == pytest.approx(base.zmin, rel=1e-6)

    @pytest.mark.parametrize("setting_type", list(get_args(SettingType)))
    def test_the_stone_is_never_fused_into_the_metal(self, setting_type):
        """LAW-006, for every family including the four new ones."""

        model = build(setting_type)
        report = inspect_model(model)
        separation = report.assemblyResult.stoneMetalSeparation
        assert separation.stoneReferenceExists is True
        assert separation.fusedIntoProductionMetal is False
        assert separation.productionIncluded is False


class TestFrameArithmetic:
    """The shared construction frame, exercised directly."""

    def test_the_axis_directions_are_unit_vectors(self):
        for angle in (0.0, 30.0, 90.0, 180.0, -45.0, 360.0):
            dx, dy = axis_direction(angle)
            assert math.hypot(dx, dy) == pytest.approx(1.0, rel=1e-12)

    def test_the_stone_extent_is_the_boxes_support_width(self):
        model = build("channel")
        setting_def = setting_definition_from_jdl(
            definition_for("channel"), model.components["stone_reference"]
        )
        stone = setting_def.stone
        size_x = stone.boundingBoxMaxMm[0] - stone.boundingBoxMinMm[0]
        size_y = stone.boundingBoxMaxMm[1] - stone.boundingBoxMinMm[1]
        assert stone_extent_along(stone, 0.0) == pytest.approx(size_x, rel=1e-12)
        assert stone_extent_along(stone, 90.0) == pytest.approx(size_y, rel=1e-12)
        assert crown_height_mm(stone) > 0

    def test_a_prism_is_rotated_about_its_own_centre(self):
        """Rotating after translating would swing it around the design origin —
        the mistake FAMILY-GOV records for `Shape.scale()`."""

        unrotated = oriented_prism(10.0, 0.0, 0.0, 1.0, 4.0, 2.0, 0.0)
        rotated = oriented_prism(10.0, 0.0, 0.0, 1.0, 4.0, 2.0, 90.0)
        assert rotated.Volume() == pytest.approx(unrotated.Volume(), rel=1e-12)
        assert rotated.Center().x == pytest.approx(10.0, abs=1e-9)
        assert rotated.Center().y == pytest.approx(0.0, abs=1e-9)

    def test_a_degenerate_prism_raises(self):
        with pytest.raises(SettingGenerationFailedError, match="non-positive"):
            oriented_prism(0.0, 0.0, 0.0, 1.0, 0.0, 2.0, 0.0)


# =========================================================================
# F. INSPECTION
# =========================================================================


class TestInspection:
    @pytest.mark.parametrize("setting_type", list(get_args(SettingType)))
    def test_the_mode_facts_are_reported_for_every_family(self, setting_type):
        report = inspect_model(build(setting_type))
        by_type = {f.factType: f for f in report.geometricFacts}
        assert by_type["SETTING_MODE_ID"].value == default_primary_mode(setting_type)
        assert by_type["SETTING_MODE_FINGERPRINT"].value
        assert by_type["SETTING_COMPONENT_PROVENANCE_COUNT"].value >= 1

    @pytest.mark.parametrize("setting_type", list(get_args(SettingType)))
    def test_every_generated_component_carries_provenance(self, setting_type):
        model = build(setting_type)
        result = model.setting_result
        provenance = {p.componentId for p in result.componentProvenance}
        assert provenance == set(result.generatedComponents)
        for record in result.componentProvenance:
            assert record.sourceStoneId
            assert record.classification in {"PRODUCTION", "REFERENCE"}

    def test_the_setting_component_is_a_required_component(self):
        """A channel-set assembly must report its OWN setting component as
        required, not fall through to the `prongs` fallback."""

        from jewelmind.geometry.inspection.assembly import required_component_names

        for setting_type, name in FAMILY_COMPONENT.items():
            model = build(setting_type)
            assert name in required_component_names(model), setting_type

    def test_a_partial_bezel_reports_a_discontinuous_wall_honestly(self):
        report = inspect_model(build("bezel", mode={"modeId": "BEZEL_PARTIAL"}))
        by_type = {f.factType: f for f in report.geometricFacts}
        assert by_type["SETTING_BEZEL_VARIANT"].value == "PARTIAL"
        assert by_type["BEZEL_WALL_CONTINUOUS"].value is False
        assert by_type["SETTING_GENERATED_OPENING_COUNT"].value == 2

    def test_tension_reports_that_its_structural_behaviour_is_not_modelled(self):
        report = inspect_model(build("tension"))
        by_type = {f.factType: f for f in report.geometricFacts}
        assert by_type["SETTING_STRUCTURAL_BEHAVIOUR_MODELLED"].value is False
        assert by_type["SETTING_PROFESSIONAL_REVIEW_REQUIREMENT"].value == "REQUIRED"

    def test_bar_requested_and_generated_counts_are_both_reported(self):
        report = inspect_model(
            build("bar", mode={"modeId": "BAR_TRANSVERSE", "parameters": {"barCount": 4}})
        )
        by_type = {f.factType: f for f in report.geometricFacts}
        assert by_type["SETTING_REQUESTED_BAR_COUNT"].value == 4
        assert by_type["SETTING_GENERATED_BAR_COUNT"].value == 4

    def test_every_new_fact_type_is_in_the_registry(self):
        registry = json.loads(
            (
                REPO_ROOT
                / "specs"
                / "geometry-inspection"
                / "v2"
                / "fact-registry.json"
            ).read_text(encoding="utf-8")
        )
        recorded = {f["factType"] for f in registry["facts"]}
        emitted = set()
        for setting_type in get_args(SettingType):
            emitted |= {
                f.factType for f in inspect_model(build(setting_type)).geometricFacts
            }
        assert emitted <= recorded, sorted(emitted - recorded)

    def test_inspection_never_mutates_the_geometry_it_reads(self):
        """INSPECT-GOV-013, re-asserted for the new components."""

        model = build("bar")
        before = {name: c.volume_mm3 for name, c in model.components.items()}
        inspect_model(model)
        after = {name: c.volume_mm3 for name, c in model.components.items()}
        assert before == after


# =========================================================================
# G. FORGE
# =========================================================================


class TestForgeRules:
    def test_a_default_design_produces_no_setting_mode_result(self):
        """The whole existing corpus stays silent: `PRONG_ROUND` is CURRENT and
        requires no review."""

        fired = [
            r.ruleId
            for r in validate_definition(default_definition())
            if r.ruleId in {f"JM-SETTING-{n:03d}" for n in range(8, 14)}
        ]
        assert fired == []

    def test_a_family_mismatch_is_an_error(self):
        results = validate_definition(
            definition_for("channel", mode={"modeId": "BEZEL_PARTIAL"})
        )
        match = [r for r in results if r.ruleId == "JM-SETTING-008"]
        assert match and match[0].severity == "error"

    def test_an_unread_parameter_is_reported_as_information(self):
        results = validate_definition(
            definition_for(
                "bezel",
                mode={"modeId": "BEZEL_PARTIAL", "parameters": {"collarWidthMm": 2.0}},
            )
        )
        match = [r for r in results if r.ruleId == "JM-SETTING-009"]
        assert match
        assert all(r.severity == "information" for r in match)
        assert "collarWidthMm" in match[0].message

    def test_a_disabled_mode_is_reported(self):
        results = validate_definition(
            definition_for("bezel", mode={"modeId": "BEZEL_PARTIAL", "enabled": False})
        )
        match = [r for r in results if r.ruleId == "JM-SETTING-009"]
        assert match and "disabled" in match[0].message

    def test_a_flush_setting_without_relief_is_an_error(self):
        definition = default_definition()
        definition.setting = SettingSpec.model_validate(
            {"type": "flush", "seatMode": "NONE"}
        )
        match = [
            r
            for r in validate_definition(definition)
            if r.ruleId == "JM-SETTING-010"
        ]
        assert match and match[0].severity == "error"
        assert match[0].suggestedValue == "REFERENCE_SEAT"

    def test_an_impossible_flush_rim_is_an_error(self):
        results = validate_definition(
            definition_for(
                "flush",
                mode={"modeId": "FLUSH_GYPSY", "parameters": {"rimHeightMm": 8.0}},
            )
        )
        match = [r for r in results if r.ruleId == "JM-SETTING-011"]
        assert match and match[0].severity == "error"

    def test_impossible_tension_supports_are_an_error(self):
        results = validate_definition(
            definition_for(
                "tension",
                mode={"modeId": "TENSION_OPPOSED", "parameters": {"padDepthMm": 9.0}},
            )
        )
        match = [r for r in results if r.ruleId == "JM-SETTING-011"]
        assert match and match[0].severity == "error"

    def test_tension_requires_professional_review(self):
        results = validate_definition(definition_for("tension"))
        match = [r for r in results if r.ruleId == "JM-SETTING-012"]
        assert match and match[0].severity == "warning"
        assert "qualified jewelry professional" in match[0].message

    def test_a_partial_mode_reports_its_status(self):
        results = validate_definition(definition_for("tension"))
        match = [r for r in results if r.ruleId == "JM-SETTING-013"]
        assert match and match[0].severity == "information"
        assert "PARTIAL" in match[0].message

    def test_no_prong_rule_fires_for_a_new_family(self):
        """Rule scoping, the defect Sprint 19 fixed for the bezel: a prong rule
        must never block a valid channel setting."""

        for setting_type in ("channel", "bar", "flush", "tension"):
            definition = definition_for(setting_type)
            definition.setting.prongCount = 99
            definition.setting.prongDiameter = 0.1
            if setting_type == "flush":
                definition.setting.seatMode = "REFERENCE_SEAT"
            fired = [
                r.ruleId
                for r in validate_definition(definition)
                if r.ruleId.startswith("JM-PRONG")
            ]
            assert fired == [], setting_type

    @pytest.mark.parametrize("setting_type", list(get_args(SettingType)))
    def test_every_family_passes_validation_on_the_defaults(self, setting_type):
        errors = [
            r
            for r in validate_definition(definition_for(setting_type))
            if r.severity == "error"
        ]
        assert errors == [], setting_type

    def test_every_new_rule_is_in_the_registry(self):
        registry = json.loads(
            (
                REPO_ROOT / "specs" / "forge" / "v1" / "current-rule-registry.json"
            ).read_text(encoding="utf-8")
        )
        listed = {r["ruleId"]: r for r in registry["rules"]}
        for number in range(8, 14):
            rule_id = f"JM-SETTING-{number:03d}"
            assert rule_id in listed, rule_id
            entry = listed[rule_id]
            # FORGE-GOV-006/008/013: blocking, validation status and stage are
            # each declared rather than implicit.
            assert entry["stage"].startswith("FORGE-")
            assert entry["professionalValidationStatus"] in {
                "not_required",
                "preliminary",
                "required",
                "validated",
            }
            assert entry["active"] is True

    def test_the_review_rule_is_the_only_one_marked_required(self):
        registry = json.loads(
            (
                REPO_ROOT / "specs" / "forge" / "v1" / "current-rule-registry.json"
            ).read_text(encoding="utf-8")
        )
        required = {
            r["ruleId"]
            for r in registry["rules"]
            if r["ruleId"].startswith("JM-SETTING-0")
            and int(r["ruleId"].rsplit("-", 1)[1]) >= 8
            and r["professionalValidationStatus"] == "required"
        }
        assert required == {"JM-SETTING-012"}


# =========================================================================
# H. EXPORT
# =========================================================================


class TestExport:
    @pytest.mark.parametrize("setting_type", list(get_args(SettingType)))
    def test_the_setting_component_is_production_metal(self, setting_type):
        name = FAMILY_COMPONENT[setting_type]
        assert GEOMETRY_ROLE[name] == "production_metal"
        assert PRODUCTION_ROLE[name] == "included_by_default"

    @pytest.mark.parametrize("setting_type", ["channel", "bar", "flush", "tension"])
    def test_step_and_stl_exports_are_real_and_exclude_the_stone(
        self, setting_type, tmp_path
    ):
        from jewelmind.exporters.step_exporter import export_step
        from jewelmind.exporters.stl_exporter import export_stl

        definition = definition_for(setting_type)
        model = build_solitaire_ring(definition)

        step = tmp_path / f"{setting_type}.step"
        export_step(model, step)
        assert step.stat().st_size > 0

        stl = tmp_path / f"{setting_type}.stl"
        export_stl(model, definition, stl, include_stone=False)
        assert stl.stat().st_size > 0

    @pytest.mark.parametrize("setting_type", ["channel", "bar", "flush", "tension"])
    def test_the_specification_export_names_the_setting_mode(self, setting_type):
        from jewelmind.exporters.specification import build_specification

        definition = definition_for(setting_type)
        model = build_solitaire_ring(definition)
        text = build_specification(
            definition,
            model,
            validate_definition(definition),
            # A FIXED timestamp, supplied by the caller. The exporter takes one
            # rather than reading the clock, which is what keeps a rendered
            # specification reproducible.
            "2026-01-01T00:00:00Z",
        )
        assert FAMILY_COMPONENT[setting_type] in text
        # LAW-010: the preliminary notice is never softened for a new family.
        assert "preliminary" in text.lower()


# =========================================================================
# I. ARCHITECTURAL AUDIT (brief §40)
# =========================================================================


def _imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


SPRINT_27_MODULES = [
    SETTING_ROOT / name
    for name in (
        "modes.py",
        "frame.py",
        "result.py",
        "channel.py",
        "bar.py",
        "flush.py",
        "tension.py",
    )
]


class TestArchitecturalAudit:
    def test_the_sprint_modules_exist(self):
        """Guards against the list above silently matching nothing, which would
        make every test below vacuously pass."""

        for path in SPRINT_27_MODULES:
            assert path.exists(), path

    @pytest.mark.parametrize("path", SPRINT_27_MODULES, ids=lambda p: p.name)
    def test_no_new_module_imports_ring_or_a_jewelry_category(self, path):
        """SETTING-GOV-001, by AST rather than by import: an import-based check
        can pass by accident on a module already cached from an earlier test."""

        forbidden = (
            "jewelmind.ring",
            "jewelmind.jewelry_category",
            "jewelmind.geometry.shank",
            "jewelmind.geometry.connection",
            "jewelmind.geometry.setting_adapter",
            "jewelmind.geometry.pave_surface",
            "jewelmind.geometry.pave_adapter",
        )
        imported = _imported_modules(path)
        violations = {
            name
            for name in imported
            for prefix in forbidden
            if name == prefix or name.startswith(prefix + ".")
        }
        assert not violations, f"{path.name}: {sorted(violations)}"

    @pytest.mark.parametrize("path", SPRINT_27_MODULES, ids=lambda p: p.name)
    def test_no_new_module_imports_the_arrangement_layer(self, path):
        """SETTINGV2-GOV-011: a setting CARRIES stone instance references and
        never resolves them."""

        assert not {
            name
            for name in _imported_modules(path)
            if name == "jewelmind.arrangement" or name.startswith("jewelmind.arrangement.")
        }

    @pytest.mark.parametrize("path", SPRINT_27_MODULES, ids=lambda p: p.name)
    def test_no_new_module_imports_the_jewelry_definition(self, path):
        """`JewelryDefinition` carries `ring`, `band` and `setting`, so
        importing it would smuggle the whole ring domain across in one
        import."""

        source = path.read_text(encoding="utf-8")
        assert "JewelryDefinition" not in source, path.name

    def test_the_domain_layers_are_kernel_free(self):
        """`modes.py` is carried in JDL and read by Forge, so it must not touch
        CadQuery — the same split `geometry/pave_surface.py` documents."""

        for name in ("modes.py",):
            source = (SETTING_ROOT / name).read_text(encoding="utf-8")
            assert "cadquery" not in source
            assert "import cq" not in source

    def test_the_pave_layer_still_does_not_import_the_setting_system(self):
        """PAVE-GOV-001, in the direction Sprint 27 could have broken: adding
        `SHARED_PRONG` to the pavé's retention literal must not have pulled the
        Setting System into the pavé package."""

        pave_root = REPO_ROOT / "backend" / "jewelmind" / "pave"
        for path in sorted(pave_root.glob("*.py")):
            violations = {
                name
                for name in _imported_modules(path)
                if name == "jewelmind.setting" or name.startswith("jewelmind.setting.")
            }
            assert not violations, f"{path.name}: {sorted(violations)}"

    def test_there_is_no_second_placement_engine(self):
        """A setting states its own extent; it never computes a stone's
        position. Asserted by refusing the arrangement resolver's own entry
        points anywhere under `jewelmind/setting/`."""

        for path in sorted(SETTING_ROOT.glob("*.py")):
            source = path.read_text(encoding="utf-8")
            for forbidden in ("compile_arrangement", "resolve_arrangement", "ring_angles_deg"):
                assert forbidden not in source, f"{path.name}: {forbidden}"

    def test_there_is_no_second_retention_implementation(self):
        """Every retention solid comes from `setting/retention.py`'s registry.

        A second bead or micro-prong builder elsewhere is what PAVE-GOV-006
        exists to prevent, so no other setting module may construct a sphere.
        """

        for path in sorted(SETTING_ROOT.glob("*.py")):
            if path.name == "retention.py":
                continue
            source = path.read_text(encoding="utf-8")
            assert "makeSphere" not in source, path.name

    def test_the_flush_family_reuses_the_bezels_verified_offset(self):
        """A second offset implementation would eventually miss the STEP-safety
        repair and ship a collar that re-imports as a zero-solid shell."""

        source = (SETTING_ROOT / "flush.py").read_text(encoding="utf-8")
        assert "offset_stone_outline" in source
        assert "offset2D" not in source

    def test_the_recess_is_a_cut_and_never_a_fuse(self):
        """LAW-006 / SETTINGV2-GOV-008, asserted on the sources that would have
        to break it."""

        for name in ("flush.py", "tension.py", "seat.py"):
            source = (SETTING_ROOT / name).read_text(encoding="utf-8")
            assert ".fuse(stone" not in source
            assert "fuse(stone_shape" not in source

    def test_no_geometry_path_bypasses_the_single_dispatch(self):
        """Every family generator is reachable ONLY through
        `setting_generators()`; the assembly calls `generate_setting()` once."""

        assembly = (
            REPO_ROOT
            / "backend"
            / "jewelmind"
            / "geometry"
            / "assemblies"
            / "solitaire.py"
        ).read_text(encoding="utf-8")
        assert assembly.count("generate_setting(") == 1
        for family in ("channel", "bar", "flush", "tension"):
            assert f"generate_{family}_setting" not in assembly


class TestNoInventedThresholds:
    """NO INVENTED PROFESSIONAL THRESHOLDS (brief §23).

    Read over this sprint's own source: a construction parameter must never be
    described as a standard, a recommendation or a manufacturing tolerance, and
    nothing may claim a setting would hold.
    """

    PROHIBITED = (
        "industry standard",
        "industry-standard",
        "professionally validated",
        "manufacturing safe",
        "manufacturing-safe",
        "jeweler approved",
        "jeweler-approved",
        "structurally safe",
        "production validated",
        "production-validated",
        "recommended minimum",
        "safe minimum",
        "minimum professional",
    )

    @pytest.mark.parametrize("path", SPRINT_27_MODULES, ids=lambda p: p.name)
    def test_no_module_makes_a_professional_claim(self, path):
        lowered = path.read_text(encoding="utf-8").lower()
        for phrase in self.PROHIBITED:
            assert phrase not in lowered, f"{path.name}: {phrase!r}"

    def test_the_capability_registry_makes_no_professional_claim(self):
        for entry in setting_modes().values():
            lowered = entry.description.lower()
            for phrase in self.PROHIBITED:
                assert phrase not in lowered, entry.settingModeId

    def test_no_forge_rule_message_claims_a_professional_threshold(self):
        for setting_type in get_args(SettingType):
            for result in validate_definition(definition_for(setting_type)):
                if not result.ruleId.startswith("JM-SETTING-0"):
                    continue
                lowered = result.message.lower()
                for phrase in self.PROHIBITED:
                    assert phrase not in lowered, result.ruleId

    def test_the_tension_family_states_what_it_does_not_model(self):
        """The substantive honesty of this sprint, asserted rather than
        assumed."""

        entry = get_setting_mode("TENSION_OPPOSED")
        assert entry is not None
        assert entry.professionalReviewRequirement == "REQUIRED"
        assert "NOT MODELLED" in entry.description
        source = (SETTING_ROOT / "tension.py").read_text(encoding="utf-8")
        assert "structuralBehaviourModelled" in source
        assert "spring-back" in source
        assert "NOT BUILT" in source


class TestCapabilityHonesty:
    def test_no_mode_is_current_without_a_geometry_and_inspection_stage(self):
        for mode_id, entry in setting_modes().items():
            if entry.status != "CURRENT":
                continue
            assert entry.pipelineCoverage["geometry"] == "CURRENT", mode_id
            assert entry.pipelineCoverage["inspection"] == "CURRENT", mode_id

    def test_the_reserved_modes_and_the_implemented_ones_do_not_overlap(self):
        assert not set(RESERVED_SETTING_MODES) & set(setting_modes())

    def test_a_reserved_mode_has_no_builder(self):
        from jewelmind.setting.modes import (
            head_architecture_for_mode,
            prong_style_for_mode,
            retention_strategy_for_mode,
        )

        for mode_id in RESERVED_SETTING_MODES:
            assert prong_style_for_mode(mode_id) is None
            assert head_architecture_for_mode(mode_id) is None
            assert retention_strategy_for_mode(mode_id) is None

    def test_the_stone_component_is_still_classified_as_a_stone(self):
        """ARRANGE-GOV-012 / LAW-006: a new component name must never shadow the
        stone prefix classification."""

        assert geometry_role("stone_reference") == "stone_reference"
        assert geometry_role("stone_reference.accent") == "stone_reference"
        for name in FAMILY_COMPONENT.values():
            assert geometry_role(name) == "production_metal"


# =========================================================================
# J. DESIGNER (brief §30)
# =========================================================================


class TestDesigner:
    """Designer must RECOGNISE the implemented modes and REFUSE the reserved
    ones, and it must never turn a relative description into a dimension.

    Every case below drives the REAL `DesignerService` with the fake provider
    the whole suite uses, so what is asserted is the shipped normalization
    pipeline rather than a table read back to itself.
    """

    @staticmethod
    def _interpret(values: list[tuple[str, str]]):
        from jewelmind.designer.provider import FakeDesignerProvider
        from jewelmind.designer.schemas import (
            NaturalLanguageDesignRequest,
            RawDesignerResponse,
            RawProposedValue,
        )
        from jewelmind.designer.service import DesignerService

        response = RawDesignerResponse(
            proposedCanonicalValues=[
                RawProposedValue(field=field, value=value, sourceText=value)
                for field, value in values
            ]
        )
        service = DesignerService(provider=FakeDesignerProvider(response=response))
        return service.interpret(
            NaturalLanguageDesignRequest(
                requestId="esm-01",
                text="setting request",
                interactionMode="CREATE",
            )
        )

    @pytest.mark.parametrize(
        ("spoken", "expected"),
        [
            ("castone", "bezel"),
            ("incastonatura a castone", "bezel"),
            ("incastonatura a canale", "channel"),
            ("channel setting", "channel"),
            ("bar setting", "bar"),
            ("barrette", "bar"),
            ("flush setting", "flush"),
            ("gypsy", "flush"),
            ("incastonatura a filo", "flush"),
            ("tension setting", "tension"),
            ("a tensione", "tension"),
            ("griffe", "prong"),
        ],
    )
    def test_a_spoken_family_reaches_the_real_setting_type(self, spoken, expected):
        result = self._interpret([("setting.type", spoken)])
        assert result.proposal.candidateJDL.setting.type == expected

    @pytest.mark.parametrize(
        ("mode_id", "expected_type"),
        [
            ("BEZEL_PARTIAL", "bezel"),
            ("CHANNEL_LINEAR", "channel"),
            ("FLUSH_GYPSY", "flush"),
            ("TENSION_OPPOSED", "tension"),
        ],
    )
    def test_designer_can_propose_a_mode_and_its_family_together(
        self, mode_id, expected_type
    ):
        """A MODE PATCH ON A DESIGN WITH NO MODE. `SettingModeSpec.modeId` is
        required, so the service seeds the domain's own default first — the same
        defect class Sprint 26 hit when Designer could not create a pave."""

        result = self._interpret(
            [
                ("setting.type", expected_type),
                ("setting.mode.modeId", mode_id),
            ]
        )
        setting = result.proposal.candidateJDL.setting
        assert setting.type == expected_type
        assert setting.mode is not None
        assert setting.mode.modeId == mode_id
        assert result.proposal.proposalStatus != "DESIGNER_PROPOSAL_INVALID"

    @pytest.mark.parametrize(
        "architecture", ["MARTINI", "TULIP", "OPEN_GALLERY", "PEG_HEAD"]
    )
    def test_designer_can_propose_a_head_architecture(self, architecture):
        """Sprint 23 gave these real builders and no proposable field; Sprint 27
        closes that gap."""

        result = self._interpret([("setting.headArchitecture", architecture)])
        assert result.proposal.candidateJDL.setting.headArchitecture == architecture

    def test_designer_reports_a_reserved_mode_as_unsupported(self):
        from jewelmind.designer.capability import KNOWN_UNSUPPORTED_CONCEPTS

        for concept in ("trellis", "head_trellis", "head_azure"):
            assert concept in KNOWN_UNSUPPORTED_CONCEPTS
            message = KNOWN_UNSUPPORTED_CONCEPTS[concept]
            assert "not currently supported" in message
            # The real technical reason travels with the refusal, so a user
            # learns what would have to exist rather than only that it does not.
            assert len(message) > 100

    def test_designer_no_longer_misreports_an_implemented_family(self):
        """The mistake Sprints 18, 20 and 26 each had to correct: reporting a
        real capability as unsupported."""

        from jewelmind.designer.capability import KNOWN_UNSUPPORTED_CONCEPTS

        for family in ("channel", "bar", "flush", "tension"):
            assert family not in KNOWN_UNSUPPORTED_CONCEPTS

    def test_a_relative_weight_term_is_recognised_but_never_converted(self):
        """A heavier channel names a WEIGHT.

        Turning one into a millimetre wall thickness is the professional
        judgment this project has no evidence for, so the term exists to become
        a QUESTION rather than a silent conversion.
        """

        from jewelmind.designer.capability import KNOWN_JDL_FIELD_PATHS
        from jewelmind.designer.normalizer import (
            SETTING_WEIGHT_TERMS,
            is_setting_weight_term,
        )

        assert is_setting_weight_term("heavier")
        assert is_setting_weight_term("piu delicato")
        assert not is_setting_weight_term("0.8mm")
        assert SETTING_WEIGHT_TERMS

        # No mode PARAMETER is proposable, which is what makes the term a
        # question rather than a silent conversion.
        for field in (
            "setting.mode.parameters.wallThicknessMm",
            "setting.mode.parameters.collarWidthMm",
            "setting.mode.parameters.barHeightMm",
            "setting.mode.parameters.padWidthMm",
        ):
            assert field not in KNOWN_JDL_FIELD_PATHS

    def test_the_designer_capability_set_is_read_from_the_live_registry(self):
        from jewelmind.designer.capability import current_capabilities

        capabilities = current_capabilities()
        assert set(capabilities["settingMode"]) == set(setting_mode_ids("PRIMARY"))
        # HEAD and RETENTION modes are chosen by their own fields, so offering
        # them here would be a second authority over an axis that has one.
        assert not set(capabilities["settingMode"]) & set(setting_mode_ids("HEAD"))
        assert not set(capabilities["settingMode"]) & set(
            setting_mode_ids("RETENTION")
        )

    def test_every_designer_term_names_a_mode_that_exists(self):
        assert set(designer_mode_terms().values()) == set(setting_modes())


# =========================================================================
# K. CONVERSATION (brief §31)
# =========================================================================


class TestConversation:
    """Incremental setting changes go through the existing mechanisms.

    No new `ConversationActionType` is introduced: "change the bezel to a prong
    setting" is a MODIFY of `setting.type`, which the engine already routes
    through `DesignerService.interpret()`.
    """

    @staticmethod
    def _engine(responses: dict[str, list[tuple[str, str]]]):
        from jewelmind.conversation.service import ConversationEngine
        from jewelmind.designer.provider import FakeDesignerProvider
        from jewelmind.designer.schemas import RawDesignerResponse, RawProposedValue
        from jewelmind.designer.service import DesignerService

        provider = FakeDesignerProvider(
            responses_by_text={
                text: RawDesignerResponse(
                    proposedCanonicalValues=[
                        RawProposedValue(field=field, value=value)
                        for field, value in values
                    ]
                )
                for text, values in responses.items()
            }
        )
        return ConversationEngine(designer_service=DesignerService(provider=provider))

    def test_an_incremental_family_change_preserves_everything_else(self):
        from jewelmind.conversation.schemas import ConversationTurnRequest
        from jewelmind.design_intent.schemas import DesignIntent

        text = "trasforma in channel setting"
        engine = self._engine({text: [("setting.type", "canale")]})

        current = default_definition()
        current.band.width = 3.1
        current.stone.diameter = 7.2

        result = engine.process_turn(
            ConversationTurnRequest(
                text=text,
                currentJDL=current,
                currentDesignIntent=DesignIntent(sourceText=text),
            )
        )
        proposal = result.session.activeProposal
        assert proposal is not None
        candidate = proposal.designerProposal.candidateJDL
        assert candidate.setting.type == "channel"
        # PRESERVATION, the invariant every MODIFY turn must hold: an untouched
        # field keeps its value rather than resetting to the schema default.
        assert candidate.band.width == 3.1
        assert candidate.stone.diameter == 7.2

    def test_no_new_action_type_was_needed(self):
        """Section 31: the thirteen canonical actions already cover an
        incremental setting change, and adding a fourteenth would change a
        published contract for no capability gain."""

        from jewelmind.conversation.schemas import ConversationActionType

        assert len(get_args(ConversationActionType)) == 13


# =========================================================================
# L. SPEC ARTIFACTS (brief §38)
# =========================================================================


SPEC_V3 = REPO_ROOT / "specs" / "setting" / "v3"


class TestSpecArtifacts:
    """`specs/setting/v3/` is a MIRROR of live code, re-derived on every run.

    Sprint 20 removed three hand-copied registries that had already drifted and
    had caused Designer and the Setting System to misreport real capabilities.
    These tests are what make that class of drift fail rather than survive.
    """

    @staticmethod
    def _load(name: str) -> dict:
        return json.loads((SPEC_V3 / name).read_text(encoding="utf-8"))

    def test_the_mode_registry_matches_the_live_registry(self):
        registry = self._load("setting-mode-registry.json")

        assert registry["taxonomyVersion"] == SETTING_MODE_TAXONOMY_VERSION
        assert registry["settingGeometryVersion"] == SETTING_GEOMETRY_VERSION
        assert registry["pipelineStages"] == list(SETTING_MODE_PIPELINE_STAGES)

        recorded = {entry["settingModeId"]: entry for entry in registry["modes"]}
        assert set(recorded) == set(setting_modes())
        for mode_id, entry in setting_modes().items():
            assert recorded[mode_id] == entry.model_dump(mode="json"), mode_id

        for axis in ("PRIMARY", "HEAD", "RETENTION"):
            assert registry["axes"][axis] == list(setting_mode_ids(axis))

    def test_the_reserved_list_matches_the_live_one(self):
        registry = self._load("setting-mode-registry.json")
        recorded = {
            entry["settingModeId"]: entry["reason"] for entry in registry["reserved"]
        }
        assert recorded == dict(RESERVED_SETTING_MODES)

    def test_the_recorded_parameter_fields_match_the_live_table(self):
        registry = self._load("setting-mode-registry.json")
        recorded = {
            mode_id: tuple(fields)
            for mode_id, fields in registry["parameterFieldsByMode"].items()
        }
        assert recorded == {
            mode_id: tuple(fields) for mode_id, fields in MODE_PARAMETER_FIELDS.items()
        }

    def test_the_recorded_designer_terms_match_the_live_index(self):
        registry = self._load("setting-mode-registry.json")
        assert registry["designerTerms"] == designer_mode_terms()

    def test_the_recorded_review_requirement_matches_the_live_table(self):
        registry = self._load("setting-mode-registry.json")
        recorded = {
            entry["settingType"]: entry["whatIsNotModelled"]
            for entry in registry["professionalReviewRequired"]
        }
        assert recorded == dict(PROFESSIONAL_REVIEW_REQUIRED)

    @pytest.mark.parametrize(
        ("filename", "import_path", "model_name"),
        [
            ("setting-mode-spec.schema.json", "jewelmind.setting.modes", "SettingModeSpec"),
            (
                "setting-mode-parameters.schema.json",
                "jewelmind.setting.modes",
                "SettingModeParameters",
            ),
            (
                "channel-setting-definition.schema.json",
                "jewelmind.setting.models",
                "ChannelSettingDefinition",
            ),
            (
                "bar-setting-definition.schema.json",
                "jewelmind.setting.models",
                "BarSettingDefinition",
            ),
            (
                "flush-setting-definition.schema.json",
                "jewelmind.setting.models",
                "FlushSettingDefinition",
            ),
            (
                "tension-setting-definition.schema.json",
                "jewelmind.setting.models",
                "TensionSettingDefinition",
            ),
            (
                "setting-component-provenance.schema.json",
                "jewelmind.setting.models",
                "SettingComponentProvenance",
            ),
        ],
    )
    def test_the_schemas_match_the_live_models(self, filename, import_path, model_name):
        import importlib

        model = getattr(importlib.import_module(import_path), model_name)
        recorded = self._load(filename)
        live = model.model_json_schema()
        for key, value in live.items():
            assert recorded[key] == value, (filename, key)

    def test_every_example_is_a_document_the_backend_accepts(self):
        for path in sorted((SPEC_V3 / "examples").glob("*.json")):
            recorded = json.loads(path.read_text(encoding="utf-8"))
            live = SettingSpec.model_validate(recorded)
            assert live.model_dump(mode="json") == recorded, path.name

    def test_the_fingerprint_vectors_reproduce_from_the_live_function(self):
        vectors = self._load("test-vectors/mode-fingerprint-vectors.json")
        assert vectors["taxonomyVersion"] == SETTING_MODE_TAXONOMY_VERSION
        recorded = {v["settingModeId"]: v for v in vectors["vectors"]}
        assert set(recorded) == set(setting_mode_ids("PRIMARY"))
        for mode_id, vector in recorded.items():
            entry = setting_modes()[mode_id]
            resolved = resolve_primary_mode(
                entry.settingType, "ROUND_PRONG", SettingModeSpec(modeId=mode_id)
            )
            assert vector["fingerprint"] == setting_mode_fingerprint(resolved), mode_id
            assert vector["settingType"] == entry.settingType

    def test_the_geometry_vectors_reproduce_from_a_live_run(self):
        """Structure and identity are compared exactly; VOLUMES relatively.

        A kernel-derived float is not bit-identical across OpenCascade builds
        (Sprint 5's CI proved it), so an exact volume comparison here would fail
        on a different OCCT build for a correct implementation
        (QUALITY-GOV-007/008).
        """

        vectors = self._load("test-vectors/family-geometry-vectors.json")
        recorded = {v["settingType"]: v for v in vectors["vectors"]}
        assert set(recorded) == set(get_args(SettingType))

        for setting_type, vector in recorded.items():
            model = build(setting_type)
            result = model.setting_result
            assert vector["settingModeId"] == result.settingModeId, setting_type
            assert (
                vector["settingModeFingerprint"] == result.settingModeFingerprint
            ), setting_type
            assert vector["generatedComponents"] == list(
                result.generatedComponents
            ), setting_type
            assert (
                vector["professionalReviewRequirement"]
                == result.professionalReviewRequirement
            ), setting_type
            assert vector["componentProvenance"] == [
                p.model_dump(mode="json") for p in result.componentProvenance
            ], setting_type
            for name, count in vector["componentSolidCounts"].items():
                assert count == len(model.components[name].shape.Solids()), name
            for name, volume in vector["componentVolumesMm3"].items():
                assert model.components[name].volume_mm3 == pytest.approx(
                    volume, rel=KERNEL_REL
                ), name


class TestGoldenCoverage:
    """The new Golden cases exist, are STABLE, and record honest limitations."""

    SUITE = REPO_ROOT / "goldens" / "solitaire-v1"
    CASES = (
        "ESM-001-channel-set-solitaire",
        "ESM-002-bar-set-solitaire",
        "ESM-003-flush-gypsy-solitaire",
        "ESM-004-partial-bezel-solitaire",
        "ESM-005-open-gallery-head",
        "ESM-006-tension-solitaire",
        "ESM-007-pave-shared-prong",
    )

    def test_every_case_is_in_the_manifest_as_stable(self):
        manifest = json.loads(
            (self.SUITE / "manifest.json").read_text(encoding="utf-8")
        )
        listed = {entry["goldenId"]: entry["status"] for entry in manifest["goldenIds"]}
        for golden_id in self.CASES:
            assert listed.get(golden_id) == "STABLE", golden_id

    def test_every_case_records_a_real_limitation(self):
        for golden_id in self.CASES:
            snapshot = json.loads(
                (self.SUITE / golden_id / "snapshot.json").read_text(encoding="utf-8")
            )
            limitations = snapshot["knownLimitations"]
            assert limitations, golden_id
            assert snapshot["description"], golden_id
            # A limitation is a sentence explaining what is not guaranteed, not
            # a label.
            assert all(len(item) > 80 for item in limitations), golden_id

    def test_the_tension_case_records_the_structural_limitation(self):
        snapshot = json.loads(
            (self.SUITE / "ESM-006-tension-solitaire" / "snapshot.json").read_text(
                encoding="utf-8"
            )
        )
        joined = " ".join(snapshot["knownLimitations"])
        assert "TENSION_STRUCTURAL_BEHAVIOUR_NOT_MODELLED" in joined
        assert "Professional review is required" in joined

    def test_no_case_claims_professional_validation(self):
        for golden_id in self.CASES:
            text = (self.SUITE / golden_id / "snapshot.json").read_text(
                encoding="utf-8"
            ).lower()
            for phrase in TestNoInventedThresholds.PROHIBITED:
                assert phrase not in text, (golden_id, phrase)

    def test_the_shared_prong_case_proves_sharing_reduces_the_piece_count(self):
        """The point of a shared strategy, measured rather than asserted.

        22 stones with individual retention would need 4 pieces each; the shared
        field records fewer, which is the only evidence that the shared-corner
        topology is real rather than a label.
        """

        snapshot = json.loads(
            (self.SUITE / "ESM-007-pave-shared-prong" / "snapshot.json").read_text(
                encoding="utf-8"
            )
        )
        components = {
            c["componentId"]: c for c in snapshot["geometrySnapshot"]["components"]
        }
        stones = [
            name
            for name in components
            if name.startswith("stone_reference.pave.")
        ]
        assert stones
        retention_solids = components["pave_retention"]["solidCount"]
        assert retention_solids < 4 * len(stones)
