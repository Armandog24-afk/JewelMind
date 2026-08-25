---
id: JM-BIBLE-331
title: Design Intent Architecture
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-330
related_documents:
  - JM-BIBLE-332
implementation_status: current
professional_validation: not_required
normative: true
---

# Design Intent Architecture

## Pipeline stages

A natural-language request produces both a technical `DesignerProposal` (Sprint 10) and a `DesignIntent` (Sprint 11) in a single deterministic pass:

```
raw statement (target, concept, value, strength, sourceText)
  ↓ normalize_target()          (normalizer.py)
  ↓ normalize_descriptor()      (normalizer.py, against vocabulary.py)
  ↓ build IntentStatement        (resolver.py, provenance=AI_NORMALIZED)
  ↓ MODIFY-mode merge            (resolver.py, keyed by (target, concept))
  ↓ detect_conflicts()           (conflicts.py)
  ↓ diagnostics appended         (diagnostics.py codes)
  ↓ DesignIntent returned on DesignerProposal.designIntent
```

Relations (`IntentRelation`) follow the same shape through `normalize_target()` + `normalize_predicate()`.

## Module ownership

| Stage | Module |
|---|---|
| Data shapes | `backend/jewelmind/design_intent/schemas.py` |
| Controlled vocabulary | `backend/jewelmind/design_intent/vocabulary.py` |
| Deterministic normalization | `backend/jewelmind/design_intent/normalizer.py` |
| Orchestration + MODIFY merge + diff | `backend/jewelmind/design_intent/resolver.py` |
| Conflict detection | `backend/jewelmind/design_intent/conflicts.py` |
| Diagnostic codes | `backend/jewelmind/design_intent/diagnostics.py` |

No module in this list imports `cadquery`, touches `JewelryDefinition`, or calls a Forge rule — see [`330-intent-governance.md`](330-intent-governance.md), INTENT-GOV-004/011.

## Where it plugs into Designer

`backend/jewelmind/designer/service.py::_build_proposal()` calls `build_design_intent()` once per request, alongside its existing technical-field resolution (see [`308-designer-validation-pipeline.md`](../12-designer/308-designer-validation-pipeline.md) for that half). The two channels run independently on the same raw provider response:

- Technical fields (`proposedFields`, `candidateJDL`) come from `raw.proposedCanonicalValues` and are validated through JDL/Forge exactly as in Sprint 10 — unchanged.
- Design intent (`designIntent`) comes from `raw.designIntentStatements`/`raw.designIntentRelations`, converted to `RawStatementInput`/`RawRelationInput`, and passed to `build_design_intent()` with `previous=request.currentDesignIntent`.

`raw.unresolvedDescriptors` (Designer's existing Sprint 10 channel) is also threaded into `build_design_intent()` as `raw_unresolved_descriptors`, so a word the provider itself couldn't classify at all still lands in `DesignIntent.unresolvedDescriptors`, not just in the legacy `DesignerProposal.unresolvedIntent` field (kept for backward compatibility, populated identically to before).

## The one real behavior change to the technical pipeline this Sprint

`service.py`'s diff computation changed from conditionally comparing (`MODIFY` only) to unconditionally calling `normalizer.compute_diff(request.currentJDL, candidate)` in both `CREATE` and `MODIFY` modes. This has nothing to do with intent semantics directly — it exists so the frontend's `diff.some(d => d.changed)` check is meaningful regardless of interaction mode, which is what lets the Studio UI (see [`357-studio-intent-review.md`](357-studio-intent-review.md)) decide whether a proposal's technical content changed at all, independently of whether it carried design intent.

## What this Sprint does not add

No new HTTP endpoint. `POST /api/designer/interpret` gained two request fields (`currentDesignIntent`) and one response field (`designIntent`) — there is no dedicated `/api/design-intent/*` route. Design Intent has no persistence layer of its own; it lives only inside a `DesignerProposal` response and, once applied, inside the frontend's `useDesignIntentStore`.

See [`332-intent-domain-model.md`](332-intent-domain-model.md) for the full shape of `DesignIntent` and `IntentStatement`, and [`356-designer-intent-extraction.md`](356-designer-intent-extraction.md) for how the provider is instructed to produce raw statements in the first place.
