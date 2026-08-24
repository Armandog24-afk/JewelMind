---
id: JM-BIBLE-149
title: Current Solitaire Geometry Mapping
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-130
related_documents:
  - JM-BIBLE-A26
implementation_status: current
professional_validation: not_required
normative: true
---

# Current Solitaire Geometry Mapping

Every JDL field that drives geometry, traced end to end through real code. **This document is factual** — every cell was confirmed by direct inspection of the builder source during this Sprint.

| JDL path | Derived value | Builder | CadQuery operation | Component | Inspection | Preview | STEP | STL | Tests |
|---|---|---|---|---|---|---|---|---|---|
| `ring.innerDiameter` | `inner_radius = innerDiameter/2`; `outer_radius = inner_radius + band.thickness`; `band_top_z = outer_radius` | `band.py`, `constants.py` | `.revolve()` (band wire drawn from `inner_r` to `outer_r`) | `band` | Test-only: bbox plausibility | Included | Included (via `combined_metal`) | Included | `test_geometry.py::test_band_bounding_box_is_plausible` |
| `band.width` | `half_width = width/2`; also bounds the fillet radius (`width * 0.15`) | `band.py` | Wire corner Y-coordinates; `.fillet()` | `band` | Test-only: bbox `ymax-ymin <= width+0.05` | Included | Included | Included | `test_geometry.py::test_band_bounding_box_is_plausible` |
| `band.thickness` | Contributes to `outer_radius`; also bounds fillet radius | `band.py`, `constants.py` | Wire corner X-coordinate (`outer_r`) | `band` | Test-only | Included | Included | Included | Same |
| `band.profile` | Selects wire-construction function | `band.py::build_ring_band` | `_build_flat_wire` or `_build_comfort_fit_wire`, then `.revolve()` | `band` | Test-only: volume differs between profiles | Included | Included | Included | `test_geometry.py::test_flat_and_comfort_fit_bands_differ_in_volume` |
| `stone.diameter` | `girdle_r = diameter/2`; `table_r = girdle_r * 0.56`; also feeds `prong_center_radius` | `stone.py`, `constants.py` | `.circle(girdle_r)` in the loft chain | `stone_reference` (and indirectly `prongs`/`basket_support` via shared center radius) | Test-only: positive volume, Z-separation from band | Included (visible) | **Excluded by default** | **Excluded by default** | `test_geometry.py::test_stone_reference_is_valid_and_separate_from_metal` |
| `stone.depth` | `crown_h = depth*0.35`; `pavilion_h = depth*0.65` | `stone.py` | Workplane offsets between the three loft cross-sections | `stone_reference` | Test-only | Included (visible) | Excluded by default | Excluded by default | Same |
| `setting.prongCount` | `generated_count` (see [`127-surface-and-solid-model.md`](127-surface-and-solid-model.md) for the `requestedCount != generated_count` edge case) | `prongs.py` | `_prong_positions()` (pure math), one `.circle().extrude()` per position | `prongs` | Test-only: `generatedCount` equals requested for supported counts | Included | Included | Included | `test_geometry.py::test_prongs_default_count_is_six`, `test_prongs_four_count` |
| `setting.prongDiameter` | `prong_r = prongDiameter/2`; also feeds `prong_center_radius` and `basket_support`'s outer/inner radii | `prongs.py`, `basket.py`, `constants.py` | `.circle(prong_r)` | `prongs`, indirectly `basket_support` | Test-only | Included | Included | Included | `test_geometry.py` |
| `setting.prongHeight` | `height = prongHeight + EMBED_MM` | `prongs.py` | `.extrude(height)` | `prongs` | Test-only | Included | Included | Included | `test_geometry.py` |
| `setting.basketHeight` | `height = basketHeight + EMBED_MM`; also feeds `stone.py`'s `girdle_z = band_top_z + basketHeight` | `basket.py`, `stone.py` | `.extrude(height)` (basket); workplane offset (stone) | `basket_support`, indirectly `stone_reference`'s placement | Test-only | Included | Included | Included | `test_geometry.py::test_basket_exists_and_has_positive_volume` |
| `preview.meshTolerance` | Passed straight through, no derivation | `preview/mesh.py`, `exporters/stl_exporter.py` | `.tessellate()`/`.exportStl(tolerance=...)` | All components (preview); `combined_metal` (STL export) | n/a — controls mesh fidelity, not geometry correctness | Controls preview mesh density | n/a (STEP is exact B-Rep, no tessellation) | Controls STL mesh density | No dedicated test asserts a specific triangle count for a specific tolerance |
| `preview.angularTolerance` | Passed straight through (radians) | Same | `.tessellate()`/`.exportStl(angularTolerance=...)` | Same | n/a | Same | n/a | Same | Same |

## Two fields with cross-component reach, worth stating explicitly

- **`setting.basketHeight`** drives both `basket_support`'s own height *and* `stone_reference`'s girdle Z placement (`stone.py`'s `girdle_z = band_top_z + basketHeight`) — a change to this one field moves the stone even though it is not itself a stone field.
- **`stone.diameter`** drives `prong_center_radius` (`constants.py`), which in turn sizes both `prongs` and `basket_support`'s radii — a change to this one field reshapes two metal components even though it is not itself a metal-geometry field.

Neither cross-reach was previously stated this explicitly anywhere in the Bible before this Sprint (Sprint 2's [`04-jewelry-domain/052-parametric-dependency-model.md`](../04-jewelry-domain/052-parametric-dependency-model.md) lists the dependency but not this specific narrative framing).
