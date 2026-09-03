"""Gem term recognition in Designer and Conversation (Sprint 21, sections 20/21).

Every case runs through the REAL `DesignerService` with `FakeDesignerProvider`,
so no automated test depends on a live AI call, and the assertions are about
what the pipeline actually produces rather than about the synonym tables.
"""

from __future__ import annotations

import pytest

from jewelmind.conversation import references
from jewelmind.designer import capability
from jewelmind.designer.gem_language import (
    AMBIGUOUS_GEM_TERMS,
    GEM_ORIGIN_SYNONYMS,
    GEM_TREATMENT_SYNONYMS,
    gem_alias_index,
    normalize_gem_term,
    normalize_origin_term,
    normalize_treatment_term,
)
from jewelmind.designer.normalizer import STONE_SHAPE_SYNONYMS, normalize_enum_token
from jewelmind.designer.prompts import build_jdl_fields_block
from jewelmind.designer.provider import FakeDesignerProvider
from jewelmind.designer.schemas import (
    NaturalLanguageDesignRequest,
    RawDesignerResponse,
    RawProposedValue,
)
from jewelmind.designer.service import DesignerService
from jewelmind.domain.defaults import default_definition
from jewelmind.gem.models import GemOrigin, GemTreatmentType
from jewelmind.gem.registry import GEM_REGISTRY


def interpret(values: list[tuple[str, object]], text: str = "request"):
    raw = RawDesignerResponse(
        proposedCanonicalValues=[
            RawProposedValue(field=field, value=value, sourceText=text)
            for field, value in values
        ]
    )
    service = DesignerService(FakeDesignerProvider(response=raw))
    return service.interpret(
        NaturalLanguageDesignRequest(
            requestId="test-request",
            text=text,
            interactionMode="MODIFY",
            currentJDL=default_definition(),
        )
    ).proposal


class TestTablesPointAtRealThings:
    def test_every_alias_resolves_to_a_real_registry_entry(self):
        for term, gem_id in gem_alias_index().items():
            assert gem_id in GEM_REGISTRY, (term, gem_id)

    def test_every_origin_synonym_is_a_real_origin(self):
        from typing import get_args

        valid = set(get_args(GemOrigin))
        for term, origin in GEM_ORIGIN_SYNONYMS.items():
            assert origin in valid, (term, origin)

    def test_every_treatment_synonym_is_a_real_treatment(self):
        from typing import get_args

        valid = set(get_args(GemTreatmentType))
        for term, treatment in GEM_TREATMENT_SYNONYMS.items():
            assert treatment in valid, (term, treatment)

    def test_the_ambiguous_terms_really_are_ambiguous(self):
        """Each one must genuinely name BOTH a cut and a gem.

        If a term stopped being a real cut name, refusing to resolve it as a gem
        would be an unhelpful blocker rather than an honest question.
        """

        for term in AMBIGUOUS_GEM_TERMS:
            assert term in STONE_SHAPE_SYNONYMS, term
            # And it must resolve as a gem when asked directly of the registry,
            # which is what makes it two-sided.
            from jewelmind.gem.registry import alias_lookup

            assert term in alias_lookup(), term

    def test_an_ambiguous_term_is_absent_from_the_designer_index(self):
        for term in AMBIGUOUS_GEM_TERMS:
            assert term not in gem_alias_index()


class TestNormalization:
    @pytest.mark.parametrize(
        "term,expected",
        [
            ("rubino", "corundum.ruby"),
            ("ruby", "corundum.ruby"),
            ("  RUBINO  ", "corundum.ruby"),
            ("zaffiro", "corundum.sapphire"),
            ("zaffiro blu", "corundum.sapphire"),
            ("diamante", "diamond"),
            ("diamante sintetico", "diamond"),
            ("materiale personalizzato", "custom"),
            ("pietra sconosciuta", "unknown"),
        ],
    )
    def test_recognized_terms_resolve(self, term: str, expected: str):
        gem_id, ambiguous = normalize_gem_term(term)
        assert gem_id == expected
        assert ambiguous is False

    @pytest.mark.parametrize("term", ["smeraldo", "emerald", "perla", "pearl"])
    def test_cut_or_species_terms_are_ambiguous(self, term: str):
        gem_id, ambiguous = normalize_gem_term(term)
        assert gem_id is None
        assert ambiguous is True

    @pytest.mark.parametrize("term", ["tanzanite", "", "a shiny thing", "kryptonite"])
    def test_unrecognized_terms_resolve_to_nothing(self, term: str):
        assert normalize_gem_term(term) == (None, False)

    def test_origin_terms(self):
        assert normalize_origin_term("sintetico") == "SYNTHETIC"
        assert normalize_origin_term("lab grown") == "SYNTHETIC"
        assert normalize_origin_term("naturale") == "NATURAL"
        assert normalize_origin_term("vintage") is None

    def test_treated_names_no_specific_treatment(self):
        assert normalize_treatment_term("trattato") == ("UNKNOWN", False)
        assert normalize_treatment_term("treated") == ("UNKNOWN", False)

    def test_a_named_treatment_resolves_to_that_treatment(self):
        assert normalize_treatment_term("riscaldato") == ("HEAT", False)
        assert normalize_treatment_term("irradiated") == ("IRRADIATION", False)

    def test_untreated_asserts_absence_rather_than_a_treatment(self):
        treatment, asserts_absence = normalize_treatment_term("non trattato")
        assert treatment is None
        assert asserts_absence is True

    def test_the_enum_router_delegates_gem_fields(self):
        assert normalize_enum_token("stone.gem.gemId", "rubino") == (
            "corundum.ruby",
            False,
        )
        assert normalize_enum_token("stone.gem.origin", "sintetico") == (
            "SYNTHETIC",
            False,
        )


class TestDesignerProposals:
    def test_a_gem_becomes_a_real_candidate_jdl_field(self):
        proposal = interpret([("stone.gem.gemId", "rubino")], "rubino centrale")
        assert proposal.candidateJDL.stone.gem is not None
        assert proposal.candidateJDL.stone.gem.gemId == "corundum.ruby"
        paths = {f.path: f.value for f in proposal.proposedFields}
        assert paths["stone.gem.gemId"] == "corundum.ruby"

    def test_a_normalized_gem_is_labelled_normalized_not_exact(self):
        proposal = interpret([("stone.gem.gemId", "rubino")])
        field = next(
            f for f in proposal.proposedFields if f.path == "stone.gem.gemId"
        )
        assert field.confidence == "NORMALIZED"
        assert field.provenance == "AI_INTERPRETATION"

    def test_gem_and_origin_are_proposed_independently(self):
        proposal = interpret(
            [
                ("stone.gem.gemId", "zaffiro blu"),
                ("stone.gem.origin", "sintetico"),
            ]
        )
        gem = proposal.candidateJDL.stone.gem
        assert gem is not None
        assert gem.gemId == "corundum.sapphire"
        assert gem.origin == "SYNTHETIC"

    def test_an_ambiguous_term_asks_instead_of_choosing(self):
        proposal = interpret([("stone.gem.gemId", "smeraldo")], "smeraldo trattato")
        assert proposal.candidateJDL.stone.gem is None
        assert not [f for f in proposal.proposedFields if f.path.startswith("stone.gem")]
        question = next(
            q for q in proposal.clarificationQuestions if q.field == "stone.gem.gemId"
        )
        assert question.ambiguityLevel == "HIGH_IMPACT_AMBIGUITY"
        assert any("cut" in option for option in question.options)

    def test_an_unknown_gem_offers_the_two_escape_hatches(self):
        proposal = interpret([("stone.gem.gemId", "tanzanite")])
        question = next(
            q for q in proposal.clarificationQuestions if q.field == "stone.gem.gemId"
        )
        assert set(question.options) == {"custom", "unknown"}
        # NOT an unsupported feature: every gem is expressible.
        assert not proposal.unsupportedFeatures

    def test_a_custom_material_carries_the_users_own_words(self):
        proposal = interpret(
            [
                ("stone.gem.gemId", "materiale personalizzato"),
                ("stone.gem.customName", "meteorite"),
            ]
        )
        gem = proposal.candidateJDL.stone.gem
        assert gem is not None
        assert gem.gemId == "custom"
        assert gem.customName == "meteorite"

    def test_unspecified_fields_are_preserved_on_a_gem_modification(self):
        base = default_definition()
        proposal = interpret([("stone.gem.gemId", "rubino")])
        candidate = proposal.candidateJDL
        assert candidate.band.width == base.band.width
        assert candidate.stone.shape == base.stone.shape
        assert candidate.stone.diameter == base.stone.diameter
        assert candidate.setting.prongCount == base.setting.prongCount

    def test_a_gem_change_is_reported_in_the_diff(self):
        proposal = interpret([("stone.gem.gemId", "rubino")])
        changed = {d.path for d in proposal.diff if d.changed}
        assert "stone.gem.gemId" in changed
        # And nothing geometric moved.
        assert not any(path.startswith("band.") for path in changed)

    def test_designer_never_proposes_a_visual_profile_or_a_treatment_list(self):
        """Both are outside Designer's field set on purpose.

        `visualProfileId` is a presentation choice, not design intent, and
        `treatments` is a list a dotted-path patch cannot express.
        """

        assert not capability.is_known_field("stone.gem.visualProfileId")
        assert not capability.is_known_field("stone.gem.treatments")
        proposal = interpret([("stone.gem.visualProfileId", "blue.pale")])
        assert proposal.candidateJDL.stone.gem is None

    def test_capabilities_report_the_live_registry(self):
        capabilities = capability.current_capabilities()
        from jewelmind.gem.registry import current_gem_ids

        assert capabilities["gemId"] == current_gem_ids()
        assert "NATURAL" in capabilities["gemOrigin"]

    def test_the_prompt_field_list_is_derived_from_the_real_field_set(self):
        block = build_jdl_fields_block()
        for path in capability.KNOWN_JDL_FIELD_PATHS:
            assert path in block, path


class TestConversationReferences:
    @pytest.mark.parametrize(
        "text",
        ["make it a ruby", "rendila un rubino", "usa uno zaffiro sintetico"],
    )
    def test_a_gem_word_resolves_the_target_to_the_stone(self, text: str):
        assert references.resolve_implicit_target(text, None) == ("STONE", False)

    def test_a_metal_word_still_resolves_to_material_appearance(self):
        """Pre-existing behaviour must not shift under the new rule."""

        assert references.resolve_implicit_target("make it rose gold", None) == (
            "MATERIAL_APPEARANCE",
            False,
        )

    @pytest.mark.parametrize("text", ["make it emerald", "make it a pearl"])
    def test_an_ambiguous_cut_or_species_word_resolves_no_target(self, text: str):
        target, ambiguous = references.resolve_implicit_target(text, None)
        assert target != "STONE"

    def test_a_bare_comparative_is_still_ambiguous(self):
        assert references.resolve_implicit_target("make it wider", None) == (None, True)
