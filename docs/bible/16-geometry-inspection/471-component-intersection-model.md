---
id: JM-BIBLE-471
title: Component Intersection Model
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
  - JM-BIBLE-465
  - JM-BIBLE-470
  - JM-BIBLE-472
implementation_status: current
professional_validation: not_required
normative: true
---

# Component Intersection Model

## The real algorithm

`intersection.py::inspect_intersection(name_a, shape_a, name_b, shape_b, *, known_separated=False) -> IntersectionResult`. If `known_separated=True`, the function returns immediately with `status="NO_INTERSECTION"`, `intersectionVolumeMm3=0.0`, `intersectionSolidCount=0`, and a note stating the boolean-common call was skipped because a prior distance measurement already proved separation. Otherwise it calls `shape_a.intersect(shape_b)` — CadQuery's wrapper around OCP's `BRepAlgoAPI_Common` — inside a `try`/`except Exception`.

On a kernel exception, the result is `status="UNKNOWN"` (never a guessed `PASS`/`FAIL`, per INSPECT-GOV-006). On success:

```python
solids = result.Solids()
volume = result.Volume() if solids else 0.0
if not solids or volume <= CONTACT_TOLERANCE_MM:
    status = "NO_INTERSECTION" if not solids else "TOUCHES"
else:
    status = "INTERSECTS"
```

So the classification is three-way, not binary: **`NO_INTERSECTION`** (the boolean-common produced zero solids — the shapes truly do not overlap), **`TOUCHES`** (the boolean-common produced at least one solid, but its volume is at or below `CONTACT_TOLERANCE_MM` — a surface-level contact with no real enclosed volume), and **`INTERSECTS`** (a positive result volume above tolerance — genuine 3D overlap). `UNKNOWN` covers a kernel-level failure to compute the boolean at all.

## `should_skip_intersection()` — broad-phase elimination

```python
def should_skip_intersection(min_distance_mm: float | None, tolerance: float = CONTACT_TOLERANCE_MM) -> bool:
    return min_distance_mm is not None and min_distance_mm > tolerance
```

`assembly.py::inspect_assembly()` looks up each pair's already-computed `DistanceResult` before running its intersection check; if the distance alone already proves the pair is separated beyond `CONTACT_TOLERANCE_MM`, `inspect_intersection()` is called with `known_separated=True` and the expensive `Shape.intersect()` call is skipped entirely. This is exactly what happens for `band`↔`stone_reference` in the real default solitaire: their measured distance is 0.9mm, well above the 1e-6mm tolerance, so `intersect()` is never invoked for that pair — a real, measured time saving, not a theoretical one (see [`484-inspection-performance-model.md`](484-inspection-performance-model.md) for the timing breakdown).

## The brief's own warning, stated explicitly

A zero or near-zero intersection volume is **not** automatically "no geometric relationship." Two shapes that merely touch at a surface can report `distance() == 0` while their boolean-common volume is zero or near-zero — this is exactly why `TOUCHES` exists as a status distinct from `NO_INTERSECTION`, rather than collapsing both into one "not intersecting" bucket. `intersection.py`'s own module docstring states this directly: "Zero intersection volume does not by itself mean 'no geometric relationship' — two shapes that merely touch at a surface can report a positive `distance()` of exactly 0 with a near-zero or zero boolean common volume."

## Real pairwise intersection volumes, default solitaire

| Pair | Intersection volume (mm³) | Status |
|---|---|---|
| `band` ↔ `basket_support` | 0.117 | `INTERSECTS` |
| `basket_support` ↔ `prongs` | 22.24 | `INTERSECTS` |
| `prongs` ↔ `stone_reference` | 2.10 | `INTERSECTS` |
| `band` ↔ `stone_reference` | 0.0 | `NO_INTERSECTION` (distance 0.9mm — broad-phase skipped) |
| `basket_support` ↔ `stone_reference` | 3.62 | `INTERSECTS` |
| `band` ↔ `prongs` | 0.022 | `INTERSECTS` |

Five of the six pairs genuinely overlap by real, positive volume — a direct consequence of `EMBED_MM = 0.4` (`geometry/constants.py`), which deliberately embeds each part's base 0.4mm into whatever it attaches to, specifically so booleans see real 3D overlap rather than a zero-volume tangent touch that OpenCascade would otherwise leave unfused. `stone_reference` intersecting `prongs` and `basket_support` is expected physical grip realism, never evidence that the stone was fused into production metal (see [`473-production-metal-integrity.md`](473-production-metal-integrity.md) and `assembly.py::_stone_metal_separation()`).

## Cross-references

[`470-component-connectivity-model.md`](470-component-connectivity-model.md) for how a pair's distance (not intersection) determines connectivity; [`472-component-distance-model.md`](472-component-distance-model.md) for the cheaper primitive this module's broad-phase elimination depends on; [`484-inspection-performance-model.md`](484-inspection-performance-model.md) for the real timing comparison between distance and intersection. `backend/tests/test_geometry_inspection.py::TestComponentIntersection` (real solitaire pairs) and `TestIntersectingFixture` (a synthetic overlapping-boxes fixture) exercise this directly.
