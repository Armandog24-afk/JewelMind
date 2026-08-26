---
id: JM-BIBLE-478
title: Boolean Result Inspection
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-INSPECTION-README
  - JM-BIBLE-460
related_documents:
  - JM-BIBLE-479
  - JM-BIBLE-465
  - JM-BIBLE-473
implementation_status: current
professional_validation: not_required
normative: true
---

# Boolean Result Inspection

## `BooleanOperationResult`

```python
class BooleanOperationResult(InspectionModel):
    operation: Literal["FUSE", "CUT", "COMMON"]
    inputComponentIds: list[str]
    outputComponentId: str
    succeeded: bool
    fallbackUsed: bool
    outputSolidCount: int | None = None
    outputVolumeMm3: float | None = None
    note: str = ""
```

Populated by `assembly.py::_boolean_operations()` (`backend/jewelmind/geometry/inspection/assembly.py:94-131`), included in `AssemblyInspectionResult.booleanOperations` (a list, currently 4 entries for the default solitaire).

## The 4 real operations tracked

| `outputComponentId` | `operation` | Real construction |
|---|---|---|
| `band` | `FUSE` | The band's outer-rim fillet — `_try_fillet_outer_rim()` in `geometry/components/band.py`. Labeled `FUSE` by `_boolean_operations()`'s own conditional (`"FUSE" if name == "band" else ...`), even though the underlying operation is a `.fillet()` call, not a `.fuse()` call — see "A labeling note" below. |
| `basket_support` | `CUT` | `outer.cut(inner)` in `geometry/components/basket.py` — a real boolean subtraction. |
| `prongs` | `FUSE` | Labeled `FUSE`, though `build_prongs()` never calls `.fuse()` at all — it builds independent solids and merges them via `cq.Compound.makeCompound()`, which is not a boolean operation. See "A labeling note" below. |
| `combined_metal` | `FUSE` | The real `band.shape.fuse(basket.shape).fuse(prongs.shape)` call in `solitaire.py::_fuse_metal()`. `inputComponentIds=["band", "prongs", "basket_support"]`. |

## A labeling note, stated honestly

For `band` and `prongs`, `_boolean_operations()`'s `operation` field is set by a fixed conditional (`"FUSE" if name == "band" else "CUT" if name == "basket_support" else "FUSE"`) rather than by inspecting what kernel operation the component's own builder actually performed. This means the per-component entries for `band` and `prongs` describe **whether that component's own construction reported a fallback** (via `comp.fallbackUsed`, itself derived from `component.warnings`), not a literal record of a specific boolean-fuse call for that individual component — `prongs`, in particular, never performs any boolean operation of its own (see [`475-prong-count-and-identity-inspection.md`](475-prong-count-and-identity-inspection.md)'s "one compound, not N components" finding: `cq.Compound.makeCompound()` is a topological grouping operation, not `.fuse()`). Only `basket_support`'s `CUT` and `combined_metal`'s `FUSE` describe a real, specific boolean kernel call. This is a real, current simplification in how `_boolean_operations()` labels its per-component entries, not a fabricated result — every other field (`succeeded`, `fallbackUsed`, `outputSolidCount`, `outputVolumeMm3`, `note`) is a genuine measurement regardless of the `operation` label's precision.

## `combined_metal`'s `fallbackUsed` derivation

Unlike the per-component entries (which read `comp.fallbackUsed`, itself `bool(component.warnings)`), the `combined_metal` entry derives `fallbackUsed` from an independent, real geometric signal:

```python
combined_solids, combined_valid, _ = inspect_topology(model.combined_metal)
...
fallbackUsed=combined_solids is not None and combined_solids.solids > 1,
```

`combined_solids.solids > 1` means the real fused shape has more than one top-level solid — the actual geometric consequence of `_fuse_metal()`'s own fallback path (`geometry/assemblies/solitaire.py::_fuse_metal()`), which returns `cq.Compound.makeCompound([band.shape, basket.shape, prongs.shape])` (3 separate solids) when the real `.fuse()` calls raise or produce zero solids. This is a re-derivation from the shape itself, not a read of `solitaire.py`'s own `fuse_warnings` list — the two signals would normally agree (a fuse failure that appends a warning also necessarily leaves `combined_metal` with more than 1 solid), but `_boolean_operations()` deliberately measures the geometric consequence directly rather than trusting the warning text.

## Real current finding: no fallback fired for the default solitaire

Verified directly by running the pipeline: `combined_metal.Solids()` has length **1** for the default solitaire — the real `.fuse()` chain succeeded, `fallbackUsed=False` for `combined_metal`. The band's own fillet also succeeded (`filletApplied: true` in its `metadata`), so `fallbackUsed=False` for `band` too. None of the 4 `BooleanOperationResult` entries report a fallback for the default solitaire.

## The `note` field's real behavior

For the 3 per-component entries (`band`, `basket_support`, `prongs`):

```python
note="; ".join(model.components[name].warnings) if model.components[name].warnings else ""
```

— a direct join of that component's own real `warnings` list, empty string when there are none. For `combined_metal`, `note` is instead a fixed explanatory sentence ("More than 1 top-level solid ... means the boolean union fell back to an unfused compound.") when `combined_solids.solids > 1`, else empty string — not a join of `solitaire.py`'s `fuse_warnings`, even though that list also exists and is folded into `GeneratedModel.warnings` separately.

## Tests

`backend/tests/test_geometry_inspection.py::TestFallbackInspection` — `test_band_fillet_fallback_state_is_visible_via_metadata` and `test_combined_metal_multi_solid_is_detectable_as_a_fallback_signal`.

## Cross-references

- [`479-fallback-result-inspection.md`](479-fallback-result-inspection.md) — how this Sprint's structured `fallbackUsed` field relates to the pre-existing free-text warning convention.
- [`07-atlas/134-boolean-operation-strategy.md`](../07-atlas/134-boolean-operation-strategy.md) — the real boolean-operation strategy this inspection observes.
- [`appendices/atlas-fallback-register.md`](../appendices/atlas-fallback-register.md) — `ATLAS-FALLBACK-001`/`002`, the two real fallback paths tracked here.
