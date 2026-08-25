---
id: JM-BIBLE-362
title: Design Intent Gap Analysis
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-361
related_documents:
  - JM-BIBLE-363
implementation_status: current
professional_validation: not_required
normative: false
---

# Design Intent Gap Analysis

This document catalogues future gaps observed while building Sprint 11, without implementing any of them. Per Bible governance, none of these are CURRENT or PARTIAL functionality — they are candidate future work, gated by the RFC/ADR process named in [`330-intent-governance.md`](330-intent-governance.md).

## Gaps identified while writing 348-357 (already-present in the real v1 code)

| Gap | Business value | Complexity | Architecture dependency | Professional-validation need | Target sprint |
|---|---|---|---|---|---|
| `IntentResolution` never constructed/persisted | Medium — needed once any resolution method exists | Low | A real resolution stage to call it | Depends on the resolution method | Sprint that first registers a profile |
| Unresolved-descriptor list never pruned or re-attempted across MODIFY turns | Medium — list can only grow in a long session | Low-Medium | None — pure `resolver.py` logic | No | Unscheduled |
| No localStorage persistence for `useDesignIntentStore` | Medium — intent is lost on page reload | Low | None — same pattern `useProjectStore` already uses | No | Unscheduled |
| No JDL/export embedding of `DesignIntent` | Medium | Medium | Requires JDL to explicitly evolve to support metadata (see [`363`](363-open-design-intent-questions.md) Q5) | No | Unscheduled — JDL evolution gated by `../05-jdl/` |
| No dedicated intent diff UI (before -> after) | Low-Medium | Low — `compute_intent_diff()` already produces the data | None — frontend-only | No | Unscheduled |
| No inline value-editing control for a statement | Low | Low-Medium | None — deliberate simplification per [`357`](357-studio-intent-review.md) | No | Not planned — deliberately simplified |
| 5 of 9 `INTENT_*` diagnostic codes never produced (`INTENT_AMBIGUOUS_DESCRIPTOR`, `INTENT_UNSUPPORTED_TARGET`, `INTENT_NO_DETERMINISTIC_RESOLUTION`, `INTENT_PROFILE_UNAVAILABLE`, `INTENT_RESOLUTION_REQUIRES_CONFIRMATION`) | Low today — schema-reserved for stages that don't exist | N/A until those stages exist | Ambiguity detection, resolution, and profile stages respectively | Depends on stage | Unscheduled |
| Real observability event emission | Medium — needed before production usage metrics are trustworthy | Low-Medium | Structured logging infrastructure beyond current generic middleware (mirrors `../12-designer/316-designer-observability.md`) | No | Unscheduled |
| Real cost/latency tracking | Medium | Low (once a live provider exists) | Depends on a configured `ANTHROPIC_API_KEY` in a real deployment (mirrors `../12-designer/317-designer-cost-and-latency-model.md`) | No | Unscheduled |

## Larger future-facing gaps (per this Sprint's brief)

| Gap | Business value | Complexity | Architecture dependency | Professional-validation need | Target sprint |
|---|---|---|---|---|---|
| Brand style profiles | High | High | First `IntentProfile` registration — ADR required | Yes | Unscheduled |
| Designer-specific profiles | Medium | High | Per-user/per-designer storage — no auth/accounts exist yet | Yes | Unscheduled |
| Trained preference embeddings | Medium | High | New ML infrastructure, outside current CAD-determinism boundary for anything geometry-affecting | Yes | Unscheduled |
| Reference-image intent | High | High | New multimodal provider capability, new privacy boundary (image data) | Yes | Unscheduled |
| Sketch semantics | Medium | High | Same multimodal dependency as reference-image intent | Yes | Unscheduled |
| Proportions learned from approved designs | Medium | High | Persistent design-history storage; feeds back into intent-to-JDL mapping only via the profile mechanism | Yes | Unscheduled |
| Automatic multiple variants | Medium | Medium | New `DesignerResult` shape (list of proposals), mirrors Designer's own open gap | No | Unscheduled |
| Aesthetic scoring | Low-Medium | High | Requires a validated aesthetic model — currently none exists or is planned | Yes | Unscheduled |
| Generated design alternatives | Medium | High | Depends on automatic multiple variants above | No | Unscheduled |
| Customer preference memory | Medium | Medium | Persistent per-user storage — out of scope (no auth/accounts) | Possibly | Unscheduled |
| Culturally specific vocabulary | Low-Medium | Medium | Extends `vocabulary.py`'s synonym tables beyond IT/EN | No | Unscheduled |
| Collection-level design language | Medium | High | Multi-project state JewelMind does not model yet | Yes | Unscheduled |
| Moodboards | Low-Medium | Medium | New input modality (images/references) | No | Unscheduled |
| Visual similarity | Low-Medium | High | Requires embeddings/vector search infrastructure | No | Unscheduled |

## Next scheduled sprint

Sprint 12 — **Conversation Engine v1** — structured multi-turn clarification and design refinement, maintaining design state, intent state, and unresolved questions without turning JewelMind into an unconstrained chatbot. Several gaps above (unresolved-descriptor pruning/re-attempt, richer resolution flows) are natural candidates for that Sprint but are not committed here.

## Cross-references

- [`330-intent-governance.md`](330-intent-governance.md) — when an RFC or ADR is required before any of these can be built.
- [`363-open-design-intent-questions.md`](363-open-design-intent-questions.md) — the open product/policy questions these gaps raise.
- `../12-designer/321-designer-gap-analysis.md` — the Sprint 10 sibling this table follows in structure.
