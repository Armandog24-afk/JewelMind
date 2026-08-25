"""Unit tests for the Design Intent Model v1 deterministic pipeline."""

from __future__ import annotations

from jewelmind.design_intent.normalizer import (
    normalize_descriptor,
    normalize_predicate,
    normalize_target,
)
from jewelmind.design_intent.resolver import (
    RawRelationInput,
    RawStatementInput,
    build_design_intent,
    compute_intent_diff,
)
from jewelmind.design_intent.vocabulary import CATEGORIES, continuum_distance


def S(target: str, concept: str, value: str, source: str | None = None) -> RawStatementInput:
    return RawStatementInput(target=target, concept=concept, value=value, sourceText=source or value)


def R(subject: str, predicate: str, obj: str, source: str = "") -> RawRelationInput:
    return RawRelationInput(subject=subject, predicate=predicate, object=obj, sourceText=source)


class TestVocabulary:
    def test_every_category_is_an_ordered_continuum_not_numeric(self):
        for name, category in CATEGORIES.items():
            assert len(category.order) >= 2
            for value in category.order:
                assert isinstance(value, str)
                assert not value.replace(".", "", 1).isdigit()

    def test_continuum_distance_is_symmetric(self):
        assert continuum_distance("VISUAL_WEIGHT", "DELICATE", "BOLD") == continuum_distance(
            "VISUAL_WEIGHT", "BOLD", "DELICATE"
        )

    def test_continuum_distance_unknown_value_returns_none(self):
        assert continuum_distance("VISUAL_WEIGHT", "DELICATE", "NOT_A_VALUE") is None


class TestNormalizeTarget:
    def test_canonical_target_passes_through(self):
        assert normalize_target("BAND") == "BAND"

    def test_english_synonym(self):
        assert normalize_target("stone") == "STONE"

    def test_italian_synonym(self):
        assert normalize_target("fascia") == "BAND"
        assert normalize_target("pietra") == "STONE"
        assert normalize_target("anello") == "RING"

    def test_unknown_target_returns_none(self):
        assert normalize_target("nonsense_target") is None


class TestNormalizeDescriptor:
    def test_exact_canonical_value(self):
        value, is_exact = normalize_descriptor("VISUAL_WEIGHT", "DELICATE")
        assert value == "DELICATE"
        assert is_exact is True

    def test_synonym_normalizes_and_is_not_exact(self):
        value, is_exact = normalize_descriptor("VISUAL_WEIGHT", "delicato")
        assert value == "DELICATE"
        assert is_exact is False

    def test_unknown_descriptor_returns_none(self):
        value, _ = normalize_descriptor("VISUAL_WEIGHT", "elegant")
        assert value is None

    def test_unknown_concept_returns_none(self):
        value, _ = normalize_descriptor("NOT_A_CONCEPT", "delicate")
        assert value is None

    def test_ambiguous_word_deliberately_excluded(self):
        # "importante" can mean either substantial or eye-catching in
        # Italian — deliberately absent from every synonym table so it
        # falls through to an unresolved descriptor rather than a guess.
        value, _ = normalize_descriptor("VISUAL_WEIGHT", "importante")
        assert value is None


class TestNormalizePredicate:
    def test_canonical_predicate(self):
        assert normalize_predicate("DOMINANT_OVER") == "DOMINANT_OVER"

    def test_phrase_synonym(self):
        assert normalize_predicate("narrower than") == "NARROWER_THAN"

    def test_unknown_predicate_returns_none(self):
        assert normalize_predicate("somehow related to") is None


class TestBuildDesignIntent:
    def test_recognized_statement_is_preserved_never_resolved_to_geometry(self):
        intent = build_design_intent(
            "Fammi una fascia delicata.", "CREATE", None,
            [S("band", "VISUAL_WEIGHT", "delicato", "delicata")],
            [],
        )
        assert len(intent.statements) == 1
        statement = intent.statements[0]
        assert statement.target == "BAND"
        assert statement.concept == "VISUAL_WEIGHT"
        assert statement.value == "DELICATE"
        assert statement.provenance == "AI_NORMALIZED"
        assert statement.resolutionStatus == "PRESERVED"
        assert statement.relatedJDLPaths == []

    def test_unrecognized_descriptor_is_preserved_as_unresolved_text(self):
        intent = build_design_intent(
            "Rendilo più elegante.", "CREATE", None,
            [S("ring", "VISUAL_EMPHASIS", "elegante")],
            [],
        )
        assert intent.statements == []
        assert "elegante" in intent.unresolvedDescriptors

    def test_unknown_target_is_preserved_as_unresolved(self):
        intent = build_design_intent(
            "text", "CREATE", None,
            [S("halo", "VISUAL_WEIGHT", "delicate", "halo delicate")],
            [],
        )
        assert intent.statements == []
        assert "halo delicate" in intent.unresolvedDescriptors

    def test_provider_level_unresolved_descriptors_pass_through(self):
        intent = build_design_intent(
            "text", "CREATE", None, [], [], raw_unresolved_descriptors=["elegant"]
        )
        assert "elegant" in intent.unresolvedDescriptors

    def test_relation_is_preserved(self):
        intent = build_design_intent(
            "The band should look slim compared with the stone.", "CREATE", None,
            [],
            [R("band", "narrower than", "stone", "band slim vs stone")],
        )
        assert len(intent.relationships) == 1
        relation = intent.relationships[0]
        assert relation.subject == "BAND"
        assert relation.predicate == "NARROWER_THAN"
        assert relation.object == "STONE"
        assert relation.resolutionStatus == "PRESERVED"

    def test_contradictory_statements_are_flagged_conflicting(self):
        intent = build_design_intent(
            "delicate but very bold", "CREATE", None,
            [S("ring", "VISUAL_WEIGHT", "delicate"), S("ring", "VISUAL_WEIGHT", "bold", "very bold")],
            [],
        )
        assert len(intent.conflicts) == 1
        assert intent.conflicts[0].type == "EXPLICIT_CONTRADICTION"
        assert all(s.resolutionStatus == "CONFLICTING" for s in intent.statements)

    def test_adjacent_continuum_values_are_not_a_conflict(self):
        intent = build_design_intent(
            "delicate and light", "CREATE", None,
            [S("ring", "VISUAL_WEIGHT", "delicate"), S("ring", "VISUAL_WEIGHT", "light")],
            [],
        )
        assert intent.conflicts == []
        assert all(s.resolutionStatus == "PRESERVED" for s in intent.statements)


class TestModifyMerge:
    def test_modify_preserves_previously_stored_statements(self):
        previous = build_design_intent(
            "Fammi un anello delicato.", "CREATE", None,
            [S("ring", "VISUAL_WEIGHT", "delicate", "delicato")],
            [],
        )
        updated = build_design_intent(
            "Rendilo più minimal.", "MODIFY", previous,
            [S("ring", "SIMPLICITY", "minimal")],
            [],
        )
        concepts = {(s.target, s.concept): s.value for s in updated.statements}
        assert concepts[("RING", "VISUAL_WEIGHT")] == "DELICATE"
        assert concepts[("RING", "SIMPLICITY")] == "MINIMAL"

    def test_modify_overrides_same_target_concept_pair(self):
        previous = build_design_intent(
            "text", "CREATE", None, [S("ring", "VISUAL_WEIGHT", "delicate")], []
        )
        updated = build_design_intent(
            "make it bolder now", "MODIFY", previous,
            [S("ring", "VISUAL_WEIGHT", "bold", "bolder")],
            [],
        )
        assert len(updated.statements) == 1
        assert updated.statements[0].value == "BOLD"

    def test_create_ignores_previous_intent(self):
        previous = build_design_intent(
            "text", "CREATE", None, [S("ring", "VISUAL_WEIGHT", "delicate")], []
        )
        fresh = build_design_intent("start over", "CREATE", previous, [], [])
        assert fresh.statements == []


class TestIntentDiff:
    def test_added_and_unchanged(self):
        before = build_design_intent(
            "text", "CREATE", None, [S("ring", "VISUAL_WEIGHT", "delicate")], []
        )
        after = build_design_intent(
            "text2", "MODIFY", before, [S("ring", "SIMPLICITY", "minimal")], []
        )
        entries = {e.key: e.changeType for e in compute_intent_diff(before, after)}
        assert entries["RING.SIMPLICITY"] == "ADDED"
        assert entries["RING.VISUAL_WEIGHT"] == "UNCHANGED"

    def test_changed_value(self):
        before = build_design_intent(
            "text", "CREATE", None, [S("ring", "VISUAL_WEIGHT", "delicate")], []
        )
        after = build_design_intent(
            "text2", "MODIFY", before, [S("ring", "VISUAL_WEIGHT", "bold")], []
        )
        entries = {e.key: e for e in compute_intent_diff(before, after)}
        assert entries["RING.VISUAL_WEIGHT"].changeType == "CHANGED"
        assert entries["RING.VISUAL_WEIGHT"].previousValue == "DELICATE"
        assert entries["RING.VISUAL_WEIGHT"].newValue == "BOLD"

    def test_no_previous_everything_added(self):
        after = build_design_intent(
            "text", "CREATE", None, [S("ring", "VISUAL_WEIGHT", "delicate")], []
        )
        entries = compute_intent_diff(None, after)
        assert entries[0].changeType == "ADDED"
