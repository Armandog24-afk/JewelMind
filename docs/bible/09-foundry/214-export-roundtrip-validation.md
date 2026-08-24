---
id: JM-BIBLE-214
title: Export Roundtrip Validation
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-202
related_documents:
  - JM-BIBLE-A38
implementation_status: current
professional_validation: not_required
normative: true
---

# Export Roundtrip Validation

## STEP: practical, and implemented

`cadquery.importers.importStep(fileName, unit="MM")` is real, available in the current environment, and requires no new dependency. `backend/tests/test_export_integrity.py::test_step_export_roundtrip_via_reimport` uses it to re-import a real exported STEP file for the default solitaire and confirms:

| Measurement | Value |
|---|---|
| Re-imported solid count | 1 |
| Re-imported volume | 341.4432078705695 mm³ |
| Original `combined_metal_volume_mm3` | 341.44334316909976 mm³ |
| Relative difference | 3.96×10⁻⁷ |
| Test tolerance used | `pytest.approx(rel=1e-3)` |

The `1e-3` tolerance is deliberately wider than Sprint 5's Atlas cross-platform kernel tolerance (`rel=1e-6`) because file-format roundtrip through STEP's decimal-precision text representation is a lossier boundary than pure in-process kernel variance — see [`07-atlas/137-determinism-and-reproducibility.md`](../07-atlas/137-determinism-and-reproducibility.md). The real measured difference (`3.96e-7`) is in fact far tighter than even that wider tolerance requires; the tolerance is set for headroom against future, different geometry, not because this specific measurement needed it.

## STL: practical, and implemented differently

CadQuery has no STL importer suited to a true geometric roundtrip (mesh-to-B-Rep is not a meaningful inverse operation). Instead, `backend/tests/test_export_integrity.py::test_stl_export_roundtrip_via_binary_header_parse` performs a dependency-free structural roundtrip: parsing the file's own binary header and confirming its declared triangle count reconciles exactly with its byte size (`84 + 10454 * 50 == 522784`, confirmed). This is a genuine, real check — it is a structural-integrity roundtrip, not a geometric-fidelity roundtrip, and this document does not claim otherwise.

## No fragile dependency introduced

Both checks use only libraries already present in `requirements.txt` (`cadquery` for STEP; Python's built-in `struct` module for STL) — no new package was added, satisfying the "do not introduce fragile dependencies" constraint for this Sprint.

## What remains a gap

A true STL *geometric* roundtrip (re-tessellating and comparing surface area/volume against the original mesh) would require either a third-party STL-to-mesh library or a hand-written parser well beyond a header check — judged out of proportion to this Sprint's hardening scope. This is recorded as a real, open gap in [`218-foundry-gap-analysis.md`](218-foundry-gap-analysis.md) and [`219-open-foundry-questions.md`](219-open-foundry-questions.md), not silently left undocumented.
