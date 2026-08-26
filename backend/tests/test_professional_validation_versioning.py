"""VERSION_CHANGE_REVALIDATION_TEST, RULE_VERSION_VALIDATION_TEST,
REVIEW_CASE_REPRODUCIBILITY_TEST — see the Sprint 13 brief's testing
section.
"""

from __future__ import annotations

from jewelmind.domain.defaults import default_definition
from jewelmind.professional_validation.review_package import _forge_registry_version
from jewelmind.professional_validation.schemas import ReviewCase
from jewelmind.professional_validation.versioning import classify_version_impact
from jewelmind.utils.hashing import definition_hash


class TestVersionChangeImpact:
    def test_identical_version_means_unchanged(self):
        assert classify_version_impact("1.0.0", "1.0.0") == "VALIDATION_VERSION_UNCHANGED"

    def test_minor_or_patch_change_requires_review_not_automatic_revalidation(self):
        assert classify_version_impact("1.0.0", "1.1.0") == "REVIEW_REQUIRED"
        assert classify_version_impact("1.0.0", "1.0.1") == "REVIEW_REQUIRED"

    def test_major_change_requires_revalidation(self):
        assert classify_version_impact("1.0.0", "2.0.0") == "REVALIDATION_REQUIRED"

    def test_a_validated_rule_does_not_silently_carry_forward_after_a_major_change(self):
        # Direct regression for docs/bible/06-forge/103-professional-validation-lifecycle.md's
        # existing rule, now backed by a real function rather than prose alone.
        impact = classify_version_impact(validated_version="1.0.0", current_version="2.0.0")
        assert impact == "REVALIDATION_REQUIRED"


class TestReviewCaseReproducibility:
    def test_the_same_jdl_produces_the_same_definition_hash_every_time(self):
        definition = default_definition()
        hash_a = definition_hash(definition)
        hash_b = definition_hash(definition)
        assert hash_a == hash_b

    def test_a_review_case_built_from_a_real_definition_carries_a_real_reproducible_hash(self):
        definition = default_definition()
        case = ReviewCase(
            caseId="JMCASE001",
            purpose="Default six-prong solitaire, baseline review case.",
            jdlDocument=definition.model_dump(mode="json"),
            definitionHash=definition_hash(definition),
            forgeRuleSetVersion=_forge_registry_version(),
            atlasVersion="unknown",
        )
        # Rebuilding a JewelryDefinition from the case's own stored JDL and
        # re-hashing it must reproduce the exact same hash the case claims.
        from jewelmind.domain.schema import JewelryDefinition

        rebuilt = JewelryDefinition.model_validate(case.jdlDocument)
        assert definition_hash(rebuilt) == case.definitionHash
