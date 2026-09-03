"""Gem Identity & Material System v1 (Sprint 21).

Covers the five separations the sprint exists to establish — geometry, gem
identity, visual representation, setting, and instance/arrangement — plus the
honesty constraints: no invented gemological claim, no guessed gem, no
user-authored ID reaching a path, and no NaN/Infinity slipping through.
"""

from __future__ import annotations

import math
from pathlib import Path

import pytest
from pydantic import ValidationError

from jewelmind.domain.defaults import default_definition
from jewelmind.domain.schema import JewelryDefinition, StoneSpec
from jewelmind.gem.errors import (
    GemIdInvalidError,
    GemNotFoundError,
    GemOriginInvalidError,
)
from jewelmind.gem.models import (
    CUSTOM_GEM_ID,
    FALLBACK_VISUAL_PROFILE_ID,
    MAX_GEM_ID_LENGTH,
    UNKNOWN_GEM_ID,
    GemDefinition,
    GemIdentity,
    GemTreatment,
    StoneInstance,
)
from jewelmind.gem.registry import (
    GEM_REGISTRY,
    GEM_REGISTRY_VERSION,
    alias_lookup,
    all_gem_ids,
    current_gem_ids,
    get_gem,
    registry_families,
)
from jewelmind.gem.resolution import (
    GEM_SYSTEM_VERSION,
    effective_display_name,
    get_gem_or_raise,
    is_valid_gem_id,
    require_gem_id,
    require_origin_applicable,
    resolve_alias,
    resolve_gem,
    treatment_summary,
)
from jewelmind.gem.visual import (
    FALLBACK_PROFILE,
    GEM_VISUAL_PROFILES,
    VISUAL_PROFILE_SET_VERSION,
    get_visual_profile,
    profile_exists,
)
from jewelmind.utils.hashing import definition_hash, geometry_hash
from jewelmind.validation.engine import validate_definition


def with_gem(gem: dict | None) -> JewelryDefinition:
    definition = default_definition()
    data = definition.stone.model_dump()
    data["gem"] = gem
    definition.stone = StoneSpec.model_validate(data)
    return definition


# --------------------------------------------------------------- the registry


class TestRegistry:
    def test_every_entry_is_self_consistent(self):
        for gem_id, entry in GEM_REGISTRY.items():
            assert entry.gemId == gem_id, gem_id
            assert is_valid_gem_id(gem_id), gem_id
            assert entry.canonicalName.strip()
            assert entry.applicableOrigins, gem_id
            assert profile_exists(entry.defaultVisualProfileId), gem_id

    def test_the_two_escape_hatches_exist(self):
        assert CUSTOM_GEM_ID in GEM_REGISTRY
        assert UNKNOWN_GEM_ID in GEM_REGISTRY

    def test_no_entry_is_professionally_validated(self):
        """Nothing in Sprint 21 is professionally reviewed.

        The registry is an internal taxonomy. Marking an entry
        `PROFESSIONALLY_VALIDATED` would require a real record in the
        professional-validation registry, which holds zero.
        """

        for entry in GEM_REGISTRY.values():
            assert entry.provenance != "PROFESSIONALLY_VALIDATED", entry.gemId

    def test_aliases_are_unique_and_resolve_to_real_entries(self):
        index = alias_lookup()
        for term, gem_id in index.items():
            assert gem_id in GEM_REGISTRY, (term, gem_id)
            assert term == term.lower(), term

    def test_current_ids_exclude_deprecated_entries(self):
        current = set(current_gem_ids())
        for gem_id, entry in GEM_REGISTRY.items():
            if entry.status == "DEPRECATED":
                assert gem_id not in current
            else:
                assert gem_id in current
        assert set(all_gem_ids()) >= current

    def test_families_group_real_entries(self):
        for family, members in registry_families().items():
            assert family
            assert members
            for gem_id in members:
                assert gem_id in GEM_REGISTRY

    def test_a_deprecated_entry_would_still_resolve(self):
        """Constructed here, not added to the registry.

        A saved design may reference an entry that was later deprecated; it must
        still load. No entry is deprecated today, so the guarantee is proved
        against a real `GemDefinition` built for the test rather than by
        deprecating something in shipped data.
        """

        entry = GemDefinition(
            gemId="test.deprecated",
            canonicalName="Test deprecated",
            materialClass="MINERAL",
            applicableOrigins=["NATURAL"],
            defaultVisualProfileId=FALLBACK_VISUAL_PROFILE_ID,
            status="DEPRECATED",
            supersededBy="diamond",
            provenance="INTERNAL_TAXONOMY",
            description="Fixture only.",
        )
        assert entry.status == "DEPRECATED"
        assert entry.supersededBy == "diamond"

    def test_version_string_identifies_both_halves(self):
        assert GEM_REGISTRY_VERSION in GEM_SYSTEM_VERSION
        assert VISUAL_PROFILE_SET_VERSION in GEM_SYSTEM_VERSION


# ------------------------------------------------------ IDs as untrusted input


class TestGemIdSafety:
    @pytest.mark.parametrize(
        "candidate",
        [
            "Ruby",
            "corundum..ruby",
            "../../etc/passwd",
            "corundum/ruby",
            "corundum\\ruby",
            "rm -rf /",
            "9lives",
            "-leading",
            ".leading",
            "trailing.",
            "a" * (MAX_GEM_ID_LENGTH + 1),
            "",
            "ruby;drop",
            "ruby ruby",
            "rubí",
        ],
    )
    def test_malformed_ids_are_rejected(self, candidate: str):
        assert not is_valid_gem_id(candidate)
        with pytest.raises(GemIdInvalidError):
            require_gem_id(candidate)

    @pytest.mark.parametrize("gem_id", sorted(GEM_REGISTRY))
    def test_every_real_id_is_valid(self, gem_id: str):
        assert is_valid_gem_id(gem_id)

    def test_a_malformed_id_never_reaches_a_lookup(self):
        with pytest.raises(GemIdInvalidError):
            get_gem_or_raise("../../secrets")

    def test_a_wellformed_unknown_id_is_a_not_found(self):
        with pytest.raises(GemNotFoundError):
            get_gem_or_raise("tanzanite")

    def test_jdl_rejects_a_malformed_id_before_the_domain_sees_it(self):
        with pytest.raises(ValidationError):
            with_gem({"gemId": "../../etc/passwd"})


# ------------------------------------------------------------------ resolution


class TestResolution:
    def test_resolution_never_raises_and_never_substitutes(self):
        resolved = resolve_gem(GemIdentity(gemId="tanzanite"))
        assert resolved.wasUnresolved is True
        assert resolved.definition.gemId == UNKNOWN_GEM_ID
        # Never a different real gem that looks similar.
        assert resolved.definition.gemId not in {"corundum.sapphire", "quartz.amethyst"}
        # The original reference is preserved, not overwritten by the fallback.
        assert resolved.identity.gemId == "tanzanite"

    def test_an_unresolved_gem_uses_the_neutral_fallback_appearance(self):
        resolved = resolve_gem(GemIdentity(gemId="tanzanite"))
        assert resolved.usedFallbackVisualProfile is True
        assert resolved.visualProfile.isFallback is True
        # NOT a brilliant colourless look, which would render an unidentified
        # gem as the most valuable possible reading of itself.
        brilliant = GEM_VISUAL_PROFILES.get("colourless.brilliant")
        assert brilliant is not None
        assert resolved.visualProfile.profileId != brilliant.profileId

    def test_no_gem_at_all_resolves_to_unknown_not_diamond(self):
        resolved = resolve_gem(None)
        assert resolved.definition.gemId == UNKNOWN_GEM_ID
        assert resolved.definition.gemId != "diamond"

    def test_a_resolved_gem_records_the_registry_version(self):
        resolved = resolve_gem(GemIdentity(gemId="diamond"))
        # Both halves, so an artifact records the visual profile set it was
        # produced with and not only the registry content.
        assert resolved.registryVersion == GEM_SYSTEM_VERSION
        assert GEM_REGISTRY_VERSION in resolved.registryVersion
        assert VISUAL_PROFILE_SET_VERSION in resolved.registryVersion

    def test_alias_resolution_is_case_and_whitespace_tolerant(self):
        assert resolve_alias("  RUBINO ") == "corundum.ruby"
        assert resolve_alias("Diamond") == "diamond"

    def test_alias_resolution_returns_none_rather_than_guessing(self):
        assert resolve_alias("tanzanite") is None
        assert resolve_alias("") is None
        assert resolve_alias("a stone that sparkles") is None

    def test_identity_override_beats_the_registry_default(self):
        default = resolve_gem(GemIdentity(gemId="corundum.sapphire"))
        override = resolve_gem(
            GemIdentity(gemId="corundum.sapphire", visualProfileId="blue.pale")
        )
        assert override.visualProfile.profileId == "blue.pale"
        assert override.visualProfile.profileId != default.visualProfile.profileId
        assert override.definition.gemId == default.definition.gemId  # still a sapphire

    def test_origin_applicability_is_enforced_where_it_is_known(self):
        require_origin_applicable(
            GemIdentity(gemId="corundum.ruby", origin="SYNTHETIC")
        )
        with pytest.raises(GemOriginInvalidError):
            require_origin_applicable(
                GemIdentity(gemId="simulant.cubic_zirconia", origin="NATURAL")
            )

    def test_unknown_origin_is_always_acceptable(self):
        for gem_id in current_gem_ids():
            # `custom` is the one entry that needs a second field to exist at
            # all; every other ID stands alone.
            identity = (
                GemIdentity(gemId=gem_id, origin="UNKNOWN", customName="fixture")
                if gem_id == CUSTOM_GEM_ID
                else GemIdentity(gemId=gem_id, origin="UNKNOWN")
            )
            require_origin_applicable(identity)

    def test_display_name_prefers_the_requested_language(self):
        resolved = resolve_gem(GemIdentity(gemId="corundum.ruby"))
        assert effective_display_name(resolved, "it") == "Rubino"
        assert effective_display_name(resolved, "en") == "Ruby"
        # An unsupported language falls back to the canonical name rather than
        # returning an empty string.
        assert effective_display_name(resolved, "xx") == "Ruby"

    def test_a_custom_gem_displays_the_users_own_words(self):
        resolved = resolve_gem(
            GemIdentity(gemId=CUSTOM_GEM_ID, customName="meteorite inlay")
        )
        assert "meteorite inlay" in effective_display_name(resolved)


# ------------------------------------------------------- treatments as claims


class TestTreatments:
    def test_nothing_recorded_is_not_a_claim_of_being_untreated(self):
        summary = treatment_summary(GemIdentity(gemId="corundum.ruby"))
        assert "not recorded" in summary.lower()
        assert "untreated" not in summary.lower()

    def test_declared_untreated_is_a_distinct_state(self):
        identity = GemIdentity(
            gemId="corundum.ruby",
            treatments=[GemTreatment(treatment="HEAT", status="NOT_PRESENT")],
        )
        summary = treatment_summary(identity)
        assert summary != treatment_summary(GemIdentity(gemId="corundum.ruby"))
        assert "untreated" in summary.lower()

    def test_a_present_treatment_is_reported(self):
        identity = GemIdentity(
            gemId="corundum.ruby",
            treatments=[GemTreatment(treatment="HEAT", status="PRESENT")],
        )
        assert "heat" in treatment_summary(identity).lower()

    def test_an_unspecified_treatment_stays_unspecified(self):
        """'Treated' names no treatment, and none is invented for the user."""

        identity = GemIdentity(
            gemId="beryl.emerald",
            treatments=[GemTreatment(treatment="UNKNOWN", status="PRESENT")],
        )
        summary = treatment_summary(identity).lower()
        assert "fracture" not in summary
        assert "oil" not in summary

    def test_treatment_other_requires_a_note(self):
        with pytest.raises(ValidationError):
            GemTreatment(treatment="OTHER", status="PRESENT")
        GemTreatment(treatment="OTHER", status="PRESENT", note="Surface waxed.")

    def test_origin_and_treatment_are_independent(self):
        identity = GemIdentity(
            gemId="corundum.ruby",
            origin="SYNTHETIC",
            treatments=[GemTreatment(treatment="HEAT", status="NOT_PRESENT")],
        )
        assert identity.origin == "SYNTHETIC"
        assert identity.treatments[0].status == "NOT_PRESENT"


# ----------------------------------------------------------- visual profiles


class TestVisualProfiles:
    def test_every_profile_is_self_consistent(self):
        for profile_id, profile in GEM_VISUAL_PROFILES.items():
            assert profile.profileId == profile_id
            assert profile.baseColor.startswith("#") and len(profile.baseColor) == 7
            assert 0.0 <= profile.metalness <= 1.0
            assert 0.0 <= profile.roughness <= 1.0
            assert 0.0 < profile.opacity <= 1.0
            assert 0.0 <= profile.transmission <= 1.0
            assert profile.ior > 0.0

    def test_exactly_one_profile_is_the_fallback(self):
        fallbacks = [p.profileId for p in GEM_VISUAL_PROFILES.values() if p.isFallback]
        assert fallbacks == [FALLBACK_PROFILE.profileId]
        assert FALLBACK_PROFILE.profileId == FALLBACK_VISUAL_PROFILE_ID

    def test_lookup_never_raises(self):
        for requested in ["not.a.profile", "", "../../etc", "Ruby"]:
            profile = get_visual_profile(requested)
            assert profile.isFallback is True

    def test_no_profile_value_is_nan_or_infinite(self):
        for profile in GEM_VISUAL_PROFILES.values():
            for name, value in profile.model_dump().items():
                if isinstance(value, float):
                    assert math.isfinite(value), (profile.profileId, name)

    def test_a_profile_cannot_be_built_with_nan(self):
        with pytest.raises(ValidationError):
            FALLBACK_PROFILE.model_copy(update={"ior": float("nan")}).model_validate(
                FALLBACK_PROFILE.model_dump() | {"ior": float("nan")}
            )


# ------------------------------------------- geometry / identity separation


class TestGeometryIdentitySeparation:
    """The sprint's central architectural claim, measured rather than asserted.

    A gem is semantic. Changing it changes what the design MEANS and not what
    Atlas BUILDS, so `definitionHash` moves and `geometryHash` does not.
    """

    def test_changing_the_gem_leaves_the_geometry_hash_untouched(self):
        ruby = with_gem({"gemId": "corundum.ruby", "origin": "NATURAL"})
        sapphire = with_gem({"gemId": "corundum.sapphire", "origin": "NATURAL"})
        assert definition_hash(ruby) != definition_hash(sapphire)
        assert geometry_hash(ruby) == geometry_hash(sapphire)

    def test_changing_the_origin_leaves_the_geometry_hash_untouched(self):
        natural = with_gem({"gemId": "corundum.ruby", "origin": "NATURAL"})
        synthetic = with_gem({"gemId": "corundum.ruby", "origin": "SYNTHETIC"})
        assert definition_hash(natural) != definition_hash(synthetic)
        assert geometry_hash(natural) == geometry_hash(synthetic)

    def test_adding_a_treatment_leaves_the_geometry_hash_untouched(self):
        plain = with_gem({"gemId": "corundum.ruby", "origin": "NATURAL"})
        treated = with_gem(
            {
                "gemId": "corundum.ruby",
                "origin": "NATURAL",
                "treatments": [{"treatment": "HEAT", "status": "PRESENT"}],
            }
        )
        assert definition_hash(plain) != definition_hash(treated)
        assert geometry_hash(plain) == geometry_hash(treated)

    def test_a_real_geometry_change_does_move_the_geometry_hash(self):
        """The complement, so the test above cannot pass by measuring nothing."""

        base = with_gem({"gemId": "corundum.ruby"})
        wider = with_gem({"gemId": "corundum.ruby"})
        wider.band.width = base.band.width + 0.5
        assert geometry_hash(base) != geometry_hash(wider)

        deeper = with_gem({"gemId": "corundum.ruby"})
        deeper.stone.depth = base.stone.depth + 0.3
        assert geometry_hash(base) != geometry_hash(deeper)

    def test_the_geometry_hash_is_deterministic(self):
        definition = with_gem({"gemId": "diamond", "origin": "NATURAL"})
        assert geometry_hash(definition) == geometry_hash(definition)
        assert geometry_hash(definition) == geometry_hash(
            with_gem({"gemId": "diamond", "origin": "NATURAL"})
        )

    def test_the_two_hashes_are_not_the_same_value(self):
        definition = with_gem({"gemId": "diamond"})
        assert definition_hash(definition) != geometry_hash(definition)


# --------------------------------------------------------------- Forge rules


class TestForgeGemRules:
    def _gem_results(self, definition: JewelryDefinition) -> dict[str, str]:
        return {
            r.ruleId: r.severity
            for r in validate_definition(definition)
            if r.ruleId.startswith("JM-GEM")
        }

    def test_a_design_with_no_gem_produces_no_gem_findings(self):
        assert self._gem_results(with_gem(None)) == {}

    def test_a_valid_gem_produces_no_gem_findings(self):
        assert self._gem_results(
            with_gem({"gemId": "corundum.ruby", "origin": "NATURAL"})
        ) == {}

    def test_an_unregistered_gem_warns_and_never_blocks(self):
        results = self._gem_results(with_gem({"gemId": "tanzanite"}))
        assert results["JM-GEM-001"] == "warning"

    def test_an_inapplicable_origin_is_an_error(self):
        results = self._gem_results(
            with_gem({"gemId": "simulant.cubic_zirconia", "origin": "NATURAL"})
        )
        assert results["JM-GEM-002"] == "error"

    def test_a_custom_name_on_a_canonical_gem_is_rejected(self):
        """Caught at the JDL layer, BEFORE Forge runs.

        `JdlGemIdentity` refuses the combination outright, so JM-GEM-003's
        "custom name on a canonical gem" branch is unreachable through the API
        and only fires for an identity built in Python. That is a real property
        of the pipeline, recorded here rather than papered over by asserting a
        Forge result that never arrives.
        """

        with pytest.raises(ValidationError):
            with_gem({"gemId": "diamond", "customName": "sparkly thing"})

        programmatic = GemIdentity(gemId=CUSTOM_GEM_ID, customName="meteorite")
        assert programmatic.customName == "meteorite"

    def test_an_unknown_visual_profile_warns_without_blocking(self):
        results = self._gem_results(
            with_gem({"gemId": "diamond", "visualProfileId": "not.a.profile"})
        )
        assert results["JM-GEM-004"] == "warning"

    def test_no_gem_rule_makes_a_gemological_claim(self):
        """GEM-GOV: no hardness, durability, heat-sensitivity or setting advice.

        Scans the real messages the engine produces, not the source, so a claim
        introduced through an f-string is caught too.
        """

        forbidden = (
            "hardness",
            "mohs",
            "durab",
            "heat sensitiv",
            "brittle",
            "fragile",
            "not suitable for",
            "recommend",
            "safe to",
            "avoid setting",
        )
        cases = [
            None,
            {"gemId": "tanzanite"},
            {"gemId": "corundum.ruby", "origin": "NATURAL"},
            {"gemId": "simulant.cubic_zirconia", "origin": "NATURAL"},
            {"gemId": "diamond", "visualProfileId": "not.a.profile"},
            {"gemId": "pearl", "origin": "NATURAL"},
            {"gemId": CUSTOM_GEM_ID, "customName": "meteorite"},
        ]
        for gem in cases:
            for result in validate_definition(with_gem(gem)):
                lowered = result.message.lower()
                for term in forbidden:
                    assert term not in lowered, (gem, result.ruleId, result.message)


# --------------------------------------------------- JDL-layer gem behaviour


class TestJdlIntegration:
    def test_a_legacy_definition_without_a_gem_is_valid(self):
        definition = default_definition()
        assert definition.stone.gem is None
        assert resolve_gem(definition.stone.gem).definition.gemId == UNKNOWN_GEM_ID

    def test_a_custom_gem_requires_a_name(self):
        with pytest.raises(ValidationError):
            with_gem({"gemId": CUSTOM_GEM_ID})
        with_gem({"gemId": CUSTOM_GEM_ID, "customName": "meteorite"})

    def test_a_blank_custom_name_is_not_a_name(self):
        with pytest.raises(ValidationError):
            with_gem({"gemId": CUSTOM_GEM_ID, "customName": "   "})

    def test_an_unknown_field_inside_the_gem_is_rejected(self):
        with pytest.raises(ValidationError):
            with_gem({"gemId": "diamond", "carat": 1.5})

    def test_the_gem_survives_a_json_round_trip(self):
        definition = with_gem(
            {
                "gemId": "corundum.sapphire",
                "origin": "SYNTHETIC",
                "treatments": [
                    {
                        "treatment": "HEAT",
                        "status": "PRESENT",
                        "disclosure": "VENDOR_DECLARED",
                    }
                ],
                "visualProfileId": "blue.pale",
                "note": "Client-supplied stone.",
            }
        )
        again = JewelryDefinition.model_validate_json(definition.model_dump_json())
        assert again.stone.gem == definition.stone.gem
        assert definition_hash(again) == definition_hash(definition)

    def test_the_stone_geometry_fields_are_untouched_by_the_gem(self):
        base = default_definition()
        gemmed = with_gem({"gemId": "corundum.ruby"})
        for field in ("shape", "diameter", "length", "width", "depth", "orientation"):
            assert getattr(gemmed.stone, field) == getattr(base.stone, field)


# ------------------------------------------------------ instance / arrangement


class TestStoneInstance:
    def test_an_instance_carries_a_role_and_its_own_gem(self):
        instance = StoneInstance(
            instanceId="center",
            role="CENTER",
            gem=GemIdentity(gemId="diamond", origin="NATURAL"),
        )
        assert instance.role == "CENTER"
        assert instance.gem is not None
        assert instance.gem.gemId == "diamond"

    def test_two_instances_may_carry_different_gems(self):
        center = StoneInstance(
            instanceId="center", role="CENTER", gem=GemIdentity(gemId="diamond")
        )
        side = StoneInstance(
            instanceId="side-1", role="SIDE", gem=GemIdentity(gemId="corundum.sapphire")
        )
        assert center.gem is not None and side.gem is not None
        assert center.gem.gemId != side.gem.gemId

    def test_an_instance_id_is_constrained_like_a_gem_id(self):
        """A user-authored instance ID is untrusted input too."""

        with pytest.raises(ValidationError):
            StoneInstance(instanceId="../../etc/passwd", role="CENTER")

    def test_multi_stone_arrangement_is_not_advertised_as_current(self):
        """`StoneInstance` exists; multi-stone GEOMETRY does not.

        The model is the forward-looking half of the type/instance split. No
        code path builds more than one stone, and this test records that rather
        than letting the model's existence imply a capability.
        """

        definition = default_definition()
        assert not hasattr(definition, "stones")
        assert isinstance(definition.stone, StoneSpec)


# --------------------------------------------------------- spec artifacts


SPECS_DIR = Path(__file__).resolve().parents[2] / "specs" / "gem" / "v1"


class TestSpecArtifactsMatchLiveCode:
    """specs/gem/v1/ is a MIRROR of live code, re-derived on every test run.

    Sprint 20 removed three hand-copied capability lists that had already
    drifted and made Designer and Setting misreport real capabilities. These
    checks make that impossible for the gem registry rather than merely
    discouraged.
    """

    def _load(self, relative: str) -> dict:
        import json

        return json.loads((SPECS_DIR / relative).read_text(encoding="utf-8"))

    def test_the_registry_spec_matches_the_live_registry(self):
        spec = self._load("gem-registry.json")
        assert spec["registryVersion"] == GEM_REGISTRY_VERSION
        assert spec["gemCount"] == len(GEM_REGISTRY)
        spec_ids = [entry["gemId"] for entry in spec["gems"]]
        assert spec_ids == list(GEM_REGISTRY)
        for entry in spec["gems"]:
            live = get_gem(entry["gemId"])
            assert live is not None
            assert entry == live.model_dump(mode="json")

    def test_the_visual_profile_spec_matches_the_live_set(self):
        spec = self._load("visual-profile-set.json")
        assert spec["profileSetVersion"] == VISUAL_PROFILE_SET_VERSION
        assert spec["profileCount"] == len(GEM_VISUAL_PROFILES)
        for entry in spec["profiles"]:
            live = GEM_VISUAL_PROFILES[entry["profileId"]]
            assert entry == live.model_dump(mode="json")

    def test_the_alias_index_spec_matches_the_live_index(self):
        spec = self._load("alias-index.json")
        assert spec["aliases"] == dict(sorted(alias_lookup().items()))

    def test_every_example_validates_against_its_schema(self):
        import jsonschema

        identity_schema = self._load("gem-identity.schema.json")
        resolved_schema = self._load("resolved-gem.schema.json")
        examples = sorted((SPECS_DIR / "examples").glob("*.json"))
        assert len(examples) >= 10
        for path in examples:
            import json

            document = json.loads(path.read_text(encoding="utf-8"))
            schema = (
                resolved_schema if path.name.startswith("resolved-") else identity_schema
            )
            jsonschema.validate(document, schema)

    def test_every_identity_example_is_a_real_identity(self):
        import json

        for path in sorted((SPECS_DIR / "examples").glob("*.json")):
            if path.name.startswith("resolved-"):
                continue
            document = json.loads(path.read_text(encoding="utf-8"))
            identity = GemIdentity.model_validate(document)
            # Re-resolving must reproduce the committed resolved example.
            resolved_path = path.with_name(f"resolved-{path.name}")
            expected = json.loads(resolved_path.read_text(encoding="utf-8"))
            assert resolve_gem(identity).model_dump(mode="json") == expected

    def test_the_hash_separation_vectors_still_hold(self):
        spec = self._load("test-vectors/geometry-identity-hash-vectors.json")
        base = with_gem({"gemId": "corundum.ruby", "origin": "NATURAL"})
        assert spec["baseDefinitionHash"] == definition_hash(base)
        assert spec["baseGeometryHash"] == geometry_hash(base)
        by_case = {v["case"]: v for v in spec["vectors"]}
        assert by_case["different gem"]["geometryHashChanged"] is False
        assert by_case["different gem"]["definitionHashChanged"] is True
        assert by_case["wider band"]["geometryHashChanged"] is True

    def test_the_forge_vectors_match_a_live_engine_run(self):
        spec = self._load("test-vectors/forge-gem-rule-vectors.json")
        for vector in spec["vectors"]:
            if vector["rejectedBySchema"]:
                with pytest.raises(ValidationError):
                    with_gem(vector["gem"])
                continue
            live = [
                r.model_dump(mode="json")
                for r in validate_definition(with_gem(vector["gem"]))
                if r.ruleId.startswith("JM-GEM")
            ]
            assert live == vector["results"], vector["case"]

    def test_the_gem_id_validation_vectors_match_live_code(self):
        spec = self._load("test-vectors/gem-id-validation-vectors.json")
        for vector in spec["vectors"]:
            assert is_valid_gem_id(vector["gemId"]) is vector["valid"], vector["gemId"]
