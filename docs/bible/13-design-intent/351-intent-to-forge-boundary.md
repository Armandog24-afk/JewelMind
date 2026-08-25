---
id: JM-BIBLE-351
title: Intent To Forge Boundary
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-350
related_documents:
  - JM-BIBLE-352
implementation_status: current
professional_validation: not_required
normative: true
---

# Intent To Forge Boundary

## Forge does not, and never will, judge subjective beauty

Forge (`backend/jewelmind/validation/engine.py`) evaluates whether a `JewelryDefinition` is geometrically, dimensionally, and manufacturably sound. It has no concept of "delicate," "classic," or "bold," and this document states plainly that it must never acquire one. Forge may only ever evaluate whether a *technical resolution derived from* an intent profile — a hypothetical future state described in [`355-intent-profile-model.md`](355-intent-profile-model.md) — is itself geometrically valid once it exists as a concrete JDL value. Forge judges the millimeter, never the mood.

This is the Design Intent Sprint's restatement of the same Atlas/Forge separation documented for geometry in `../07-atlas/README.md` (ATLAS-GOV-001/002): a downstream authority may evaluate a fact, but must never be the layer that decides what the fact should mean aesthetically.

## Today: Forge has zero awareness that Design Intent exists

`validation/engine.py` contains no reference to `design_intent/`, `DesignIntent`, `IntentStatement`, or any `INTENT_*` code. `DesignerProposal.forgeEvaluation` — the Forge run attached to a Designer proposal — only ever evaluates `candidateJDL`, and `candidateJDL` never contains an intent-derived value, because no such value is ever produced (see [`350-intent-to-jdl-boundary.md`](350-intent-to-jdl-boundary.md)). Forge's verdict on a proposal is therefore identical whether or not the accompanying `DesignIntent` contains statements, conflicts, or unresolved descriptors — the two are evaluated in parallel by `_build_proposal()`, not in sequence, and neither result depends on the other.

## What Forge would evaluate, if resolution ever existed

If a future `IntentProfile` mapping ever produced a JDL value (per [`349-deterministic-resolution-policy.md`](349-deterministic-resolution-policy.md)'s seven conditions), that value would need to flow into `candidateJDL` and be evaluated by the exact same `validate_definition()` call every other field goes through — condition 6 of that policy makes this explicit. Forge would still have no opinion on whether "delicate" was correctly interpreted; it would only ever check whether the resulting band width, prong count, or stone dimension is itself valid per the existing 21-rule registry (`specs/forge/v1/current-rule-registry.json`).

## What Forge must never do

- Define what "minimal" or "classic" means as a rule.
- Reject or accept a `DesignIntent` statement directly — Forge has no input type for one.
- Treat `IntentStrength` (`OPTIONAL`/`PREFERRED`/`IMPORTANT`/`REQUIRED`) as if it were a manufacturing severity — the two vocabularies are unrelated (INTENT-GOV-008).
- Gate whether an unresolved or conflicting `DesignIntent` blocks proposal acceptance — see [`352-unresolved-intent-lifecycle.md`](352-unresolved-intent-lifecycle.md) for why unresolved intent is a normal outcome, not a validation failure.

## Cross-references

- [`330-intent-governance.md`](330-intent-governance.md) — INTENT-GOV-008, INTENT-GOV-011.
- [`350-intent-to-jdl-boundary.md`](350-intent-to-jdl-boundary.md) — the upstream boundary this document mirrors on the Forge side.
- `../07-atlas/README.md` — the equivalent Atlas/Forge fact-vs-rule separation for geometry.
- `../12-designer/308-designer-validation-pipeline.md` — how `forgeEvaluation` is produced for a Designer proposal today.
