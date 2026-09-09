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
| `band.architecture` (Sprint 28) | Selects the whole shank construction: `UNIFORM` keeps the pre-Sprint-17 revolve, `SPLIT` builds two rails plus a bottom bridge, `BYPASS` builds one open rail past a full turn | `shank/builder.py::_build_architecture`, `shank/architecture.py` | `build_split_shank()` / `build_bypass_shank()`: `makeLoft(ruled=True)` over 48 sections per turn, plus a boolean intersect with a pie sector for the arcs | `band` | Real: `SHANK_RAIL_COUNT`, `SHANK_SEPARATED_AT_HEAD` | Included | Included | Included | `test_ring_families.py::TestVariantGeometryDiffers`, `goldens/RF-003`, `goldens/RF-005` |
| `band.splitSeparation` (Sprint 28) | The axial gap between the rails AND, because they SHARE the band's width, the rails' own width `(width − separation) / 2` | `shank/architecture.py::rail_half_width` | Section translation on Y before the shape is placed | `band` | Real: `SHANK_RAIL_COUNT` | Included | Included | Included | `JM-RINGFAM-004`, `test_ring_families.py` |
| `band.splitJoinSpan` (Sprint 28) | How much of the ring's bottom the rails are joined over, and therefore where they separate | `shank/architecture.py::build_split_shank` | Pie-sector angle for the bridge | `band` | Real: `SHANK_SEPARATED_AT_HEAD` | Included | Included | Included | `test_ring_families.py`, `goldens/RF-003` |
| `band.bypassSeparation` / `band.bypassOverlap` (Sprint 28) | The axial travel across the sweep and how far past a full turn the rail goes — together, whether the two ends pass each other | `shank/architecture.py::build_bypass_shank` | Interpolated Y offset per section over `360 + overlap` degrees | `band` | Real: `SHANK_RAIL_COUNT` = 1 | Included | Included | Included | `test_ring_families.py`, `goldens/RF-005` |
| `ringFamily.variant` (Sprint 28) | INDIRECT, and that indirection is the design: it derives the band architecture, the shoulder architecture, the body architecture, the head-height factor and the `family`/`halo`/`pave` blocks, and the DOCUMENT then drives the geometry | `ring_family/resolve.py`, `geometry/ring_family_adapter.py` | None directly — the layer builds nothing | every component the derivation reaches | Real: `RING_FAMILY_VARIANT`, `RING_FAMILY_FINGERPRINT`, `RING_FAMILY_DERIVED_PATH_COUNT` | n/a | n/a | n/a | `test_ring_families.py::TestParametricPropagation` |
| `setting.basketHeight` × `ringFamily` head factors (Sprint 28) | The head's height, and therefore the stone's girdle Z — MODULATED, never replaced: `basketHeight × variant factor × headHeightFactor` | `ring_family/resolve.py`, then `components/basket.py` unchanged | The existing basket construction, at a derived height | `basket_support`, `stone_reference`, `prongs` | Real: measured basket volume 53.305 / 83.156 / 116.738 mm³ for low-profile / classic / elevated | Included | Included | Included | `test_ring_families.py::test_the_head_height_factor_actually_moves_the_head` |
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
