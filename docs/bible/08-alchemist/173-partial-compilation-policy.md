---
id: JM-BIBLE-173
title: Partial Compilation Policy
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-172
related_documents: []
implementation_status: partial
professional_validation: not_required
normative: true
---

# Partial Compilation Policy

## Acceptable partial success

| Scenario | Acceptable? | Current behavior |
|---|---|---|
| STEP succeeds, preview fails | Yes | **Cannot currently occur as stated** — preview happens first, inline, inside `generate()`; if it failed, STEP export would never even be reachable (no `ModelRecord` would exist to export from) |
| JSON succeeds, STL fails | Yes | Correctly independent today — JSON export (`export_json_text()`) reads only `record.definition`, never touches geometry/tessellation at all |
| Geometry succeeds, optional specification fails | Yes | Correctly independent today — specification export only fails if `build_specification()` itself raises, unrelated to geometry validity |

## Not acceptable for a complete solitaire

Missing band; missing required prongs; missing required basket support when the current plan requires it; missing production geometry. **All four are structurally impossible to reach as a "silent" partial state today** — `build_solitaire_ring()` either returns a `GeneratedModel` with all four components present (LAW-005, ATLAS-GOV-006), or an exception propagates and generation fails outright. There is no code path that could return a `GeneratedModel` missing one of the four required components.

## Artifact independence, and where it currently breaks down

STEP, STL, JSON, and specification exports are each independently requestable once a model is generated, and a failure in one never affects the others — this is correct, current, and tested (`test_api.py::test_export_with_unknown_model_id_returns_404` and the export-success tests). **Preview generation is the one exception**: it is not independently requestable — it happens automatically, inline, as part of `generate()` itself, coupled to core geometry construction. This means the "acceptable partial success" table's first row (STEP succeeds, preview fails) describes a target architecture, not current behavior.

## Never silently report COMPLETED when required outputs fail

Confirmed true today: `ModelService.generate()` has no code path that catches a preview-generation exception and proceeds anyway — if it fails, the whole call fails, which is at least honest (no silent COMPLETED-with-a-hidden-failure state exists), even though it is the wrong failure boundary (see [`172-diagnostics-and-failure-propagation.md`](172-diagnostics-and-failure-propagation.md)).

## What "artifact independence" would require to reach the target state

Decoupling preview generation from `generate()` into its own later, independently-callable step (mirroring how STEP/STL/JSON/specification already work) — a real, identifiable, non-trivial future change, not performed in this Sprint.
