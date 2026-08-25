---
id: JM-BIBLE-352
title: Unresolved Intent Lifecycle
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-351
related_documents:
  - JM-BIBLE-353
implementation_status: current
professional_validation: not_required
normative: true
---

# Unresolved Intent Lifecycle

## Unresolved intent is a normal outcome, not an error

No `INTENT_*` diagnostic ever fails an HTTP request (see [`358-intent-diagnostics.md`](358-intent-diagnostics.md)). A statement JewelMind cannot classify, or a descriptor with no recognized value, is an expected, everyday result of natural-language input — not a bug to be fixed or a request to be rejected.

## The real lifecycle, step by step

1. **Raw text arrives** — a Designer provider emits a `RawIntentStatement` (`target`, `concept`, `value`, `sourceText`) or Designer's own pre-existing free-text `unresolvedDescriptors` (Sprint 10, top-level statements the provider couldn't classify at all).
2. **`normalize_target()` / `normalize_descriptor()` attempt to classify it** — `design_intent/normalizer.py`'s deterministic vocabulary lookup.
3. **On failure, it is appended to `unresolvedDescriptors`** — `resolver.py::_resolve_statements()` appends `raw.sourceText or raw.value` when `target is None` or `concept not in KNOWN_CONCEPTS` (unrecognized target/concept), and again when `normalize_descriptor()` returns `None` (recognized concept, unrecognized value). An `INTENT_UNKNOWN_DESCRIPTOR` diagnostic (severity `info`) is appended alongside it in both cases.
4. **It is preserved in the returned `DesignIntent`** — never dropped, per INTENT-GOV-005/006. Every entry in `unresolvedDescriptors` also gets an `INTENT_PRESERVED_UNRESOLVED` diagnostic (`resolver.py:196-203`) recording that it was preserved rather than converted into a dimension.
5. **It is surfaced in Studio** with the exact required copy, rendered verbatim by `DesignerPanel.tsx`: *"'{text}' has been preserved as design intent. JewelMind does not currently convert this subjective preference into arbitrary dimensions."*
6. **In MODIFY mode, it is unioned forward** — `build_design_intent()`'s MODIFY branch computes `previous.unresolvedDescriptors + [new entries not already seen]` (`resolver.py:177-178`), so a descriptor from an earlier turn survives every later turn in the same session.

## The real, current limitation: never pruned, never re-attempted

Step 6 is a strict union with deduplication by exact string match — there is no code path that ever removes an entry from `unresolvedDescriptors`, and no code path that re-attempts classification on a later turn even if the vocabulary would now recognize it (e.g. after a hypothetical vocabulary update mid-session). Across repeated MODIFY turns in the same session, this list can only grow, never shrink automatically. The only way an entry leaves the list today is the frontend's `removeUnresolvedDescriptor()` action — an explicit user click on a tag's × button in `DesignerPanel.tsx`'s persistent summary (see [`357-studio-intent-review.md`](357-studio-intent-review.md)), which is a local UI-state removal, not a backend re-resolution.

This is a real, current gap, not a hidden one — it is named again in [`362-design-intent-gap-analysis.md`](362-design-intent-gap-analysis.md) as a concrete candidate for a future sprint (automatic re-attempt on vocabulary update, or a staleness/expiry policy for old unresolved entries).

## Cross-references

- [`330-intent-governance.md`](330-intent-governance.md) — INTENT-GOV-005, INTENT-GOV-006.
- [`353-intent-preservation.md`](353-intent-preservation.md) — how the resulting `DesignIntent` survives the rest of the review/apply lifecycle.
- [`357-studio-intent-review.md`](357-studio-intent-review.md) — the exact UI copy and removal control.
- [`358-intent-diagnostics.md`](358-intent-diagnostics.md) — `INTENT_UNKNOWN_DESCRIPTOR` and `INTENT_PRESERVED_UNRESOLVED` in full.
