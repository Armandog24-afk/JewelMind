---
id: JM-BIBLE-092
title: Rule Anatomy
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-091
related_documents:
  - JM-BIBLE-A14
implementation_status: partial
professional_validation: not_required
normative: true
---

# Rule Anatomy

The normative `ForgeRule` model is `specs/forge/v1/rule.schema.json`. This document explains each field and which are required.

## Fields

| Field | Required | Meaning |
|---|---|---|
| `ruleId` | Yes | Stable identifier, e.g. `JM-BAND-001` |
| `name` | Yes | Short human-readable name |
| `description` | Yes | Full explanation of what the rule checks |
| `version` | Yes | Rule semantic version — see [`108-rule-versioning.md`](108-rule-versioning.md) |
| `category` | Yes | One of 11 classifications — see [`093-rule-classification-model.md`](093-rule-classification-model.md) |
| `stage` | Yes | `FORGE-0`..`FORGE-9` — see [`096-rule-evaluation-pipeline.md`](096-rule-evaluation-pipeline.md) |
| `severity` | Yes | `INFORMATION` \| `WARNING` \| `ERROR` \| `FATAL` |
| `blockingScope` | Yes | Which workflows this rule can block — see [`099-severity-and-blocking-semantics.md`](099-severity-and-blocking-semantics.md) |
| `condition` | Yes | Human-readable description of the check, optionally naming the implementing function. **Never executable code.** |
| `targetFields` | Yes | Canonical JDL field paths read by this rule |
| `dependencies` | No | Other `ruleId`s this rule's evaluation depends on |
| `evaluationContext` | No | What context data (beyond the document) this rule needs |
| `resultCode` | No | Usually identical to `ruleId` |
| `messageTemplate` | No | The diagnostic message text |
| `suggestedCorrection` | No | Human-readable fix suggestion |
| `autoFixCapability` | No | `NONE` \| `SUGGEST_ONLY` \| `SAFE_NORMALIZATION` — see [`102-suggestions-and-auto-fix-contract.md`](102-suggestions-and-auto-fix-contract.md) |
| `provenance` | Yes | See [`094-rule-provenance-model.md`](094-rule-provenance-model.md) |
| `professionalValidationStatus` | Yes | `not_required` \| `preliminary` \| `required` \| `validated` |
| `applicableJewelryCategories` | No | e.g. `["ring"]`; omitted means all currently supported |
| `applicableStyles` | No | e.g. `["solitaire"]` |
| `applicableMaterials` | No | e.g. `["yellow_gold_18k"]`; empty today for every current rule — no rule is material-specific |
| `applicableManufacturingMethods` | No | e.g. `["direct_resin_printing"]` — used by `JM-MANUFACTURING-001` |
| `introducedIn` | Yes | The rule version this `ruleId` first appeared at |
| `deprecatedIn` | No | The rule version this `ruleId` was deprecated at, or absent/null if active |
| `lifecycleState` | No (recommended) | See [`095-rule-lifecycle.md`](095-rule-lifecycle.md) |
| `tests` | No (required in practice by FORGE-GOV-011) | Repository-relative test identifiers |
| `relatedDocuments` | No | Bible document IDs |

## Why `condition` is a string, not an executable expression

JewelMind never introduces a rule-condition DSL that can execute arbitrary code, per [`062-design-goals-and-non-goals.md`](../05-jdl/062-design-goals-and-non-goals.md)'s non-goal 1 (extended here to Forge). `condition` is documentation of the check for a human reader and for cross-referencing against the real implementing function — the actual check always lives in real, reviewed Python (`backend/jewelmind/validation/engine.py`) or TypeScript (`shared/validation/engine.ts`), never in data. If a structured, declarative condition representation is ever needed (e.g. for a future rule-authoring UI), it is a PLANNED condition DSL — see open question JDL-OQ-004-adjacent discussion in [`115-open-forge-questions.md`](115-open-forge-questions.md) — and would still not be permitted to execute arbitrary code.

## Worked examples

See `specs/forge/v1/examples/valid/jm-band-001.json` (a `PROTOTYPE_HEURISTIC` pre-generation rule) and `specs/forge/v1/examples/valid/forge-geom-001.json` (a `GEOMETRY_INSPECTION` post-generation rule) for two complete, schema-valid instances covering both halves of the pipeline described in [`091-rule-system-overview.md`](091-rule-system-overview.md).
