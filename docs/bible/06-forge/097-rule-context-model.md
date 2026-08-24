---
id: JM-BIBLE-097
title: Rule Context Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-096
related_documents: []
implementation_status: partial
professional_validation: not_required
normative: true
---

# Rule Context Model

The normative `ForgeEvaluationContext` shape is `specs/forge/v1/rule-context.schema.json`.

## Fields

`document` (the JDL Canonical Document), `jewelryCategory`, `style`, `materialContext`, `manufacturingContext`, `requestedArtifacts`, `compilerVersion`, `geometryGeneratorVersion`, `generatedGeometryMetadata`, `componentManifest`, `featureCapabilities`, `professionalRuleProfile`.

## What the current implementation actually passes

`backend/jewelmind/validation/engine.py::validate_definition(definition)` receives **only** the `document` field — a bare `JewelryDefinition`. Every other field in the conceptual context above is either:

- **Derivable at the API layer without being threaded into the rule engine** (`compilerVersion`, `geometryGeneratorVersion` — the API response adds these separately, from `GENERATOR_VERSION`/`SCHEMA_VERSION` constants, after validation and generation, not as rule inputs); or
- **Genuinely unpopulated today** (`generatedGeometryMetadata`, `componentManifest` — null before FORGE-6 has run, and no current rule reads them back even after generation, since `FORGE-GEOM-001` is implemented as inline logic inside `_fuse_metal`, not as a rule that receives a context object); or
- **Entirely PLANNED** (`featureCapabilities`, `professionalRuleProfile` — no such concepts exist in the current codebase at all).

## No secrets, no executable content

Every field in `rule-context.schema.json` is either the document itself, a plain scalar, or a plain object — there is no field capable of carrying credentials, and no field capable of carrying code. This mirrors the same design discipline already established for JDL documents in [`05-jdl/062-design-goals-and-non-goals.md`](../05-jdl/062-design-goals-and-non-goals.md).

## Why a context object is worth specifying even though nothing consumes most of it yet

Two reasons: first, it gives `applicableJewelryCategories`/`applicableStyles`/`applicableManufacturingMethods` (see [`092-rule-anatomy.md`](092-rule-anatomy.md)) something concrete to filter against once rule selection becomes context-aware, rather than the current unconditional "run every rule" behavior; second, it gives `professionalRuleProfile` a defined slot to exist in once a first professionally-validated rule set is ever created, rather than requiring an architecture change to add it later.
