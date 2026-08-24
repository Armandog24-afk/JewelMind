---
id: JM-BIBLE-174
title: Determinism and Version Fingerprint
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-160
related_documents:
  - JM-BIBLE-137
implementation_status: partial
professional_validation: not_required
normative: true
---

# Determinism and Version Fingerprint

## `CompilationEnvironmentFingerprint` (conceptual)

| Field | Current value | Recorded anywhere today? |
|---|---|---|
| JDL schema version | `0.1.0` | Yes — `schemaVersion` on every definition |
| Compiler version | Not distinct from `GENERATOR_VERSION` | No |
| Forge rule-set version | No aggregate exists (each rule is independently `1.0.0`) | No |
| Atlas generator version | `0.1.0` | Yes — `GeneratedModel.generator_version` |
| CadQuery version | Pinned as `>=2.5` (minimum, not exact) in `requirements.txt` | **No** — never recorded on any generated model |
| OpenCascade version | Whatever CadQuery's installed build bundles | **No** |
| Exporter version | No separate exporter versioning exists | No |
| Operating environment | N/A today | No |

**Only 2 of 8 conceptual fingerprint fields are recorded anywhere in current output.** This is the same gap Sprint 5's [`07-atlas/137-determinism-and-reproducibility.md`](../07-atlas/137-determinism-and-reproducibility.md) already identified (`ATLAS-OQ-009`, `ATLAS-OQ-010`) — this document is the compiler-level restatement, with the fingerprint concept named explicitly.

## Geometric vs. binary reproducibility, restated at the compiler level

This Sprint's own new test (`backend/tests/test_alchemist_registry.py`) and Sprint 5's fix to `test_atlas_registry.py` both apply a numeric tolerance to any OCCT-kernel-derived comparison, precisely because geometric reproducibility (same volumes/bounding boxes within a small tolerance) is what's actually guaranteed — not binary reproducibility (identical floating-point bit patterns) across different CadQuery/OCCT builds. This is empirically proven, not merely hypothesized: Sprint 5's CI run demonstrated exactly this divergence in `combined_metal_volume_mm3` between a Windows and a Linux OCCT build.

## What this means for `compilationHash`

A future `compilationHash` (see [`175-definition-hash-vs-compilation-hash.md`](175-definition-hash-vs-compilation-hash.md)) that includes a kernel version would let two different kernel builds carry two different hashes for the same design intent — arguably more honest than today's `definitionHash`, which is silent about which kernel build actually produced a given cached `GeneratedModel`.
