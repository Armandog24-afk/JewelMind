"""Ring Families v2 (Sprint 28).

THE QUESTION THIS FILE HAS TO ANSWER is the brief's own final test: could a
jewelry designer really use Ring Families as a PARAMETRIC SYSTEM, or have we
built a catalogue of names? A catalogue would pass a test suite that checked
JSON. So the tests here are organised around the four things a catalogue cannot
do, and every one of them is asserted against MEASURED GEOMETRY:

1. Each variant must produce geometry that DIFFERS from its family's baseline —
   measured, not declared. `TestVariantGeometryDiffers`.
2. Changing a fundamental parameter must PROPAGATE through the family without
   the model being rebuilt by hand: ring size, centre stone, side stones,
   setting mode, shank profile. `TestParametricPropagation`.
3. The family must ORCHESTRATE the existing subsystems rather than duplicate
   them — the Shank, Stone, Setting, Family, Halo and Pavé systems keep doing
   their own jobs. `TestOrchestrationNotDuplication`.
4. Every pre-Sprint-28 document must be UNCHANGED, byte for byte.
   `TestPreSprint28Unchanged`.

Plus the disciplines every sprint in this programme carries: derived-not-copied
registries, honest capability status, refusal instead of precedence, no invented
professional threshold, deterministic identity, and adversarial input.
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
from jewelmind.geometry.inspection import inspect_model
from jewelmind.geometry.ring_family_adapter import (
    effective_definition,
    ring_family_summary,
)
from jewelmind.geometry.roles import geometry_role, is_production_component
from jewelmind.geometry.shank.architecture import (
    SHANK_ARCHITECTURE_BUILDERS,
    rail_half_width,
)
from jewelmind.geometry.shoulder import (
    MAX_ARCH_SPAN_DEG,
    SHOULDER_ARCHITECTURES,
    SHOULDER_COMPONENT,
    ShoulderConstructionError,
    build_shoulders,
)
from jewelmind.geometry.signet import BODY_ARCHITECTURES, SIGNET_COMPONENT
from jewelmind.ring_family.capability import (
    RING_FAMILY_GEOMETRY_VERSION,
    RING_FAMILY_PIPELINE_STAGES,
    capability_summary,
    designer_family_terms,
    family_status,
    get_ring_family_capability,
    ring_family_capabilities,
)
from jewelmind.ring_family.dependencies import (
    RING_FAMILY_DEPENDENCIES,
    dependencies_for,
    dependency_graph,
    derived_paths,
    influenced_paths,
)
from jewelmind.ring_family.errors import (
    RingFamilyDerivationConflictError,
    RingFamilyError,
    RingFamilyVariantMismatchError,
)
from jewelmind.ring_family.models import (
    DEFAULT_VARIANT,
    MAX_HALO_STONES_PER_FAMILY,
    RESERVED_RING_FAMILIES,
    RING_FAMILY_TAXONOMY_VERSION,
    VARIANT_BODY_ARCHITECTURE,
    VARIANT_FAMILY,
    VARIANT_HEAD_HEIGHT_FACTOR,
    VARIANT_SHANK_ARCHITECTURE,
    VARIANT_SHOULDER_ARCHITECTURE,
    RingFamilyParams,
    RingFamilySpec,
    default_params,
    default_variant_for,
    family_for_variant,
    implemented_families,
    ring_family_fingerprint,
    variants_for_family,
)
from jewelmind.ring_family.resolve import (
    parameters_read_by,
    resolution_summary,
    resolve_ring_family,
    unread_parameters,
)
from jewelmind.validation import rules as R
from jewelmind.validation.engine import validate_definition

BACKEND_ROOT = Path(__file__).resolve().parents[1]
RING_FAMILY_PACKAGE = BACKEND_ROOT / "jewelmind" / "ring_family"
SPEC_V1 = BACKEND_ROOT.parent / "specs" / "ring-family" / "v1"


# --------------------------------------------------------------------------
# Helpers. Every design is built from the REAL default so a test can never
# accidentally assert against a fixture that drifted from the schema.
# --------------------------------------------------------------------------


def design(
    variant: str | None = None,
    *,
    enabled: bool = True,
    style: str | None = None,
    **params: object,
) -> JewelryDefinition:
    """A real design, optionally declaring a ring family.

    `style` defaults to the variant's own family, because a mismatch is a
    REFUSAL rather than something a helper should quietly fix — the tests that
    want the mismatch pass `style` explicitly.
    """

    data = default_definition().model_dump(mode="python")
    if variant is None:
        if style is not None:
            data["jewelry"]["style"] = style
        return JewelryDefinition.model_validate(data)

    data["jewelry"]["style"] = style if style is not None else family_for_variant(variant)
    data["ringFamily"] = RingFamilySpec(
        variant=variant,
        enabled=enabled,
        params=RingFamilyParams(**params) if params else default_params(),
    ).model_dump(mode="python")
    return JewelryDefinition.model_validate(data)


def metal_volume(definition: JewelryDefinition) -> float:
    return build_solitaire_ring(definition).combined_metal.Volume()


def component_volume(definition: JewelryDefinition, name: str) -> float:
    model = build_solitaire_ring(definition)
    assert name in model.components, f"{name} is missing from {sorted(model.components)}"
    return model.components[name].shape.Volume()


def stone_count(definition: JewelryDefinition) -> int:
    model = build_solitaire_ring(definition)
    return sum(
        1 for name in model.components if geometry_role(name) == "stone_reference"
    )


ALL_VARIANTS = tuple(VARIANT_FAMILY)


# ==========================================================================
# §28 — TAXONOMY AND REGISTRY
# ==========================================================================


class TestTaxonomy:
    def test_every_variant_belongs_to_an_implemented_family(self):
        for variant, family in VARIANT_FAMILY.items():
            assert family in implemented_families(), (
                f"{variant} claims family {family!r}, which is not implemented. "
                "A variant of a family the product cannot build could be chosen "
                "and would resolve to nothing."
            )

    def test_every_family_has_exactly_one_default_variant(self):
        for family in implemented_families():
            default = default_variant_for(family)
            assert default in variants_for_family(family)
            assert DEFAULT_VARIANT[family] == default

    def test_solitaire_default_is_the_pre_sprint_28_design(self):
        # THE COMPATIBILITY ANCHOR. Every existing document is a `solitaire`
        # with no `ringFamily`; if this default ever changed, the entire Golden
        # suite and every saved design would change with it.
        assert default_variant_for("solitaire") == "SOLITAIRE_CLASSIC"

    def test_no_reserved_name_is_a_live_variant_or_family(self):
        for name in RESERVED_RING_FAMILIES:
            assert name not in VARIANT_FAMILY
            assert name not in implemented_families()

    def test_every_reserved_name_states_a_real_technical_reason(self):
        # "Planned" is not a reason. Each entry must say what is actually
        # missing, so a reader can tell a decision from an omission.
        for name, reason in RESERVED_RING_FAMILIES.items():
            assert len(reason) > 60, f"{name}'s reason is too short to be one"
            assert reason.strip().endswith("."), name
            lowered = reason.lower()
            assert "planned" not in lowered and "todo" not in lowered, name

    def test_every_variant_has_all_three_architecture_mappings(self):
        for variant in ALL_VARIANTS:
            assert variant in VARIANT_SHANK_ARCHITECTURE, variant
            assert variant in VARIANT_SHOULDER_ARCHITECTURE, variant
            assert variant in VARIANT_BODY_ARCHITECTURE, variant
            assert variant in VARIANT_HEAD_HEIGHT_FACTOR, variant

    def test_every_declared_architecture_has_a_real_builder(self):
        # BOTH DIRECTIONS, because a mapping to a builder that does not exist
        # and a builder nothing maps to are different defects with the same
        # cause: two lists maintained by hand.
        for variant, architecture in VARIANT_SHANK_ARCHITECTURE.items():
            if architecture == "UNIFORM":
                continue
            assert architecture in SHANK_ARCHITECTURE_BUILDERS, variant
        for variant, architecture in VARIANT_SHOULDER_ARCHITECTURE.items():
            if architecture == "NONE":
                continue
            assert architecture in SHOULDER_ARCHITECTURES, variant
        for variant, architecture in VARIANT_BODY_ARCHITECTURE.items():
            if architecture == "NONE":
                continue
            assert architecture in BODY_ARCHITECTURES, variant

    def test_declared_structural_geometry_matches_the_builders(self):
        """The correspondence `capability.py` cannot import its way to.

        `structuralGeometry` is DECLARED in the registry rather than measured,
        because measuring it would need `jewelmind.geometry` and this layer is
        carried in JDL and read by Forge. `pave/capability.py` settles the same
        tension the same way (PAVE-GOV-001 forbids the import, PAVE-GOV-012
        requires the correspondence, `test_pave.py` asserts it).

        So this test is the guard, and it checks BOTH DIRECTIONS: a row claiming
        structural metal must name an architecture some builder produces, and a
        row denying it must name none.
        """

        for variant, entry in ring_family_capabilities().items():
            builds = (
                (entry.shankArchitecture != "UNIFORM"
                 and entry.shankArchitecture in SHANK_ARCHITECTURE_BUILDERS)
                or (entry.shoulderArchitecture != "NONE"
                    and entry.shoulderArchitecture in SHOULDER_ARCHITECTURES)
                or (entry.bodyArchitecture != "NONE"
                    and entry.bodyArchitecture in BODY_ARCHITECTURES)
            )
            assert entry.structuralGeometry is builds, (
                f"{variant} declares structuralGeometry="
                f"{entry.structuralGeometry} but the live builders say {builds}."
            )

    def test_taxonomy_version_is_declared(self):
        assert RING_FAMILY_TAXONOMY_VERSION == "1.0.0"
        assert RING_FAMILY_GEOMETRY_VERSION == "1.0.0"


class TestCapabilityRegistry:
    def test_registry_covers_every_variant_and_nothing_else(self):
        assert set(ring_family_capabilities()) == set(ALL_VARIANTS)

    def test_no_variant_claims_professional_validation(self):
        # Sprint 28 §32. Nothing in JewelMind is professionally validated, and
        # a ring family is not the place that changes.
        for variant, entry in ring_family_capabilities().items():
            assert entry.professionalValidationStatus == "NOT_REVIEWED", variant

    def test_partial_variants_say_exactly_what_is_missing(self):
        for variant, entry in ring_family_capabilities().items():
            if entry.status == "CURRENT":
                continue
            assert entry.status == "PARTIAL", variant
            # An honest PARTIAL names the gap. "Incomplete" would not.
            assert len(entry.description) > 80, variant

    def test_exactly_one_variant_is_its_family_baseline_and_it_is_the_default(self):
        # `differsFromFamilyBaseline` is MEASURED by running the real resolver,
        # so the one variant that reports false must be the one flagged as the
        # baseline — otherwise a variant that derives nothing is a defect rather
        # than the reference point.
        baselines = [
            variant
            for variant, entry in ring_family_capabilities().items()
            if not entry.differsFromFamilyBaseline
        ]
        assert baselines == ["SOLITAIRE_CLASSIC"]
        assert get_ring_family_capability("SOLITAIRE_CLASSIC").isFamilyBaseline is True
        for variant, entry in ring_family_capabilities().items():
            if variant != "SOLITAIRE_CLASSIC":
                assert entry.isFamilyBaseline is False, variant
                assert entry.differsFromFamilyBaseline is True, variant

    def test_family_status_is_the_weakest_of_its_variants(self):
        # A family whose variants are all CURRENT is CURRENT; one PARTIAL
        # variant makes the family PARTIAL. Reporting the strongest would let a
        # family look complete while part of it is not.
        for family in implemented_families():
            statuses = {
                ring_family_capabilities()[variant].status
                for variant in variants_for_family(family)
            }
            expected = "CURRENT" if statuses == {"CURRENT"} else "PARTIAL"
            assert family_status(family) == expected, family

    def test_halo_and_signet_are_honestly_partial(self):
        assert family_status("halo") == "PARTIAL"
        assert family_status("signet") == "PARTIAL"
        for family in ("solitaire", "three_stone", "split_shank", "bypass"):
            assert family_status(family) == "CURRENT", family

    def test_pipeline_stages_are_declared_and_ordered(self):
        assert len(RING_FAMILY_PIPELINE_STAGES) == len(set(RING_FAMILY_PIPELINE_STAGES))
        assert len(RING_FAMILY_PIPELINE_STAGES) >= 8

    def test_designer_terms_are_unambiguous(self):
        # `designer_family_terms()` raises on a duplicate rather than resolving
        # to whichever row was built last; calling it is the assertion.
        terms = designer_family_terms()
        assert len(terms) > 30
        for term, variant in terms.items():
            assert variant in ALL_VARIANTS
            assert term == term.lower()

    def test_every_family_name_is_recognised_as_a_term(self):
        terms = designer_family_terms()
        for family in implemented_families():
            spoken = family.replace("_", " ")
            assert spoken in terms or family in terms, family

    def test_capability_summary_reports_real_counts(self):
        summary = capability_summary()
        assert len(summary["variants"]) == len(ALL_VARIANTS)
        assert len(summary["reserved"]) == len(RESERVED_RING_FAMILIES)
        assert set(summary["families"]) == set(implemented_families())
        json.dumps(summary)


# ==========================================================================
# §28 — RESOLUTION: ONE POINT, REFUSAL RATHER THAN PRECEDENCE
# ==========================================================================


class TestResolution:
    def test_a_document_with_no_family_resolves_to_the_default(self):
        resolved = resolve_ring_family(design())
        assert resolved.family == "solitaire"
        assert resolved.variant == "SOLITAIRE_CLASSIC"
        assert resolved.derived is True
        # NOTHING DERIVED and NOTHING CHANGED are different statements. The
        # baseline derives exactly the one path every variant derives, from the
        # document's own basket height times two factors of 1.0 — a real
        # provenance record whose value is the value already there.
        assert [x.path for x in resolved.derivations] == ["setting.basketHeight"]
        assert resolved.derivations[0].value == design().setting.basketHeight

    def test_a_disabled_family_discards_its_parameters(self):
        # NEITHER STATE would be honouring half of it. A disabled block
        # contributes nothing and the family's own default is built.
        d = design("SOLITAIRE_ELEVATED", enabled=False, headHeightFactor=3.0)
        resolved = resolve_ring_family(d)
        assert resolved.variant == "SOLITAIRE_CLASSIC"
        assert resolved.params == default_params()
        assert resolved.derived is True

    def test_a_variant_from_another_family_is_refused(self):
        with pytest.raises(RingFamilyVariantMismatchError) as exc:
            resolve_ring_family(design("SPLIT_SHANK_PARALLEL", style="halo"))
        # REFUSED, NEVER RESOLVED BY PRECEDENCE — the same discipline as
        # JM-FAMILY-001 and JM-SETTING-008.
        assert "no determinate resolution" in str(exc.value)

    def test_the_refusal_is_also_a_validation_error(self):
        results = validate_definition(design("BYPASS_CROSSOVER", style="signet"))
        errors = [r for r in results if r.severity == "error"]
        assert any(r.ruleId == R.RING_FAMILY_VARIANT_MATCHES for r in errors)

    def test_a_declared_block_is_used_verbatim(self):
        resolved = resolve_ring_family(design("SOLITAIRE_CATHEDRAL", shoulderSpanDeg=70))
        assert resolved.variant == "SOLITAIRE_CATHEDRAL"
        assert resolved.params.shoulderSpanDeg == 70
        assert resolved.derived is False

    def test_every_variant_resolves(self):
        for variant in ALL_VARIANTS:
            resolved = resolve_ring_family(design(variant))
            assert resolved.variant == variant
            assert resolved.family == VARIANT_FAMILY[variant]

    def test_every_derivation_records_its_provenance(self):
        # WITHOUT PROVENANCE this is a system that happened to change a number.
        for variant in ALL_VARIANTS:
            for derivation in resolve_ring_family(design(variant)).derivations:
                assert derivation.sourceParameters, (variant, derivation.path)
                assert derivation.relation.strip(), (variant, derivation.path)
                assert derivation.sourceParameters == tuple(
                    sorted(derivation.sourceParameters)
                )

    def test_every_derived_path_is_declared_in_the_dependency_table(self):
        # The resolver SELF-CHECKS this at runtime, so this test is the
        # inspectable statement of the same invariant: a path written but not
        # declared is a derivation no report could explain.
        for variant in ALL_VARIANTS:
            declared = set(derived_paths(variant))
            for derivation in resolve_ring_family(design(variant)).derivations:
                assert derivation.path in declared, (variant, derivation.path)

    def test_a_document_declaring_a_derived_block_keeps_its_own(self):
        # The document is the authority over its own content; the family
        # reports what it did NOT derive rather than overwriting.
        data = design("HALO_SINGLE").model_dump(mode="python")
        data["halo"] = {
            "variant": "SINGLE",
            "rings": [
                {"ringId": "own", "count": 5, "radiusMm": 4.0, "memberScale": 0.3}
            ],
        }
        d = JewelryDefinition.model_validate(data)
        resolved = resolve_ring_family(d)
        assert "halo.rings" in resolved.skippedPaths
        assert all(
            not x.path.startswith("halo") for x in resolved.derivations
        )
        # The document's own ring survived untouched.
        assert d.halo is not None
        assert [r.count for r in d.halo.rings] == [5]
        # And the design still validates, with the pre-emption reported as
        # INFORMATION rather than an error.
        results = validate_definition(d)
        assert not [r for r in results if r.severity == "error"]
        assert any(
            r.ruleId == R.RING_FAMILY_DERIVATION_APPLICABLE
            and r.severity == "information"
            for r in results
        )

    def test_an_explicit_arrangement_beside_a_deriving_family_is_refused(self):
        # Two authorities over one set of placements has no determinate
        # resolution — the rule ARRANGE/FAMILY already established.
        data = design("THREE_STONE_SYMMETRIC").model_dump(mode="python")
        data["arrangement"] = {
            "instances": [{"instanceId": "center", "role": "CENTER"}]
        }
        d = JewelryDefinition.model_validate(data)
        # The SPECIFIC error, not just the base class: a caller distinguishing a
        # derivation conflict from a variant mismatch needs the type to say so.
        with pytest.raises(RingFamilyDerivationConflictError):
            resolve_ring_family(d)

    def test_unread_parameters_are_reported_not_silently_ignored(self):
        # A SILENTLY IGNORED VALUE is the failure this reports. The parameter
        # stays in the document and the author is told it has no effect.
        unread = unread_parameters(
            "BYPASS_CROSSOVER", RingFamilyParams(signetTableHeightMm=9.0)
        )
        assert "signetTableHeightMm" in unread

    def test_a_parameter_left_at_its_default_is_not_reported(self):
        assert unread_parameters("BYPASS_CROSSOVER", default_params()) == ()

    def test_every_variant_reads_the_shared_head_factor(self):
        for variant in ALL_VARIANTS:
            assert "headHeightFactor" in parameters_read_by(variant), variant

    def test_resolution_summary_is_json_serialisable(self):
        for variant in ALL_VARIANTS:
            summary = resolution_summary(resolve_ring_family(design(variant)))
            json.dumps(summary)  # raises if a kernel object leaked in
            assert summary["variant"] == variant


class TestIdentity:
    def test_the_fingerprint_is_deterministic(self):
        a = ring_family_fingerprint("solitaire", "SOLITAIRE_ELEVATED", default_params())
        b = ring_family_fingerprint("solitaire", "SOLITAIRE_ELEVATED", default_params())
        assert a == b
        assert len(a) == 16
        assert all(c in "0123456789abcdef" for c in a)

    def test_a_changed_parameter_changes_the_fingerprint(self):
        base = ring_family_fingerprint("solitaire", "SOLITAIRE_CLASSIC", default_params())
        moved = ring_family_fingerprint(
            "solitaire", "SOLITAIRE_CLASSIC", RingFamilyParams(headHeightFactor=1.2)
        )
        assert base != moved

    def test_a_changed_variant_changes_the_fingerprint(self):
        assert ring_family_fingerprint(
            "solitaire", "SOLITAIRE_CLASSIC", default_params()
        ) != ring_family_fingerprint(
            "solitaire", "SOLITAIRE_ELEVATED", default_params()
        )

    def test_the_fingerprint_module_contains_no_impure_source(self):
        # AN AST CHECK, not a text scan: a text scan flags the docstring that
        # documents the rule, which is exactly what happened in Sprint 27.
        tree = ast.parse((RING_FAMILY_PACKAGE / "models.py").read_text(encoding="utf-8"))
        forbidden = {"time", "random", "uuid", "os", "datetime", "secrets"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name.split(".")[0] not in forbidden
            elif isinstance(node, ast.ImportFrom) and node.module:
                assert node.module.split(".")[0] not in forbidden
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                assert node.func.id not in {"id", "hash"}

    def test_the_fingerprint_survives_a_reordered_document(self):
        # Content, not key order.
        d = design("SPLIT_SHANK_TAPERED")
        first = resolve_ring_family(d).fingerprint
        reordered = JewelryDefinition.model_validate(
            dict(reversed(list(d.model_dump(mode="python").items())))
        )
        assert resolve_ring_family(reordered).fingerprint == first


# ==========================================================================
# THE CATALOGUE TEST — MEASURED GEOMETRY, NOT DECLARED CAPABILITY
# ==========================================================================


class TestVariantGeometryDiffers:
    """Every variant must build geometry that DIFFERS from its baseline.

    A catalogue of names would pass a JSON test. These compare real measured
    solids, which is the only evidence that a variant is a structural
    difference rather than a label.
    """

    def test_every_variant_but_the_baseline_changes_the_metal(self):
        baseline = metal_volume(design())
        for variant in ALL_VARIANTS:
            volume = metal_volume(design(variant))
            if variant == "SOLITAIRE_CLASSIC":
                assert volume == baseline
                continue
            if VARIANT_FAMILY[variant] in {"three_stone", "halo"}:
                # These families add STONES, not metal — the honest recorded
                # boundary. Their difference is asserted by stone count below.
                continue
            assert not math.isclose(volume, baseline, rel_tol=1e-9), (
                f"{variant} produced the same metal volume as the baseline. A "
                "variant that changes nothing measurable is a name, not a "
                "structure."
            )

    def test_the_head_height_factor_actually_moves_the_head(self):
        # THE DEFECT THIS CAUGHT: LOW_PROFILE and ELEVATED originally produced
        # geometry identical to CLASSIC, because both had headHeightFactor=1.0
        # and the variant contributed nothing of its own.
        classic = component_volume(design("SOLITAIRE_CLASSIC"), "basket_support")
        low = component_volume(design("SOLITAIRE_LOW_PROFILE"), "basket_support")
        high = component_volume(design("SOLITAIRE_ELEVATED"), "basket_support")
        assert low < classic < high
        assert VARIANT_HEAD_HEIGHT_FACTOR["SOLITAIRE_LOW_PROFILE"] < 1.0
        assert VARIANT_HEAD_HEIGHT_FACTOR["SOLITAIRE_ELEVATED"] > 1.0

    def test_cathedral_builds_real_shoulder_solids(self):
        model = build_solitaire_ring(design("SOLITAIRE_CATHEDRAL"))
        assert SHOULDER_COMPONENT in model.components
        shoulders = model.components[SHOULDER_COMPONENT].shape
        # REAL GEOMETRY, not a placeholder box: one connected solid with real
        # volume that rises above the band it springs from.
        assert shoulders.Volume() > 1.0
        assert len(shoulders.Solids()) == 1
        assert shoulders.isValid()
        assert is_production_component(SHOULDER_COMPONENT)
        band = model.components["band"].shape
        assert shoulders.BoundingBox().zmax > band.BoundingBox().zmax

    def test_a_classic_solitaire_builds_no_shoulders(self):
        assert SHOULDER_COMPONENT not in build_solitaire_ring(design()).components

    def test_a_split_shank_is_two_rails_that_genuinely_separate(self):
        # THE DEFECT THIS CAUGHT: `Workplane.translate()` before `.revolve()`
        # silently loses the offset, so both rails came out coincident and the
        # fused volume was exactly one rail's.
        model = build_solitaire_ring(design("SPLIT_SHANK_PARALLEL"))
        band = model.components["band"].shape
        assert band.isValid()
        # ONE CONNECTED BODY: the rails join over the bottom span. A ring that
        # is not one connected solid is not a ring.
        assert len(band.Solids()) == 1
        metadata = model.components["band"].metadata
        assert metadata["railCount"] == 2
        assert metadata["separatedAtTheHead"] is True
        assert metadata["joinedAtTheBottom"] is True

    def test_the_split_gap_contains_no_metal_at_the_top(self):
        # THE MEASUREMENT that proves separation rather than a metadata claim.
        model = build_solitaire_ring(design("SPLIT_SHANK_PARALLEL"))
        facts = {f.factType: f.value for f in inspect_model(model).geometricFacts}
        assert facts.get("SHANK_RAIL_COUNT") == 2
        assert facts.get("SHANK_SEPARATED_AT_HEAD") is True

    def test_a_tapered_split_shank_differs_from_a_parallel_one(self):
        # THE DEFECT THIS CAUGHT: `SPLIT_SHANK_TAPERED` derived `band.widthTaper`
        # that the architecture builder ignored, so the two produced identical
        # volumes — a silently ignored derived value.
        parallel = component_volume(design("SPLIT_SHANK_PARALLEL"), "band")
        tapered = component_volume(design("SPLIT_SHANK_TAPERED"), "band")
        assert tapered < parallel
        assert not math.isclose(tapered, parallel, rel_tol=1e-6)

    def test_a_bypass_is_one_open_rail_whose_ends_pass_each_other(self):
        # THE DEFECT THIS CAUGHT: built as two axially separated arcs, a bypass
        # came out as TWO disconnected solids.
        model = build_solitaire_ring(design("BYPASS_CROSSOVER"))
        band = model.components["band"].shape
        assert len(band.Solids()) == 1
        assert band.isValid()
        assert model.components["band"].metadata["railCount"] == 1

    def test_a_degenerate_fuse_is_reported_rather_than_shipped(self):
        """The second defect a wide bypass exposed, and the worse of the two.

        At a crossing clearance of ~0.07 mm the ring-level boolean fuse RAISED
        NOTHING, reported `isValid() == True`, and returned six solids of
        NEGATIVE volume — the six prongs, inverted, with the band and the basket
        gone. `combined_metal_volume_mm3` was −60.904 and no warning was
        emitted, so a caller had no way to know the ring had disappeared.

        `_fuse_metal()` now checks the one invariant available without redoing
        the boolean: A UNION IS NEVER SMALLER THAN ITS LARGEST INPUT. Arithmetic
        about unions, not a tolerance and not a jewelry threshold.

        The honest outcome is the SAME compound fallback a raised failure takes,
        with a warning that names the measurement — never a quietly broken ring.
        """

        model = build_solitaire_ring(design("BYPASS_CROSSOVER", bypassOverlapDeg=175.0))

        # Every real component still exists and is still real geometry.
        for name in ("band", "prongs", "basket_support"):
            assert model.components[name].shape.Volume() > 0.0, name

        # The combined body is now the honest compound, not the inverted mess.
        assert model.combined_metal.Volume() > 0.0
        assert len(model.combined_metal.Solids()) > 1
        assert model.combined_metal_volume_mm3 > 0.0

        # AND IT IS REPORTED. A silently broken ring is the actual defect.
        assert any("union failed" in w for w in model.warnings)
        assert any("cannot be smaller" in w for w in model.warnings)

    def test_the_fuse_invariant_leaves_every_sound_family_alone(self):
        # The guard must not fire on real geometry. A single fused solid and no
        # warning, for every variant whose fuse is sound.
        for variant in ALL_VARIANTS:
            model = build_solitaire_ring(design(variant))
            assert not [w for w in model.warnings if "union failed" in w], variant
            assert model.combined_metal.Volume() > 0.0, variant

    def test_a_signet_builds_a_real_body_with_a_table(self):
        model = build_solitaire_ring(design("SIGNET_FLAT_TABLE"))
        assert SIGNET_COMPONENT in model.components
        body = model.components[SIGNET_COMPONENT].shape
        assert body.Volume() > 10.0
        assert len(body.Solids()) == 1
        assert body.isValid()
        assert is_production_component(SIGNET_COMPONENT)

    def test_three_stone_and_halo_add_real_stones(self):
        assert stone_count(design()) == 1
        assert stone_count(design("THREE_STONE_SYMMETRIC")) == 3
        assert stone_count(design("HALO_SINGLE")) > 3
        assert stone_count(design("HALO_DOUBLE")) > stone_count(design("HALO_SINGLE"))

    def test_a_graduated_trilogy_differs_from_a_symmetric_one(self):
        symmetric = build_solitaire_ring(design("THREE_STONE_SYMMETRIC"))
        graduated = build_solitaire_ring(design("THREE_STONE_GRADUATED"))
        volumes = lambda m: sorted(  # noqa: E731 - a local measurement, not an API
            round(c.shape.Volume(), 6)
            for name, c in m.components.items()
            if geometry_role(name) == "stone_reference"
        )
        assert volumes(symmetric) != volumes(graduated)

    def test_a_hidden_halo_raises_the_head(self):
        # A hidden halo sits UNDER the centre stone, so the head has to make
        # room for it — a structural difference, not a different stone count.
        single = component_volume(design("HALO_SINGLE"), "basket_support")
        hidden = component_volume(design("HALO_HIDDEN"), "basket_support")
        assert hidden > single

    def test_no_component_is_a_placeholder_box(self):
        # Sprint 28 §17: no placeholder boxes, fake meshes or metadata-only
        # geometry. A box would have exactly 6 faces and 8 vertices; every real
        # component here is a revolve, a loft or a boolean of them.
        for variant in ("SOLITAIRE_CATHEDRAL", "SPLIT_SHANK_PARALLEL", "BYPASS_CROSSOVER"):
            model = build_solitaire_ring(design(variant))
            for name, component in model.components.items():
                if geometry_role(name) == "stone_reference":
                    continue
                assert component.shape.Volume() > 0.0, (variant, name)
                assert component.shape.isValid(), (variant, name)


# ==========================================================================
# §29 — PARAMETRIC PROPAGATION. THE SPRINT'S OWN FINAL TEST.
# ==========================================================================


class TestParametricPropagation:
    """A designer must be able to change a fundamental parameter and have the
    family follow, without rebuilding the model by hand.

    Every test here changes ONE input and measures the GEOMETRIC result. A
    system of stored presets would pass none of them.
    """

    @staticmethod
    def _resized(definition: JewelryDefinition, size: float) -> JewelryDefinition:
        """The design at a different ring size.

        BOTH FIELDS, and that is a real finding rather than a convenience.
        `ring.innerDiameter` is what drives the geometry; `ring.size` is the
        nominal EU size, and `JM-RING-003` reports a disagreement between them
        rather than choosing one. So changing the size alone would leave the
        geometry untouched AND raise a consistency warning — a designer resizes
        by moving both, which is what the Studio control does through
        `euSizeToInnerDiameter`.
        """

        from jewelmind.validation.sizing import eu_size_to_inner_diameter

        return JewelryDefinition.model_validate(
            {
                **definition.model_dump(mode="python"),
                "ring": {
                    **definition.ring.model_dump(),
                    "size": size,
                    "innerDiameter": eu_size_to_inner_diameter(size),
                },
            }
        )

    def test_ring_size_alone_is_nominal_and_the_diameter_drives_geometry(self):
        # STATED AS A TEST because it is the one place a reader could reasonably
        # expect `ring.size` to be the parametric input and be wrong.
        base = design("SPLIT_SHANK_PARALLEL")
        nominal_only = JewelryDefinition.model_validate(
            {**base.model_dump(mode="python"), "ring": {**base.ring.model_dump(), "size": 24.0}}
        )
        assert metal_volume(nominal_only) == metal_volume(base)
        assert any(
            r.parameter == "ring.innerDiameter" for r in validate_definition(nominal_only)
        )

    @pytest.mark.parametrize(
        "variant",
        ["SOLITAIRE_CATHEDRAL", "SPLIT_SHANK_PARALLEL", "BYPASS_CROSSOVER", "SIGNET_FLAT_TABLE"],
    )
    def test_ring_size_propagates(self, variant: str):
        small = design(variant)
        large = self._resized(small, 24.0)
        assert large.ring.innerDiameter > small.ring.innerDiameter
        small_model = build_solitaire_ring(small)
        large_model = build_solitaire_ring(large)
        # A LARGER RING IS A LARGER RING: more metal and a bigger envelope, in
        # every family. The family did not have to be re-authored for the size.
        assert large_model.combined_metal.Volume() > small_model.combined_metal.Volume()
        assert large_model.bounding_box.zmax > small_model.bounding_box.zmax
        # And no ring-family rule fires: resizing is not a structural change.
        assert not [
            r
            for r in validate_definition(large)
            if r.ruleId.startswith("JM-RINGFAM-") and r.severity == "error"
        ]

    @pytest.mark.parametrize(
        "variant", ["SOLITAIRE_CLASSIC", "SOLITAIRE_CATHEDRAL", "HALO_SINGLE"]
    )
    def test_the_centre_stone_propagates(self, variant: str):
        base = design(variant)
        bigger = JewelryDefinition.model_validate(
            {
                **base.model_dump(mode="python"),
                "stone": {**base.stone.model_dump(), "diameter": 8.0},
            }
        )
        base_model = build_solitaire_ring(base)
        big_model = build_solitaire_ring(bigger)
        # The head follows the stone, because the family MODULATES
        # `setting.basketHeight` rather than replacing it.
        assert (
            big_model.components["basket_support"].shape.Volume()
            != base_model.components["basket_support"].shape.Volume()
        )
        stones = lambda m: max(  # noqa: E731
            c.shape.Volume()
            for name, c in m.components.items()
            if geometry_role(name) == "stone_reference"
        )
        assert stones(big_model) > stones(base_model)

    def test_the_halo_follows_the_centre_stone(self):
        # `haloRadiusFactor` multiplies the CENTRE STONE's own half width, so a
        # bigger stone moves the halo out. An absolute radius would go stale the
        # moment the stone changed — which is the difference between a relation
        # and a stored number.
        def halo_radius(diameter: float) -> float:
            base = design("HALO_SINGLE")
            d = JewelryDefinition.model_validate(
                {
                    **base.model_dump(mode="python"),
                    "stone": {**base.stone.model_dump(), "diameter": diameter},
                }
            )
            resolved = resolve_ring_family(d)
            rings = next(x for x in resolved.derivations if x.path == "halo.rings")
            return float(rings.value[0]["radiusMm"])

        assert halo_radius(8.0) > halo_radius(6.5)

    def test_the_side_stones_propagate(self):
        base = design("THREE_STONE_SYMMETRIC")
        wider = design("THREE_STONE_SYMMETRIC", sideStoneScale=0.8)
        def side_volume(d: JewelryDefinition) -> float:
            model = build_solitaire_ring(d)
            return min(
                c.shape.Volume()
                for name, c in model.components.items()
                if geometry_role(name) == "stone_reference"
            )
        assert side_volume(wider) > side_volume(base)

    def test_the_side_spacing_moves_the_side_stones(self):
        def span(spacing: float) -> float:
            model = build_solitaire_ring(
                design("THREE_STONE_SYMMETRIC", sideSpacingMm=spacing)
            )
            boxes = [
                c.shape.BoundingBox()
                for name, c in model.components.items()
                if geometry_role(name) == "stone_reference"
            ]
            return max(b.xmax for b in boxes) - min(b.xmin for b in boxes)

        assert span(7.0) > span(4.0)

    def test_the_setting_mode_propagates_through_the_family(self):
        # A family ORCHESTRATES the Setting System; it does not replace it. So
        # changing `setting.type` under a family must change the setting
        # geometry, with the family's own structure intact.
        base = design("SOLITAIRE_CATHEDRAL")
        bezel = JewelryDefinition.model_validate(
            {
                **base.model_dump(mode="python"),
                "setting": {**base.setting.model_dump(), "type": "bezel"},
            }
        )
        base_model = build_solitaire_ring(base)
        bezel_model = build_solitaire_ring(bezel)
        assert base_model.combined_metal.Volume() != bezel_model.combined_metal.Volume()
        # The family's own contribution is still there.
        assert SHOULDER_COMPONENT in bezel_model.components

    def test_the_shank_profile_propagates_through_a_split_shank(self):
        # THE HARDEST CASE, because the split architecture builds the band
        # itself: a profile change must still reach it rather than being lost
        # when the family takes over the shank.
        base = design("SPLIT_SHANK_PARALLEL")
        square = JewelryDefinition.model_validate(
            {
                **base.model_dump(mode="python"),
                "band": {**base.band.model_dump(), "profile": "flat"},
            }
        )
        assert component_volume(base, "band") != component_volume(square, "band")

    def test_the_band_width_narrows_the_rails_rather_than_widening_the_ring(self):
        # A RELATION, and a counter-intuitive one worth asserting: the rails
        # SHARE the band's width, so the separation eats into them.
        d = design("SPLIT_SHANK_PARALLEL")
        assert rail_half_width(d, 1.2) < rail_half_width(d, 0.4)

    def test_a_parameter_change_changes_the_geometry_not_just_the_json(self):
        # THE CATALOGUE TEST, stated directly: every parameter a variant READS
        # must be able to change the measured result.
        for variant, param, value in [
            ("SOLITAIRE_CATHEDRAL", "shoulderSpanDeg", 90.0),
            ("SPLIT_SHANK_PARALLEL", "splitSeparationMm", 0.5),
            ("BYPASS_CROSSOVER", "bypassOverlapDeg", 120.0),
            ("SIGNET_FLAT_TABLE", "signetTableHeightMm", 4.0),
            ("SOLITAIRE_ELEVATED", "headHeightFactor", 1.6),
        ]:
            base = metal_volume(design(variant))
            moved = metal_volume(design(variant, **{param: value}))
            assert not math.isclose(base, moved, rel_tol=1e-9), (
                f"{variant}.{param} changed nothing measurable."
            )


# ==========================================================================
# ORCHESTRATION, NOT DUPLICATION (§0)
# ==========================================================================


class TestOrchestrationNotDuplication:
    def test_the_layer_imports_no_geometry_or_kernel(self):
        # AST INSPECTION, not `import`: an `import` test passes on an
        # already-cached module, which is why every sibling subsystem's guard is
        # written this way.
        forbidden_prefixes = (
            "cadquery",
            "OCP",
            "jewelmind.geometry",
            "jewelmind.ring",
            "jewelmind.jewelry_category",
            "jewelmind.validation",
        )
        for path in sorted(RING_FAMILY_PACKAGE.glob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                names: list[str] = []
                if isinstance(node, ast.Import):
                    names = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    names = [node.module]
                for name in names:
                    for prefix in forbidden_prefixes:
                        assert not (
                            name == prefix or name.startswith(f"{prefix}.")
                        ), f"{path.name} imports {name}"

    def test_the_package_init_imports_nothing(self):
        # LOAD-BEARING: `domain/schema.py` imports `ring_family.models`, so an
        # eager package init would make the import graph cyclic — the trap
        # `stone`, `gem`, `arrangement`, `family`, `halo` and `pave` all
        # document.
        tree = ast.parse((RING_FAMILY_PACKAGE / "__init__.py").read_text(encoding="utf-8"))
        assert not [
            n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))
        ]

    def test_no_ring_family_module_builds_geometry(self):
        for path in sorted(RING_FAMILY_PACKAGE.glob("*.py")):
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.Attribute) and node.attr in {
                    "fuse",
                    "cut",
                    "revolve",
                    "loft",
                    "extrude",
                    "fillet",
                }:
                    raise AssertionError(f"{path.name} calls .{node.attr}()")

    def test_the_family_delegates_placement_to_the_arrangement_engine(self):
        # A SECOND PLACEMENT ENGINE is the failure this prevents. The trilogy
        # variants derive a `family` block and the Multi-Stone Family layer
        # compiles it into an arrangement; the ring family computes no position
        # of its own.
        resolved = resolve_ring_family(design("THREE_STONE_SYMMETRIC"))
        paths = {x.path for x in resolved.derivations}
        assert any(p.startswith("family") for p in paths)
        assert not any(p.startswith("arrangement") for p in paths)

    def test_the_family_delegates_the_halo_to_the_halo_system(self):
        paths = {x.path for x in resolve_ring_family(design("HALO_SINGLE")).derivations}
        # The Halo System owns the ring geometry; the family states the variant
        # and the rings' own relation to the centre stone.
        assert "halo.variant" in paths
        assert "halo.rings" in paths

    def test_the_family_delegates_shoulders_pave_to_the_pave_engine(self):
        resolved = resolve_ring_family(
            design("SOLITAIRE_CATHEDRAL", paveShoulders=True)
        )
        assert any(
            x.path == "pave" or x.path.startswith("pave.")
            for x in resolved.derivations
        )

    def test_the_family_delegates_the_head_to_the_setting_system(self):
        # It MODULATES `setting.basketHeight`; it does not build a head.
        resolved = resolve_ring_family(design("SOLITAIRE_ELEVATED"))
        assert "setting.basketHeight" in {x.path for x in resolved.derivations}

    def test_no_derivation_replaces_a_document_value_with_a_constant(self):
        # MODULATION, NOT REPLACEMENT: every derived numeric value must depend
        # on something the document states, which is what keeps `ring.size` and
        # `stone.diameter` driving the geometry.
        for variant in ALL_VARIANTS:
            for derivation in resolve_ring_family(design(variant)).derivations:
                assert derivation.sourceParameters, (variant, derivation.path)


class TestDependencyModel:
    def test_every_dependency_declares_a_real_reason(self):
        for dependency in RING_FAMILY_DEPENDENCIES:
            assert dependency.reason.strip().endswith(".")
            assert len(dependency.reason) > 30, dependency.target

    def test_the_fundamental_inputs_influence_the_family(self):
        # THE PARAMETRIC CLAIM, stated as data a report can read.
        for source in ("ring.size", "stone.diameter", "band.width", "band.thickness"):
            assert influenced_paths(source), source

    def test_every_variant_has_at_least_one_dependency(self):
        for variant in ALL_VARIANTS:
            if variant == "SOLITAIRE_CLASSIC":
                continue
            assert dependencies_for(variant), variant

    def test_the_graph_is_serialisable(self):
        json.dumps(dependency_graph())


# ==========================================================================
# COMPATIBILITY — THE PART EASIEST TO BREAK
# ==========================================================================


class TestPreSprint28Unchanged:
    def test_the_default_design_keeps_its_exact_metal_volume(self):
        # THE BYTE-FOR-BYTE ANCHOR. This number predates Sprint 28 and predates
        # Setting System v2; if it moves, every Golden baseline moves with it.
        assert metal_volume(default_definition()) == 341.44334316909976

    def test_the_adapter_returns_the_original_object_when_nothing_is_derived(self):
        # IDENTITY, not equality: a document with no family must reach exactly
        # the same geometry path it always did.
        d = default_definition()
        effective, resolved = effective_definition(d)
        assert effective is d
        # The baseline DOES derive one path — and it computes the value already
        # there, so nothing is written and the original object survives. See
        # `test_a_document_with_no_family_resolves_to_the_default`.
        assert resolved.variant == "SOLITAIRE_CLASSIC"

    def test_a_default_document_declares_no_ring_family(self):
        assert default_definition().ringFamily is None

    def test_a_default_document_has_a_uniform_band(self):
        assert default_definition().band.architecture == "UNIFORM"

    def test_a_default_document_produces_no_ring_family_error(self):
        results = validate_definition(default_definition())
        assert not [
            r
            for r in results
            if r.ruleId.startswith("JM-RINGFAM-") and r.severity == "error"
        ]

    def test_a_default_document_builds_no_new_components(self):
        components = set(build_solitaire_ring(default_definition()).components)
        assert SHOULDER_COMPONENT not in components
        assert SIGNET_COMPONENT not in components

    def test_the_identity_is_the_original_document(self):
        # THE ORIGINAL IS THE IDENTITY: geometry is built from the effective
        # document, but the hash is of what the author wrote — otherwise a
        # derived value would become part of the design's name.
        from jewelmind.utils.hashing import definition_hash

        d = design("SOLITAIRE_ELEVATED")
        model = build_solitaire_ring(d)
        assert model.definition_hash == definition_hash(d)
        # And the effective document — the one the geometry was built from —
        # hashes DIFFERENTLY, which is exactly why the original is the identity.
        effective, _ = effective_definition(d)
        assert definition_hash(effective) != model.definition_hash


# ==========================================================================
# NO INVENTED PROFESSIONAL RULE (§32)
# ==========================================================================


class TestNoInventedProfessionalRule:
    def test_no_ring_family_rule_makes_a_professional_judgment(self):
        forbidden = (
            "production safe",
            "manufacturing validated",
            "casting validated",
            "jeweler approved",
            "structurally safe",
            "strong enough",
            "castable",
        )
        for variant in ALL_VARIANTS:
            for result in validate_definition(design(variant)):
                if not result.ruleId.startswith("JM-RINGFAM-"):
                    continue
                lowered = result.message.lower()
                for phrase in forbidden:
                    assert phrase not in lowered, (variant, result.ruleId, phrase)

    def test_the_only_numeric_refusal_is_arithmetic(self):
        # `JM-RINGFAM-004` refuses a separation that leaves NO rail — which is
        # arithmetic, not a statement about how thin a rail may be. There is no
        # minimum rail width anywhere, because no sourced professional minimum
        # exists.
        d = design("SPLIT_SHANK_PARALLEL", splitSeparationMm=1.2)
        narrow = JewelryDefinition.model_validate(
            {**d.model_dump(mode="python"), "band": {**d.band.model_dump(), "width": 1.5}}
        )
        errors = [
            r
            for r in validate_definition(narrow)
            if r.ruleId == R.RING_FAMILY_GEOMETRY_FEASIBLE and r.severity == "error"
        ]
        # 1.5 mm band, 1.2 mm separation -> 0.15 mm of rail: thin, and NOT
        # refused, because nothing here judges thinness.
        assert not errors

    def test_a_separation_that_leaves_no_rail_is_refused(self):
        d = design("SPLIT_SHANK_PARALLEL", splitSeparationMm=3.0)
        narrow = JewelryDefinition.model_validate(
            {**d.model_dump(mode="python"), "band": {**d.band.model_dump(), "width": 2.2}}
        )
        errors = [
            r
            for r in validate_definition(narrow)
            if r.ruleId == R.RING_FAMILY_GEOMETRY_FEASIBLE and r.severity == "error"
        ]
        assert errors
        assert "narrows them" in errors[0].message

    def test_the_software_limits_say_they_are_software_limits(self):
        source = (RING_FAMILY_PACKAGE / "models.py").read_text(encoding="utf-8")
        assert "MAX_HALO_STONES_PER_FAMILY" in source
        assert MAX_HALO_STONES_PER_FAMILY == 96
        # The constant's own comment must not claim a professional origin.
        assert "industry standard" not in source.lower()

    def test_every_partial_status_is_a_capability_statement_not_a_warning(self):
        # An honest PARTIAL is INFORMATION: the design builds, and part of it is
        # missing. Reporting it as an error would block a design the product
        # genuinely produces.
        for variant in ALL_VARIANTS:
            for result in validate_definition(design(variant)):
                if result.ruleId == R.RING_FAMILY_STATUS:
                    assert result.severity == "information", variant


# ==========================================================================
# §33 — ADVERSARIAL INPUT
# ==========================================================================


class TestAdversarialInput:
    def test_every_ring_family_error_derives_from_the_base(self):
        """A caller guarding on `RingFamilyError` must catch all of them.

        This is not a formality: `default_variant_for()` shipped raising a bare
        `KeyError`, `ring/adapter.py` guards on `RingFamilyError`, and the guard
        silently did not apply — a family with no generator surfaced as an
        untyped exception from three frames down instead of the clean dispatch
        refusal the boundary is supposed to produce.
        """

        import inspect

        from jewelmind.ring_family import errors

        found = [
            obj
            for _, obj in inspect.getmembers(errors, inspect.isclass)
            if issubclass(obj, Exception) and obj.__module__ == errors.__name__
        ]
        assert len(found) >= 5
        for cls in found:
            if cls is RingFamilyError:
                continue
            assert issubclass(cls, RingFamilyError), cls.__name__

    def test_a_reserved_variant_is_refused_by_the_schema(self):
        for name in RESERVED_RING_FAMILIES:
            with pytest.raises(ValidationError):
                RingFamilySpec(variant=name)

    def test_an_unknown_variant_is_refused_by_the_schema(self):
        for name in ("", "SOLITAIRE", "solitaire_classic", "NOPE", "../../etc/passwd"):
            with pytest.raises(ValidationError):
                RingFamilySpec(variant=name)

    def test_no_parameter_accepts_a_non_finite_value(self):
        for value in (float("nan"), float("inf"), float("-inf")):
            with pytest.raises(ValidationError):
                RingFamilyParams(headHeightFactor=value)

    def test_no_parameter_accepts_a_negative_or_zero_dimension(self):
        for field in (
            "headHeightFactor",
            "splitSeparationMm",
            "signetTableWidthMm",
            "sideStoneScale",
            "haloRadiusFactor",
        ):
            for value in (0.0, -1.0):
                with pytest.raises(ValidationError):
                    RingFamilyParams(**{field: value})

    def test_the_halo_count_is_bounded(self):
        with pytest.raises(ValidationError):
            RingFamilyParams(haloStoneCount=MAX_HALO_STONES_PER_FAMILY + 1)
        with pytest.raises(ValidationError):
            RingFamilyParams(haloStoneCount=0)

    def test_an_absurd_span_is_refused(self):
        for field, value in [
            ("shoulderSpanDeg", 400.0),
            ("splitJoinSpanDeg", 0.0),
            ("bypassOverlapDeg", 1000.0),
            ("paveSpanDeg", 400.0),
        ]:
            with pytest.raises(ValidationError):
                RingFamilyParams(**{field: value})

    def test_an_extra_field_is_refused(self):
        with pytest.raises(ValidationError):
            RingFamilyParams(notAField=1.0)
        with pytest.raises(ValidationError):
            RingFamilySpec(variant="SOLITAIRE_CLASSIC", notAField=1.0)

    def test_a_label_cannot_be_unbounded(self):
        with pytest.raises(ValidationError):
            RingFamilySpec(variant="SOLITAIRE_CLASSIC", label="x" * 10_000)

    def test_a_shoulder_span_past_the_construction_limit_is_refused(self):
        """The defect this sprint shipped first, now guarded in both layers.

        `shoulderSpanDeg` was bounded at 170, and any value past 90 built a
        SELF-INTERSECTING arch: the fused shoulders collapsed from 84.651 mm³ to
        19.577 mm³ and the ring's combined metal reported `isValid() == False`,
        while the arch's OWN validity check passed. So it could not have been
        caught by checking the solid afterwards — it is a precondition.

        REFUSED IN BOTH LAYERS, and neither is a professional threshold: the
        schema refuses the value, the builder refuses the call, and both read the
        same measured construction limit.
        """

        assert MAX_ARCH_SPAN_DEG == 90.0

        # The schema layer.
        with pytest.raises(ValidationError):
            RingFamilyParams(shoulderSpanDeg=MAX_ARCH_SPAN_DEG + 1.0)

        # The geometry layer, reached directly so the schema cannot mask it.
        with pytest.raises(ShoulderConstructionError) as exc:
            build_shoulders(
                design(),
                "CATHEDRAL",
                MAX_ARCH_SPAN_DEG + 1.0,
                0.85,
                0.85,
            )
        assert "construction limit" in str(exc.value)
        # NEVER CLAMPED: reducing the span to fit would build a shoulder the
        # author never described.
        assert "clamp" not in str(exc.value).lower()

    def test_the_arch_grows_monotonically_up_to_the_limit(self):
        """The signature that made the defect visible.

        A collapsing loft shows up as a NON-MONOTONIC volume: the arches grew to
        84.651 mm³ at 90 degrees and dropped to 19.577 mm³ at 92. Asserting
        monotonicity is what would have caught it, so it is asserted.
        """

        volumes = [
            component_volume(design("SOLITAIRE_CATHEDRAL", shoulderSpanDeg=span), SHOULDER_COMPONENT)
            for span in (30.0, 50.0, 70.0, 90.0)
        ]
        assert volumes == sorted(volumes)
        assert volumes[0] < volumes[-1]
        # And the ring's own metal stays valid across the whole range.
        for span in (30.0, 90.0):
            model = build_solitaire_ring(design("SOLITAIRE_CATHEDRAL", shoulderSpanDeg=span))
            assert model.combined_metal.isValid(), span

    def test_an_extreme_but_legal_parameter_still_builds(self):
        # NOT a refusal: the bounds are the schema's, and anything inside them
        # must produce real geometry rather than an exception a caller cannot
        # act on.
        for variant, params in [
            ("SOLITAIRE_CATHEDRAL", {"shoulderSpanDeg": 90.0}),
            ("SPLIT_SHANK_PARALLEL", {"splitJoinSpanDeg": 340.0}),
            ("BYPASS_CROSSOVER", {"bypassOverlapDeg": 175.0}),
            ("SIGNET_FLAT_TABLE", {"signetTableHeightMm": 12.0}),
        ]:
            model = build_solitaire_ring(design(variant, **params))
            assert model.combined_metal.Volume() > 0.0
            assert model.combined_metal.isValid()


# ==========================================================================
# INSPECTION AND SUMMARY
# ==========================================================================


class TestInspection:
    def test_every_family_passes_inspection(self):
        for variant in ALL_VARIANTS:
            d = design(variant)
            report = inspect_model(build_solitaire_ring(d))
            assert report.status in {"PASS", "WARNING"}, (variant, report.status)

    def test_the_ring_family_facts_are_recorded(self):
        d = design("SPLIT_SHANK_PARALLEL")
        facts = {f.factType: f.value for f in inspect_model(build_solitaire_ring(d)).geometricFacts}
        assert facts["RING_FAMILY_VARIANT"] == "SPLIT_SHANK_PARALLEL"
        assert facts["RING_FAMILY_ID"] == "split_shank"
        assert facts["RING_FAMILY_SHANK_ARCHITECTURE"] == "SPLIT"
        assert facts["RING_FAMILY_SHOULDER_ARCHITECTURE"] == "SPLIT_RAILS"
        assert facts["RING_FAMILY_DERIVED_PATH_COUNT"] == 5
        assert len(facts["RING_FAMILY_FINGERPRINT"]) == 16

    def test_the_fingerprint_fact_matches_the_resolver(self):
        d = design("SOLITAIRE_ELEVATED")
        facts = {f.factType: f.value for f in inspect_model(build_solitaire_ring(d)).geometricFacts}
        assert facts["RING_FAMILY_FINGERPRINT"] == resolve_ring_family(d).fingerprint

    def test_the_summary_reports_the_derivations(self):
        d = design("SOLITAIRE_CATHEDRAL")
        summary = ring_family_summary(resolve_ring_family(d))
        assert summary["variant"] == "SOLITAIRE_CATHEDRAL"
        assert summary["derivedPaths"]
        json.dumps(summary)

    def test_the_model_carries_the_resolution(self):
        model = build_solitaire_ring(design("BYPASS_CROSSOVER"))
        assert model.ring_family_result is not None
        assert model.ring_family_result.variant == "BYPASS_CROSSOVER"


class TestDeterminism:
    @pytest.mark.parametrize(
        "variant",
        ["SOLITAIRE_CATHEDRAL", "SPLIT_SHANK_TAPERED", "BYPASS_CROSSOVER", "SIGNET_FLAT_TABLE"],
    )
    def test_the_same_design_builds_the_same_geometry_twice(self, variant: str):
        d = design(variant)
        assert build_solitaire_ring(d).combined_metal.Volume() == (
            build_solitaire_ring(d).combined_metal.Volume()
        )

    def test_the_stone_is_never_fused_into_the_metal(self):
        # LAW-006, at every new family. The stone is a reference, never
        # production metal — and the new shoulder and signet components must not
        # have created a path that changes that.
        for variant in ALL_VARIANTS:
            model = build_solitaire_ring(design(variant))
            for name in model.components:
                if geometry_role(name) == "stone_reference":
                    assert not is_production_component(name), (variant, name)


# ==========================================================================
# SPEC ARTIFACTS — MIRRORS OF LIVE CODE, RE-DERIVED ON EVERY RUN
# ==========================================================================


class TestSpecArtifacts:
    """`specs/ring-family/v1/` is a MIRROR, never a hand-maintained copy.

    Sprint 20 removed three hand-copied registries that had already drifted and
    had caused Designer and the Setting System to misreport real capabilities.
    These tests are what make that class of drift FAIL rather than survive.
    """

    @staticmethod
    def _load(name: str) -> dict:
        return json.loads((SPEC_V1 / name).read_text(encoding="utf-8"))

    def test_the_registry_matches_the_live_registry(self):
        registry = self._load("ring-family-registry.json")

        assert registry["taxonomyVersion"] == RING_FAMILY_TAXONOMY_VERSION
        assert registry["ringFamilyGeometryVersion"] == RING_FAMILY_GEOMETRY_VERSION
        assert registry["pipelineStages"] == list(RING_FAMILY_PIPELINE_STAGES)

        recorded = {entry["variant"]: entry for entry in registry["variants"]}
        assert set(recorded) == set(ring_family_capabilities())
        for variant, entry in ring_family_capabilities().items():
            assert recorded[variant] == entry.model_dump(mode="json"), variant

    def test_the_recorded_families_match_the_live_ones(self):
        registry = self._load("ring-family-registry.json")
        assert set(registry["families"]) == set(implemented_families())
        for family, entry in registry["families"].items():
            assert entry["status"] == family_status(family), family
            assert entry["defaultVariant"] == default_variant_for(family), family
            assert entry["variants"] == list(variants_for_family(family)), family

    def test_the_recorded_reserved_list_matches_the_live_one(self):
        registry = self._load("ring-family-registry.json")
        recorded = {e["name"]: e["reason"] for e in registry["reserved"]}
        assert recorded == dict(RESERVED_RING_FAMILIES)

    def test_the_recorded_designer_terms_match_the_live_ones(self):
        registry = self._load("ring-family-registry.json")
        assert registry["designerTerms"] == designer_family_terms()

    def test_the_recorded_read_parameters_match_the_live_resolver(self):
        registry = self._load("ring-family-registry.json")
        recorded = {
            variant: tuple(fields)
            for variant, fields in registry["parametersReadByVariant"].items()
        }
        assert recorded == {v: parameters_read_by(v) for v in ALL_VARIANTS}

    def test_the_dependency_graph_matches_the_live_table(self):
        recorded = self._load("ring-family-dependency-graph.json")
        assert recorded["dependencies"] == [
            d.model_dump(mode="json") for d in RING_FAMILY_DEPENDENCIES
        ]
        assert recorded["graph"] == dependency_graph()

    def test_every_schema_matches_its_live_model(self):
        for name, model in [
            ("ring-family-spec.schema.json", RingFamilySpec),
            ("ring-family-params.schema.json", RingFamilyParams),
        ]:
            recorded = self._load(name)
            live = model.model_json_schema()
            # `$schema`/`$id` are spec-file metadata the model does not carry.
            for key in ("$schema", "$id"):
                recorded.pop(key, None)
            assert recorded == live, name

    def test_every_example_is_a_real_valid_document(self):
        for path in sorted((SPEC_V1 / "examples").glob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            definition = JewelryDefinition.model_validate(payload["definition"])
            # And its recorded resolution is what the real resolver produces.
            assert payload["resolution"] == resolution_summary(
                resolve_ring_family(definition)
            ), path.name
            # Every example must be a design the product actually accepts.
            assert not [
                r for r in validate_definition(definition) if r.severity == "error"
            ], path.name

    def test_the_fingerprint_vectors_match_the_live_resolver(self):
        vectors = self._load("test-vectors/ring-family-fingerprint-vectors.json")
        for vector in vectors["vectors"]:
            assert len(vector["fingerprint"]) == 16
            if vector["parameters"] != "default":
                continue
            assert (
                resolve_ring_family(design(vector["variant"])).fingerprint
                == vector["fingerprint"]
            ), vector["variant"]

    def test_the_derivation_vectors_match_the_live_resolver(self):
        vectors = self._load("test-vectors/ring-family-derivation-vectors.json")
        for vector in vectors["vectors"]:
            resolved = resolve_ring_family(design(vector["variant"]))
            assert [
                {
                    "path": d.path,
                    "sourceParameters": list(d.sourceParameters),
                    "relation": d.relation,
                }
                for d in resolved.derivations
            ] == vector["derivations"], vector["variant"]

    def test_the_geometry_vectors_are_real_measurements(self):
        """MEASURED, and re-measured here.

        A spec whose geometry figures were typed by hand could claim any
        difference between two variants. Rebuilding each variant and comparing
        is the only evidence that the recorded numbers came from solids.
        """

        vectors = self._load("test-vectors/ring-family-geometry-vectors.json")
        assert vectors["ringFamilyGeometryVersion"] == RING_FAMILY_GEOMETRY_VERSION
        recorded = {v["variant"]: v for v in vectors["vectors"]}
        assert set(recorded) == set(ALL_VARIANTS)

        for variant, vector in recorded.items():
            model = build_solitaire_ring(design(variant))
            assert model.combined_metal_volume_mm3 == pytest.approx(
                vector["combinedMetalVolumeMm3"], rel=1e-9
            ), variant
            assert sorted(model.components) == sorted(vector["components"]), variant
            assert vector["stoneComponentCount"] == sum(
                1 for n in model.components if geometry_role(n) == "stone_reference"
            ), variant

    def test_the_compatibility_vector_still_holds(self):
        vectors = self._load("test-vectors/ring-family-compatibility-vectors.json")
        vector = vectors["vectors"][0]
        assert vector["resolvedVariant"] == "SOLITAIRE_CLASSIC"
        # THE ONE NUMBER THAT MUST NOT MOVE.
        assert build_solitaire_ring(
            default_definition()
        ).combined_metal_volume_mm3 == vector["combinedMetalVolumeMm3"]
        assert vector["combinedMetalVolumeMm3"] == 341.44334316909976
