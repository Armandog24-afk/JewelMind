---
id: JM-BIBLE-106
title: Generated Geometry Inspection Rules
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-093
related_documents:
  - JM-BIBLE-111
  - JM-BIBLE-140
implementation_status: partial
professional_validation: not_required
normative: true
---

# Generated Geometry Inspection Rules

**Relationship to Atlas (Sprint 5):** [`07-atlas/140-geometry-inspection-framework.md`](../07-atlas/140-geometry-inspection-framework.md)
is the full Atlas-level formalization of the finding below, with the
complete GEOMETRIC-FACT-vs-FORGE-INTERPRETATION vocabulary
(`checkType`, `status`: `PASS`/`FAIL`/`UNKNOWN`/`NOT_APPLICABLE`) this
document's table anticipates but does not itself define. Nothing in
Sprint 5 changes the finding immediately below — it remains the single
most important open geometry-inspection gap in the system.

## CURRENT: one runtime rule, several test-time-only guarantees

**Only one geometry-inspection check runs at request time and can affect a real API response: `FORGE-GEOM-001`** — `_fuse_metal()`'s `if not fused.Solids(): raise ValueError(...)` (caught internally, triggering the documented compound fallback with a warning; see `backend/jewelmind/geometry/assemblies/solitaire.py`). This is the only geometry-inspection logic a live user request actually executes.

Everything else in the table below is verified **only by `backend/tests/test_geometry.py`**, at development/CI time, against a fixed set of test definitions — it is not re-checked for every real user-submitted definition, and no diagnostic is returned to an API caller if one of these properties happens to fail for their specific input.

| Property | Verified by | Runtime or test-only? |
|---|---|---|
| Component exists (band, stone_reference, prongs, basket_support all present) | `test_solitaire_assembly_has_all_required_components` | Test-only |
| Shape not null / has solids | `test_flat_band_is_valid_solid_with_positive_volume`, `test_stone_reference_is_valid_and_separate_from_metal`, `test_basket_exists_and_has_positive_volume` | Test-only |
| Positive volume | Same three tests, plus `test_solitaire_assembly_has_all_required_components` | Test-only |
| Plausible bounding box | `test_band_bounding_box_is_plausible`, `test_solitaire_assembly_bounding_box_plausible` | Test-only |
| Requested prong count equals generated count | `test_prongs_default_count_is_six`, `test_prongs_four_count`, `test_four_and_six_prong_models_visibly_differ` (via `component.metadata["generatedCount"]`) | Test-only |
| Stone remains separate from metal | `test_stone_reference_is_valid_and_separate_from_metal` | Test-only |
| Combined metal is a usable solid (or falls back to a compound) | `_fuse_metal()` (`FORGE-GEOM-001`) | **Runtime** |
| Export shape exists | Implicit in `export_step`/`export_stl` succeeding; no dedicated pre-export geometry check | Test-only (via `backend/tests/test_api.py`'s export endpoint tests) |

## This is a real, honest gap, not a documentation omission

There is currently no runtime mechanism that would tell a caller "your specific definition produced a component with zero volume" or "your specific definition produced an implausible bounding box" — if such a defect ever occurred for a real user's input outside the fixed set of test cases, it would either surface as a downstream CadQuery exception (`MODEL_GENERATION_FAILED`) or pass through silently. See [`111-domain-rule-gap-analysis.md`](111-domain-rule-gap-analysis.md) for this recorded as a gap, and open question territory in [`115-open-forge-questions.md`](115-open-forge-questions.md).

## PLANNED checks (not implemented, do not exist in any form)

Disconnected metal bodies detection, self-intersection detection, minimum local thickness analysis, non-manifold geometry detection, stone-metal interference detection, support continuity verification, trapped-volume detection, inaccessible-polishing-region detection. **None of these has any code, test, or partial implementation in this repository.** They are listed here only because Sprint 2/3's domain and JDL documents anticipate them as the kind of check a mature CAD-inspection pipeline would eventually need — see [`111-domain-rule-gap-analysis.md`](111-domain-rule-gap-analysis.md) for why each matters and what expertise would be needed to implement it correctly.
