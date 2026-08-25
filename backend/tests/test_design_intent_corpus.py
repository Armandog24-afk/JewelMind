"""Deterministic natural-language test corpus for Design Intent Model v1.

Mirrors the structure of backend/tests/test_designer_corpus.py: every case
supplies the raw statements/relations a correctly-behaving provider should
have extracted for that request text (never a live LLM call), and asserts
what the real deterministic pipeline does with them. At least 60 cases,
covering explicit descriptor extraction, normalization, target
resolution, relations, unresolved/unknown descriptors, and — the mandatory
category from docs/bible/13-design-intent/318 (evaluation) and 39 of the
Sprint 11 brief — that no aesthetic descriptor ever produces an arbitrary
numeric JDL change.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

import pytest

from jewelmind.design_intent.schemas import DesignIntent
from jewelmind.designer.provider import FakeDesignerProvider
from jewelmind.designer.schemas import NaturalLanguageDesignRequest
from jewelmind.designer.schemas import RawDesignerResponse as Raw
from jewelmind.designer.schemas import RawIntentRelation as REL
from jewelmind.designer.schemas import RawIntentStatement as STMT
from jewelmind.designer.service import DesignerService


def stmt(target: str, concept: str, value: str, source: str | None = None) -> STMT:
    return STMT(target=target, concept=concept, value=value, sourceText=source or value)


def rel(subject: str, predicate: str, obj: str, source: str = "") -> REL:
    return REL(subject=subject, predicate=predicate, object=obj, sourceText=source)


def one_stmt(target: str, concept: str, value: str, source: str | None = None) -> Raw:
    return Raw(designIntentStatements=[stmt(target, concept, value, source)])


def one_rel(subject: str, predicate: str, obj: str, source: str = "") -> Raw:
    return Raw(designIntentRelations=[rel(subject, predicate, obj, source)])


def unresolved(*texts: str) -> Raw:
    return Raw(unresolvedDescriptors=list(texts))


@dataclass
class Case:
    id: str
    category: str
    text: str
    check: Callable[..., None]
    raw: Raw = field(default_factory=Raw)


def _check(condition: bool) -> None:
    assert condition


def has_statement(target: str, concept: str, value: str) -> Callable:
    def _fn(intent: DesignIntent, proposal) -> None:
        _check(
            any(s.target == target and s.concept == concept and s.value == value for s in intent.statements)
        )

    return _fn


def has_relation(subject: str, predicate: str, obj: str) -> Callable:
    def _fn(intent: DesignIntent, proposal) -> None:
        _check(
            any(
                r.subject == subject and r.predicate == predicate and r.object == obj
                for r in intent.relationships
            )
        )

    return _fn


def has_unresolved(text: str) -> Callable:
    return lambda intent, proposal: _check(text in intent.unresolvedDescriptors)


def no_numeric_field_changed() -> Callable:
    def _fn(intent: DesignIntent, proposal) -> None:
        _check(not any(d.changed for d in proposal.diff))

    return _fn


def has_conflict_count(n: int) -> Callable:
    return lambda intent, proposal: _check(len(intent.conflicts) == n)


def all_of(*checks: Callable) -> Callable:
    def _combined(intent: DesignIntent, proposal) -> None:
        for c in checks:
            c(intent, proposal)

    return _combined


def has_two_statements(t1: str, c1: str, v1: str, t2: str, c2: str, v2: str) -> Callable:
    return all_of(has_statement(t1, c1, v1), has_statement(t2, c2, v2))


def two_stmts(t1: str, c1: str, v1: str, t2: str, c2: str, v2: str) -> Raw:
    return Raw(designIntentStatements=[stmt(t1, c1, v1), stmt(t2, c2, v2)])


CASES: list[Case] = [
    # --- explicit descriptor extraction ---
    Case(
        "desc-01", "DESCRIPTOR_EXTRACTION", "Vorrei un anello delicato.",
        has_statement("RING", "VISUAL_WEIGHT", "DELICATE"),
        one_stmt("ring", "VISUAL_WEIGHT", "delicato"),
    ),
    Case(
        "desc-02", "DESCRIPTOR_EXTRACTION", "Make it delicate.",
        has_statement("RING", "VISUAL_WEIGHT", "DELICATE"),
        one_stmt("ring", "VISUAL_WEIGHT", "delicate"),
    ),
    Case(
        "desc-03", "DESCRIPTOR_EXTRACTION", "Fammi qualcosa di molto minimal.",
        has_statement("RING", "SIMPLICITY", "MINIMAL"),
        one_stmt("ring", "SIMPLICITY", "minimal"),
    ),
    Case(
        "desc-04", "DESCRIPTOR_EXTRACTION", "Keep the ring minimal.",
        has_statement("RING", "SIMPLICITY", "MINIMAL"),
        one_stmt("ring", "SIMPLICITY", "minimal"),
    ),
    Case(
        "desc-05", "DESCRIPTOR_EXTRACTION", "Lo voglio classico e pulito.",
        has_two_statements("RING", "STYLE_TEMPORALITY", "CLASSIC", "RING", "SIMPLICITY", "CLEAN"),
        two_stmts("ring", "STYLE_TEMPORALITY", "classico", "ring", "SIMPLICITY", "pulito"),
    ),
    Case(
        "desc-06", "DESCRIPTOR_EXTRACTION", "I want a classic clean solitaire.",
        has_two_statements("RING", "STYLE_TEMPORALITY", "CLASSIC", "RING", "SIMPLICITY", "CLEAN"),
        two_stmts("ring", "STYLE_TEMPORALITY", "classic", "ring", "SIMPLICITY", "clean"),
    ),
    Case(
        "desc-07", "DESCRIPTOR_EXTRACTION", "Più moderno.",
        has_statement("RING", "STYLE_TEMPORALITY", "MODERN"),
        one_stmt("ring", "STYLE_TEMPORALITY", "moderno", "più moderno"),
    ),
    Case(
        "desc-08", "DESCRIPTOR_EXTRACTION", "Molto semplice.",
        has_statement("RING", "SIMPLICITY", "CLEAN"),
        one_stmt("ring", "SIMPLICITY", "semplice", "molto semplice"),
    ),
    Case(
        "desc-09", "DESCRIPTOR_EXTRACTION", "Make it bold but understated.",
        has_two_statements("RING", "VISUAL_WEIGHT", "BOLD", "RING", "VISUAL_EMPHASIS", "UNDERSTATED"),
        two_stmts("ring", "VISUAL_WEIGHT", "bold", "ring", "VISUAL_EMPHASIS", "understated"),
    ),
    Case(
        "desc-10", "DESCRIPTOR_EXTRACTION", "Voglio una fascia sottile.",
        has_statement("BAND", "PROPORTIONAL_CHARACTER", "SLIM"),
        one_stmt("band", "PROPORTIONAL_CHARACTER", "sottile"),
    ),
    Case(
        "desc-11", "DESCRIPTOR_EXTRACTION", "A slim band, please.",
        has_statement("BAND", "PROPORTIONAL_CHARACTER", "SLIM"),
        one_stmt("band", "PROPORTIONAL_CHARACTER", "slim"),
    ),
    Case(
        "desc-12", "DESCRIPTOR_EXTRACTION", "Un design morbido.",
        has_statement("RING", "STRUCTURAL_CHARACTER", "SOFT"),
        one_stmt("ring", "STRUCTURAL_CHARACTER", "morbido"),
    ),
    Case(
        "desc-13", "DESCRIPTOR_EXTRACTION", "Fammi qualcosa di delicato e leggero.",
        has_statement("RING", "VISUAL_WEIGHT", "DELICATE"),
        one_stmt("ring", "VISUAL_WEIGHT", "delicato"),
    ),
    Case(
        "desc-14", "DESCRIPTOR_EXTRACTION", "Something bold and modern.",
        has_two_statements("RING", "VISUAL_WEIGHT", "BOLD", "RING", "STYLE_TEMPORALITY", "MODERN"),
        two_stmts("ring", "VISUAL_WEIGHT", "bold", "ring", "STYLE_TEMPORALITY", "modern"),
    ),
    Case(
        "desc-15", "DESCRIPTOR_EXTRACTION", "Voglio un design pulito e bilanciato.",
        has_two_statements("RING", "SIMPLICITY", "CLEAN", "RING", "VISUAL_WEIGHT", "BALANCED"),
        two_stmts("ring", "SIMPLICITY", "pulito", "ring", "VISUAL_WEIGHT", "bilanciato"),
    ),
    Case(
        "desc-16", "DESCRIPTOR_EXTRACTION", "I'd like it clean and balanced.",
        has_two_statements("RING", "SIMPLICITY", "CLEAN", "RING", "VISUAL_WEIGHT", "BALANCED"),
        two_stmts("ring", "SIMPLICITY", "clean", "ring", "VISUAL_WEIGHT", "balanced"),
    ),
    Case(
        "desc-17", "DESCRIPTOR_EXTRACTION", "Fascia ampia e robusta.",
        has_two_statements(
            "BAND", "PROPORTIONAL_CHARACTER", "BROAD", "BAND", "STRUCTURAL_CHARACTER", "STRONG"
        ),
        two_stmts("band", "PROPORTIONAL_CHARACTER", "ampia", "band", "STRUCTURAL_CHARACTER", "robusta"),
    ),
    Case(
        "desc-18", "DESCRIPTOR_EXTRACTION", "A broad, strong band.",
        has_two_statements(
            "BAND", "PROPORTIONAL_CHARACTER", "BROAD", "BAND", "STRUCTURAL_CHARACTER", "STRONG"
        ),
        two_stmts("band", "PROPORTIONAL_CHARACTER", "broad", "band", "STRUCTURAL_CHARACTER", "strong"),
    ),
    Case(
        "desc-19", "DESCRIPTOR_EXTRACTION", "Griffe dal design pulito.",
        has_statement("PRONGS", "SIMPLICITY", "CLEAN"),
        one_stmt("griffe", "SIMPLICITY", "pulito"),
    ),
    Case(
        "desc-20", "DESCRIPTOR_EXTRACTION", "Clean-looking prongs.",
        has_statement("PRONGS", "SIMPLICITY", "CLEAN"),
        one_stmt("prongs", "SIMPLICITY", "clean"),
    ),
    Case(
        "desc-21", "DESCRIPTOR_EXTRACTION", "Basket solido.",
        has_statement("BASKET", "STRUCTURAL_CHARACTER", "STRONG"),
        one_stmt("basket", "STRUCTURAL_CHARACTER", "solido"),
    ),
    Case(
        "desc-22", "DESCRIPTOR_EXTRACTION", "A solid-feeling basket.",
        has_statement("BASKET", "STRUCTURAL_CHARACTER", "STRONG"),
        one_stmt("basket", "STRUCTURAL_CHARACTER", "strong", "solid-feeling"),
    ),
    Case(
        "desc-23", "DESCRIPTOR_EXTRACTION", "Fammi un gioiello contemporaneo.",
        has_statement("JEWELRY_PRODUCT", "STYLE_TEMPORALITY", "CONTEMPORARY"),
        one_stmt("gioiello", "STYLE_TEMPORALITY", "contemporaneo"),
    ),
    Case(
        "desc-24", "DESCRIPTOR_EXTRACTION", "A contemporary piece of jewelry.",
        has_statement("JEWELRY_PRODUCT", "STYLE_TEMPORALITY", "CONTEMPORARY"),
        one_stmt("jewelry", "STYLE_TEMPORALITY", "contemporary"),
    ),
    Case(
        "desc-25", "DESCRIPTOR_EXTRACTION", "Voglio una pietra dal peso visivo audace.",
        has_statement("STONE", "VISUAL_WEIGHT", "BOLD"),
        one_stmt("pietra", "VISUAL_WEIGHT", "audace"),
    ),
    Case(
        "desc-26", "DESCRIPTOR_EXTRACTION", "A bold-looking diamond.",
        has_statement("STONE", "VISUAL_WEIGHT", "BOLD"),
        one_stmt("diamond", "VISUAL_WEIGHT", "bold", "bold-looking"),
    ),

    # --- normalization: multiple synonyms per concept ---
    Case(
        "norm-01", "NORMALIZATION", "leggero visivamente",
        has_statement("RING", "VISUAL_WEIGHT", "LIGHT"),
        one_stmt("ring", "VISUAL_WEIGHT", "leggero", "leggero visivamente"),
    ),
    Case(
        "norm-02", "NORMALIZATION", "lightweight-looking",
        has_statement("RING", "VISUAL_WEIGHT", "LIGHT"),
        one_stmt("ring", "VISUAL_WEIGHT", "lightweight-looking"),
    ),
    Case(
        "norm-03", "NORMALIZATION", "sostanzioso",
        has_statement("RING", "VISUAL_WEIGHT", "SUBSTANTIAL"),
        one_stmt("ring", "VISUAL_WEIGHT", "sostanzioso"),
    ),
    Case(
        "norm-04", "NORMALIZATION", "substantial",
        has_statement("RING", "VISUAL_WEIGHT", "SUBSTANTIAL"),
        one_stmt("ring", "VISUAL_WEIGHT", "substantial"),
    ),
    Case(
        "norm-05", "NORMALIZATION", "audace",
        has_statement("RING", "VISUAL_WEIGHT", "BOLD"),
        one_stmt("ring", "VISUAL_WEIGHT", "audace"),
    ),
    Case(
        "norm-06", "NORMALIZATION", "dettagliato",
        has_statement("RING", "SIMPLICITY", "DETAILED"),
        one_stmt("ring", "SIMPLICITY", "dettagliato"),
    ),
    Case(
        "norm-07", "NORMALIZATION", "elaborato",
        has_statement("RING", "SIMPLICITY", "ORNATE"),
        one_stmt("ring", "SIMPLICITY", "elaborato"),
    ),
    Case(
        "norm-08", "NORMALIZATION", "timeless",
        has_statement("RING", "STYLE_TEMPORALITY", "TIMELESS"),
        one_stmt("ring", "STYLE_TEMPORALITY", "timeless"),
    ),
    Case(
        "norm-09", "NORMALIZATION", "vistoso",
        has_statement("RING", "VISUAL_EMPHASIS", "STATEMENT"),
        one_stmt("ring", "VISUAL_EMPHASIS", "vistoso"),
    ),
    Case(
        "norm-10", "NORMALIZATION", "ampio",
        has_statement("BAND", "PROPORTIONAL_CHARACTER", "BROAD"),
        one_stmt("band", "PROPORTIONAL_CHARACTER", "ampio"),
    ),
    Case(
        "norm-11", "NORMALIZATION", "robusto",
        has_statement("SETTING", "STRUCTURAL_CHARACTER", "STRONG"),
        one_stmt("setting", "STRUCTURAL_CHARACTER", "robusto"),
    ),
    Case(
        "norm-12", "NORMALIZATION", "sobrio",
        has_statement("RING", "VISUAL_EMPHASIS", "UNDERSTATED"),
        one_stmt("ring", "VISUAL_EMPHASIS", "sobrio"),
    ),
    Case(
        "norm-13", "NORMALIZATION", "fine",
        has_statement("RING", "VISUAL_WEIGHT", "DELICATE"),
        one_stmt("ring", "VISUAL_WEIGHT", "fine"),
    ),
    Case(
        "norm-14", "NORMALIZATION", "narrow",
        has_statement("BAND", "PROPORTIONAL_CHARACTER", "SLIM"),
        one_stmt("band", "PROPORTIONAL_CHARACTER", "narrow"),
    ),
    Case(
        "norm-15", "NORMALIZATION", "largo",
        has_statement("BAND", "PROPORTIONAL_CHARACTER", "BROAD"),
        one_stmt("band", "PROPORTIONAL_CHARACTER", "largo"),
    ),
    Case(
        "norm-16", "NORMALIZATION", "morbida",
        has_statement("RING", "STRUCTURAL_CHARACTER", "SOFT"),
        one_stmt("ring", "STRUCTURAL_CHARACTER", "morbida"),
    ),
    Case(
        "norm-17", "NORMALIZATION", "soft",
        has_statement("RING", "STRUCTURAL_CHARACTER", "SOFT"),
        one_stmt("ring", "STRUCTURAL_CHARACTER", "soft"),
    ),
    Case(
        "norm-18", "NORMALIZATION", "detailed",
        has_statement("RING", "SIMPLICITY", "DETAILED"),
        one_stmt("ring", "SIMPLICITY", "detailed"),
    ),
    Case(
        "norm-19", "NORMALIZATION", "ornate",
        has_statement("RING", "SIMPLICITY", "ORNATE"),
        one_stmt("ring", "SIMPLICITY", "ornate"),
    ),
    Case(
        "norm-20", "NORMALIZATION", "bilanciata",
        has_statement("RING", "SIMPLICITY", "BALANCED"),
        one_stmt("ring", "SIMPLICITY", "bilanciata"),
    ),

    # --- target resolution ---
    Case(
        "target-01", "TARGET_RESOLUTION", "La fascia deve sembrare delicata.",
        has_statement("BAND", "VISUAL_WEIGHT", "DELICATE"),
        one_stmt("fascia", "VISUAL_WEIGHT", "delicata"),
    ),
    Case(
        "target-02", "TARGET_RESOLUTION", "The stone should feel bold.",
        has_statement("STONE", "VISUAL_WEIGHT", "BOLD"),
        one_stmt("stone", "VISUAL_WEIGHT", "bold"),
    ),
    Case(
        "target-03", "TARGET_RESOLUTION", "Le griffe discrete.",
        has_statement("PRONGS", "VISUAL_EMPHASIS", "UNDERSTATED"),
        one_stmt("griffe", "VISUAL_EMPHASIS", "discreto", "discrete"),
    ),
    Case(
        "target-04", "TARGET_RESOLUTION", "Overall it should feel balanced.",
        has_statement("RING", "VISUAL_WEIGHT", "BALANCED"),
        one_stmt("overall", "VISUAL_WEIGHT", "balanced"),
    ),
    Case(
        "target-05", "TARGET_RESOLUTION", "Il castone deve essere semplice.",
        has_statement("SETTING", "SIMPLICITY", "CLEAN"),
        one_stmt("castone", "SIMPLICITY", "semplice"),
    ),

    # --- relations ---
    Case(
        "rel-01", "RELATION", "La fascia deve sembrare sottile rispetto alla pietra.",
        has_relation("BAND", "NARROWER_THAN", "STONE"),
        one_rel("band", "narrower than", "stone", "fascia sottile rispetto alla pietra"),
    ),
    Case(
        "rel-02", "RELATION", "The band should look slim compared with the stone.",
        has_relation("BAND", "NARROWER_THAN", "STONE"),
        one_rel("band", "narrower than", "stone", "band slim vs stone"),
    ),
    Case(
        "rel-03", "RELATION", "Vorrei che la pietra fosse la protagonista.",
        has_relation("STONE", "DOMINANT_OVER", "RING"),
        one_rel("stone", "dominant over", "ring", "pietra protagonista"),
    ),
    Case(
        "rel-04", "RELATION", "Make the center stone the visual focus.",
        has_statement("STONE", "VISUAL_EMPHASIS", "CENTER_FOCUSED"),
        one_stmt("stone", "VISUAL_EMPHASIS", "center_focused", "visual focus"),
    ),
    Case(
        "rel-05", "RELATION", "Le griffe discrete rispetto alla pietra.",
        has_relation("PRONGS", "DISCREET_RELATIVE_TO", "STONE"),
        one_rel("prongs", "discreet relative to", "stone", "griffe discrete rispetto alla pietra"),
    ),
    Case(
        "rel-06", "RELATION", "Setting and stone should feel balanced with each other.",
        has_relation("SETTING", "BALANCED_WITH", "STONE"),
        one_rel("setting", "balanced with", "stone", "setting balanced with stone"),
    ),

    # --- unresolved / unknown descriptors ---
    Case(
        "unresolved-01", "UNRESOLVED_DESCRIPTOR", "Più elegante.",
        has_unresolved("elegante"), unresolved("elegante"),
    ),
    Case(
        "unresolved-02", "UNRESOLVED_DESCRIPTOR", "More elegant.",
        has_unresolved("elegant"), unresolved("elegant"),
    ),
    Case(
        "unresolved-03", "UNRESOLVED_DESCRIPTOR", "Lo voglio importante ma non vistoso.",
        has_unresolved("importante"),
        Raw(
            unresolvedDescriptors=["importante"],
            designIntentStatements=[stmt("ring", "VISUAL_EMPHASIS", "vistoso", "non vistoso")],
        ),
    ),
    Case(
        "unresolved-04", "UNRESOLVED_DESCRIPTOR", "Delicato ma con una pietra importante.",
        all_of(has_statement("RING", "VISUAL_WEIGHT", "DELICATE"), has_unresolved("pietra importante")),
        Raw(
            designIntentStatements=[stmt("ring", "VISUAL_WEIGHT", "delicato")],
            unresolvedDescriptors=["pietra importante"],
        ),
    ),
    Case(
        "unresolved-05", "UNRESOLVED_DESCRIPTOR", "Fai la fascia più larga.",
        has_unresolved("più larga"), unresolved("più larga"),
    ),
    Case(
        "unresolved-06", "UNRESOLVED_DESCRIPTOR", "Something bold and unique.",
        has_unresolved("unique"),
        Raw(designIntentStatements=[stmt("ring", "VISUAL_WEIGHT", "bold")], unresolvedDescriptors=["unique"]),
    ),
    Case(
        "unresolved-07", "UNRESOLVED_DESCRIPTOR", "Fai la fascia più stretta.",
        has_unresolved("più stretta"), unresolved("più stretta"),
    ),
    Case(
        "unresolved-08", "UNRESOLVED_DESCRIPTOR", "Make the prongs thinner.",
        has_unresolved("thinner"), unresolved("thinner"),
    ),

    # --- unknown target / unknown concept (still preserved, not crashed) ---
    Case(
        "unknown-01", "UNKNOWN_DESCRIPTOR", "sculptural feel",
        has_unresolved("sculptural feel"),
        one_stmt("halo", "VISUAL_WEIGHT", "delicate", "sculptural feel"),
    ),
    Case(
        "unknown-02", "UNKNOWN_DESCRIPTOR", "vibe check",
        has_unresolved("vibe check"),
        one_stmt("ring", "MOOD", "cool", "vibe check"),
    ),

    # --- NO_ARBITRARY_NUMERIC_MAPPING (mandatory category) ---
    Case(
        "no-numeric-01", "NO_ARBITRARY_NUMERIC_MAPPING", "make the band delicate",
        no_numeric_field_changed(),
        one_stmt("band", "VISUAL_WEIGHT", "delicate"),
    ),
    Case(
        "no-numeric-02", "NO_ARBITRARY_NUMERIC_MAPPING", "make it bolder",
        no_numeric_field_changed(),
        one_stmt("ring", "VISUAL_WEIGHT", "bold", "bolder"),
    ),
    Case(
        "no-numeric-03", "NO_ARBITRARY_NUMERIC_MAPPING", "Rendilo più minimal.",
        no_numeric_field_changed(),
        one_stmt("ring", "SIMPLICITY", "minimal", "più minimal"),
    ),
    Case(
        "no-numeric-04", "NO_ARBITRARY_NUMERIC_MAPPING", "Voglio una fascia sottile.",
        no_numeric_field_changed(),
        one_stmt("band", "PROPORTIONAL_CHARACTER", "slim", "sottile"),
    ),
    Case(
        "no-numeric-05", "NO_ARBITRARY_NUMERIC_MAPPING", "A bigger, bolder stone feel.",
        no_numeric_field_changed(),
        one_stmt("stone", "VISUAL_WEIGHT", "bold", "bigger, bolder"),
    ),
    Case(
        "no-numeric-06", "NO_ARBITRARY_NUMERIC_MAPPING", "Very substantial and important-looking.",
        no_numeric_field_changed(),
        one_stmt("ring", "VISUAL_WEIGHT", "substantial", "very substantial"),
    ),
    Case(
        "no-numeric-07", "NO_ARBITRARY_NUMERIC_MAPPING", "Fai la fascia più stretta.",
        no_numeric_field_changed(),
        unresolved("più stretta"),
    ),
    Case(
        "no-numeric-08", "NO_ARBITRARY_NUMERIC_MAPPING", "Make the prongs thinner.",
        no_numeric_field_changed(),
        unresolved("thinner"),
    ),
    Case(
        "no-numeric-09", "NO_ARBITRARY_NUMERIC_MAPPING", "Un anello importante ma delicato.",
        no_numeric_field_changed(),
        Raw(
            unresolvedDescriptors=["importante"],
            designIntentStatements=[stmt("ring", "VISUAL_WEIGHT", "delicato")],
        ),
    ),
    Case(
        "no-numeric-10", "NO_ARBITRARY_NUMERIC_MAPPING", "Statement stone, understated band.",
        no_numeric_field_changed(),
        Raw(designIntentStatements=[
            stmt("stone", "VISUAL_EMPHASIS", "statement", "statement stone"),
            stmt("band", "VISUAL_EMPHASIS", "understated", "understated band"),
        ]),
    ),

    # --- multilingual convergence ---
    Case(
        "multi-01", "MULTILINGUAL", "Vorrei un anello delicato.",
        has_statement("RING", "VISUAL_WEIGHT", "DELICATE"),
        one_stmt("ring", "VISUAL_WEIGHT", "delicato"),
    ),
    Case(
        "multi-02", "MULTILINGUAL", "I would like a delicate ring.",
        has_statement("RING", "VISUAL_WEIGHT", "DELICATE"),
        one_stmt("ring", "VISUAL_WEIGHT", "delicate"),
    ),
    Case(
        "multi-03", "MULTILINGUAL", "Lo voglio classico.",
        has_statement("RING", "STYLE_TEMPORALITY", "CLASSIC"),
        one_stmt("ring", "STYLE_TEMPORALITY", "classico"),
    ),
    Case(
        "multi-04", "MULTILINGUAL", "I want it classic.",
        has_statement("RING", "STYLE_TEMPORALITY", "CLASSIC"),
        one_stmt("ring", "STYLE_TEMPORALITY", "classic"),
    ),
    Case(
        "multi-05", "MULTILINGUAL", "Molto minimal.",
        has_statement("RING", "SIMPLICITY", "MINIMAL"),
        one_stmt("ring", "SIMPLICITY", "minimal", "molto minimal"),
    ),
    Case(
        "multi-06", "MULTILINGUAL", "Very minimal.",
        has_statement("RING", "SIMPLICITY", "MINIMAL"),
        one_stmt("ring", "SIMPLICITY", "minimal", "very minimal"),
    ),
    Case(
        "multi-07", "MULTILINGUAL", "Fascia larga.",
        has_statement("BAND", "PROPORTIONAL_CHARACTER", "BROAD"),
        one_stmt("band", "PROPORTIONAL_CHARACTER", "larga"),
    ),
    Case(
        "multi-08", "MULTILINGUAL", "Broad band.",
        has_statement("BAND", "PROPORTIONAL_CHARACTER", "BROAD"),
        one_stmt("band", "PROPORTIONAL_CHARACTER", "broad"),
    ),

    # --- conflicts ---
    Case(
        "conflict-01", "CONFLICT", "minimal and highly ornate",
        has_conflict_count(1),
        Raw(designIntentStatements=[
            stmt("ring", "SIMPLICITY", "minimal"),
            stmt("ring", "SIMPLICITY", "ornate", "highly ornate"),
        ]),
    ),
    Case(
        "conflict-02", "CONFLICT", "delicate but very substantial",
        has_conflict_count(1),
        Raw(designIntentStatements=[
            stmt("ring", "VISUAL_WEIGHT", "delicate"),
            stmt("ring", "VISUAL_WEIGHT", "substantial", "very substantial"),
        ]),
    ),
    Case(
        "conflict-03", "CONFLICT", "understated but also a real statement piece",
        has_conflict_count(1),
        Raw(designIntentStatements=[
            stmt("ring", "VISUAL_EMPHASIS", "understated"),
            stmt("ring", "VISUAL_EMPHASIS", "statement", "a real statement piece"),
        ]),
    ),
]


def test_corpus_has_at_least_60_cases():
    assert len(CASES) >= 60


@pytest.mark.parametrize("case", CASES, ids=[c.id for c in CASES])
def test_corpus_case(case: Case):
    service = DesignerService(provider=FakeDesignerProvider(response=case.raw))
    request = NaturalLanguageDesignRequest(requestId=case.id, text=case.text, interactionMode="CREATE")
    result = service.interpret(request)
    case.check(result.proposal.designIntent, result.proposal)
