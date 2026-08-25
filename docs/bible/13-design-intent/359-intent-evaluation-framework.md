---
id: JM-BIBLE-359
title: Intent Evaluation Framework
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-358
related_documents:
  - JM-BIBLE-360
implementation_status: current
professional_validation: not_required
normative: true
---

# Intent Evaluation Framework

## The 9 metrics

Design Intent quality is framed around nine metrics, mirroring the evaluation discipline Sprint 10 applied to Designer's own technical-field accuracy:

| Metric | What it measures |
|---|---|
| `DESCRIPTOR_EXTRACTION_ACCURACY` | Whether a raw aesthetic phrase produces a statement at all. |
| `CANONICAL_CONCEPT_ACCURACY` | Whether the extracted statement lands on the correct `IntentConceptCategory`. |
| `TARGET_ACCURACY` | Whether the statement's `target` correctly identifies which component it describes. |
| `RELATION_EXTRACTION_ACCURACY` | Whether comparative language ("more X than Y") produces the correct `IntentRelation`. |
| `INTENT_PRESERVATION_RATE` | Whether recognized statements survive review/apply/regeneration without being lost (`353-intent-preservation.md`). |
| `FALSE_NUMERIC_RESOLUTION_RATE` | Whether any statement was ever incorrectly converted into a numeric JDL value. |
| `CONFLICT_DETECTION_ACCURACY` | Whether `conflicts.py` correctly flags genuinely contradictory statements without over- or under-flagging. |
| `UNRESOLVED_INTENT_RECALL` | Whether every statement JewelMind cannot classify is actually captured in `unresolvedDescriptors`, rather than silently dropped. |
| `INTENT_LOSS_RATE` | Whether any statement disappears across a MODIFY-mode merge that should have preserved it. |

## The single most critical metric: `FALSE_NUMERIC_RESOLUTION_RATE`

This is the one metric with a real, provable zero today, not merely an aspiration. No code path in `design_intent/` can produce a numeric JDL change from a statement — see [`350-intent-to-jdl-boundary.md`](350-intent-to-jdl-boundary.md)'s grep-verified finding that the package never imports `JewelryDefinition`. This is verified negatively by `backend/tests/test_designer_intent_integration.py::TestNoArbitraryNumericMapping` and the corpus's dedicated `NO_ARBITRARY_NUMERIC_MAPPING` category (10 cases, including the exact "delicate never touches `band.width`" and "bolder never increases `band.width`/`stone.diameter`/`setting.prongDiameter`" examples from this Sprint's brief). The target philosophy is not "keep this rate low" — it is **zero, always**, and any future change that would make it nonzero (i.e. any change registering a deterministic mapping) is gated behind an ADR (`330-intent-governance.md`).

## What the 89-case corpus is, and is not, a proxy for today

The corpus (`backend/tests/test_design_intent_corpus.py`, [`360-intent-test-corpus.md`](360-intent-test-corpus.md)) is a first deterministic proxy for several of these metrics — `DESCRIPTOR_EXTRACTION_ACCURACY`, `CANONICAL_CONCEPT_ACCURACY`, `TARGET_ACCURACY`, `RELATION_EXTRACTION_ACCURACY`, `UNRESOLVED_INTENT_RECALL`, `CONFLICT_DETECTION_ACCURACY`, and `FALSE_NUMERIC_RESOLUTION_RATE` all have direct, passing test coverage today. `INTENT_PRESERVATION_RATE` and `INTENT_LOSS_RATE` are covered only for the specific MODIFY-merge scenarios the corpus and integration tests exercise (e.g. `test_designer_intent_integration.py`'s "MODIFY preserving intent across a technical-only change" case) — neither is tracked as a running production metric, because there is no telemetry pipeline collecting live usage data yet (the same gap Sprint 10 documented for its own observability — `../12-designer/316-designer-observability.md`).

## What this framework is not

It is not a live dashboard, a scoring service, or an automated regression gate beyond the existing pytest suite. It is the vocabulary this Sprint uses to reason about quality, backed today entirely by deterministic, `FakeDesignerProvider`-only tests — never a live-LLM benchmark (no live LLM interpretation was exercised this Sprint at all, see [`360-intent-test-corpus.md`](360-intent-test-corpus.md)).

## Cross-references

- [`330-intent-governance.md`](330-intent-governance.md) — INTENT-GOV-001.
- [`360-intent-test-corpus.md`](360-intent-test-corpus.md) — the corpus these metrics are proxied against.
- `../12-designer/316-designer-observability.md`, `317-designer-cost-and-latency-model.md` — the parallel Sprint 10 gaps this framework does not yet close either.
- [`362-design-intent-gap-analysis.md`](362-design-intent-gap-analysis.md) — real observability/telemetry as future work.
