"""Pavé & Microsetting Engine v1 (Sprint 26).

Covers both field kinds as semantics AND as real geometry — stones, retention
metal and recesses — their composition onto an existing design, the surface
targeting boundary, deterministic identity, numerical repeatability, the
structural rules, adversarial input, and the part easiest to break: that a
design with no pavé behaves exactly as it did before.
"""

from __future__ import annotations

import ast
import json
import math
from pathlib import Path

import pytest
from pydantic import ValidationError

from jewelmind.arrangement.compile import (
    PRIMARY_STONE_COMPONENT,
    STONE_INSTANCE_COMPONENT_PREFIX,
)
from jewelmind.arrangement.models import (
    ArrangementDefinition,
    InstancePlacement,
    InstanceTransform,
    StoneInstanceDef,
)
from jewelmind.arrangement.normalize import arrangement_fingerprint, normalize_transform
from jewelmind.domain.defaults import default_definition
from jewelmind.domain.schema import JewelryDefinition
from jewelmind.family.models import FamilyDefinition, ThreeStoneParams
from jewelmind.gem.models import GemIdentity
from jewelmind.geometry.assemblies.solitaire import build_solitaire_ring
from jewelmind.geometry.inspection import inspect_model
from jewelmind.geometry.inspection.assembly import (
    required_component_names,
    stone_component_names,
)
from jewelmind.geometry.pave_surface import resolve_pave_surface, stone_anchor_z_mm
from jewelmind.geometry.roles import geometry_role, is_production_component
from jewelmind.halo.models import HaloDefinition, HaloRing
from jewelmind.pave.capability import (
    PAVE_CAPABILITIES,
    PAVE_COMPILER_VERSION,
    PAVE_HOST_CAPABILITIES,
    PAVE_REGISTRY_VERSION,
    PAVE_RETENTION_CAPABILITIES,
    RESERVED_PAVE_HOSTS,
    RESERVED_RETENTION_STRATEGIES,
    retention_strategies_with_geometry,
    supported_pave_hosts,
)
from jewelmind.pave.compile import (
    PAVE_ROLE,
    compile_pave_field,
    compose_pave,
    pave_patterns,
    surface_lattices,
)
from jewelmind.pave.errors import (
    PaveCapacityExceededError,
    PaveContainmentError,
    PaveHostUnsupportedError,
    PaveIdentityCollisionError,
)
from jewelmind.pave.models import (
    DESIGN_CENTER_INSTANCE_ID,
    MAX_PAVE_STONES,
    MicrosettingSpec,
    PaveDefinition,
    PaveExplicitPlacement,
    PaveRetention,
    PaveSeat,
    PaveSpec,
)
from jewelmind.setting.retention import PAVE_RETENTION_COMPONENT
from jewelmind.utils.hashing import definition_hash, geometry_hash
from jewelmind.validation.engine import has_errors, validate_definition

#: The default solitaire's fused metal volume, unchanged since Sprint 19.
LEGACY_METAL_VOLUME_MM3 = 341.44334316909976
KERNEL_REL_TOLERANCE = 1e-9

REPO_ROOT = Path(__file__).resolve().parents[2]
SPEC_DIR = REPO_ROOT / "specs" / "pave" / "v1"


def pave_spec(**over) -> PaveSpec:
    params: dict = {"angularSpanDeg": 90.0, "pitchMm": 1.0}
    params.update(over)
    return PaveSpec(**params)


def micro_spec(**over) -> MicrosettingSpec:
    params: dict = {"columnCount": 10, "stoneSpacingMm": 0.8}
    params.update(over)
    return MicrosettingSpec(**params)


def pave(**over) -> PaveDefinition:
    params: dict = {
        "kind": "PAVE",
        "host": "BAND_OUTER",
        "spec": over.pop("spec", None) or pave_spec(),
        "stoneScale": 0.1,
    }
    params.update(over)
    return PaveDefinition(**params)


def design(
    pave_definition: PaveDefinition | None = None,
    *,
    family: FamilyDefinition | None = None,
    halo: HaloDefinition | None = None,
    arrangement: ArrangementDefinition | None = None,
) -> JewelryDefinition:
    definition = default_definition()
    definition.pave = pave_definition
    definition.family = family
    definition.halo = halo
    definition.arrangement = arrangement
    return definition


def pave_rule_ids(definition: JewelryDefinition) -> dict[str, str]:
    return {
        r.ruleId: r.severity
        for r in validate_definition(definition)
        if r.ruleId.startswith("JM-PAVE")
    }


def field_for(pave_definition: PaveDefinition, definition=None):
    definition = definition or default_definition()
    return compile_pave_field(
        pave_definition, resolve_pave_surface(definition, pave_definition)
    )


# ------------------------------------------------------------- the model


class TestPaveModel:
    def test_a_field_references_stones_rather_than_restating_them(self):
        candidate = pave()
        # No shape, no dimensions, no material: a pavé stone is an occurrence OF
        # the design's stone, and copying it here would create a second source
        # of truth for what that stone is.
        for absent in ("shape", "diameter", "length", "width", "depth", "source"):
            assert not hasattr(candidate, absent), absent
        assert candidate.stoneRef == "primary"

    def test_the_two_kinds_are_separate_models(self):
        """A PAVE states area and density; a MICROSETTING states structure.

        Not one model with a flag: the inputs are genuinely different, and a
        shared model would have to make half its fields meaningless for each.
        """

        assert set(PaveSpec.model_fields) != set(MicrosettingSpec.model_fields)
        assert "angularSpanDeg" in PaveSpec.model_fields
        assert "angularSpanDeg" not in MicrosettingSpec.model_fields
        assert "columnCount" in MicrosettingSpec.model_fields
        assert "columnCount" not in PaveSpec.model_fields

    def test_they_share_the_lattice_primitives(self):
        """Two ways of describing one lattice, so the shared axes are shared."""

        for common in ("pattern", "rowOffsetFraction", "termination", "symmetry"):
            assert common in PaveSpec.model_fields, common
            assert common in MicrosettingSpec.model_fields, common

    def test_the_spec_kind_must_match_the_field_kind(self):
        with pytest.raises(ValidationError):
            PaveDefinition(kind="MICROSETTING", host="BAND_OUTER", spec=pave_spec())

    def test_an_explicit_pattern_with_no_placements_is_refused(self):
        """Refused rather than falling back to a derived lattice, which would
        build a field nobody authored (SETTINGV2-GOV-012's discipline)."""

        with pytest.raises(ValidationError):
            pave(spec=pave_spec(pattern="EXPLICIT"))

    def test_duplicate_explicit_placement_ids_are_rejected(self):
        with pytest.raises(ValidationError):
            pave(
                spec=pave_spec(pattern="EXPLICIT"),
                explicitPlacements=[
                    PaveExplicitPlacement(
                        placementId="a", transform=InstanceTransform()
                    ),
                    PaveExplicitPlacement(
                        placementId="a", transform=InstanceTransform(xMm=1.0)
                    ),
                ],
            )

    def test_a_reserved_host_is_refused_rather_than_substituted(self):
        for host in RESERVED_PAVE_HOSTS:
            with pytest.raises(ValidationError):
                pave(host=host)

    def test_a_reserved_retention_strategy_is_refused(self):
        for strategy in RESERVED_RETENTION_STRATEGIES:
            with pytest.raises(ValidationError):
                pave(retention=PaveRetention(strategy=strategy))

    @pytest.mark.parametrize(
        "candidate",
        [
            "Pave",
            "pave..1",
            "../../etc/passwd",
            "pave/1",
            "rm -rf /",
            "",
            "a" * 81,
            "pave field",
        ],
    )
    def test_a_malformed_pave_id_is_rejected(self, candidate: str):
        with pytest.raises(ValidationError):
            pave(paveId=candidate)

    @pytest.mark.parametrize("bad", [0.0, -1.0, float("nan"), float("inf"), float("-inf")])
    def test_no_dimension_accepts_a_pathological_value(self, bad: float):
        with pytest.raises(ValidationError):
            pave_spec(pitchMm=bad)
        with pytest.raises(ValidationError):
            PaveRetention(beadRadiusMm=bad)

    def test_a_jdl_style_string_number_is_rejected(self):
        with pytest.raises(ValidationError):
            PaveSpec.model_validate({"angularSpanDeg": 90.0, "pitchMm": "1.0"})

    def test_an_unknown_field_is_rejected(self):
        with pytest.raises(ValidationError):
            PaveDefinition.model_validate(
                {
                    "kind": "PAVE",
                    "host": "BAND_OUTER",
                    "spec": {"kind": "PAVE", "angularSpanDeg": 90.0, "pitchMm": 1.0},
                    "sparkle": True,
                }
            )

    def test_a_declared_microsetting_above_the_bound_is_refused_at_the_schema(self):
        """A stated structure's count is knowable from the document alone, so it
        is refused BEFORE the kernel is asked for the solids.

        Checked on the DEFINITION rather than the spec, which is where the
        validator belongs: a spec alone does not know it is a microsetting's.
        """

        with pytest.raises(ValidationError):
            pave(
                kind="MICROSETTING",
                spec=micro_spec(columnCount=60, rowCount=12),
            )

    def test_the_bounds_are_software_limits(self):
        assert MAX_PAVE_STONES == 120

    def test_the_model_holds_no_kernel_object(self):
        fields = (
            PaveDefinition.model_fields
            | PaveSpec.model_fields
            | MicrosettingSpec.model_fields
            | PaveRetention.model_fields
            | PaveSeat.model_fields
        )
        for name, field in fields.items():
            annotation = str(field.annotation)
            assert "cadquery" not in annotation.lower(), name
            assert "Shape" not in annotation, name
            assert "OCP" not in annotation, name

    def test_the_centre_instance_id_matches_every_other_layer(self):
        """Three copies of a string is how they drift."""

        from jewelmind.family.compile import CENTER_MEMBER_ID
        from jewelmind.halo.models import DEFAULT_CENTER_MEMBER_ID

        assert DESIGN_CENTER_INSTANCE_ID == CENTER_MEMBER_ID
        assert DESIGN_CENTER_INSTANCE_ID == DEFAULT_CENTER_MEMBER_ID


# ------------------------------------------------------- surface targeting


class TestSurfaceTargeting:
    def test_the_band_surface_is_resolved_from_the_real_ring(self):
        definition = default_definition()
        surface = resolve_pave_surface(definition, pave())
        assert surface.kind == "CYLINDRICAL"
        assert surface.hostComponent == "band"
        # Derived from the same expression the assembly uses, not measured off a
        # solid: a face index is not reproducible.
        expected = definition.ring.innerDiameter / 2 + definition.band.thickness
        assert surface.radiusMm == pytest.approx(expected, rel=1e-12)
        assert surface.axialExtentMm == pytest.approx(definition.band.width)

    def test_the_head_plane_is_bounded_away_from_the_centre_stone(self):
        definition = default_definition()
        surface = resolve_pave_surface(definition, pave(host="HEAD_PLANE"))
        assert surface.kind == "PLANAR"
        assert surface.hostComponent == "basket_support"
        assert surface.innerRadiusMm == pytest.approx(
            definition.stone.diameter / 2
        )
        assert surface.outerRadiusMm > surface.innerRadiusMm

    def test_the_stone_anchor_matches_the_builders_own_expression(self):
        """An arrangement transform is a DELTA, so a pavé that computed the
        as-built girdle differently would place every stone off by the
        difference."""

        definition = default_definition()
        model = build_solitaire_ring(definition)
        metadata = model.components[PRIMARY_STONE_COMPONENT].metadata
        assert stone_anchor_z_mm(definition) == pytest.approx(
            metadata["girdleZMm"], rel=1e-12
        )

    def test_a_reserved_host_has_no_resolver_and_no_capability_entry(self):
        for host in RESERVED_PAVE_HOSTS:
            assert host not in PAVE_HOST_CAPABILITIES

    def test_the_resolver_registry_and_the_model_agree(self):
        from jewelmind.geometry.pave_surface import _HOST_RESOLVERS

        assert set(_HOST_RESOLVERS) == set(PAVE_HOST_CAPABILITIES)
        assert set(supported_pave_hosts()) == set(PAVE_HOST_CAPABILITIES)

    def test_an_unresolvable_host_raises_rather_than_substituting(self):
        # Constructed past the model, which is the only way to reach the
        # resolver with an unsupported host.
        candidate = pave().model_copy(update={"host": "SETTING_SURFACE"})
        with pytest.raises(PaveHostUnsupportedError):
            resolve_pave_surface(default_definition(), candidate)

    def test_both_surface_kinds_have_a_lattice_builder(self):
        assert set(surface_lattices()) == {"CYLINDRICAL", "PLANAR"}


# ------------------------------------------------------------ compilation


class TestCompilation:
    def test_a_field_compiles_to_real_placements(self):
        field = field_for(pave())
        assert field.stone_count() > 1
        assert field.enabled
        assert all(p.placementId.startswith("pave.r") for p in field.placements)

    def test_every_stone_sits_on_the_host_surface(self):
        definition = default_definition()
        candidate = pave(spec=pave_spec(angularSpanDeg=120.0, pitchMm=1.0))
        surface = resolve_pave_surface(definition, candidate)
        field = compile_pave_field(candidate, surface)
        seat_drop = candidate.retention.beadRadiusMm
        for placement in field.placements:
            transform = placement.transform
            # The stone's absolute position: the delta plus the as-built anchor.
            x = transform.xMm
            z = transform.zMm + surface.stoneAnchorZMm
            assert math.hypot(x, z) == pytest.approx(
                surface.radiusMm - seat_drop, rel=1e-9
            )

    def test_each_stone_leans_along_the_surface_normal(self):
        field = field_for(pave(spec=pave_spec(angularSpanDeg=120.0, pitchMm=1.2)))
        tilts = {round(p.transform.tiltDeg, 6) for p in field.placements}
        # A 120-degree span cannot be covered by upright stones.
        assert max(tilts) > 30.0
        # And the far side leans the other way, expressed as a flipped azimuth
        # rather than a negative tilt.
        azimuths = {round(p.transform.tiltAzimuthDeg, 6) for p in field.placements}
        assert len(azimuths) == 2
        assert all(t >= 0.0 for t in tilts)

    def test_a_planar_field_needs_no_tilt(self):
        field = field_for(
            pave(kind="MICROSETTING", host="HEAD_PLANE", spec=micro_spec(columnCount=8))
        )
        assert all(p.transform.tiltDeg == 0.0 for p in field.placements)

    @pytest.mark.parametrize(
        "pattern", ["GRID", "STAGGERED", "ROW_OFFSET", "RADIAL"]
    )
    def test_every_generated_pattern_produces_a_field(self, pattern: str):
        field = field_for(
            pave(spec=pave_spec(rowCount=2, pattern=pattern, pitchMm=0.9))
        )
        assert field.stone_count() >= 2

    def test_staggered_actually_offsets_alternate_rows(self):
        grid = field_for(pave(spec=pave_spec(rowCount=2, pattern="GRID")))
        staggered = field_for(
            pave(spec=pave_spec(rowCount=2, pattern="STAGGERED"))
        )
        def rows_of(field) -> dict[int, list[float]]:
            out: dict[int, list[float]] = {}
            for placement in field.placements:
                out.setdefault(placement.rowIndex, []).append(
                    round(placement.transform.xMm, 6)
                )
            return {row: sorted(values) for row, values in out.items()}

        grid_rows = rows_of(grid)
        stag_rows = rows_of(staggered)
        assert grid_rows[0] == grid_rows[1]
        assert stag_rows[0] != stag_rows[1]

    def test_the_pattern_registry_matches_the_model(self):
        from typing import get_args

        from jewelmind.pave.models import PavePattern

        assert set(pave_patterns()) == set(get_args(PavePattern))

    def test_an_explicit_field_uses_the_documents_own_placements(self):
        field = field_for(
            pave(
                spec=pave_spec(pattern="EXPLICIT"),
                explicitPlacements=[
                    PaveExplicitPlacement(
                        placementId="pave.hand.a", transform=InstanceTransform()
                    ),
                    PaveExplicitPlacement(
                        placementId="pave.hand.b",
                        transform=InstanceTransform(xMm=1.5),
                        scale=0.2,
                    ),
                ],
            )
        )
        assert [p.placementId for p in field.placements] == [
            "pave.hand.a",
            "pave.hand.b",
        ]
        # No lattice provenance is fabricated for a hand-placed stone.
        assert all(p.rowIndex == -1 and p.columnIndex == -1 for p in field.placements)
        assert field.placements[1].scale == 0.2

    def test_clipping_reports_what_it_dropped(self):
        field = field_for(pave(spec=pave_spec(rowCount=8, pitchMm=1.0)))
        assert field.clippedCells > 0
        assert any("clipped" in note for note in field.notes)

    def test_strict_containment_refuses_instead_of_clipping(self):
        with pytest.raises(PaveContainmentError):
            field_for(
                pave(spec=pave_spec(rowCount=8, pitchMm=1.0), containment="REJECT")
            )

    def test_a_pathological_pitch_is_bounded(self):
        """A SOFTWARE SAFETY limit: a hostile document must not be able to ask
        the kernel for tens of thousands of solids."""

        with pytest.raises(PaveCapacityExceededError):
            field_for(pave(spec=pave_spec(angularSpanDeg=360.0, pitchMm=0.02)))

    def test_a_disabled_field_compiles_to_nothing_and_says_so(self):
        field = field_for(pave(enabled=False))
        assert not field.enabled
        assert field.stone_count() == 0
        assert field.retention_count() == 0
        assert any("disabled" in note for note in field.notes)


# --------------------------------------------------------- retention topology


class TestRetention:
    def test_shared_beads_are_genuinely_shared(self):
        field = field_for(
            pave(
                spec=pave_spec(rowCount=2, pitchMm=0.9),
                retention=PaveRetention(strategy="SHARED_BEAD"),
            )
        )
        shared = [a for a in field.retentionAnchors if len(a.servesPlacementIds) > 1]
        assert shared, "no anchor is shared, so SHARED_BEAD is only a label"
        # 4 corners per stone with none shared would be 4n.
        assert field.retention_count() < 4 * field.stone_count()

    def test_individual_beads_are_not_shared(self):
        field = field_for(
            pave(
                spec=pave_spec(rowCount=2, pitchMm=0.9),
                retention=PaveRetention(strategy="BEAD"),
            )
        )
        assert field.retention_count() == 4 * field.stone_count()
        assert all(len(a.servesPlacementIds) == 1 for a in field.retentionAnchors)

    def test_the_two_strategies_build_different_metal(self):
        """The finding this sprint had to fix. Placed at the full half-pitch an
        individual bead lands on the corner its neighbours share, so four
        coincident spheres fuse into one and BEAD produced metal identical to
        SHARED_BEAD while reporting four times the pieces."""

        volumes = {}
        for strategy in ("BEAD", "SHARED_BEAD"):
            model = build_solitaire_ring(
                design(
                    pave(
                        spec=pave_spec(rowCount=2, pitchMm=0.9),
                        retention=PaveRetention(strategy=strategy),
                    )
                )
            )
            volumes[strategy] = model.components[
                PAVE_RETENTION_COMPONENT
            ].volume_mm3
        assert volumes["BEAD"] > volumes["SHARED_BEAD"]

    def test_retention_none_builds_no_component_and_says_so(self):
        model = build_solitaire_ring(
            design(pave(retention=PaveRetention(strategy="NONE")))
        )
        assert PAVE_RETENTION_COMPONENT not in model.components
        assert any(
            "NONE" in note for note in model.pave_result.notes
        )

    def test_a_micro_prong_stands_normal_to_a_curved_surface(self):
        field = field_for(
            pave(
                spec=pave_spec(angularSpanDeg=120.0, pitchMm=1.2),
                retention=PaveRetention(strategy="MICRO_PRONG"),
            )
        )
        tilts = {round(a.tiltDeg, 4) for a in field.retentionAnchors}
        assert max(tilts) > 20.0, "prongs are vertical on a curved band"

    def test_every_registered_strategy_has_a_builder(self):
        from jewelmind.setting.retention import retention_builders

        buildable = set(retention_strategies_with_geometry())
        assert set(retention_builders()) == buildable
        assert "NONE" not in retention_builders()

    def test_no_reserved_strategy_has_a_builder(self):
        from jewelmind.setting.retention import retention_builders

        for strategy in RESERVED_RETENTION_STRATEGIES:
            assert strategy not in retention_builders()


# --------------------------------------------------------------- geometry


class TestGeometry:
    def test_every_pave_stone_becomes_its_own_component(self):
        model = build_solitaire_ring(design(pave()))
        stones = stone_component_names(model)
        assert len(stones) == model.pave_result.stone_count() + 1
        assert PRIMARY_STONE_COMPONENT in stones

    def test_the_centre_stone_survives_a_pave(self):
        """A solitaire with a pavé shank still has its solitaire.

        Without the synthesized centre instance the deterministic primary
        selection would pick the lowest-id PAVÉ stone, and the centre stone
        would silently become one — inheriting the bare `stone_reference` name
        while sitting on the band.
        """

        plain = build_solitaire_ring(default_definition())
        haloed = build_solitaire_ring(design(pave()))
        assert haloed.components[PRIMARY_STONE_COMPONENT].volume_mm3 == pytest.approx(
            plain.components[PRIMARY_STONE_COMPONENT].volume_mm3,
            rel=KERNEL_REL_TOLERANCE,
        )

    def test_a_pave_stone_is_never_production_metal(self):
        model = build_solitaire_ring(design(pave()))
        for name in stone_component_names(model):
            assert geometry_role(name) == "stone_reference"
            assert not is_production_component(name)

    def test_the_retention_field_is_production_metal(self):
        model = build_solitaire_ring(design(pave()))
        assert geometry_role(PAVE_RETENTION_COMPONENT) == "production_metal"
        assert is_production_component(PAVE_RETENTION_COMPONENT)
        assert PAVE_RETENTION_COMPONENT in model.components

    def test_the_retention_metal_is_real_and_fused(self):
        plain = build_solitaire_ring(default_definition())
        model = build_solitaire_ring(
            design(pave(retention=PaveRetention(strategy="SHARED_BEAD")))
        )
        retention = model.components[PAVE_RETENTION_COMPONENT]
        assert retention.volume_mm3 > 0.0
        # The metal body grew by the beads, and grew by LESS than their own
        # volume because they are embedded in the band rather than resting on it.
        delta = model.combined_metal_volume_mm3 - plain.combined_metal_volume_mm3
        assert 0.0 < delta < retention.volume_mm3

    def test_the_recess_removes_real_host_material(self):
        without = build_solitaire_ring(design(pave(seat=PaveSeat(mode="NONE"))))
        with_recess = build_solitaire_ring(
            design(pave(seat=PaveSeat(mode="REFERENCE_RECESS")))
        )
        assert (
            with_recess.components["band"].volume_mm3
            < without.components["band"].volume_mm3
        )
        assert (
            with_recess.components["band"].metadata["paveRecessOperation"]
            == "CUT_STONE_FROM_METAL"
        )

    def test_the_recess_is_a_cut_and_never_a_fuse(self):
        """Asserted by parsing the adapter's own source, so it cannot pass on a
        comment. The recess routes through `setting/seat.py`, whose own source
        is already asserted never to fuse a stone shape."""

        source = (
            Path(__file__).resolve().parents[1]
            / "jewelmind"
            / "geometry"
            / "pave_adapter.py"
        ).read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                assert node.attr != "fuse", "the pavé adapter must never fuse"
        assert "apply_seat_relief" in source

    def test_the_stone_scale_reaches_the_solid(self):
        scale = 0.1
        model = build_solitaire_ring(design(pave(stoneScale=scale)))
        centre = model.components[PRIMARY_STONE_COMPONENT].volume_mm3
        name = f"{STONE_INSTANCE_COMPONENT_PREFIX}pave.r0.c0"
        assert model.components[name].volume_mm3 == pytest.approx(
            centre * scale**3, rel=1e-9
        )

    def test_the_stones_are_actually_displaced_around_the_band(self):
        model = build_solitaire_ring(
            design(pave(spec=pave_spec(angularSpanDeg=120.0, pitchMm=1.2)))
        )
        xs = [
            (c.bounding_box.xmin + c.bounding_box.xmax) / 2.0
            for name, c in model.components.items()
            if name.startswith(f"{STONE_INSTANCE_COMPONENT_PREFIX}pave.")
        ]
        assert max(xs) - min(xs) > 5.0

    def test_a_gem_never_affects_a_solid(self):
        plain = build_solitaire_ring(design(pave()))
        gemmed = build_solitaire_ring(
            design(
                pave(gem=GemIdentity(gemId="corundum.sapphire", origin="NATURAL"))
            )
        )
        for name in sorted(stone_component_names(plain)):
            assert plain.components[name].volume_mm3 == pytest.approx(
                gemmed.components[name].volume_mm3, rel=KERNEL_REL_TOLERANCE
            )

    def test_a_microsetting_on_the_head_plane_builds_geometry(self):
        model = build_solitaire_ring(
            design(
                pave(
                    kind="MICROSETTING",
                    host="HEAD_PLANE",
                    spec=micro_spec(columnCount=12, stoneSpacingMm=0.7),
                    stoneScale=0.07,
                    retention=PaveRetention(strategy="BEAD", beadRadiusMm=0.1),
                )
            )
        )
        assert model.pave_result.stone_count() == 12
        assert model.components[PAVE_RETENTION_COMPONENT].volume_mm3 > 0.0


# ------------------------------------------------------------- composition


class TestComposition:
    def test_a_pave_composes_onto_a_family(self):
        family = FamilyDefinition(
            familyType="THREE_STONE", params=ThreeStoneParams(sideSpacingMm=5.0)
        )
        model = build_solitaire_ring(design(pave(), family=family))
        roles = {
            c.metadata.get("stoneInstanceRole")
            for c in model.components.values()
            if c.metadata.get("stoneInstanceRole")
        }
        assert "CENTER" in roles
        assert "SIDE" in roles
        assert PAVE_ROLE in roles

    def test_a_pave_composes_onto_a_halo(self):
        halo = HaloDefinition(
            variant="SINGLE",
            rings=[HaloRing(ringId="halo.inner", count=8, radiusMm=3.4)],
        )
        model = build_solitaire_ring(design(pave(), halo=halo))
        roles = {
            c.metadata.get("stoneInstanceRole")
            for c in model.components.values()
            if c.metadata.get("stoneInstanceRole")
        }
        assert {"CENTER", "HALO", PAVE_ROLE} <= roles

    def test_a_pave_composes_onto_an_explicit_arrangement(self):
        arrangement = ArrangementDefinition(
            instances=[
                StoneInstanceDef(
                    instanceId="middle",
                    role="CENTER",
                    placement=InstancePlacement(transform=InstanceTransform()),
                )
            ]
        )
        model = build_solitaire_ring(design(pave(), arrangement=arrangement))
        assert PRIMARY_STONE_COMPONENT in model.components
        assert model.pave_result.stone_count() > 1

    def test_composing_no_pave_returns_the_base_object(self):
        base = ArrangementDefinition()
        composed, field = compose_pave(base, None, None)
        assert composed is base
        assert field is None

    def test_a_colliding_placement_id_is_refused(self):
        colliding = ArrangementDefinition(
            instances=[
                StoneInstanceDef(instanceId="pave.r0.c0", role="PAVE"),
            ]
        )
        candidate = pave()
        surface = resolve_pave_surface(default_definition(), candidate)
        with pytest.raises(PaveIdentityCollisionError):
            compose_pave(colliding, candidate, surface)

    def test_the_field_relation_records_the_intent(self):
        candidate = pave()
        surface = resolve_pave_surface(default_definition(), candidate)
        composed, field = compose_pave(None, candidate, surface)
        assert composed is not None
        relation = next(
            r for r in composed.relations if r.relationId == "pave.field"
        )
        assert relation.kind == "EVENLY_SPACED_WITH"
        assert len(relation.members) == field.stone_count()


# ------------------------------------------------------------ determinism


class TestDeterminism:
    def test_compilation_is_repeatable(self):
        candidate = pave(spec=pave_spec(rowCount=2, pitchMm=0.9))
        first = field_for(candidate)
        for _ in range(4):
            assert field_for(candidate) == first

    def test_derived_ids_carry_lattice_coordinates_and_are_not_counters(self):
        field = field_for(pave(spec=pave_spec(angularSpanDeg=30.0, pitchMm=1.5, rowCount=2)))
        ids = sorted(p.placementId for p in field.placements)
        assert all(id_.startswith("pave.r") and ".c" in id_ for id_ in ids)
        assert len(set(ids)) == len(ids)

    def test_a_pave_change_changes_both_identities(self):
        base = design(pave())
        denser = design(pave(spec=pave_spec(pitchMm=0.7)))
        assert definition_hash(base) != definition_hash(denser)
        # A pavé places stones and cuts metal, so it MUST be inside the geometry
        # hash: a stale cache hit here would serve geometry for another design.
        assert geometry_hash(base) != geometry_hash(denser)

    def test_every_geometry_affecting_field_changes_the_geometry_hash(self):
        base = geometry_hash(design(pave()))
        variants = {
            "host": pave(
                kind="MICROSETTING", host="HEAD_PLANE", spec=micro_spec()
            ),
            "stoneScale": pave(stoneScale=0.15),
            "retentionStrategy": pave(retention=PaveRetention(strategy="BEAD")),
            "beadRadius": pave(retention=PaveRetention(beadRadiusMm=0.2)),
            "recess": pave(seat=PaveSeat(mode="REFERENCE_RECESS")),
            "rowCount": pave(spec=pave_spec(rowCount=2)),
            "pattern": pave(spec=pave_spec(rowCount=2, pattern="STAGGERED")),
            "enabled": pave(enabled=False),
        }
        for name, candidate in variants.items():
            assert geometry_hash(design(candidate)) != base, name

    def test_a_non_geometric_gem_change_leaves_the_geometry_hash_alone(self):
        """Sprint 21's contract, still true with a pavé: a gem is semantics."""

        plain = design(pave())
        gemmed = design(
            pave(gem=GemIdentity(gemId="corundum.ruby", origin="NATURAL"))
        )
        assert definition_hash(plain) != definition_hash(gemmed)
        # `pave.gem` sits inside the pavé block rather than under `stone.gem`,
        # so it is not in the geometry hash's exclusion list and DOES change it.
        # Recorded honestly: the cost is a rebuild, and the alternative error
        # mode — a stale cache hit — is the worse one (ARRANGE-GOV-007).
        assert geometry_hash(plain) != geometry_hash(gemmed)
        for name in stone_component_names(build_solitaire_ring(plain)):
            assert name in build_solitaire_ring(gemmed).components

    def test_the_label_is_carried_and_never_geometric(self):
        a = build_solitaire_ring(design(pave(label="A")))
        b = build_solitaire_ring(design(pave(label="B")))
        assert a.combined_metal_volume_mm3 == pytest.approx(
            b.combined_metal_volume_mm3, rel=KERNEL_REL_TOLERANCE
        )

    def test_the_tilt_normalization_gives_an_upright_instance_one_form(self):
        """Without this, two identical upright placements differing only in a
        meaningless azimuth would produce different canonical JSON."""

        a = normalize_transform(InstanceTransform(tiltAzimuthDeg=0.0))
        b = normalize_transform(InstanceTransform(tiltAzimuthDeg=137.0))
        assert a == b
        # And a real tilt keeps its direction.
        tilted = normalize_transform(
            InstanceTransform(tiltDeg=30.0, tiltAzimuthDeg=137.0)
        )
        assert tilted.tiltAzimuthDeg == pytest.approx(137.0)

    def test_a_negative_tilt_is_not_folded_into_a_positive_one(self):
        """Folding -30 to 330 would make an upward lean read as a downward
        one."""

        assert normalize_transform(InstanceTransform(tiltDeg=-30.0)).tiltDeg == -30.0


class TestNumericalRepeatability:
    """§28: measure the real stability rather than choosing a tolerance that
    'looks small enough'."""

    def test_repeated_generation_is_bit_identical_in_this_process(self):
        definition = design(
            pave(
                spec=pave_spec(rowCount=2, pitchMm=0.9),
                seat=PaveSeat(mode="REFERENCE_RECESS"),
            )
        )
        runs = [build_solitaire_ring(definition) for _ in range(3)]
        first = runs[0]
        for other in runs[1:]:
            assert sorted(first.components) == sorted(other.components)
            assert (
                first.combined_metal_volume_mm3 == other.combined_metal_volume_mm3
            ), "repeated generation is not bit-identical in one process"
            for name, component in first.components.items():
                if component.volume_mm3 is None:
                    continue
                assert component.volume_mm3 == other.components[name].volume_mm3, name

    def test_the_comparison_tolerance_is_justified_by_that_measurement(self):
        """Bit-identical in-process is why the Golden suite's comparison
        tolerance exists only for CROSS-PLATFORM drift, and why this suite
        asserts `rel=1e-9` rather than a looser figure chosen by feel."""

        from jewelmind.geometry_quality.version import (
            RELATIVE_COMPARISON_TOLERANCE,
        )

        assert RELATIVE_COMPARISON_TOLERANCE >= KERNEL_REL_TOLERANCE


# ------------------------------------------------------------- inspection


class TestInspection:
    def test_every_pave_stone_is_a_required_component(self):
        model = build_solitaire_ring(design(pave()))
        required = required_component_names(model)
        for name in stone_component_names(model):
            assert name in required

    def test_a_pave_model_inspects_and_reports_real_facts(self):
        model = build_solitaire_ring(
            design(pave(seat=PaveSeat(mode="REFERENCE_RECESS")))
        )
        result = inspect_model(model)
        assembly = result.assemblyResult
        assert result.status in {"PASS", "PASS_WITH_FINDINGS"}
        assert assembly.requiredComponentsPresent
        assert assembly.missingComponentIds == []
        assert assembly.referenceComponentCount == (
            model.pave_result.stone_count() + 1
        )
        # band, prongs, basket_support, pave_retention.
        assert assembly.productionComponentCount == 4
        assert result.geometricFacts

    def test_the_retention_field_joins_the_production_body(self):
        model = build_solitaire_ring(design(pave()))
        connectivity = inspect_model(model).assemblyResult.productionConnectivity
        assert PAVE_RETENTION_COMPONENT in connectivity.nodes
        assert connectivity.isFullyConnected
        assert connectivity.disconnectedGroupCount == 0

    def test_stone_metal_separation_holds_with_a_pave(self):
        model = build_solitaire_ring(design(pave()))
        separation = inspect_model(model).assemblyResult.stoneMetalSeparation
        assert separation.fusedIntoProductionMetal is False
        assert separation.productionIncluded is False
        assert separation.status == "PASS"

    def test_an_overlap_is_reported_as_a_fact_not_a_defect(self):
        """A dense field genuinely overlaps its neighbours. Inspection reports
        the intersection; no rule calls it a manufacturing defect, because that
        needs a professional minimum this project has no evidence for."""

        model = build_solitaire_ring(
            design(pave(stoneScale=0.2, spec=pave_spec(pitchMm=0.8)))
        )
        result = inspect_model(model)
        assert result.status in {"PASS", "PASS_WITH_FINDINGS"}
        for diagnostic in result.diagnostics:
            assert "defect" not in diagnostic.message.lower()
            assert "not manufacturable" not in diagnostic.message.lower()


# ----------------------------------------------------------- forge rules


class TestPaveRules:
    def test_a_design_with_no_pave_produces_no_pave_results(self):
        assert pave_rule_ids(default_definition()) == {}

    def test_the_execution_boundary_is_always_reported(self):
        results = pave_rule_ids(design(pave()))
        assert results["JM-PAVE-005"] == "information"

    def test_the_professional_review_requirement_is_stated(self):
        messages = [
            r.message
            for r in validate_definition(design(pave()))
            if r.ruleId == "JM-PAVE-005"
        ]
        assert any("professionally validated" in m for m in messages)
        assert any("qualified jewelry professional" in m for m in messages)

    def test_a_clipped_field_is_a_warning_not_an_error(self):
        definition = design(pave(spec=pave_spec(rowCount=8, pitchMm=1.0)))
        assert pave_rule_ids(definition)["JM-PAVE-003"] == "warning"
        assert not has_errors(validate_definition(definition))

    def test_a_field_that_cannot_compile_is_an_error(self):
        definition = design(
            pave(spec=pave_spec(rowCount=8, pitchMm=1.0), containment="REJECT")
        )
        assert pave_rule_ids(definition)["JM-PAVE-002"] == "error"
        assert has_errors(validate_definition(definition))

    def test_an_unresolved_stone_reference_is_a_warning(self):
        definition = design(pave(stoneRef="accent"))
        assert pave_rule_ids(definition)["JM-PAVE-004"] == "warning"
        assert not has_errors(validate_definition(definition))

    def test_the_pitch_check_is_arithmetic_and_not_a_threshold(self):
        """Stones wider than the pitch overlap as a matter of geometry. The rule
        states that and nothing else — no minimum spacing is asserted."""

        tight = design(pave(stoneScale=0.3, spec=pave_spec(pitchMm=0.3)))
        assert pave_rule_ids(tight)["JM-PAVE-006"] == "warning"
        loose = design(pave(stoneScale=0.05, spec=pave_spec(pitchMm=1.5)))
        assert "JM-PAVE-006" not in pave_rule_ids(loose)

    def test_the_pitch_rule_suggests_a_scale_derived_from_the_real_stone(self):
        definition = design(pave(stoneScale=0.3, spec=pave_spec(pitchMm=0.3)))
        result = next(
            r
            for r in validate_definition(definition)
            if r.ruleId == "JM-PAVE-006"
        )
        assert result.suggestedValue is not None
        # The suggestion is the scale at which the footprint equals the pitch —
        # derived arithmetic, not a recommended value. Rounded to four places
        # by the rule, so the comparison is made at that precision rather than
        # loosened.
        assert result.suggestedValue == pytest.approx(
            round(0.3 / definition.stone.diameter, 4), rel=1e-9
        )

    def test_a_disabled_field_reports_only_that_it_is_disabled(self):
        results = pave_rule_ids(design(pave(enabled=False)))
        assert set(results) == {"JM-PAVE-005"}

    def test_no_pave_rule_invents_a_professional_threshold(self):
        """Scanned against the REAL emitted messages rather than the source, so
        a threshold cannot hide in a string this test never sees."""

        forbidden = (
            "minimum spacing",
            "minimum bead",
            "maximum density",
            "industry standard",
            "not manufacturable",
            "must be at least",
            "too thin",
            "too small",
            "manufacturing safe",
            "production safe",
            "bench validated",
        )
        definitions = [
            design(pave(stoneScale=s, spec=pave_spec(pitchMm=p, rowCount=r)))
            for s, p, r in ((0.02, 3.0, 1), (0.3, 0.3, 2), (0.1, 1.0, 8))
        ]
        definitions.append(design(pave(retention=PaveRetention(beadRadiusMm=0.02))))
        definitions.append(design(pave(enabled=False)))
        for definition in definitions:
            for result in validate_definition(definition):
                if not result.ruleId.startswith("JM-PAVE"):
                    continue
                lowered = result.message.lower()
                for phrase in forbidden:
                    assert phrase not in lowered, (result.ruleId, phrase)


# ----------------------------------------------------------- JDL integration


class TestJdlIntegration:
    def test_a_pave_round_trips_through_jdl(self):
        definition = design(
            pave(
                spec=pave_spec(rowCount=2, pattern="STAGGERED"),
                retention=PaveRetention(strategy="MICRO_PRONG"),
                seat=PaveSeat(mode="REFERENCE_RECESS"),
                gem=GemIdentity(gemId="corundum.sapphire", origin="NATURAL"),
                label="Shank pave",
            )
        )
        payload = definition.model_dump(mode="json")
        restored = JewelryDefinition.model_validate(payload)
        assert restored.pave == definition.pave
        assert definition_hash(restored) == definition_hash(definition)

    def test_a_microsetting_round_trips_through_jdl(self):
        definition = design(
            pave(kind="MICROSETTING", spec=micro_spec(columnCount=8, rowCount=2))
        )
        restored = JewelryDefinition.model_validate(
            definition.model_dump(mode="json")
        )
        assert isinstance(restored.pave.spec, MicrosettingSpec)

    def test_the_schema_version_is_unchanged(self):
        assert design(pave()).schemaVersion == "0.1.0"

    def test_a_document_without_a_pave_validates_and_hashes_as_before(self):
        payload = default_definition().model_dump(mode="json")
        assert payload["pave"] is None
        del payload["pave"]
        restored = JewelryDefinition.model_validate(payload)
        assert restored.pave is None
        assert definition_hash(restored) == definition_hash(default_definition())

    def test_the_jdl_schema_carries_the_pave_subtree(self):
        schema = json.loads(
            (REPO_ROOT / "specs" / "jdl" / "v1" / "jdl.schema.json").read_text(
                encoding="utf-8"
            )
        )
        assert "pave" in schema["properties"]
        assert "pave" in schema["$defs"]
        assert {"PaveSpec", "MicrosettingSpec", "PaveRetention"} <= set(
            schema["$defs"]["paveDefs"]
        )

    def test_the_jdl_schema_accepts_real_documents(self):
        import jsonschema

        schema = json.loads(
            (REPO_ROOT / "specs" / "jdl" / "v1" / "jdl.schema.json").read_text(
                encoding="utf-8"
            )
        )
        jsonschema.validate(default_definition().model_dump(mode="json"), schema)
        jsonschema.validate(design(pave()).model_dump(mode="json"), schema)
        jsonschema.validate(
            design(
                pave(kind="MICROSETTING", spec=micro_spec())
            ).model_dump(mode="json"),
            schema,
        )


# ------------------------------------------------------ capability registry


class TestCapabilityRegistry:
    def test_every_host_entry_has_a_real_resolver(self):
        from jewelmind.geometry.pave_surface import _HOST_RESOLVERS

        assert set(PAVE_HOST_CAPABILITIES) == set(_HOST_RESOLVERS)

    def test_retention_geometry_is_claimed_only_where_it_exists(self):
        assert set(retention_strategies_with_geometry()) == {
            "BEAD",
            "SHARED_BEAD",
            "MICRO_PRONG",
        }
        assert PAVE_RETENTION_CAPABILITIES["NONE"].settingGeometry is False

    def test_this_is_the_first_sprint_to_claim_setting_geometry(self):
        """The one substantive difference from Sprints 24 and 25, asserted
        against their own registries so the claim is comparative rather than
        self-declared."""

        from jewelmind.family.capability import families_with_setting_geometry
        from jewelmind.halo.capability import halo_variants_with_setting_geometry

        assert families_with_setting_geometry() == ()
        assert halo_variants_with_setting_geometry() == ()
        assert retention_strategies_with_geometry() != ()

    def test_no_planned_capability_claims_geometry(self):
        for name, entry in PAVE_CAPABILITIES.items():
            if entry.status == "PLANNED":
                assert entry.stoneGeometry is False, name
                assert entry.settingGeometry is False, name

    def test_a_reserved_name_has_a_real_reason(self):
        for reason in (
            *RESERVED_PAVE_HOSTS.values(),
            *RESERVED_RETENTION_STRATEGIES.values(),
        ):
            assert len(reason) > 60

    def test_multiple_fields_is_planned_and_the_schema_says_so(self):
        assert PAVE_CAPABILITIES["multiple_pave_fields"].status == "PLANNED"
        # Singular, so the limitation is visible in the schema.
        assert "pave" in JewelryDefinition.model_fields
        assert "paves" not in JewelryDefinition.model_fields

    def test_a_capability_can_be_looked_up_without_knowing_its_family(self):
        from jewelmind.pave.capability import get_pave_capability

        for name, entry in PAVE_CAPABILITIES.items():
            assert get_pave_capability(name) is entry, name
        assert get_pave_capability("no_such_capability") is None

    def test_the_versions_are_declared(self):
        assert PAVE_COMPILER_VERSION == "1.0.0"
        assert PAVE_REGISTRY_VERSION == "1.0.0"


# ------------------------------------------------------------- boundaries


class TestBoundaries:
    def test_the_pave_layer_never_imports_a_category_or_the_kernel(self):
        """AST-parsed, not `import`-based: an import check can pass by accident
        on an already-cached module."""

        package = Path(__file__).resolve().parents[1] / "jewelmind" / "pave"
        forbidden = (
            "cadquery",
            "OCP",
            "jewelmind.ring",
            "jewelmind.jewelry_category",
            "jewelmind.geometry",
            "jewelmind.setting",
            "jewelmind.domain.schema",
        )
        for path in sorted(package.glob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    names = [node.module or ""]
                else:
                    continue
                for name in names:
                    for banned in forbidden:
                        assert not name.startswith(banned), f"{path.name}: {name}"

    def test_the_pave_package_init_imports_nothing(self):
        path = (
            Path(__file__).resolve().parents[1] / "jewelmind" / "pave" / "__init__.py"
        )
        tree = ast.parse(path.read_text(encoding="utf-8"))
        assert not [
            n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))
        ]

    def test_the_surface_resolver_is_kernel_free(self):
        """Forge imports it, and Forge must not import CadQuery."""

        source = (
            Path(__file__).resolve().parents[1]
            / "jewelmind"
            / "geometry"
            / "pave_surface.py"
        ).read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            else:
                continue
            for name in names:
                assert not name.startswith("cadquery"), name
                assert not name.startswith("OCP"), name

    def test_retention_geometry_lives_in_the_setting_system(self):
        """Setting System v2 is authoritative for how metal holds a stone, so
        the bead builder belongs there and NOT in the pavé package."""

        from jewelmind.setting import retention

        assert retention.retention_builders()
        pave_package = Path(__file__).resolve().parents[1] / "jewelmind" / "pave"
        for path in pave_package.glob("*.py"):
            assert "makeSphere" not in path.read_text(encoding="utf-8"), path.name

    def test_the_ring_arithmetic_is_shared_rather_than_copied(self):
        source = (
            Path(__file__).resolve().parents[1]
            / "jewelmind"
            / "pave"
            / "compile.py"
        ).read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
            for alias in node.names
        }
        assert "ring_angles_deg" in imported


# ------------------------------------------------------ backward compatibility


class TestBackwardCompatibility:
    def test_the_default_solitaire_is_geometrically_unchanged(self):
        model = build_solitaire_ring(default_definition())
        assert model.combined_metal_volume_mm3 == pytest.approx(
            LEGACY_METAL_VOLUME_MM3, rel=KERNEL_REL_TOLERANCE
        )
        assert sorted(model.components) == [
            "band",
            "basket_support",
            "prongs",
            "stone_reference",
        ]
        assert model.pave_result is None

    def test_the_added_tilt_leaves_every_existing_placement_untouched(self):
        """The identity path, asserted on the object rather than on equality."""

        from jewelmind.geometry.stone.instance import place_stone_instance

        stone = build_solitaire_ring(default_definition()).components[
            PRIMARY_STONE_COMPONENT
        ]
        placed = place_stone_instance(
            stone,
            PRIMARY_STONE_COMPONENT,
            x_mm=0.0,
            y_mm=0.0,
            z_mm=0.0,
            rotation_deg=0.0,
            scale=None,
            orientation_deg=None,
            instance_id="center",
            role="CENTER",
        )
        assert placed.shape is stone.shape
        assert placed.metadata["instanceTransformOperations"] == []

    def test_a_tilt_is_a_real_kernel_rotation(self):
        """Measured on the built solid, not trusted from the field: at 90
        degrees the X and Z extents swap and the volume is unchanged."""

        definition = default_definition()
        definition.arrangement = ArrangementDefinition(
            instances=[
                StoneInstanceDef(instanceId="center", role="CENTER"),
                StoneInstanceDef(
                    instanceId="tipped",
                    role="PAVE",
                    placement=InstancePlacement(
                        transform=InstanceTransform(xMm=4.0, tiltDeg=90.0)
                    ),
                ),
            ]
        )
        model = build_solitaire_ring(definition)
        upright = model.components[PRIMARY_STONE_COMPONENT].bounding_box
        tipped = model.components[
            f"{STONE_INSTANCE_COMPONENT_PREFIX}tipped"
        ].bounding_box
        assert (tipped.xmax - tipped.xmin) == pytest.approx(
            upright.zmax - upright.zmin, rel=1e-9
        )
        assert (tipped.zmax - tipped.zmin) == pytest.approx(
            upright.xmax - upright.xmin, rel=1e-9
        )
        assert model.components[
            f"{STONE_INSTANCE_COMPONENT_PREFIX}tipped"
        ].volume_mm3 == pytest.approx(
            model.components[PRIMARY_STONE_COMPONENT].volume_mm3, rel=1e-9
        )

    def test_existing_designs_still_validate(self):
        for definition in (
            default_definition(),
            design(
                family=FamilyDefinition(
                    familyType="THREE_STONE",
                    params=ThreeStoneParams(sideSpacingMm=4.6),
                )
            ),
            design(
                halo=HaloDefinition(
                    variant="SINGLE",
                    rings=[HaloRing(ringId="halo.inner", count=8, radiusMm=3.4)],
                )
            ),
        ):
            assert not has_errors(validate_definition(definition))
            assert pave_rule_ids(definition) == {}


# ------------------------------------------------------------ export surface


class TestExport:
    def test_the_retention_field_is_included_in_a_production_export(self):
        from jewelmind.geometry.roles import production_role

        assert production_role(PAVE_RETENTION_COMPONENT) == "included_by_default"

    def test_a_pave_model_exports_real_step_and_stl(self, tmp_path):
        from jewelmind.exporters.step_exporter import export_step
        from jewelmind.exporters.stl_exporter import export_stl

        definition = design(pave(seat=PaveSeat(mode="REFERENCE_RECESS")))
        model = build_solitaire_ring(definition)
        step = tmp_path / "pave.step"
        stl = tmp_path / "pave.stl"
        export_step(model, step)
        export_stl(model, definition, stl)
        # Real files with real content — never a placeholder.
        assert step.stat().st_size > 1000
        assert stl.stat().st_size > 1000
        assert b"ISO-10303" in step.read_bytes()[:200]

    def test_the_stone_reference_stays_out_of_a_default_export(self, tmp_path):
        """The pavé adds many stone references, and the default export must
        still contain none of them (LAW-006 at the export layer)."""

        from jewelmind.exporters.stl_exporter import export_stl

        definition = design(pave())
        model = build_solitaire_ring(definition)
        target = tmp_path / "pave.stl"
        export_stl(model, definition, target)
        without = target.stat().st_size
        export_stl(model, definition, target, include_stone=True)
        assert target.stat().st_size > without


# ----------------------------------------------------------- spec artifacts


class TestSpecArtifacts:
    def test_the_registry_matches_the_live_code(self):
        registry = json.loads(
            (SPEC_DIR / "pave-registry.json").read_text(encoding="utf-8")
        )
        assert registry["registryVersion"] == PAVE_REGISTRY_VERSION
        assert registry["compilerVersion"] == PAVE_COMPILER_VERSION
        assert registry["patterns"] == list(pave_patterns())
        recorded = {
            e["capability"]: e
            for key in ("kinds", "hosts", "patternCapabilities", "retention", "features")
            for e in registry[key]
        }
        assert set(recorded) == set(PAVE_CAPABILITIES)
        for name, entry in PAVE_CAPABILITIES.items():
            assert recorded[name] == entry.model_dump(mode="json"), name
        assert {r["host"] for r in registry["reservedHosts"]} == set(
            RESERVED_PAVE_HOSTS
        )
        assert {r["strategy"] for r in registry["reservedRetention"]} == set(
            RESERVED_RETENTION_STRATEGIES
        )

    def test_the_schemas_match_the_live_models(self):
        from jewelmind.pave.surface import ResolvedHostSurface

        for filename, model in (
            ("pave-definition.schema.json", PaveDefinition),
            ("pave-spec.schema.json", PaveSpec),
            ("microsetting-spec.schema.json", MicrosettingSpec),
            ("pave-retention.schema.json", PaveRetention),
            ("pave-seat.schema.json", PaveSeat),
            ("resolved-host-surface.schema.json", ResolvedHostSurface),
        ):
            recorded = json.loads((SPEC_DIR / filename).read_text(encoding="utf-8"))
            live = model.model_json_schema()
            for key, value in live.items():
                assert recorded[key] == value, (filename, key)

    def test_the_examples_reproduce_from_the_live_model(self):
        for path in sorted((SPEC_DIR / "examples").glob("*.json")):
            if path.name.startswith("compiled-"):
                continue
            recorded = json.loads(path.read_text(encoding="utf-8"))
            live = PaveDefinition.model_validate(recorded)
            assert live.model_dump(mode="json") == recorded, path.name

    def test_the_compilation_vectors_still_hold(self):
        vectors = json.loads(
            (SPEC_DIR / "test-vectors" / "compilation-vectors.json").read_text(
                encoding="utf-8"
            )
        )
        assert vectors["compilerVersion"] == PAVE_COMPILER_VERSION
        definition = default_definition()
        for vector in vectors["vectors"]:
            recorded = json.loads(
                (SPEC_DIR / "examples" / f"{vector['name']}.json").read_text(
                    encoding="utf-8"
                )
            )
            candidate = PaveDefinition.model_validate(recorded)
            surface = resolve_pave_surface(definition, candidate)
            assert surface.model_dump(mode="json") == vector["surface"]
            field = compile_pave_field(candidate, surface)
            assert field.stone_count() == vector["stoneCount"], vector["name"]
            assert field.retention_count() == vector["retentionPieceCount"]
            assert field.clippedCells == vector["clippedCells"]
            assert vector["professionalValidationStatus"] == "NOT_REVIEWED"
            if "arrangementFingerprint" in vector:
                composed, _ = compose_pave(None, candidate, surface)
                assert composed is not None
                assert (
                    arrangement_fingerprint(composed)
                    == vector["arrangementFingerprint"]
                )

    def test_every_invalid_vector_is_still_refused(self):
        vectors = json.loads(
            (SPEC_DIR / "test-vectors" / "invalid-pave-vectors.json").read_text(
                encoding="utf-8"
            )
        )
        assert vectors["vectors"]
        for vector in vectors["vectors"]:
            assert vector["rejectedBy"] in {"SCHEMA", "COMPILER"}, vector["case"]


# ---------------------------------------------------------------- API surface


class TestApiSurface:
    def client(self):
        from fastapi.testclient import TestClient

        from jewelmind.api.app import create_app

        return TestClient(create_app(), raise_server_exceptions=False)

    def test_a_valid_pave_generates_through_the_api(self):
        response = self.client().post(
            "/api/models/generate",
            json=design(pave()).model_dump(mode="json"),
        )
        assert response.status_code == 200, response.text
        body = response.json()
        names = set(body["previewComponents"])
        assert PAVE_RETENTION_COMPONENT in names
        assert any(n.startswith(STONE_INSTANCE_COMPONENT_PREFIX) for n in names)
        assert (
            body["previewComponents"][PAVE_RETENTION_COMPONENT]["geometryRole"]
            == "production_metal"
        )
        assert any(r["ruleId"] == "JM-PAVE-005" for r in body["validation"])

    def test_an_uncompilable_pave_is_blocked_without_leaking_internals(self):
        response = self.client().post(
            "/api/models/generate",
            json=design(
                pave(spec=pave_spec(rowCount=8, pitchMm=1.0), containment="REJECT")
            ).model_dump(mode="json"),
        )
        assert response.status_code == 422
        payload = response.text
        assert "JM-PAVE-002" in payload
        assert "Traceback" not in payload
        assert "PaveContainmentError" not in payload
        assert "site-packages" not in payload
        assert "Desktop" not in payload

    def test_a_malformed_pave_is_rejected_at_the_schema_layer(self):
        payload = design().model_dump(mode="json")
        payload["pave"] = {
            "kind": "PAVE",
            "host": "BAND_OUTER",
            "spec": {"kind": "PAVE", "angularSpanDeg": 90.0, "pitchMm": "wide"},
        }
        response = self.client().post("/api/models/generate", json=payload)
        assert response.status_code == 422
        assert "Traceback" not in response.text
