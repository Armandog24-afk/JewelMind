---
id: JM-BIBLE-349
title: Deterministic Resolution Policy
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-348
related_documents:
  - JM-BIBLE-350
implementation_status: current
professional_validation: not_required
normative: true
---

# Deterministic Resolution Policy

## The central policy of Sprint 11

This is the most important document in the Design Intent Sprint, because it is the one that explains why the Sprint's headline finding — zero automatic subjective-to-numeric mappings — is a *policy outcome*, not a missing feature.

## The seven conditions a mapping must satisfy before it may run automatically

An intent-to-JDL mapping may be registered and allowed to run without a human confirming each individual application only if all of the following hold:

1. **Explicit** — the mapping states exactly which `(target, concept, value)` triple produces exactly which JDL field path and value; no fuzzy or inferred correspondence.
2. **Deterministic** — the same intent statement always produces the same JDL change, with no randomness, model call, or external state (restates CLAUDE.md's CAD-determinism rule at the intent layer).
3. **Versioned** — the mapping carries its own version, so a later change to it is a new version, never a silent edit (INTENT-GOV-012).
4. **Clear provenance** — the mapping's origin (who defined it, on what basis) is recorded and traceable, mirroring `docs/bible/04-jewelry-domain/040-domain-governance.md`'s "no invented measurement without a source" rule.
5. **Produces valid JDL** — the resulting `JewelryDefinition` must pass structural/schema validation like any other JDL, with no special-cased bypass.
6. **Still evaluated by Forge** — a JDL value that originated from an intent mapping is evaluated by `validation/engine.py` exactly like a value the user typed by hand; Forge has no separate, weaker gate for intent-derived values (see [`351-intent-to-forge-boundary.md`](351-intent-to-forge-boundary.md)).
7. **Honors the user-review policy** — the resulting change is still shown to the user for review before being applied to `currentDefinition`, exactly like every other Designer proposal field (see `../12-designer/310-user-review-and-acceptance.md`).

## The v1 answer: zero mappings, and that is correct

`backend/jewelmind/design_intent/resolver.py` registers no deterministic mapping table at all — there is no data structure anywhere in `design_intent/` that maps an `(target, concept, value)` triple to a JDL field path. Every recognized statement resolves to `resolutionStatus: "PRESERVED"` unconditionally (see [`348-intent-resolution-model.md`](348-intent-resolution-model.md)).

This Sprint's own brief states the reasoning directly, and this document adopts it as policy: current v1 should have very few or zero subjective-to-numeric automatic mappings, and that is acceptable — mappings must never be invented merely to make the feature look more capable than it safely is. A mapping that does not yet satisfy all seven conditions above is worse than no mapping: it would quietly turn "delicate" into a specific millimeter value nobody explicitly approved, which is precisely the failure mode INTENT-GOV-001 exists to prevent.

## What would change this

The first mapping that satisfies all seven conditions would be expressed as a real `IntentProfile` (see [`355-intent-profile-model.md`](355-intent-profile-model.md)) with a non-empty `jdlMapping`. Registering it is explicitly called out in [`330-intent-governance.md`](330-intent-governance.md) as one of the two conditions requiring an ADR before it can ship — it is an architectural decision, not a routine content addition, because it is the first time Design Intent would gain any ability, however narrow, to influence JDL automatically.

## Relationship to Sprint 10's own honesty pattern

This mirrors how Sprint 10 handled `../12-designer/` scope: several `DESIGNER_*` diagnostic codes and vocabulary entries exist in schema before the corresponding behavior is built, and the documentation says so plainly rather than describing planned behavior as current. This policy document is the Design Intent equivalent of that same discipline, applied to the single highest-risk capability in the whole Sprint: turning subjective language into numbers.

## Cross-references

- [`330-intent-governance.md`](330-intent-governance.md) — INTENT-GOV-001, INTENT-GOV-010, INTENT-GOV-018.
- [`348-intent-resolution-model.md`](348-intent-resolution-model.md) — the resolution statuses this policy gates.
- [`355-intent-profile-model.md`](355-intent-profile-model.md) — the shape a future mapping would take.
- `../04-jewelry-domain/040-domain-governance.md` — the parallel "no invented measurement" rule for jewelry constants generally.
