---
id: JM-BIBLE-578
title: Current Code Mapping and Gaps
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-STONE-README
  - JM-BIBLE-560
related_documents:
  - JM-BIBLE-561
  - JM-BIBLE-573
  - JM-BIBLE-579
implementation_status: current
professional_validation: not_required
normative: true
---

# Current Code Mapping and Gaps

## File-by-file map

### New this Sprint

| File | Responsibility |
|---|---|
| `backend/jewelmind/domain/stone_dimensions.py` | `resolved_length_mm()` / `resolved_width_mm()` / `resolved_depth_mm()` — the single LENGTH/WIDTH/DEPTH reconciliation point. In `domain/` so both Atlas and Forge can depend on it without new coupling. |
| `backend/jewelmind/geometry/stone/__init__.py` | Deliberately **non-eager** (imports nothing) — prevents a real circular import, see below. |
| `backend/jewelmind/geometry/stone/outline.py` | 7 pure 2D outline primitives → closed `cq.Wire`. Holds `_EMERALD_CORNER_CLIP_RATIO`, `_CUSHION_CORNER_RATIO`, `_COS_45`. |
| `backend/jewelmind/geometry/stone/builder.py` | `build_stone()` dispatch, `_build_round_stone()`, `_build_non_round_stone()`, `_apply_orientation()`, `_NON_ROUND_OUTLINE_BUILDERS`. Holds the shared reference proportions. |
| `backend/jewelmind/geometry/stone/capability.py` | `STONE_SHAPE_CAPABILITIES`, `get_stone_shape_capability()`, `REFERENCE_GEOMETRY_VERSION`. |
| `backend/jewelmind/geometry/stone/errors.py` | `StoneShapeUnsupportedError`, `StoneGenerationError`. |
| `backend/tests/test_stone.py` | 92 tests — generation, dimensions, orientation, asymmetry, inspection, export, assembly, Forge scoping. |
| `backend/tests/test_stone_schemas.py` | 18 tests — schema/example/vector/registry validation and live re-derivation. |
| `backend/tests/test_stone_system_no_ring_dependency.py` | 8 tests — AST-based architecture proof (STONE-GOV-001). |

### Modified this Sprint

| File | Change |
|---|---|
| `domain/schema.py` | `StoneShape` widened to 7 members; `StoneSpec` gained `length`/`width`/`orientation`, `diameter` → `float \| None`, plus a `@model_validator`. |
| `geometry/components/stone.py` | Reduced to a thin re-export of `build_stone`. |
| `geometry/constants.py` | `prong_center_radius()` now reads `resolved_width_mm()` instead of `stone.diameter`. |
| `geometry/inspection/models.py` | `FactType` gained the 6 `STONE_*` values. |
| `geometry/inspection/inspector.py` | New `_stone_dimension_facts()`, called for `stone_reference` only. |
| `validation/engine.py` | `JM-STONE-001`/`JM-PRONG-003` scoped `ROUND_ONLY`; `JM-STONE-002` generalized. |
| `exporters/specification.py` | Round prints Diameter; non-round prints Length/Width/Orientation. |
| `designer/normalizer.py` | `STONE_SHAPE_SYNONYMS` for all 7 shapes (IT+EN); `_NUMERIC_FIELDS` gained the new paths. |
| `designer/capability.py` | 6 stale `KNOWN_UNSUPPORTED_CONCEPTS` entries removed; `KNOWN_JDL_FIELD_PATHS` extended. |
| `designer/prompts.py` | Field list documents the shape/dimension relationship. |
| `shared/types/jewelry-definition.ts` | Mirrored types, `STONE_SHAPES`, new `isValidStone()`. |
| `shared/validation/engine.ts` | Mirrored Forge scoping (FORGE-GOV-004). |
| `frontend/src/components/ConfigurationPanel.tsx` | Shape selector + conditional dimension fields + orientation. |
| `tests/test_geometry_inspection_schemas.py` | Registry count assertion replaced with a live-`FactType`-derived one. |

### Unchanged, deliberately

`geometry/assemblies/solitaire.py`, `geometry/components/prongs.py`, `geometry/components/basket.py`, `geometry/connection.py`, `preview/mesh.py`, `services/model_service.py`, `api/routes.py`, `ring/models.py`, `ring/adapter.py`, and all of `frontend/src/vision/`. Each consumes stone data only through interfaces that already generalized — which is why no change was needed.

## Forge rule classification

| Rule ID | Name | Classification | Rationale |
|---|---|---|---|
| `JM-STONE-001` | `STONE_DIAMETER_RANGE` (2–15 mm) | **ROUND_ONLY** | Only round has a `diameter`. Guarded by `if d.stone.shape == "round"`. |
| `JM-STONE-002` | `STONE_DEPTH_RANGE` | **SHARED** | Genuinely generalized: `depth < diameter` → `depth < min(resolved_length, resolved_width)`. A structural fact (depth must not exceed the stone's own footprint), true for every shape. |
| `JM-PRONG-003` | `PRONG_COUNT_VS_STONE_SIZE` (> 8 mm + 4 prongs) | **ROUND_ONLY** / REQUIRES_RULE_EVOLUTION | The 8 mm threshold was calibrated against a round diameter. Generalizing needs justification this Sprint does not have. |
| `JM-GEOMETRY-001` | non-positive dimension | SHARED | Reads band dimensions; unaffected by stone shape. |

`JM-STONE-002`'s generalization deserves the distinction spelled out, because it is the one rule that *did* change semantics. It is **not** a fake equivalent diameter. The old form compared depth against `diameter`, which for a circle *is* the minimum horizontal extent. The new form compares against the real minimum horizontal extent, which for a circle is still `diameter`. Round's behaviour is therefore bit-identical, and the rule now expresses the actual geometric invariant it always meant.

### No fake equivalent diameter — count: 0

An `oval 8 × 6` is never collapsed to `diameter = 7`. Verified by real tests:

- `TestForgeRoundRuleScope::test_stone_diameter_range_never_fires_for_non_round` — an oval at 100 × 100 (which would grossly violate the 2–15 mm range if the rule were misapplied) produces no `JM-STONE-001`.
- `TestForgeRoundRuleScope::test_prong_count_vs_stone_size_never_fires_for_non_round` — an oval at 20 × 20 with 4 prongs produces no `JM-PRONG-003`.
- `TestForgeRoundRuleScope::test_stone_depth_range_fires_for_non_round_using_real_minimum_extent` — an oval 8 × 6 with depth 6.5 correctly errors, because 6.5 > min(8, 6).

## `stone.diameter` code audit

Every remaining reference, classified:

| Location | Classification |
|---|---|
| `stone_dimensions.py` (×4) | **ROUND-SPECIFIC VALID** — this *is* the resolution point; reads are inside a `shape == "round"` branch with an assert documenting the validator's guarantee. |
| `validation/engine.py` (×4) | **ROUND-SPECIFIC VALID** — all inside `shape == "round"` guards. |
| `shared/validation/engine.ts` (×5) | **ROUND-SPECIFIC VALID** — the identical mirror. |
| `geometry/stone/builder.py::_build_round_stone` (×4) | **ROUND-SPECIFIC VALID** — only reachable for round. |
| `exporters/specification.py:60` | **ROUND-SPECIFIC VALID** — inside the `if shape == "round"` branch. |
| `designer/capability.py`, `normalizer.py`, `prompts.py` | **ROUND-SPECIFIC VALID** — these are *field-path strings*, not value reads. `stone.diameter` remains a real, proposable JDL path. |
| `frontend/ConfigurationPanel.tsx` (×3) | **ROUND-SPECIFIC VALID** — guarded by the shape conditional and defensively `?? 6.5`. |
| `geometry/constants.py:58` | **ROUND-SPECIFIC VALID** — a docstring mention explaining why the code no longer reads it. |

**Architectural leaks found and fixed: 1.** `geometry/constants.py::prong_center_radius()` read `stone.diameter / 2` unconditionally, which would have raised `TypeError` on `None / 2` for every non-round stone. Now reads `resolved_width_mm()`. This was the one genuine leak — a supposedly shape-agnostic construction helper assuming round.

**Architectural leaks remaining: 0.** No unguarded `stone.diameter` value read exists outside the round-only paths above.

## The real circular import

`geometry/constants.py` needs `resolved_width_mm`; `geometry/stone/builder.py` needs `band_top_z` from `geometry/constants.py`. An eager `from ...builder import build_stone` in `geometry/stone/__init__.py` closed the loop:

```
ImportError: cannot import name 'band_top_z' from partially initialized module
jewelmind.geometry.constants (most likely due to a circular import)
```

Fixed by making `geometry/stone/__init__.py` non-eager; its docstring records why so the "missing" convenience re-export is not restored. Verified from 6 independent fresh-process entry points (`jewelmind.geometry.stone`, `jewelmind.geometry.constants`, `jewelmind.ring`, `jewelmind.jewelry_category`, `jewelmind.geometry.components.stone`, `jewelmind.api.app`).

Same class as Sprint 17's finding, different cause: Sprint 17's was a **layer** violation (a module in the wrong package); this was an **eager-package-init** violation with layers already correct. See [`561-stone-architecture-overview.md`](561-stone-architecture-overview.md).

## Honest remaining gaps

| Gap | Status | Why not closed this Sprint |
|---|---|---|
| **No dimension-range rule for non-round `length`/`width`** | REQUIRES_RULE_EVOLUTION | Nothing analogous to `JM-STONE-001`'s 2–15 mm bound applies to a non-round stone. Inventing bounds would be a fabricated professional threshold (STONE-GOV-010). Needs a real sourced range and a Forge rule version bump. |
| **`JM-PRONG-003` not generalized** | REQUIRES_RULE_EVOLUTION | The 8 mm threshold has no defensible non-round analogue without an equivalent-size metric, which needs its own domain semantics. |
| **Prong placement is not shape-aware** | Sprint 19 | The generic circular layout leaves marquise/pear tips and angular-stone corners unsupported. Honestly recorded as `EXPERIMENTAL` per shape. |
| **Measured dimensions are not orientation-aware** | Open | `STONE_MEASURED_LENGTH`/`WIDTH` read an axis-aligned bounding box, so they isolate length from width exactly only at `orientation == 0`. See [`574-stone-inspection-contract.md`](574-stone-inspection-contract.md). |
| **Golden snapshots do not capture centroid offset** | Accepted | A silently symmetrized shape preserving volume and extents would pass Golden verification; covered instead by `TestPearAsymmetry`. |
| **No `FACETED_GEM_MODEL` / `MEASURED_STONE`** | Future, ADR required | Explicitly out of scope. |
| **Pear outline is non-tangent** | Accepted limitation | Robust and deterministic; a tangent-continuous variant needs spline fitting with no reference-usefulness gain. |
| **`definitionHash` drift on additive change** | Documented tension | Recurs on every additive schema change; see [`576-current-round-migration.md`](576-current-round-migration.md). |
| **No Studio control for stone orientation on round** | Deliberate | Orientation is geometrically inert for a `RADIAL` shape, so the field is hidden for round. |

## Layer-boundary audit

| Boundary | Status |
|---|---|
| Stone → Ring | **Clean.** Zero imports, AST-verified. |
| Stone → Forge | **Clean.** No `jewelmind.validation` import anywhere under `geometry/stone/`. |
| Forge → Stone geometry | **Clean.** Forge imports only `domain/stone_dimensions.py`, never `geometry/stone/`. |
| Atlas → Forge | **Clean.** Unchanged. |
| Stone → Setting | **Clean.** No prong/basket/bezel concept in Stone System. |
| Frontend → shape-specific geometry | **Clean.** No shape-specific mesh code; Vision is generic. |
