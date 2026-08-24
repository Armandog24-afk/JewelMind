---
id: JM-BIBLE-215
title: Foundry Performance Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-190
related_documents:
  - JM-BIBLE-185
implementation_status: current
professional_validation: not_required
normative: true
---

# Foundry Performance Model

## No arbitrary SLA

Restating [`08-alchemist/185-compiler-performance-model.md`](../08-alchemist/185-compiler-performance-model.md)'s approach at the export layer: no numeric export-latency target is asserted anywhere in this codebase, and none is invented here. Export duration depends on shape complexity (solid count, triangle count for STL) and is not currently measured or logged per request — see [`201-artifact-manifest-model.md`](201-artifact-manifest-model.md)'s `generationDuration` field, marked PLANNED.

## What is known, qualitatively

- STEP export cost scales with the underlying B-Rep's topological complexity, not with any artificial pagination or streaming — the whole file is written in one `exportStep()` call.
- STL export cost is dominated by tessellation (`meshTolerance`/`angularTolerance`), already computed once at preview-generation time for preview meshes and recomputed independently for a dedicated STL export request (a real, minor duplication of work, not a correctness issue).
- Integrity checks added this Sprint (`sha256_checksum()`, `validate_non_empty()`) read the file once, sequentially, in 64KB chunks — a fixed, small, additive cost proportional to file size, not expected to be a meaningful fraction of total export time for files in the hundreds-of-kilobytes range observed today (STEP: 197081 bytes; STL: 522784 bytes, for the default solitaire).

## Why re-import/roundtrip validation stays test-only

As stated in [`202-artifact-integrity-model.md`](202-artifact-integrity-model.md), the deciding factor was cost/benefit, not a measured latency number — re-importing a STEP file to validate it a second time approximately doubles the CAD-kernel work for a marginal benefit (proving the exporter's own correctness, already proven once per code change by the test suite) that does not scale with the number of times a single already-known-correct exporter runs.

## No load testing performed

This Sprint did not perform concurrent-load or stress testing of the export endpoints. Nothing in this document should be read as a claim about behaviour under concurrent load beyond what [`207-temp-file-lifecycle.md`](207-temp-file-lifecycle.md) already establishes structurally (unique per-request temp files, independent cleanup).
