---
id: JM-BIBLE-360
title: Intent Test Corpus
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-359
related_documents:
  - JM-BIBLE-361
implementation_status: current
professional_validation: not_required
normative: true
---

# Intent Test Corpus

## The real numbers

`backend/tests/test_design_intent_corpus.py` runs 89 parametrized natural-language corpus cases — well above this Sprint's own "at least 60 if practical" target — spanning these categories: `DESCRIPTOR_EXTRACTION`, `NORMALIZATION`, `TARGET_RESOLUTION`, `RELATION`, `UNRESOLVED_DESCRIPTOR`, `UNKNOWN_DESCRIPTOR`, `NO_ARBITRARY_NUMERIC_MAPPING` (10 dedicated cases), `MULTILINGUAL`, `CONFLICT`. The exhaustive per-case listing lives in [`../appendices/intent-test-case-catalog.md`](../appendices/intent-test-case-catalog.md) once the parallel agent covering Sprint 11's earlier documents (331-347) has written it; this document covers the corpus's structure and testing discipline.

## What each category proves

- **`DESCRIPTOR_EXTRACTION`** — a raw aesthetic phrase produces a statement.
- **`NORMALIZATION`** — a recognized synonym maps to its canonical value (e.g. `"delicato"` and `"delicate"` both normalize to `DELICATE`).
- **`TARGET_RESOLUTION`** — the statement lands on the correct `IntentTarget`.
- **`RELATION`** — comparative language produces the correct `IntentRelation` with the correct predicate.
- **`UNRESOLVED_DESCRIPTOR`** — a phrase JewelMind cannot classify correctly lands in `unresolvedDescriptors`, never silently dropped.
- **`UNKNOWN_DESCRIPTOR`** — a recognized target/concept with an unrecognized value correctly produces `INTENT_UNKNOWN_DESCRIPTOR`.
- **`NO_ARBITRARY_NUMERIC_MAPPING`** — 10 dedicated cases proving specific aesthetic statements never touch specific JDL fields (the "delicate never touches `band.width`" and "bolder never increases `band.width`/`stone.diameter`/`setting.prongDiameter`" cases named directly in this Sprint's brief).
- **`MULTILINGUAL`** — the same descriptor in Italian and English converges on the same canonical concept/value (INTENT-GOV-013).
- **`CONFLICT`** — genuinely contradictory statement pairs are correctly flagged by `conflicts.py::detect_conflicts()`.

## The `FakeDesignerProvider`-only CI discipline

Identical to Designer v1's own testing discipline (`../12-designer/README.md`): every corpus case runs against `FakeDesignerProvider`, a deterministic, hand-authored stand-in for a real LLM provider — never a live API call. This keeps CI deterministic, fast, and free of API cost or flakiness, at the cost of not exercising real-LLM extraction quality in CI (see [`361-current-code-mapping.md`](361-current-code-mapping.md) for the live-browser verification that *did* exercise the real request path, with the real provider unavailable in this dev environment — a `503 DESIGNER_PROVIDER_UNAVAILABLE`, not a live interpretation).

## The full backend test count this Sprint added

132 new backend tests total: 28 in `test_design_intent.py` (unit), 89 in `test_design_intent_corpus.py` (corpus), 7 in `test_design_intent_schemas.py` (JSON Schema validation against 7 real generated examples, plus the vocabulary file's no-numeric-CAD-mapping property and one live-reproducibility check), 8 in `test_designer_intent_integration.py` (Designer<->DesignIntent boundary: technical/aesthetic separation, 4 no-arbitrary-numeric-mapping variants, MODIFY preserving intent across a technical-only change, multilingual convergence, fake-provider round-trip). 444 backend tests pass overall (312 pre-existing + 132 new); backend ruff lint clean.

## Frontend coverage added this Sprint

`DesignerPanel.test.tsx` gained 3 tests (design-intent rendering+apply, intent-only-no-stale, real-change-does-stale); a new `useDesignIntentStore.test.ts` (6 tests); `useProjectStore.test.ts` gained 1 test (reset clears intent). 121 frontend tests pass overall (111 pre-existing + 10 new); `tsc -b` clean; `oxlint` clean; `vite build` succeeds.

## Cross-references

- [`330-intent-governance.md`](330-intent-governance.md) — INTENT-GOV-013.
- [`359-intent-evaluation-framework.md`](359-intent-evaluation-framework.md) — what these tests are a proxy for.
- [`../appendices/intent-test-case-catalog.md`](../appendices/intent-test-case-catalog.md) — the exhaustive case listing.
- `../12-designer/README.md` — the identical `FakeDesignerProvider`-only pattern this Sprint continues.
