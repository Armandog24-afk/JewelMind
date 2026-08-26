---
id: JM-BIBLE-464
title: Component Inspection Contract
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
  - JM-BIBLE-463
  - JM-BIBLE-466
  - JM-BIBLE-467
  - JM-BIBLE-468
  - JM-BIBLE-469
  - JM-BIBLE-130
implementation_status: current
professional_validation: not_required
normative: true
---

# Component Inspection Contract

The normative function is `backend/jewelmind/geometry/inspection/components.py::inspect_component(name: str, component: GeneratedComponent) -> ComponentInspectionResult`.

## Step by step, exactly as the code runs

1. **Existence.** `exists = bool(shape.Solids())`. If `False`, the function returns immediately: `status="FAIL"`, `solidCount=0`, `volumeMm3=0.0`, `fallbackUsed=bool(component.warnings)`, `metadata=dict(component.metadata)` (still carried forward even for a missing component), and a single `INSPECTION_COMPONENT_MISSING` diagnostic (`severity="warning"`).
2. **Bounding box.** `bounding_box_fact(shape)` is called inside a `try`/`except Exception`. On failure, `bbox = None` and an `INSPECTION_BOUNDING_BOX_FAILED` diagnostic (`severity="error"`) is appended — this is the one diagnostic in this function that can flip the component's overall `status` to `FAIL` on its own.
3. **Topology.** `inspect_topology(shape)` returns `(counts, valid, topology_status)`. If `topology_status == "ERROR"`, an `INSPECTION_TOPOLOGY_FAILED` diagnostic (`severity="error"`) is appended. `counts` supplies `solidCount`/`TopologyCounts`; `valid` supplies `shapeValid`.
4. **Volume.** `volume = component.volume_mm3` (already computed by the geometry builder — this function never recomputes it). `volume_ok = volume is not None and volume >= 0.0 and volume == volume` — the `volume == volume` clause is a self-equality NaN check (`NaN != NaN` in IEEE 754, so this is `False` only for NaN). If not `volume_ok`, an `INSPECTION_VOLUME_FAILED` diagnostic (`severity="error"`) is appended.
5. **Status.** `status = "FAIL" if any(d.severity == "error" for d in diagnostics) else "PASS"` — a component with only warning-level diagnostics (or none) is `PASS`.
6. **Metadata and fallback.** `metadata=dict(component.metadata)` — the real, unmodified metadata dict from the geometry builder, copied (not referenced) so a caller mutating the result can never corrupt the original. `fallbackUsed=bool(component.warnings)` — this function never inspects the *content* of `warnings`, only whether the list is non-empty; a component with any warning at all is reported as having used a fallback path.

## `shapeType`

`shape.ShapeType() if hasattr(shape, "ShapeType") else None` — a defensive `hasattr` check, since `shape` is typed as `cq.Shape` but in practice `GeneratedComponent.shape` can hold a `cq.Compound` (e.g. `prongs`) which also implements `ShapeType()`, so in current code this branch always resolves; the `hasattr` guard exists for robustness against a future component type that might not.

## Real metadata carried forward, per component

`inspect_component()` never special-cases a component by name — every one of the 4 current components (`band`, `stone_reference`, `prongs`, `basket_support`) goes through the exact same 5 steps above. What differs is only the real, pre-existing `metadata` dict each builder already attaches, which this function copies through unmodified:

| Component | Real metadata keys (from the builder) |
|---|---|
| `band` (`geometry/components/band.py`) | `filletApplied` (boolean — `not fallback_used` at construction time). |
| `prongs` (`geometry/components/prongs.py`) | `requestedCount`, `generatedCount`, `prongRadiusMm`, `centerRadiusMm`, `positions` (a list of `{x, y}` dicts, one per generated prong). |
| `basket_support` (`geometry/components/basket.py`) | `outerRadiusMm`, `innerRadiusMm` (plus other builder-specific keys). |
| `stone_reference` (`geometry/components/stone.py`) | `isGemologicalReproduction: False` — an explicit, deliberate statement that the stone reference is a CAD placeholder, never a gemologically accurate reproduction. |

No inspection-specific logic reads or interprets any of these keys except `prongs`' `requestedCount`/`generatedCount`, which `assembly.py::_prong_count()` reads at the assembly level (see [`465-assembly-inspection-contract.md`](465-assembly-inspection-contract.md)) — `inspect_component()` itself treats `metadata` as opaque pass-through data.

## Cross-references

The three sub-checks this function orchestrates each have their own dedicated document: [`466-shape-validity-inspection.md`](466-shape-validity-inspection.md) (`shapeValid`), [`467-solid-count-inspection.md`](467-solid-count-inspection.md) (`solidCount`), [`468-volume-inspection.md`](468-volume-inspection.md) (`volumeMm3`), [`469-bounding-box-inspection.md`](469-bounding-box-inspection.md) (`boundingBox`). The Atlas-level component-field mapping this function's output feeds is [`07-atlas/130-component-contract.md`](../07-atlas/130-component-contract.md), whose `inspectionResults` row is marked `PLANNED` — this Sprint's `ComponentInspectionResult` is exactly that field's real, current shape, not yet cross-linked back into the Atlas component schema itself (a genuine documentation-wiring gap left for a future pass, not this Sprint's scope).

`backend/tests/test_geometry_inspection.py::TestComponentExistsInspection`, `TestComponentVolumeInspection`, and `TestComponentBoundingBox` exercise this function directly against the real solitaire.
