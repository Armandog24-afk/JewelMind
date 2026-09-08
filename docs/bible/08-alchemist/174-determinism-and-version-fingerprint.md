---
id: JM-BIBLE-174
title: Determinism and Version Fingerprint
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-08
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
| Compiler version | `jewelmind.__version__` | **Yes** — in `compilationHash` and in the Golden fingerprint |
| Forge rule-set version | `registryVersion` in `specs/forge/v1/current-rule-registry.json` — an aggregate **does** now exist, which it did not when this table was written | **Yes** — read by `compilation/environment.py` |
| Atlas generator version | `0.1.0` | Yes — `GeneratedModel.generator_version` |
| CadQuery version | `cadquery.__version__` at runtime | **Yes** — in `compilationHash` and in the Golden fingerprint |
| OpenCascade version | `OCP.__version__` where readable, else recorded as absent | **Yes** — in `compilationHash` and in the Golden fingerprint |
| Exporter version | No separate exporter versioning exists | No |
| Operating environment | N/A today | No |

**6 of 8 conceptual fingerprint fields are now recorded** (the two remaining — a separate exporter version and the operating environment — still do not exist as versioned things). This table previously read "only 2 of 8"; `compilationHash` ([`ADR-012`](../03-decisions/ADR-012-compilation-hash-as-cache-key.md)) closed the gap for the six that affect output. This is the same gap Sprint 5's [`07-atlas/137-determinism-and-reproducibility.md`](../07-atlas/137-determinism-and-reproducibility.md) already identified (`ATLAS-OQ-009`, `ATLAS-OQ-010`) — this document is the compiler-level restatement, with the fingerprint concept named explicitly.

## Geometric vs. binary reproducibility, restated at the compiler level

This Sprint's own new test (`backend/tests/test_alchemist_registry.py`) and Sprint 5's fix to `test_atlas_registry.py` both apply a numeric tolerance to any OCCT-kernel-derived comparison, precisely because geometric reproducibility (same volumes/bounding boxes within a small tolerance) is what's actually guaranteed — not binary reproducibility (identical floating-point bit patterns) across different CadQuery/OCCT builds. This is empirically proven, not merely hypothesized: Sprint 5's CI run demonstrated exactly this divergence in `combined_metal_volume_mm3` between a Windows and a Linux OCCT build.

## What this meant for `compilationHash`

This document argued that a `compilationHash` including a kernel version "would let two different kernel builds carry two different hashes for the same design intent — arguably more honest than today's `definitionHash`, which is silent about which kernel build actually produced a given cached `GeneratedModel`". That is now implemented: `kernelVersion` and `ocpVersion` are both components of `compilationHash`, and the cache is keyed on it, so a cached `GeneratedModel` can no longer be silent about the build that produced it.
