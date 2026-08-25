---
id: JM-BIBLE-298
title: Defaulting Policy
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-297
related_documents:
  - JM-BIBLE-299
implementation_status: current
professional_validation: not_required
normative: true
---

# Defaulting Policy

## The rule

Designer may only ever apply a default JewelMind itself already defines. It may never invent a new one. There is no code anywhere in `backend/jewelmind/designer/` that maps a descriptive word to a numeric or enum value that isn't already a value the schema or an existing design already holds.

## The two real sources of a "default"

1. **CREATE**: `JewelryDefinition()`'s own Pydantic field defaults, exactly as they exist for every other entry point (manual editing, the API's other routes). `service.py::interpret()`: `base = JewelryDefinition() if request.interactionMode == "CREATE" else ...`.
2. **MODIFY**: whatever value is already present on `request.currentJDL` for any field the request doesn't touch. Nothing is defaulted in the Designer-specific sense here — an unspecified field simply keeps its current value, because `_apply_patch()` only overwrites paths present in the accepted patch dict.

## What this explicitly forbids

- Designer never maps "delicate" to a specific `band.thickness` value. No such mapping exists in `normalizer.py`, `capability.py`, or anywhere else — this is a direct instruction from CLAUDE.md ("Never invent a jewelry measurement... no default, tolerance, density, shrinkage value, or proportion may be added to code or docs without a traceable source") and this Sprint's own governance (DESIGNER-GOV-006).
- Designer never substitutes a "reasonable-sounding" enum value for an ambiguous or unsupported one. See [`299-ambiguity-model.md`](299-ambiguity-model.md) and [`301-unsupported-request-handling.md`](301-unsupported-request-handling.md).
- The synonym tables in `normalizer.py` only ever map a spoken word to a value that **already exists** in the schema (`"oro giallo"` → `"yellow_gold_18k"`, a real enum member) — never to a value invented for the occasion. The module's own docstring states this directly: "Only mappings for values that actually exist in the current schema are implemented here."

## `DEFAULTED` confidence exists, but is narrow

`ConfidenceCategory` includes a `DEFAULTED` value (see [`302-confidence-model.md`](302-confidence-model.md)), but nothing in `service.py::_build_proposal()` currently assigns it — every `ProposedField` the pipeline constructs today gets `EXACT`, `NORMALIZED`, or `INFERRED`. `DEFAULTED` is reserved in the enum for a future case (e.g. a field JewelMind decides to auto-populate from a *derived* value, distinct from a schema default) but is not exercised by any current code path. This is worth naming explicitly rather than assuming the enum's presence implies the behavior exists.

## Why this matters for trust

A user reading "System default" (`SYSTEM_DEFAULT` provenance) or seeing an unspecified field silently keep its prior value must be able to trust that JewelMind, not the AI, chose that number — because it's the same default every manual "new design" gets, traceable to `domain/schema.py`, never to a provider's guess.

See [`299-ambiguity-model.md`](299-ambiguity-model.md) for what happens when a value is named but not resolvable to one supported member.
