---
id: JM-BIBLE-302
title: Confidence Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-301
related_documents:
  - JM-BIBLE-303
implementation_status: current
professional_validation: not_required
normative: true
---

# Confidence Model

## The 6-value `ConfidenceCategory` enum

`designer/schemas.py::ConfidenceCategory` is `Literal["EXACT", "NORMALIZED", "INFERRED", "DEFAULTED", "AMBIGUOUS", "UNSUPPORTED"]`. Per DESIGNER-GOV-010, this is JewelMind's own classification derived entirely from provenance/normalization facts — no raw provider confidence score (a number an LLM might return) is ever read, stored, or displayed anywhere in `backend/jewelmind/designer/` or `DesignerPanel.tsx`.

## What `service.py` actually assigns

Only three of the six values are emitted by current code, all in `_build_proposal()`:

- **`EXACT`** — an enum field whose raw provider token was already the canonical value (`already_canonical = str(pv.value).strip().lower() == str(value).strip().lower()`), and unconditionally for `project.name`.
- **`NORMALIZED`** — an enum field whose raw provider token mapped through a synonym table (e.g. `normalizer.METAL_SYNONYMS`) to a canonical value that differs from the raw token as typed (e.g. `"oro giallo"` -> `yellow_gold_18k`).
- **`INFERRED`** — every numeric field (`normalizer.is_numeric_field()`), because a bare number extracted from natural language has no canonical/synonym form to compare against — it is simply accepted once it parses as a float.

## What exists in the type but is not emitted

`DEFAULTED`, `AMBIGUOUS`, and `UNSUPPORTED` are real members of the `ConfidenceCategory` `Literal`, but no code path in `service.py` currently constructs a `ProposedField` with any of them:

- `DEFAULTED` would describe a field JewelMind's own system default filled in rather than the user — but Designer never proposes system defaults as `ProposedField`s at all today (see [`298-defaulting-policy.md`](298-defaulting-policy.md)); unspecified fields are simply left out of the patch and inherited from the base definition.
- `AMBIGUOUS` and `UNSUPPORTED` describe fields that, by the time `_build_proposal()` finishes processing them, have already been redirected into a `ClarificationQuestion` or an `UnsupportedFeature` instead of becoming a `ProposedField` at all — so a `ProposedField` with either confidence value would be a contradiction in the current pipeline.

This is the same honesty pattern as [`300-clarification-policy.md`](300-clarification-policy.md)'s note on `CLARIFICATION_RESPONSE` provenance: the schema is deliberately wider than the current implementation, to leave room for future refinement without a breaking schema change. See [`321-designer-gap-analysis.md`](321-designer-gap-analysis.md).

See [`303-field-provenance-model.md`](303-field-provenance-model.md) for the companion (and more safety-critical) provenance axis.
