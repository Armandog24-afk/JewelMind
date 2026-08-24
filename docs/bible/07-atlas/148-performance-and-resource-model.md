---
id: JM-BIBLE-148
title: Performance and Resource Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-132
related_documents: []
implementation_status: partial
professional_validation: not_required
normative: false
---

# Performance and Resource Model

## What is actually measured today

`GeneratedModel.generation_duration_s` (`time.perf_counter()` around the four builder calls + fuse, in `solitaire.py::build_solitaire_ring`) is the **only** timing measurement anywhere in the geometry pipeline. For the default definition, one real run measured `0.730515600182116` seconds — this is a single observed sample, not a benchmark, and varies by machine/load; it is not asserted as a performance target.

## What is not measured

Tessellation cost (preview or export), boolean (fuse) cost specifically (folded into the one overall `generation_duration_s`), export cost (STEP/STL write time), memory use of any kind, and repeated-generation cache-hit behavior are **not separately instrumented anywhere** in this codebase.

## Cache and temporary file behavior (documented elsewhere, cross-referenced here)

`MAX_CACHED_MODELS = 20` with LRU eviction (`services/model_service.py`), unique per-request temp files for exports (`tempfile.mkstemp()`), `BackgroundTask`-scheduled cleanup after response — already fully documented in [`05-jdl/083-security-and-resource-limits.md`](../05-jdl/083-security-and-resource-limits.md) and `docs/known-limitations.md`; not repeated in full here.

## Future benchmark categories (none implemented, no targets invented)

- Generation duration vs. prong count (does N=6 vs. a hypothetical larger N scale linearly?).
- Fuse duration in isolation, vs. total generation duration.
- Tessellation duration vs. `meshTolerance` (finer tolerance should cost more; unmeasured).
- Export duration for STEP vs. STL.
- Memory footprint of a single `GeneratedModel` and its cached temp directory.

**No specific numeric performance target is stated anywhere in this document**, per this Sprint's explicit instruction not to invent performance targets without measurements. A future sprint that actually benchmarks these categories should populate this document with real numbers, not this one.

## No unstable CI thresholds added

Per this Sprint's explicit instruction, no benchmark test with a numeric pass/fail threshold was added to the CI suite. A benchmark test skeleton was considered but not created in this Sprint — see [`150-atlas-gap-analysis.md`](150-atlas-gap-analysis.md) (`ATLAS-GAP-016`, performance benchmarks) for this recorded as a future gap rather than implemented speculatively.
