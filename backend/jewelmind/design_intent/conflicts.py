"""Conflict detection over a set of intent statements/relations.

Not every tension is invalid — see
docs/bible/13-design-intent/346-intent-conflict-model.md: a conflict is
recorded and surfaced, never silently rejected, and never blocks a
proposal from being returned. `EXPLICIT_CONTRADICTION`/`SOFT_TENSION` are
detected from real distance on the same concept's ordered continuum
(vocabulary.py); `TARGET_CONFLICT` is detected from two relations that
assert opposite orderings between the same subject/object pair.
`PRIORITY_CONFLICT` and `RESOLUTION_CONFLICT` are reserved for richer
future detection — see 362-design-intent-gap-analysis.md.
"""

from __future__ import annotations

import itertools

from jewelmind.design_intent.schemas import IntentConflict, IntentRelation, IntentStatement
from jewelmind.design_intent.vocabulary import concept_values, continuum_distance

_OPPOSITE_PREDICATE: dict[str, str] = {
    "DOMINANT_OVER": "SUBORDINATE_TO",
    "SUBORDINATE_TO": "DOMINANT_OVER",
    "NARROWER_THAN": "BROADER_THAN",
    "BROADER_THAN": "NARROWER_THAN",
}


def detect_conflicts(
    statements: list[IntentStatement], relations: list[IntentRelation]
) -> list[IntentConflict]:
    conflicts: list[IntentConflict] = []
    conflicts.extend(_value_conflicts(statements))
    conflicts.extend(_relation_conflicts(relations))
    return conflicts


def _value_conflicts(statements: list[IntentStatement]) -> list[IntentConflict]:
    conflicts: list[IntentConflict] = []
    groups: dict[tuple[str, str], list[IntentStatement]] = {}
    for stmt in statements:
        groups.setdefault((stmt.target, stmt.concept), []).append(stmt)

    for (target, concept), group in groups.items():
        order = concept_values(concept)
        if len(order) < 2:
            continue
        max_distance = len(order) - 1
        for a, b in itertools.combinations(group, 2):
            distance = continuum_distance(concept, a.value, b.value)
            if distance is None or distance <= 1:
                continue
            both_required = a.strength == "REQUIRED" and b.strength == "REQUIRED"
            if distance >= max_distance:
                conflict_type = "PRIORITY_CONFLICT" if both_required else "EXPLICIT_CONTRADICTION"
            else:
                conflict_type = "SOFT_TENSION"
            conflicts.append(
                IntentConflict(
                    conflictId=f"conflict-{a.intentId}-{b.intentId}",
                    type=conflict_type,
                    statementIds=[a.intentId, b.intentId],
                    description=(
                        f"{target}.{concept}: '{a.value}' ({a.sourceText!r}) vs "
                        f"'{b.value}' ({b.sourceText!r})"
                    ),
                )
            )
    return conflicts


def _relation_conflicts(relations: list[IntentRelation]) -> list[IntentConflict]:
    conflicts: list[IntentConflict] = []
    by_pair: dict[tuple[str, str], list[IntentRelation]] = {}
    for rel in relations:
        by_pair.setdefault((rel.subject, rel.object), []).append(rel)

    for (subject, obj), group in by_pair.items():
        for a, b in itertools.combinations(group, 2):
            if _OPPOSITE_PREDICATE.get(a.predicate) == b.predicate:
                conflicts.append(
                    IntentConflict(
                        conflictId=f"conflict-{a.relationId}-{b.relationId}",
                        type="TARGET_CONFLICT",
                        statementIds=[a.relationId, b.relationId],
                        description=(
                            f"{subject} both {a.predicate} and {b.predicate} {obj}"
                        ),
                    )
                )
    return conflicts


def conflicting_ids(conflicts: list[IntentConflict]) -> frozenset[str]:
    ids: set[str] = set()
    for c in conflicts:
        ids.update(c.statementIds)
    return frozenset(ids)
