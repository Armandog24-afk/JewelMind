---
id: JM-BIBLE-A57
title: "Appendix: Designer Field Provenance Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-DESIGNER-README
  - JM-BIBLE-290
related_documents:
  - JM-BIBLE-303
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Designer Field Provenance Catalog

The 8 `FieldProvenance` values defined in `backend/jewelmind/designer/schemas.py`. Verified by grepping `provenance=` across `backend/jewelmind/designer/service.py`: **only `AI_INTERPRETATION` is ever actually constructed by the current pipeline** (3 call sites, all in `DesignerService._build_proposal()` — the enum-field branch, the `project.name` branch, and the numeric-field branch). The other 7 values exist in the schema for completeness and for future stages (DESIGNER-GOV-011 requires every `ProposedField` to carry a provenance value; it does not require all 8 to be reachable today).

| `FieldProvenance` value | Currently emitted by `service.py`? | When it is (or would be) assigned |
|---|---|---|
| `AI_INTERPRETATION` | **Yes** — the only value emitted today | Every `ProposedField` built from a provider-extracted, normalizer-validated value in `_build_proposal()`, whether the confidence ends up `EXACT`, `NORMALIZED`, or `INFERRED` |
| `USER_EXPLICIT` | No | Reserved for a future stage where a user directly edits a specific proposed field in the review UI before acceptance (not implemented; `DesignerPanel.tsx` has no per-field edit control today) |
| `USER_CONTEXT` | No | Reserved for a value inferred from user-supplied context outside the request text itself (e.g. a stated preference from an earlier turn) — requires multi-turn conversation, which is explicitly out of scope for v1 (see `290-designer-governance.md`'s "When an RFC is required") |
| `CURRENT_DESIGN` | No | Reserved for explicitly tagging a field carried forward unchanged from `currentJDL` during MODIFY; today, unspecified fields are preserved by `_apply_patch()` operating on a full `model_dump()` of the base definition, but they never become a `ProposedField` at all — they simply remain absent from `proposedFields`, so no provenance tag is emitted for them |
| `SYSTEM_DEFAULT` | No | Reserved for explicitly tagging a field that fell back to `JewelryDefinition()`'s schema default on CREATE; today, defaulted fields are likewise never surfaced as a `ProposedField` — they are only visible by inspecting `candidateJDL` itself |
| `DETERMINISTIC_DERIVATION` | No | Reserved for a value computed by a deterministic rule from other proposed values (e.g. a derived dimension) — no such derivation exists in the current pipeline |
| `CLARIFICATION_RESPONSE` | No | Reserved for a field whose value came specifically from the user picking a `ClarificationQuestion` option; today, `DesignerPanel.tsx::handleClarify()` re-runs the full `/api/designer/interpret` call with the appended answer text, so the resulting field is re-extracted and tagged `AI_INTERPRETATION` like any other, not tagged as a clarification response |
| `UNRESOLVED` | No | Reserved for a field-level placeholder distinct from `DesignerProposal.unresolvedIntent` (a plain string list); no code path constructs a `ProposedField` with this provenance today |

## Honesty note

This is a real, currently-narrower-than-the-schema implementation, not a documentation gap: the schema was designed for the full provenance model described in `303-field-provenance-model.md`, but `service.py` as shipped in Sprint 10 only exercises one branch of it. Any future change that starts emitting one of the other 7 values must update this table in the same change.
