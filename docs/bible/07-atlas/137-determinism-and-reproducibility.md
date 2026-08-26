---
id: JM-BIBLE-137
title: Determinism and Reproducibility
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-120
related_documents:
  - JM-BIBLE-076
implementation_status: current
professional_validation: not_required
normative: true
---

# Determinism and Reproducibility

## What "same canonical JDL" should produce

Same canonical JDL + same JDL schema version + same geometry generator version + same Forge rules (where relevant) + same CAD-kernel environment should produce **geometrically equivalent** outputs.

## Binary reproducibility vs. geometric reproducibility — these are different claims

**JewelMind does not claim byte-identical STEP files across runs, and this has not been tested in this Sprint.** What is actually guaranteed and verified (`backend/tests/test_geometry.py::test_definition_hash_is_deterministic`) is: the same `JewelryDefinition`, run twice in the same process, produces the same `definitionHash` and the same `combined_metal_volume_mm3` — i.e., **geometric** reproducibility (same volumes, same bounding boxes, same topology), not necessarily **binary** reproducibility of the exported file bytes (STEP files can, in principle, embed generation timestamps or entity-ordering details that are not guaranteed identical byte-for-byte across runs — this has not been measured either way in this codebase).

## Sources of potential non-determinism, assessed

| Source | Risk assessment |
|---|---|
| Floating-point behavior | Low — all arithmetic is standard IEEE-754 double precision, deterministic for a fixed CPU/compiler/library stack; not tested across different hardware architectures |
| OpenCascade version | **Unassessed** — this codebase pins `cadquery>=2.5` in `backend/requirements.txt` (a minimum, not an exact pin), so OCCT's bundled version could differ across installs; no cross-version reproducibility test exists |
| Topology ordering (e.g. face/edge iteration order after a boolean) | **Unassessed** — no test checks whether `.Solids()`/`.Faces()` ordering is stable across runs; volumes and bounding boxes (which are order-independent) are what's actually tested |
| Mesh tessellation | Deterministic for fixed tolerance values and a fixed OCCT version (tessellation is itself a deterministic algorithm given the same inputs), but not cross-version tested |
| Timestamps | `ModelRecord.generated_at` is real wall-clock time by design (it is a generation timestamp, not a geometry input) — it never participates in `definitionHash` or in any geometric comparison (see [`05-jdl/076-canonicalization-and-definition-hashing.md`](../05-jdl/076-canonicalization-and-definition-hashing.md)) |
| Random values | None — no randomness exists anywhere in `geometry/` |
| Temporary IDs | Temp file paths (`tempfile.mkdtemp()`/`mkstemp()`) are randomized per the OS, but only for file *storage location*, never for geometry content |

## What JewelMind currently guarantees

1. **Geometric determinism within one process, one dependency install**: same input → same volumes, same bounding boxes, same `definitionHash` (tested, `test_geometry.py`).
2. **No randomness or wall-clock dependency in geometry construction** (LAW-003, confirmed by direct code inspection — no `random`, `time.time()`, or `datetime.now()` call appears in any `geometry/` file except the deliberate, input-independent `time.perf_counter()` duration measurement in `solitaire.py`).

## What JewelMind does not currently guarantee, and has not tested

Cross-OCCT-version geometric equivalence; cross-machine binary STEP/STL file identity; topology (face/edge) ordering stability across runs. These are recorded as open questions (`ATLAS-OQ-009` in [`151-open-atlas-questions.md`](151-open-atlas-questions.md)) and gaps (see [`150-atlas-gap-analysis.md`](150-atlas-gap-analysis.md)), not silently assumed to be fine.

## Sprint 15 update — cross-platform drift is now measured, not just theorized

Sprint 15 ("Geometry Quality & Golden Models v1") measured a real, non-hypothetical instance of the "unassessed" cross-machine risk above: Sprint 14's own CI run showed a Windows-vs-Linux OCCT divergence of ~1.3e-5 relative on a near-tangent sliver intersection volume (see [`docs/bible/16-geometry-inspection/486-inspection-determinism.md`](../16-geometry-inspection/486-inspection-determinism.md)). Sprint 15 does not resolve the open questions above, but it does give this codebase its first empirically-derived, documented software-regression comparison tolerance (`RELATIVE_COMPARISON_TOLERANCE = 1e-3` in `backend/jewelmind/geometry_quality/version.py`) built around that real measurement — see [`docs/bible/17-geometry-quality/505-comparison-tolerance-policy.md`](../17-geometry-quality/505-comparison-tolerance-policy.md). This tolerance is a comparison tool for detecting regressions, never a claim about geometric determinism itself.
