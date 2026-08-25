"""Orchestrates raw statements/relations into a `DesignIntent`.

Deterministic Resolution Policy (see
docs/bible/13-design-intent/349-deterministic-resolution-policy.md):
every recognized statement resolves to `PRESERVED`, never to a numeric
JDL change — v1 registers zero automatic subjective-to-numeric mappings,
which is the deliberately correct, safe state (INTENT-GOV-001/010).
`build_design_intent()` also implements MODIFY-mode merge semantics,
directly analogous to how a JDL MODIFY preserves every unspecified field
(see docs/bible/13-design-intent/353-intent-preservation.md).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from jewelmind.design_intent import diagnostics as D
from jewelmind.design_intent.conflicts import conflicting_ids, detect_conflicts
from jewelmind.design_intent.normalizer import (
    KNOWN_CONCEPTS,
    normalize_descriptor,
    normalize_predicate,
    normalize_target,
)
from jewelmind.design_intent.schemas import (
    DesignIntent,
    IntentDiagnostic,
    IntentDiffEntry,
    IntentRelation,
    IntentStatement,
    IntentStrength,
)

_STRENGTH_VALUES: frozenset[str] = frozenset({"OPTIONAL", "PREFERRED", "IMPORTANT", "REQUIRED"})


def _normalize_strength(raw: str | None) -> IntentStrength:
    if raw is None:
        return "PREFERRED"
    token = raw.strip().upper()
    return token if token in _STRENGTH_VALUES else "PREFERRED"  # type: ignore[return-value]


@dataclass
class RawStatementInput:
    target: str
    concept: str
    value: str
    strength: str | None = None
    sourceText: str = ""


@dataclass
class RawRelationInput:
    subject: str
    predicate: str
    object: str
    strength: str | None = None
    sourceText: str = ""


@dataclass
class BuildResult:
    statements: list[IntentStatement] = field(default_factory=list)
    relations: list[IntentRelation] = field(default_factory=list)
    unresolved: list[str] = field(default_factory=list)
    diagnostics: list[IntentDiagnostic] = field(default_factory=list)


def _resolve_statements(raw_statements: list[RawStatementInput]) -> BuildResult:
    result = BuildResult()
    for raw in raw_statements:
        target = normalize_target(raw.target)
        concept = raw.concept.strip().upper() if raw.concept else None
        if target is None or concept not in KNOWN_CONCEPTS:
            result.unresolved.append(raw.sourceText or raw.value)
            result.diagnostics.append(
                IntentDiagnostic(
                    code=D.INTENT_UNKNOWN_DESCRIPTOR,
                    severity="info",
                    message=f"Could not place {raw.sourceText or raw.value!r} in the known vocabulary.",
                )
            )
            continue

        value, is_exact = normalize_descriptor(concept, raw.value)
        if value is None:
            result.unresolved.append(raw.sourceText or raw.value)
            result.diagnostics.append(
                IntentDiagnostic(
                    code=D.INTENT_UNKNOWN_DESCRIPTOR,
                    severity="info",
                    message=f"'{raw.value}' is not a recognized {concept} descriptor.",
                )
            )
            continue

        statement = IntentStatement(
            intentId=f"intent-{uuid.uuid4()}",
            target=target,  # type: ignore[arg-type]
            concept=concept,  # type: ignore[arg-type]
            value=value,
            strength=_normalize_strength(raw.strength),
            provenance="AI_NORMALIZED",
            confidenceClass="EXACT" if is_exact else "HIGH_CONFIDENCE_NORMALIZATION",
            sourceText=raw.sourceText or raw.value,
            resolutionStatus="PRESERVED",
        )
        result.statements.append(statement)
    return result


def _resolve_relations(raw_relations: list[RawRelationInput]) -> BuildResult:
    result = BuildResult()
    for raw in raw_relations:
        subject = normalize_target(raw.subject)
        obj = normalize_target(raw.object)
        predicate = normalize_predicate(raw.predicate)
        if subject is None or obj is None or predicate is None:
            result.unresolved.append(raw.sourceText or f"{raw.subject} {raw.predicate} {raw.object}")
            result.diagnostics.append(
                IntentDiagnostic(
                    code=D.INTENT_INVALID_RELATION,
                    severity="info",
                    message=f"Could not resolve relation {raw.subject!r} {raw.predicate!r} {raw.object!r}.",
                )
            )
            continue
        result.relations.append(
            IntentRelation(
                relationId=f"relation-{uuid.uuid4()}",
                subject=subject,  # type: ignore[arg-type]
                predicate=predicate,  # type: ignore[arg-type]
                object=obj,  # type: ignore[arg-type]
                strength=_normalize_strength(raw.strength),
                provenance="AI_NORMALIZED",
                resolutionStatus="PRESERVED",
                sourceText=raw.sourceText,
            )
        )
    return result


def build_design_intent(
    source_text: str,
    mode: str,
    previous: DesignIntent | None,
    raw_statements: list[RawStatementInput],
    raw_relations: list[RawRelationInput],
    raw_unresolved_descriptors: list[str] | None = None,
) -> DesignIntent:
    statement_result = _resolve_statements(raw_statements)
    relation_result = _resolve_relations(raw_relations)

    statements = statement_result.statements
    relations = relation_result.relations
    unresolved = list(statement_result.unresolved) + list(relation_result.unresolved)
    unresolved.extend(raw_unresolved_descriptors or [])
    diagnostics = list(statement_result.diagnostics) + list(relation_result.diagnostics)

    if mode == "MODIFY" and previous is not None:
        merged_statements: dict[tuple[str, str], IntentStatement] = {
            (s.target, s.concept): s for s in previous.statements
        }
        for s in statements:
            merged_statements[(s.target, s.concept)] = s
        statements = list(merged_statements.values())

        merged_relations: dict[tuple[str, str], IntentRelation] = {
            (r.subject, r.object): r for r in previous.relationships
        }
        for r in relations:
            merged_relations[(r.subject, r.object)] = r
        relations = list(merged_relations.values())

        seen = set(previous.unresolvedDescriptors)
        unresolved = list(previous.unresolvedDescriptors) + [u for u in unresolved if u not in seen]

    conflicts = detect_conflicts(statements, relations)
    conflicted = conflicting_ids(conflicts)
    if conflicted:
        statements = [
            s.model_copy(update={"resolutionStatus": "CONFLICTING"}) if s.intentId in conflicted else s
            for s in statements
        ]
        relations = [
            r.model_copy(update={"resolutionStatus": "CONFLICTING"}) if r.relationId in conflicted else r
            for r in relations
        ]
        for c in conflicts:
            diagnostics.append(
                IntentDiagnostic(code=D.INTENT_CONFLICT, severity="warning", message=c.description)
            )

    for text in unresolved:
        diagnostics.append(
            IntentDiagnostic(
                code=D.INTENT_PRESERVED_UNRESOLVED,
                severity="info",
                message=f"{text!r} has been preserved as design intent, not converted into a dimension.",
            )
        )

    return DesignIntent(
        sourceText=source_text,
        statements=statements,
        relationships=relations,
        unresolvedDescriptors=unresolved,
        conflicts=conflicts,
        profile=None,
        diagnostics=diagnostics,
    )


def compute_intent_diff(previous: DesignIntent | None, after: DesignIntent) -> list[IntentDiffEntry]:
    """Deterministic before/after comparison — never LLM-generated.

    See docs/bible/13-design-intent/354-intent-diff-model.md.
    """

    before_by_key = (
        {f"{s.target}.{s.concept}": s.value for s in previous.statements} if previous is not None else {}
    )
    after_by_key = {f"{s.target}.{s.concept}": s.value for s in after.statements}

    entries: list[IntentDiffEntry] = []
    for key in sorted(set(before_by_key) | set(after_by_key)):
        before_value = before_by_key.get(key)
        after_value = after_by_key.get(key)
        if before_value is None and after_value is not None:
            change_type = "ADDED"
        elif before_value is not None and after_value is None:
            change_type = "REMOVED"
        elif before_value != after_value:
            change_type = "CHANGED"
        else:
            change_type = "UNCHANGED"
        entries.append(
            IntentDiffEntry(key=key, previousValue=before_value, newValue=after_value, changeType=change_type)
        )
    return entries
