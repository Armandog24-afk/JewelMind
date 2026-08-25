---
id: JM-BIBLE-358
title: Intent Diagnostics
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-357
related_documents:
  - JM-BIBLE-359
implementation_status: current
professional_validation: not_required
normative: true
---

# Intent Diagnostics

## The 9 codes

`design_intent/diagnostics.py` defines 9 verbatim `INTENT_*` constants, mirrored in `IntentDiagnosticCode` (`schemas.py`) and enumerated in `ALL_INTENT_DIAGNOSTIC_CODES`: `INTENT_UNKNOWN_DESCRIPTOR`, `INTENT_AMBIGUOUS_DESCRIPTOR`, `INTENT_CONFLICT`, `INTENT_UNSUPPORTED_TARGET`, `INTENT_NO_DETERMINISTIC_RESOLUTION`, `INTENT_PROFILE_UNAVAILABLE`, `INTENT_RESOLUTION_REQUIRES_CONFIRMATION`, `INTENT_INVALID_RELATION`, `INTENT_PRESERVED_UNRESOLVED`. The exhaustive per-code table — trigger, severity, real vs. reserved — lives in [`../appendices/intent-diagnostic-catalog.md`](../appendices/intent-diagnostic-catalog.md); this document explains the pattern behind it.

## Why none of the 9 ever fail an HTTP request

Unlike several of Designer's own `DESIGNER_*` codes (`../12-designer/` — some of which are real HTTP-level failure codes, e.g. `DESIGNER_PROVIDER_UNAVAILABLE`'s 503), every `INTENT_*` code is purely an in-band diagnostic attached to `DesignIntent.diagnostics`. An unresolved statement, an unrecognized relation, or a detected conflict is a normal, expected outcome of interpreting natural aesthetic language — never a backend failure. The request that produced them always returns a normal `DesignerProposal`; the diagnostics simply describe what happened inside it. This is the direct consequence of [`352-unresolved-intent-lifecycle.md`](352-unresolved-intent-lifecycle.md): unresolved intent is data, not an error.

## Which codes are real today (verified directly in `resolver.py`)

Grepping `resolver.py` for `diagnostics.append` and `D.` usage shows exactly four codes are ever constructed by real code:

- **`INTENT_UNKNOWN_DESCRIPTOR`** — emitted twice in `_resolve_statements()`: once when the target/concept cannot be normalized at all, once when the concept is recognized but the value cannot be. Severity `info`.
- **`INTENT_INVALID_RELATION`** — emitted in `_resolve_relations()` when subject, object, or predicate cannot be normalized. Severity `info`.
- **`INTENT_CONFLICT`** — emitted once per detected `IntentConflict` in `build_design_intent()`, after `conflicts.py::detect_conflicts()` runs. Severity `warning`.
- **`INTENT_PRESERVED_UNRESOLVED`** — emitted once per entry in the final `unresolvedDescriptors` list, regardless of which of the above two "unresolved" paths produced it. Severity `info`.

## Which codes are schema-reserved, not yet produced

- `INTENT_AMBIGUOUS_DESCRIPTOR` — would require an ambiguity-detection stage (a descriptor with more than one plausible normalization) that does not exist; `normalize_descriptor()` today returns either exactly one value or `None`, never an ambiguous set.
- `INTENT_UNSUPPORTED_TARGET` — would require a recognized-but-declared-unsupported target/concept combination; today, recognized always means preserved.
- `INTENT_NO_DETERMINISTIC_RESOLUTION` — would require an attempted deterministic resolution to fail; no resolution is ever attempted (`349-deterministic-resolution-policy.md`).
- `INTENT_PROFILE_UNAVAILABLE` — would require a referenced profile to be missing; zero profiles are ever referenced (`355-intent-profile-model.md`).
- `INTENT_RESOLUTION_REQUIRES_CONFIRMATION` — would require a proposed numeric resolution awaiting user approval; none is ever proposed.

This is exactly the same pattern Designer v1 used in Sprint 10 for several of its own diagnostic codes: schema-complete ahead of the behavior that would produce them, documented honestly rather than silently implemented as always-triggering placeholders.

## Cross-references

- [`330-intent-governance.md`](330-intent-governance.md) — INTENT-GOV-006, INTENT-GOV-007.
- [`../appendices/intent-diagnostic-catalog.md`](../appendices/intent-diagnostic-catalog.md) — the full per-code table.
- [`352-unresolved-intent-lifecycle.md`](352-unresolved-intent-lifecycle.md) — the lifecycle these codes narrate.
- [`346-intent-conflict-model.md`](346-intent-conflict-model.md) — how `INTENT_CONFLICT` diagnostics relate to `conflicts.py`.
