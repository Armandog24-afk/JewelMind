"""Forge rule scope classification (brief section 31) — additive only,
never a Forge rewrite. Every real rule ID already carries a domain
prefix (`JM-RING-*`, `JM-BAND-*`, ...); this module classifies those
prefixes into the shared-vs-category-specific boundary Ring Architecture
formalizes, so a future non-ring category is never evaluated against a
ring-only rule. See
docs/bible/18-ring-architecture/521-shared-vs-category-specific-domain.md.

This is a pure, derived classification — it does not modify
`ValidationResult`, `validation/engine.py`, or any existing rule ID.
"""

from __future__ import annotations

from typing import Literal

RuleScope = Literal[
    "ring_sizing",
    "ring_shank",
    "ring_head",
    "shared_stone",
    "shared_setting",
    "shared_manufacturing",
    "engineering",
    "unknown",
]

# Keyed by the rule ID's domain prefix (everything before the trailing
# "-NNN"). Real prefixes only — one entry per prefix actually emitted by
# validation/engine.py, verified against validation/rules.py.
_SCOPE_BY_PREFIX: dict[str, RuleScope] = {
    "JM-RING": "ring_sizing",
    "JM-BAND": "ring_shank",
    "JM-SETTING": "ring_head",
    "JM-STONE": "shared_stone",
    "JM-PRONG": "shared_setting",
    "JM-MANUFACTURING": "shared_manufacturing",
    "JM-GEOMETRY": "engineering",
}


def rule_scope(rule_id: str) -> RuleScope:
    prefix = rule_id.rsplit("-", 1)[0]
    return _SCOPE_BY_PREFIX.get(prefix, "unknown")


def is_ring_specific(rule_id: str) -> bool:
    return rule_scope(rule_id) in ("ring_sizing", "ring_shank", "ring_head")


def is_shared_scope(rule_id: str) -> bool:
    return rule_scope(rule_id) in ("shared_stone", "shared_setting", "shared_manufacturing", "engineering")
