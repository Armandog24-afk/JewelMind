---
id: JM-BIBLE-107
title: Export Precondition Rules
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-093
related_documents:
  - JM-BIBLE-079
implementation_status: current
professional_validation: not_required
normative: true
---

# Export Precondition Rules

## Current behavior

| Precondition | Enforced where | Backend or frontend only? |
|---|---|---|
| No validation errors | `has_errors()` gated at generation time (`ModelService.generate()`); export itself does not re-run `validate_definition()` — it only requires a previously-generated `ModelRecord` | Backend, but only indirectly (checked once, at generation, not again at export time) |
| Valid generated model exists | `ModelService.get_record(modelId)` raises `ModelNotFoundError` (404) if absent | Backend |
| Current model must not be stale | **Frontend-only.** `useProjectStore.ts`'s `isStale` flag (true whenever `generatedModel !== null` and the definition has since changed) disables the export action client-side. **The backend has no staleness concept at all** — if a stale `modelId` from an older definition is still cached, the backend will happily export it; nothing server-side re-checks that the exported model matches the currently-edited definition | **Frontend only — a real, current gap, not enforced end-to-end** |
| Required geometry present | Implicit — `export_step`/`export_stl` operate on `record.generated_model`, which by construction always has all four components (LAW-005's fallback guarantees a usable `combined_metal` even under fuse failure) | Backend |
| Valid export parameters | `api/schemas.py::ExportStlRequest`/`ExportStepRequest` (e.g. `angularTolerance: float | None = Field(default=None, gt=0, allow_inf_nan=False)`) | Backend |
| Valid filenames | `exporters/filenames.py::sanitize_filename()` | Backend |

## `FORGE-EXPORT-001`, precisely

This registry entry bundles the two backend-enforced preconditions above (`ModelNotFoundError` + the transitive effect of `ValidationBlockedError` having prevented generation in the first place) under one rule ID for cataloging purposes — it is not a single literal function in the codebase, but an accurate composite of `model_service.get_record()`'s existence check plus the fact that a `ModelRecord` can only ever exist for a definition that passed `has_errors() == False` at generation time.

## Conceptual future checks (not implemented)

- **Export capability supported** — a declared-capability check (see [`05-jdl/082-extension-and-capability-model.md`](../05-jdl/082-extension-and-capability-model.md)) confirming the requested format is currently supported before attempting generation; today the only "check" is that the API route exists at all.
- **Geometry inspection completed** — a future explicit gate requiring FORGE-7 (see [`106-generated-geometry-inspection-rules.md`](106-generated-geometry-inspection-rules.md)) to have run and passed before export, rather than export only depending on FORGE-6 having produced *some* `GeneratedModel`.
- **Artifact-specific rules satisfied** — e.g. a STEP-specific precision check distinct from a generic STL mesh-quality check, made possible once blocking scope is genuinely per-artifact (see [`099-severity-and-blocking-semantics.md`](099-severity-and-blocking-semantics.md)).

## The staleness gap, stated plainly

This is the most concrete, actionable finding in this document: **a user could, in principle, export STEP/STL/JSON for a stale cached model even though the frontend UI would normally prevent it**, by calling the export endpoints directly (bypassing the UI) with a `modelId` from before their latest edits. This is not a security vulnerability (no unauthorized data is exposed — the user already owns their own definition), but it is a real end-to-end gap between the documented and the actual precondition, recorded here rather than silently assumed away, and flagged again in [`111-domain-rule-gap-analysis.md`](111-domain-rule-gap-analysis.md).
