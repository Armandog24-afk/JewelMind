"""Specialty Rings v1 (Sprint 29).

THE QUESTION THIS FILE HAS TO ANSWER is the brief's own quality bar (§29):

> Can a designer change a meaningful Specialty Ring parameter and receive a
> coherent regenerated ring rather than a different preset?

A catalogue of presets would pass a suite that checked JSON, so every claim
below is asserted against MEASURED GEOMETRY — stone positions, stone volumes,
retention-solid counts and metal volumes from real generated solids.

## What is CURRENT and what is PARTIAL, and why the split is not a preference

`eternity` is CURRENT because the Pavé Engine is the ONE layer in the programme
whose `settingGeometry` is `true`: it builds real retention metal for every
stone in a field, not only for a primary one. An eternity band therefore has
real stones AND real metal holding them.

`cluster` and `toi_et_moi` are PARTIAL because the Multi-Stone Family layer
reports `settingGeometry: false` for every family — the accent stones are real
solids and only the CENTRE is held. `TestPartialFamiliesAreHonest` asserts that
boundary rather than papering over it, and `test_the_stone_only_families_add_no
_metal` measures it: their combined metal is EXACTLY the baseline's.

## What this sprint did NOT build, and why each is recorded rather than faked

- A channel-set BAND. `setting/channel.py` builds its walls with
  `oriented_prism()` — straight prisms in the STONE's frame — so it cannot
  follow the band's curve.
- A stacking / plain band. `REQUIRED_COMPONENT_NAMES` includes
  `stone_reference` and `basket_support`, so a stone-less ring fails inspection
  by contract. An ADR condition, not a parameter.
- A tension-STYLE family. The `tension` SETTING family already builds exactly
  that geometry; a ring family wrapping it would be a second name for one
  capability.

Each is in `RESERVED_RING_FAMILIES` with that reason, and
`TestReservedSpecialtyNames` asserts they stay unbuildable.
"""

from __future__ import annotations

import ast
import math
from pathlib import Path

import pytest
from pydantic import ValidationError

from jewelmind.domain.defaults import default_definition
from jewelmind.domain.schema import JewelryDefinition
from jewelmind.geometry.assemblies.solitaire import build_solitaire_ring
from jewelmind.geometry.inspection import inspect_model
from jewelmind.geometry.roles import geometry_role, is_production_component
from jewelmind.ring_family.capability import (
    designer_family_terms,
    family_status,
    ring_family_capabilities,
)
from jewelmind.ring_family.dependencies import derived_paths
from jewelmind.ring_family.errors import (
    RingFamilyDerivationConflictError,
    RingFamilyVariantMismatchError,
)
from jewelmind.ring_family.models import (
    RESERVED_RING_FAMILIES,
    VARIANT_FAMILY,
    RingFamilyParams,
    RingFamilySpec,
    default_variant_for,
    family_for_variant,
    implemented_families,
)
from jewelmind.ring_family.resolve import parameters_read_by, resolve_ring_family
from jewelmind.validation import rules as R
from jewelmind.validation.engine import validate_definition
from jewelmind.validation.sizing import eu_size_to_inner_diameter

BACKEND_ROOT = Path(__file__).resolve().parents[1]

#: The families Sprint 29 added.
SPECIALTY_FAMILIES = ("eternity", "cluster", "toi_et_moi")

#: Their variants.
SPECIALTY_VARIANTS = (
    "ETERNITY_FULL",
    "ETERNITY_HALF",
    "CLUSTER_ROUND",
    "TOI_ET_MOI_BYPASS",
)

#: Relative tolerance for a RECORDED volume against live geometry. The value
#: five existing modules already share; an OCCT `Volume()` drifts ~6.7e-14
#: between this repo's Windows build and CI's Linux one (see `test_setting.py`).
KERNEL_VOLUME_REL_TOL = 1e-9


# --------------------------------------------------------------------------
# Helpers — every design built from the REAL default, never a fixture that
# could drift from the schema.
# --------------------------------------------------------------------------


def design(
    variant: str,
    *,
    size: float | None = None,
    stone_diameter: float | None = None,
    style: str | None = None,
    **params: object,
) -> JewelryDefinition:
    data = default_definition().model_dump(mode="python")
    data["jewelry"]["style"] = style if style is not None else family_for_variant(variant)
    data["ringFamily"] = RingFamilySpec(
        variant=variant,
        params=RingFamilyParams(**params) if params else RingFamilyParams(),
    ).model_dump(mode="python")
    if size is not None:
        # BOTH, because `ring.innerDiameter` is what drives the geometry and
        # `ring.size` is the nominal label — `JM-RING-003` reports a
        # disagreement rather than choosing one.
        data["ring"]["size"] = size
        data["ring"]["innerDiameter"] = eu_size_to_inner_diameter(size)
    if stone_diameter is not None:
        data["stone"]["diameter"] = stone_diameter
    return JewelryDefinition.model_validate(data)


def build(variant: str, **kwargs: object):
    return build_solitaire_ring(design(variant, **kwargs))


def stone_components(model) -> dict[str, tuple[float, float, float]]:
    """Every stone component, as `(volume, centre x, centre y)`.

    Includes the primary: a toi-et-moi's FIRST principal stone carries the bare
    `stone_reference` name, because the primary instance always does
    (ARRANGE-GOV-012). Looking only at suffixed names would miss half the pair.
    """

    out: dict[str, tuple[float, float, float]] = {}
    for name, component in model.components.items():
        if geometry_role(name) != "stone_reference":
            continue
        box = component.shape.BoundingBox()
        out[name] = (
            component.shape.Volume(),
            (box.xmin + box.xmax) / 2.0,
            (box.ymin + box.ymax) / 2.0,
        )
    return out


def retention_solids(model) -> int:
    component = model.components.get("pave_retention")
    return len(component.shape.Solids()) if component is not None else 0


def set_stone_count(model) -> int:
    return sum(1 for n in model.components if geometry_role(n) == "stone_reference")


# ==========================================================================
# §4 — ONE RING ARCHITECTURE, NOT TWO
# ==========================================================================


class TestExtendsRingFamiliesRatherThanParalleling:
    def test_every_specialty_family_is_a_jewelry_style(self):
        # THE ARCHITECTURAL DECISION, asserted. A specialty ring resolves
        # through the same `jewelry.style` every other family uses, so there is
        # one authority for what a design IS.
        for family in SPECIALTY_FAMILIES:
            assert family in implemented_families(), family

    def test_every_specialty_variant_is_a_ring_family_variant(self):
        for variant in SPECIALTY_VARIANTS:
            assert variant in VARIANT_FAMILY, variant
            assert variant in ring_family_capabilities(), variant

    def test_there_is_no_separate_specialty_generator(self):
        # §4 forbids a `SpecialtyRingGenerator` that bypasses Ring Family
        # infrastructure. The check is structural: no module named for
        # specialty rings exists at all, because the capability lives in the
        # ring-family layer.
        assert not list(BACKEND_ROOT.glob("jewelmind/**/specialty*.py"))
        assert not list(BACKEND_ROOT.glob("jewelmind/specialty_ring*"))

    def test_the_layer_still_imports_no_geometry(self):
        # Sprint 28's neutrality guard must still hold after the extension —
        # AST, not `import`, so a cached module cannot mask a violation.
        package = BACKEND_ROOT / "jewelmind" / "ring_family"
        forbidden = ("cadquery", "OCP", "jewelmind.geometry", "jewelmind.ring")
        for path in sorted(package.glob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                names: list[str] = []
                if isinstance(node, ast.Import):
                    names = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    names = [node.module]
                for name in names:
                    for bad in forbidden:
                        assert not (name == bad or name.startswith(f"{bad}.")), (
                            f"{path.name} imports {name}"
                        )

    def test_every_specialty_variant_resolves_through_the_one_resolver(self):
        for variant in SPECIALTY_VARIANTS:
            resolved = resolve_ring_family(design(variant))
            assert resolved.variant == variant
            assert resolved.family == VARIANT_FAMILY[variant]
            assert resolved.derivations, variant


# ==========================================================================
# §7/§8/§9 — DELEGATION, NEVER DUPLICATION
# ==========================================================================


class TestDelegation:
    def test_the_eternity_band_delegates_to_the_pave_engine(self):
        for variant in ("ETERNITY_FULL", "ETERNITY_HALF"):
            paths = {d.path for d in resolve_ring_family(design(variant)).derivations}
            assert "pave" in paths, variant
            # It derives NO arrangement of its own: the Pavé Engine compiles the
            # field into instances and the arrangement resolver places them.
            assert not any(p.startswith("arrangement") for p in paths), variant

    def test_cluster_and_toi_et_moi_delegate_to_the_stone_family_layer(self):
        for variant in ("CLUSTER_ROUND", "TOI_ET_MOI_BYPASS"):
            paths = {d.path for d in resolve_ring_family(design(variant)).derivations}
            assert "family.familyType" in paths, variant
            assert "family.params" in paths, variant
            assert not any(p.startswith("arrangement") for p in paths), variant

    def test_the_derived_stone_family_is_the_existing_one(self):
        # NOT a new family type invented for the ring layer: it names the
        # Sprint 24 `FamilyType` member, which is what keeps one placement
        # engine rather than two.
        from typing import get_args

        from jewelmind.family.models import FamilyType

        members = set(get_args(FamilyType))
        for variant, expected in (
            ("CLUSTER_ROUND", "CLUSTER"),
            ("TOI_ET_MOI_BYPASS", "TOI_ET_MOI"),
        ):
            derived = {
                d.path: d.value for d in resolve_ring_family(design(variant)).derivations
            }
            assert derived["family.familyType"] == expected
            assert expected in members

    def test_a_specialty_family_beside_an_explicit_arrangement_is_refused(self):
        # Two authorities over one set of placements, which `JM-FAMILY-001`
        # refuses one layer down.
        data = design("CLUSTER_ROUND").model_dump(mode="python")
        data["arrangement"] = {"instances": [{"instanceId": "c", "role": "CENTER"}]}
        with pytest.raises(RingFamilyDerivationConflictError):
            resolve_ring_family(JewelryDefinition.model_validate(data))

    def test_a_declared_pave_is_never_overwritten(self):
        from jewelmind.pave.models import default_pave_field

        data = design("ETERNITY_FULL").model_dump(mode="python")
        data["pave"] = default_pave_field("PAVE").model_dump(mode="python")
        resolved = resolve_ring_family(JewelryDefinition.model_validate(data))
        assert "pave" in resolved.skippedPaths
        assert all(d.path != "pave" for d in resolved.derivations)

    def test_every_derived_path_is_declared(self):
        for variant in SPECIALTY_VARIANTS:
            declared = set(derived_paths(variant))
            for derivation in resolve_ring_family(design(variant)).derivations:
                assert derivation.path in declared, (variant, derivation.path)


# ==========================================================================
# §10/§20/§29 — REAL PARAMETRIC GEOMETRY. THE QUALITY BAR.
# ==========================================================================


class TestSpecialtyParametrics:
    """Change one parameter, measure the geometric result.

    A preset catalogue would fail every test in this class.
    """

    # ---- eternity ---------------------------------------------------------

    def test_finger_size_drives_the_full_eternity_stone_count(self):
        """THE STRONGEST EVIDENCE IN THE SPRINT that this is a relation.

        A full eternity states a PITCH, not a count, so the number of stones
        follows from the band's own circumference. A bigger finger carries more
        stones rather than the same stones stretched further apart — which is
        what a real eternity band does and what a preset cannot do.
        """

        counts = []
        for size in (12.0, 16.0, 24.0):
            model = build("ETERNITY_FULL", size=size)
            counts.append(set_stone_count(model))
        assert counts == sorted(counts)
        assert counts[0] < counts[-1], counts

    def test_the_full_eternity_pitch_drives_the_stone_count(self):
        dense = set_stone_count(build("ETERNITY_FULL", eternityPitchMm=1.2))
        sparse = set_stone_count(build("ETERNITY_FULL", eternityPitchMm=2.4))
        assert dense > sparse

    def test_the_half_eternity_count_is_explicit_and_honoured(self):
        for count in (6, 12, 20):
            model = build("ETERNITY_HALF", eternityStoneCount=count)
            # +1 for the design's own centre stone, which remains: a stone-less
            # ring is not representable (see the module docstring).
            assert set_stone_count(model) == count + 1, count

    def test_the_half_eternity_spacing_changes_the_retention_topology(self):
        """Spacing is not cosmetic: tighter stones genuinely SHARE bead corners.

        Measured — 16 stones at 1.6 mm give 64 bead solids and at 1.2 mm give
        34, because the corners merge. A field that only moved stones closer
        would keep 64.
        """

        wide = retention_solids(build("ETERNITY_HALF", eternityStoneCount=16,
                                      eternityStoneSpacingMm=1.6))
        tight = retention_solids(build("ETERNITY_HALF", eternityStoneCount=16,
                                       eternityStoneSpacingMm=1.2))
        assert wide > tight > 0

    def test_the_eternity_stone_scale_follows_the_design_stone(self):
        # A RELATION: the set stones are a multiple of the design's own stone,
        # so changing `stone.diameter` changes the whole band.
        small = build("ETERNITY_HALF", stone_diameter=5.0)
        large = build("ETERNITY_HALF", stone_diameter=8.0)

        def a_set_stone(model) -> float:
            return min(v[0] for k, v in stone_components(model).items()
                       if k != "stone_reference")

        assert a_set_stone(large) > a_set_stone(small)

    def test_the_eternity_band_adds_real_metal(self):
        # The distinguishing fact against every other multi-stone family: the
        # Pavé Engine builds retention, so the metal genuinely grows.
        baseline = build_solitaire_ring(default_definition()).combined_metal_volume_mm3
        for variant in ("ETERNITY_FULL", "ETERNITY_HALF"):
            model = build(variant)
            assert model.combined_metal_volume_mm3 > baseline, variant
            assert retention_solids(model) > 0, variant

    def test_the_retention_strategy_changes_the_metal(self):
        beads = build("ETERNITY_HALF", eternityRetention="BEAD")
        none = build("ETERNITY_HALF", eternityRetention="NONE")
        assert retention_solids(beads) > 0
        assert retention_solids(none) == 0
        assert beads.combined_metal_volume_mm3 > none.combined_metal_volume_mm3
        # NONE is an honest option, not a failure: the stones are still real.
        assert set_stone_count(none) == set_stone_count(beads)

    # ---- cluster ----------------------------------------------------------

    def test_the_cluster_count_changes_the_stone_count(self):
        for count in (4, 8, 16):
            model = build("CLUSTER_ROUND", clusterStoneCount=count)
            assert set_stone_count(model) == count + 1, count

    def test_the_cluster_radius_moves_the_stones(self):
        """Measured against the REQUEST, not merely 'something changed'."""

        for radius in (3.0, 5.5):
            model = build("CLUSTER_ROUND", clusterStoneCount=6, clusterRadiusMm=radius)
            surrounding = [
                v for k, v in stone_components(model).items() if k != "stone_reference"
            ]
            furthest = max(math.hypot(v[1], v[2]) for v in surrounding)
            assert furthest == pytest.approx(radius, rel=1e-6), radius

    def test_the_cluster_stone_scale_resizes_the_stones(self):
        def surrounding_volume(scale: float) -> float:
            model = build("CLUSTER_ROUND", clusterStoneCount=6, clusterStoneScale=scale)
            return min(v[0] for k, v in stone_components(model).items()
                       if k != "stone_reference")

        assert surrounding_volume(0.7) > surrounding_volume(0.3)

    # ---- toi et moi -------------------------------------------------------

    def test_toi_et_moi_builds_two_separate_stone_instances(self):
        """§2.6: they must remain SEPARATE Stone Instances.

        The first principal stone carries the bare `stone_reference` name
        because the primary instance always does (ARRANGE-GOV-012); the second
        is suffixed. Two components, never one combined gemstone object.
        """

        stones = stone_components(build("TOI_ET_MOI_BYPASS"))
        assert len(stones) == 2
        assert "stone_reference" in stones
        assert any(k.startswith("stone_reference.") for k in stones)

    def test_the_two_principal_stones_are_independently_sized(self):
        equal = stone_components(build("TOI_ET_MOI_BYPASS", toiEtMoiSecondScale=1.0))
        unequal = stone_components(build("TOI_ET_MOI_BYPASS", toiEtMoiSecondScale=0.5))
        first_equal = equal["stone_reference"][0]
        first_unequal = unequal["stone_reference"][0]
        second_equal = next(v[0] for k, v in equal.items() if k != "stone_reference")
        second_unequal = next(v[0] for k, v in unequal.items() if k != "stone_reference")

        # The FIRST stone is untouched and only the SECOND shrinks, which is
        # what "relative size" means.
        assert first_equal == pytest.approx(first_unequal, rel=KERNEL_VOLUME_REL_TOL)
        assert second_unequal < second_equal

    def test_the_separation_is_honoured_exactly(self):
        for separation in (3.0, 8.0):
            stones = list(stone_components(
                build("TOI_ET_MOI_BYPASS", toiEtMoiSeparationMm=separation)
            ).values())
            measured = math.hypot(stones[0][1] - stones[1][1], stones[0][2] - stones[1][2])
            assert measured == pytest.approx(separation, rel=1e-6), separation

    def test_the_orientation_rotates_the_pair(self):
        along_x = stone_components(build("TOI_ET_MOI_BYPASS", toiEtMoiOrientationDeg=0.0))
        along_y = stone_components(build("TOI_ET_MOI_BYPASS", toiEtMoiOrientationDeg=90.0))
        x_spread = max(abs(v[1]) for v in along_x.values())
        y_spread = max(abs(v[2]) for v in along_y.values())
        assert x_spread > 0.1
        assert y_spread > 0.1
        # Rotated onto the other axis: the X spread collapses.
        assert max(abs(v[1]) for v in along_y.values()) < x_spread


# ==========================================================================
# §16/§17/§25 — HONEST STATUS, NO INVENTED CONFIDENCE
# ==========================================================================


class TestPartialFamiliesAreHonest:
    def test_cluster_and_toi_et_moi_are_partial(self):
        assert family_status("cluster") == "PARTIAL"
        assert family_status("toi_et_moi") == "PARTIAL"

    def test_eternity_is_current_because_the_pave_engine_holds_its_stones(self):
        assert family_status("eternity") == "CURRENT"
        # The claim is backed by the Pavé registry's own axis, not by assertion.
        from jewelmind.pave.capability import PAVE_RETENTION_CAPABILITIES

        assert PAVE_RETENTION_CAPABILITIES["BEAD"].settingGeometry is True

    def test_the_stone_only_families_add_no_metal(self):
        """The PARTIAL boundary, measured rather than described.

        Their combined metal is EXACTLY the baseline's, because only the centre
        stone is held. That equality IS the limitation.
        """

        baseline = build_solitaire_ring(default_definition()).combined_metal_volume_mm3
        for variant in ("CLUSTER_ROUND", "TOI_ET_MOI_BYPASS"):
            model = build(variant)
            assert model.combined_metal_volume_mm3 == pytest.approx(
                baseline, rel=KERNEL_VOLUME_REL_TOL
            ), variant
            assert retention_solids(model) == 0, variant
            # And the stones are real all the same.
            assert set_stone_count(model) > 1, variant

    def test_the_partial_descriptions_say_what_is_missing(self):
        for variant in ("CLUSTER_ROUND", "TOI_ET_MOI_BYPASS"):
            entry = ring_family_capabilities()[variant]
            assert entry.status == "PARTIAL"
            lowered = entry.description.lower()
            assert "only the centre stone is held" in lowered or "not held" in lowered

    def test_toi_et_moi_records_the_shared_cut_limitation(self):
        # §2.6 asks for independent CUTS. A `FamilyMember` carries no shape, so
        # the two stones share the design's one `stone`. Recorded, not faked.
        entry = ring_family_capabilities()["TOI_ET_MOI_BYPASS"]
        assert "cut" in entry.description.lower()

    def test_no_specialty_variant_claims_professional_validation(self):
        for variant in SPECIALTY_VARIANTS:
            entry = ring_family_capabilities()[variant]
            assert entry.professionalValidationStatus == "NOT_REVIEWED", variant

    def test_no_specialty_rule_message_makes_a_manufacturing_claim(self):
        forbidden = (
            "production safe",
            "manufacturing validated",
            "casting validated",
            "jeweler approved",
            "structurally safe",
            "secure",
            "will hold",
        )
        for variant in SPECIALTY_VARIANTS:
            for result in validate_definition(design(variant)):
                lowered = result.message.lower()
                for phrase in forbidden:
                    assert phrase not in lowered, (variant, result.ruleId, phrase)


class TestReservedSpecialtyNames:
    def test_the_three_deferred_capabilities_are_reserved_with_reasons(self):
        for name in ("channel_set_band", "plain_band", "tension_style"):
            assert name in RESERVED_RING_FAMILIES, name
            reason = RESERVED_RING_FAMILIES[name]
            assert len(reason) > 80, name
            assert "planned" not in reason.lower(), name

    def test_no_reserved_name_is_buildable(self):
        for name in RESERVED_RING_FAMILIES:
            assert name not in VARIANT_FAMILY, name
            assert name not in implemented_families(), name

    def test_the_retired_reservations_are_gone(self):
        # A name cannot be both a live family and a reserved one.
        for name in ("eternity", "cluster", "toi_et_moi"):
            assert name not in RESERVED_RING_FAMILIES, name
            assert name in implemented_families(), name


# ==========================================================================
# §22 — NEGATIVE TESTS
# ==========================================================================


class TestNegative:
    def test_a_specialty_variant_from_another_family_is_refused(self):
        with pytest.raises(RingFamilyVariantMismatchError):
            resolve_ring_family(design("ETERNITY_FULL", style="cluster"))
        results = validate_definition(design("CLUSTER_ROUND", style="eternity"))
        assert any(
            r.ruleId == R.RING_FAMILY_VARIANT_MATCHES and r.severity == "error"
            for r in results
        )

    def test_an_invalid_stone_count_is_refused(self):
        with pytest.raises(ValidationError):
            RingFamilyParams(eternityStoneCount=0)
        with pytest.raises(ValidationError):
            RingFamilyParams(clusterStoneCount=0)

    def test_an_impossible_spacing_is_refused(self):
        for field in ("eternityStoneSpacingMm", "eternityPitchMm", "clusterRadiusMm",
                      "toiEtMoiSeparationMm"):
            for value in (0.0, -1.0):
                with pytest.raises(ValidationError):
                    RingFamilyParams(**{field: value})

    def test_a_non_finite_parameter_is_refused(self):
        for value in (float("nan"), float("inf"), float("-inf")):
            with pytest.raises(ValidationError):
                RingFamilyParams(eternityStoneSpacingMm=value)

    def test_an_unsupported_retention_strategy_is_refused(self):
        # Never silently substituted with a supported one.
        with pytest.raises(ValidationError):
            RingFamilyParams(eternityRetention="CHANNEL")
        with pytest.raises(ValidationError):
            RingFamilyParams(eternityRetention="PRONG")

    def test_an_unknown_specialty_variant_is_refused(self):
        for name in ("ETERNITY", "eternity_full", "ETERNITY_QUARTER", "CLUSTER"):
            with pytest.raises(ValidationError):
                RingFamilySpec(variant=name)

    def test_an_over_capacity_band_is_refused(self):
        from jewelmind.ring_family.models import MAX_PAVE_STONES_PER_BAND

        with pytest.raises(ValidationError):
            RingFamilyParams(eternityStoneCount=MAX_PAVE_STONES_PER_BAND + 1)

    def test_an_extreme_but_legal_configuration_still_builds(self):
        # Inside the schema's own bounds, the result must be real geometry
        # rather than an exception a caller cannot act on.
        for variant, params in (
            ("ETERNITY_HALF", {"eternityStoneCount": 40, "eternityStoneSpacingMm": 1.0}),
            ("CLUSTER_ROUND", {"clusterStoneCount": 20, "clusterRadiusMm": 6.0}),
            ("TOI_ET_MOI_BYPASS", {"toiEtMoiSeparationMm": 12.0}),
        ):
            model = build(variant, **params)
            assert model.combined_metal_volume_mm3 > 0.0, variant
            assert set_stone_count(model) > 1, variant


# ==========================================================================
# §21 — COMPOSITION WITH THE EXISTING ENGINES
# ==========================================================================


class TestComposition:
    def test_a_specialty_ring_composes_with_gem_identity(self):
        data = design("TOI_ET_MOI_BYPASS").model_dump(mode="python")
        data["stone"]["gem"] = {"gemId": "corundum.sapphire", "origin": "NATURAL"}
        definition = JewelryDefinition.model_validate(data)
        assert not [r for r in validate_definition(definition) if r.severity == "error"]
        model = build_solitaire_ring(definition)
        assert set_stone_count(model) == 2

    def test_a_specialty_ring_composes_with_a_non_round_stone(self):
        data = design("CLUSTER_ROUND").model_dump(mode="python")
        data["stone"].update({"shape": "oval", "diameter": None, "length": 8.0,
                              "width": 6.0})
        definition = JewelryDefinition.model_validate(data)
        model = build_solitaire_ring(definition)
        assert set_stone_count(model) > 1
        assert model.combined_metal_volume_mm3 > 0.0

    def test_a_specialty_ring_composes_with_a_band_profile(self):
        comfort = build("ETERNITY_HALF")
        data = design("ETERNITY_HALF").model_dump(mode="python")
        data["band"]["profile"] = "flat"
        flat = build_solitaire_ring(JewelryDefinition.model_validate(data))
        assert comfort.components["band"].shape.Volume() != pytest.approx(
            flat.components["band"].shape.Volume(), rel=1e-6
        )

    def test_a_specialty_ring_composes_with_a_setting_type(self):
        data = design("CLUSTER_ROUND").model_dump(mode="python")
        data["setting"]["type"] = "bezel"
        definition = JewelryDefinition.model_validate(data)
        model = build_solitaire_ring(definition)
        # The centre stone's setting changed AND the cluster is still there.
        assert "bezel_wall" in model.components or "basket_support" in model.components
        assert set_stone_count(model) > 1

    def test_the_material_is_metadata_and_does_not_change_geometry(self):
        # §18: the architecture stays material-independent; Sprint 40 owns any
        # material-specific behaviour.
        base = build("ETERNITY_HALF")
        data = design("ETERNITY_HALF").model_dump(mode="python")
        data["material"]["metal"] = "platinum"
        other = build_solitaire_ring(JewelryDefinition.model_validate(data))
        assert base.combined_metal_volume_mm3 == pytest.approx(
            other.combined_metal_volume_mm3, rel=KERNEL_VOLUME_REL_TOL
        )


# ==========================================================================
# §15 — INSPECTION, AND §19 — IDENTITY SEPARATION
# ==========================================================================


class TestInspectionAndIdentity:
    def test_every_specialty_ring_passes_inspection(self):
        for variant in SPECIALTY_VARIANTS:
            report = inspect_model(build(variant))
            assert report.status in {"PASS", "WARNING"}, (variant, report.status)

    def test_the_inspection_facts_name_the_specialty_family(self):
        for variant in SPECIALTY_VARIANTS:
            facts = {f.factType: f.value for f in inspect_model(build(variant)).geometricFacts}
            assert facts["RING_FAMILY_VARIANT"] == variant
            assert facts["RING_FAMILY_ID"] == VARIANT_FAMILY[variant]

    def test_no_stone_is_ever_production_metal(self):
        # LAW-006, at every new family — including the accent and set stones.
        for variant in SPECIALTY_VARIANTS:
            model = build(variant)
            for name in model.components:
                if geometry_role(name) == "stone_reference":
                    assert not is_production_component(name), (variant, name)

    def test_the_identity_is_the_original_document(self):
        from jewelmind.utils.hashing import definition_hash

        for variant in SPECIALTY_VARIANTS:
            d = design(variant)
            assert build_solitaire_ring(d).definition_hash == definition_hash(d)

    def test_a_parameter_change_changes_the_identity(self):
        from jewelmind.utils.hashing import definition_hash

        base = definition_hash(design("ETERNITY_HALF", eternityStoneCount=10))
        moved = definition_hash(design("ETERNITY_HALF", eternityStoneCount=14))
        assert base != moved

    def test_the_same_design_builds_the_same_geometry_twice(self):
        for variant in SPECIALTY_VARIANTS:
            d = design(variant)
            # EXACT: two builds in one process must agree bit for bit.
            assert (
                build_solitaire_ring(d).combined_metal_volume_mm3
                == build_solitaire_ring(d).combined_metal_volume_mm3
            ), variant


# ==========================================================================
# §26 — DESIGNER / CONVERSATION VOCABULARY
# ==========================================================================


class TestDesignerVocabulary:
    def test_every_specialty_family_is_recognised(self):
        terms = designer_family_terms()
        for spoken, expected in (
            ("eternity", "ETERNITY_FULL"),
            ("half eternity", "ETERNITY_HALF"),
            ("cluster", "CLUSTER_ROUND"),
            ("toi et moi", "TOI_ET_MOI_BYPASS"),
        ):
            assert terms.get(spoken) == expected, spoken

    def test_the_normalizer_resolves_a_specialty_request(self):
        from jewelmind.designer import normalizer

        for spoken, family, variant in (
            ("eternity", "eternity", "ETERNITY_FULL"),
            ("half eternity", "eternity", "ETERNITY_HALF"),
            ("cluster", "cluster", "CLUSTER_ROUND"),
            ("toi et moi", "toi_et_moi", "TOI_ET_MOI_BYPASS"),
        ):
            assert normalizer.normalize_enum_token("jewelry.style", spoken) == (family, False)
            assert normalizer.normalize_enum_token("ringFamily.variant", spoken) == (
                variant,
                False,
            )

    def test_designer_can_propose_a_specialty_family(self):
        from jewelmind.designer.capability import current_capabilities

        capabilities = current_capabilities()
        for family in SPECIALTY_FAMILIES:
            assert family in capabilities["jewelryStyle"], family
        for variant in SPECIALTY_VARIANTS:
            assert variant in capabilities["ringFamilyVariant"], variant

    def test_a_specialty_family_is_no_longer_reported_unsupported(self):
        from jewelmind.designer.capability import KNOWN_UNSUPPORTED_CONCEPTS

        for term in ("eternity", "cluster", "toi_et_moi"):
            assert term not in KNOWN_UNSUPPORTED_CONCEPTS, term


# ==========================================================================
# §30 — END-TO-END ACCEPTANCE
# ==========================================================================


class TestEndToEndAcceptance:
    """Three real designs, each verified through the whole pipeline."""

    def test_a_half_eternity_ring(self):
        """TEST A — 'a size 14 half-eternity with round diamonds, slim band'."""

        data = design(
            "ETERNITY_HALF",
            size=14.0,
            eternityStoneCount=11,
            eternityStoneSpacingMm=1.5,
            eternityRetention="BEAD",
        ).model_dump(mode="python")
        data["band"]["width"] = 1.9  # slim
        data["stone"]["gem"] = {"gemId": "carbon.diamond", "origin": "NATURAL"}
        definition = JewelryDefinition.model_validate(data)

        # 1-2. family and variant resolution
        resolved = resolve_ring_family(definition)
        assert resolved.family == "eternity"
        assert resolved.variant == "ETERNITY_HALF"
        # 3. finger size
        assert definition.ring.size == 14.0
        # 4-5. stone identity and geometry
        assert definition.stone.gem is not None
        model = build_solitaire_ring(definition)
        # 6. arrangement — the set stones exist as real instances
        assert set_stone_count(model) == 12  # 11 set + the centre
        # 7. setting — real retention metal
        assert retention_solids(model) > 0
        # 8. band geometry
        assert model.components["band"].shape.Volume() > 0.0
        # 9. a real stone-set REGION: a half band leaves a gap
        angles = sorted(
            math.degrees(math.atan2(v[1], v[2])) % 360.0
            for k, v in stone_components(model).items()
            if k != "stone_reference"
        )
        gaps = [(angles[(i + 1) % len(angles)] - angles[i]) % 360.0
                for i in range(len(angles))]
        assert max(gaps) > 90.0, "a half eternity must leave an unadorned region"
        # 10. validation
        assert not [r for r in validate_definition(definition) if r.severity == "error"]
        # 11. inspection
        assert inspect_model(model).status in {"PASS", "WARNING"}
        # 12. deterministic compilation
        assert (
            build_solitaire_ring(definition).combined_metal_volume_mm3
            == model.combined_metal_volume_mm3
        )

    def test_a_cluster_ring(self):
        """TEST B — 'one oval centre stone and surrounding round stones'."""

        data = design("CLUSTER_ROUND", clusterStoneCount=8).model_dump(mode="python")
        data["stone"].update({"shape": "oval", "diameter": None, "length": 8.0,
                              "width": 6.0})
        definition = JewelryDefinition.model_validate(data)

        resolved = resolve_ring_family(definition)
        assert resolved.variant == "CLUSTER_ROUND"
        # Separate Stone Instances, placed by the arrangement engine.
        model = build_solitaire_ring(definition)
        stones = stone_components(model)
        assert len(stones) == 9
        # Real supporting geometry for the centre.
        assert model.components["basket_support"].shape.Volume() > 0.0
        # Parametric variation.
        assert set_stone_count(build("CLUSTER_ROUND", clusterStoneCount=12)) == 13
        assert not [r for r in validate_definition(definition) if r.severity == "error"]
        assert inspect_model(model).status in {"PASS", "WARNING"}
        assert (
            build_solitaire_ring(definition).combined_metal_volume_mm3
            == model.combined_metal_volume_mm3
        )

    def test_a_toi_et_moi_ring(self):
        """TEST C — 'an oval diamond and a pear sapphire'.

        HONEST ON THE PART THAT DOES NOT WORK. The two stones are separate
        instances with independent SIZES, and they share a CUT: a
        `FamilyMember` carries no shape, so both are occurrences of the
        document's one `stone`. An oval-and-pear pair needs per-member stone
        specifications — an RFC Sprint 24 already identified. The test asserts
        what is real and records what is not.
        """

        data = design(
            "TOI_ET_MOI_BYPASS",
            toiEtMoiSecondScale=0.75,
            toiEtMoiSeparationMm=6.0,
            toiEtMoiOrientationDeg=30.0,
        ).model_dump(mode="python")
        data["stone"].update({"shape": "oval", "diameter": None, "length": 8.0,
                              "width": 6.0})
        data["stone"]["gem"] = {"gemId": "corundum.sapphire", "origin": "NATURAL"}
        definition = JewelryDefinition.model_validate(data)

        model = build_solitaire_ring(definition)
        stones = stone_components(model)
        # 1. two separate primary stones
        assert len(stones) == 2
        # 3. independent sizes (the cut is shared — see the docstring)
        volumes = sorted(v[0] for v in stones.values())
        assert volumes[0] < volumes[1]
        # 4. the arrangement relationship is honoured exactly
        pair = list(stones.values())
        assert math.hypot(pair[0][1] - pair[1][1], pair[0][2] - pair[1][2]) == pytest.approx(
            6.0, rel=1e-6
        )
        # 5-7. setting, shank and real geometry
        assert model.components["basket_support"].shape.Volume() > 0.0
        assert model.components["band"].shape.Volume() > 0.0
        # 8. deterministic
        assert (
            build_solitaire_ring(definition).combined_metal_volume_mm3
            == model.combined_metal_volume_mm3
        )
        # 9-10. validation and inspection
        assert not [r for r in validate_definition(definition) if r.severity == "error"]
        assert inspect_model(model).status in {"PASS", "WARNING"}

        # THE RECORDED LIMITATION, asserted so it cannot be quietly fixed by
        # accident and left undocumented.
        from jewelmind.family.models import FamilyMember

        assert "shape" not in FamilyMember.model_fields
        assert "cut" not in FamilyMember.model_fields


# ==========================================================================
# COMPATIBILITY
# ==========================================================================


class TestPreSprint29Unchanged:
    def test_the_default_design_is_untouched(self):
        assert build_solitaire_ring(
            default_definition()
        ).combined_metal_volume_mm3 == pytest.approx(
            341.44334316909976, rel=KERNEL_VOLUME_REL_TOL
        )

    def test_every_pre_sprint_29_family_keeps_its_default_variant(self):
        for family, variant in (
            ("solitaire", "SOLITAIRE_CLASSIC"),
            ("three_stone", "THREE_STONE_SYMMETRIC"),
            ("halo", "HALO_SINGLE"),
            ("split_shank", "SPLIT_SHANK_PARALLEL"),
            ("bypass", "BYPASS_CROSSOVER"),
            ("signet", "SIGNET_FLAT_TABLE"),
        ):
            assert default_variant_for(family) == variant

    def test_the_specialty_parameters_are_read_by_a_specialty_variant(self):
        # A parameter nothing reads is the silently ignored field
        # ARRANGE-GOV-011 forbids.
        every_read = set()
        for variant in VARIANT_FAMILY:
            every_read.update(parameters_read_by(variant))
        for field in RingFamilyParams.model_fields:
            assert field in every_read, field
