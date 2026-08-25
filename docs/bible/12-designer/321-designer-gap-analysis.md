---
id: JM-BIBLE-321
title: Designer Gap Analysis
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-320
related_documents:
  - JM-BIBLE-322
implementation_status: current
professional_validation: not_required
normative: false
---

# Designer Gap Analysis

This document catalogues future gaps observed while building Sprint 10, without implementing any of them. Per Bible governance, none of these are CURRENT or PARTIAL functionality — they are candidate future work, gated by the RFC/ADR process named in [`290-designer-governance.md`](290-designer-governance.md).

| Gap | Business value | Complexity | Architecture dependency | Professional-validation need | Target sprint |
|---|---|---|---|---|---|
| Richer descriptive intent (aesthetic language -> deterministic rules) | High — "delicate"/"bold" currently only reach `unresolvedIntent` as plain strings | High | New semantic layer, likely a new schema | Yes — any resulting geometric mapping needs professional review | Sprint 11 — Design Intent Model |
| Style embeddings / learned preference matching | Medium | High | New ML infrastructure, outside current CAD-determinism boundary for anything geometry-affecting | Yes | Unscheduled |
| Reference-image / sketch input | High | High | New multimodal provider capability, new privacy boundary (image data) | Yes | Unscheduled |
| Voice input | Low-Medium | Medium | Speech-to-text integration ahead of the existing text pipeline | No (transcription only) | Unscheduled |
| Multi-turn conversation | Medium | Medium | Stateful session model; current Designer is stateless request/response | No | Unscheduled |
| Design memory / preference profiles | Medium | Medium | Persistent per-user storage — currently out of scope (no auth/accounts) | Possibly | Unscheduled |
| Multiple competing proposals per request | Medium | Medium | New `DesignerResult` shape (list of proposals) | No | Unscheduled |
| Automatic alternatives for unsupported requests | Medium | Low-Medium | Extends `UnsupportedFeature.suggestedSupportedAlternative` from a hint to a generated candidate | No | Unscheduled |
| Cost-aware / manufacturing-aware suggestions | Medium | High | Requires real Foundry/manufacturing cost data JewelMind does not model yet | Yes | Unscheduled |
| Professional vocabulary by locale beyond IT/EN | Low-Medium | Medium | Extends `normalizer.py`'s synonym tables and `SupportedLocale` | No | Unscheduled |
| Literal 3-button proposal review mockup ([Apply] [Edit] [Cancel]) | Low — superseded by the always-visible `ConfigurationPanel` (see [`310-user-review-and-acceptance.md`](310-user-review-and-acceptance.md)) | Low | None | No | Not planned — deliberately simplified, not deferred |
| Real observability event emission (10-event taxonomy) | Medium — needed before production usage metrics are trustworthy | Low-Medium | Structured logging infrastructure beyond the current generic middleware (see [`316-designer-observability.md`](316-designer-observability.md)) | No | Unscheduled |
| Real cost/latency tracking | Medium | Low (once a live provider exists) | Depends on a configured `ANTHROPIC_API_KEY` in a real deployment (see [`317-designer-cost-and-latency-model.md`](317-designer-cost-and-latency-model.md)) | No | Unscheduled |
| Richer proposal-diff UI (before -> after view) | Medium | Low — `compute_diff()` already produces the data (see [`311-proposal-diff-model.md`](311-proposal-diff-model.md)) | None — frontend-only | No | Unscheduled |
| Distinct `CLARIFICATION_RESPONSE` provenance | Low-Medium | Low | None — `FieldProvenance` already has the enum member (see [`300-clarification-policy.md`](300-clarification-policy.md), [`303-field-provenance-model.md`](303-field-provenance-model.md)) | No | Unscheduled |

See [`322-open-designer-questions.md`](322-open-designer-questions.md) for the open product/policy questions these gaps raise, and [`290-designer-governance.md`](290-designer-governance.md) for when an RFC or ADR is required before any of these can be built.
