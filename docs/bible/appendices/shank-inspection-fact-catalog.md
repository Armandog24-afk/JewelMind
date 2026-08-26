---
id: JM-BIBLE-A112
title: "Appendix: Shank Inspection Fact Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-SHANK-README
  - JM-BIBLE-540
  - JM-BIBLE-460
related_documents:
  - JM-BIBLE-A93
implementation_status: partial
professional_validation: not_required
normative: true
---

# Appendix: Shank Inspection Fact Catalog

What is actually observable about a generated Shank (the `band` component) today, cross-checked against `specs/geometry-inspection/v2/fact-registry.json` and `backend/jewelmind/geometry/inspection/`. This appendix distinguishes two categories, per SHANK-GOV-013/INSPECT-GOV-001: **MEASURED_GEOMETRY** (independently re-derived from the real solid by `geometry/inspection/`) and **CONSTRUCTION_PARAMETER** (a value the builder itself computed while constructing the solid, reported as metadata but never independently re-measured).

## MEASURED_GEOMETRY — generic component-level facts (from `geometry/inspection/`)

These are the same generic `FactType` entries every component gets — `geometry/inspection/` has no Shank-specific code path and does not know "band" is a shank. They apply to a tapered `band` exactly as they apply to a uniform one.

| Fact | `FactType` | Scope | Meaning for `band` |
|---|---|---|---|
| Shape exists | `SHAPE_EXISTS` | COMPONENT | Whether `build_shank()` produced at least one solid. |
| Shape valid | `SHAPE_VALID` | COMPONENT | OpenCascade's `BRepCheck_Analyzer` validity check on the resulting `band` shape. |
| Solid count | `SOLID_COUNT` | COMPONENT | Number of top-level solids — always 1 for both uniform and tapered `band` (`ShankConstructionError` is raised, not swallowed, if a loft produces more than one or zero). |
| Volume | `VOLUME` | COMPONENT | `band.volume_mm3` — the real `Shape.Volume` of the revolved or lofted solid. |
| Bounding box | `BOUNDING_BOX` | COMPONENT | Axis-aligned min/max/size/center from `Shape.BoundingBox()` — for a tapered shank this still reflects the true head dimensions, since `TOWARD_BOTTOM` never reduces the head (SHANK-GOV-011). |
| Connectivity | `CONNECTED`/`DISCONNECTED` | ASSEMBLY | Whether `band` stays part of one connected production-metal group with `prongs`/`basket_support` — verified for tapered shanks by `backend/tests/test_shank.py::TestHeadConnection`/`TestShankConnectivity`. |
| Stone/metal separation | `STONE_METAL_SEPARATE` | ASSEMBLY | Structural check that `stone_reference` was never an argument to a production-metal fuse call — unaffected by taper, since no code in `geometry/shank/` ever touches stone geometry. |

## CONSTRUCTION_PARAMETER — Shank-specific metadata (from `geometry/shank/builder.py`)

These fields live only in `GeneratedComponent.metadata` for `band`. They are computed from the exact same `taper_ratio()` function used to build the loft's section wires — not an independent second measurement of the solid — and are labeled as such here per SHANK-GOV-013.

| Field | Type | Present on | Meaning |
|---|---|---|---|
| `profile` | string | both | `"flat"` or `"comfort_fit"` — echoes `definition.band.profile`. |
| `innerRadiusMm` / `outerRadiusMm` | number | both | The resolved base radii used to build the profile — a construction input, not a re-measurement. |
| `filletApplied` | boolean | both | Whether the outer-rim fillet was actually applied (uniform path only — always `false` on the tapered path). |
| `filletSkippedReason` | string | tapered only | Explicit reason the fillet step was skipped — `"Outer-rim fillet is not yet implemented for a tapered shank (v1 limitation)."` |
| `variation` | string | both | `"UNIFORM"` or `"TAPERED"` — which construction path ran. |
| `widthTaperMode` / `thicknessTaperMode` | string | both | Echoes the requested taper mode. |
| `widthTaperBottomRatio` / `thicknessTaperBottomRatio` | number | tapered only | Echoes the requested `bottomRatio`. |
| `sectionCount` | integer | both | `1` for uniform (revolve), `SECTION_COUNT` (48) for tapered (loft). |
| `widthSamplesMm.headMm` / `widthSamplesMm.bottomMm` | number | tapered only | `base_half_width * 2 * taper_ratio(u, widthTaper)` evaluated at `u=0.0` and `u=0.5` — a construction-time sample of the same function used to build the loft, not an independent re-measurement of the resulting solid. |
| `thicknessSamplesMm.headMm` / `thicknessSamplesMm.bottomMm` | number | tapered only | Same construction as `widthSamplesMm`, for thickness. |
| `connectionInterface.{topZMm,embedMm,headCenterRadiusMm}` | object | both | Echoes `ShankConnectionInterface` — the Shank → RingHead handoff, identical for every taper configuration (SHANK-GOV-011). |

## The real, honest gap

**There is currently no dedicated per-`u` Shank `FactType` in `geometry/inspection/`.** `specs/geometry-inspection/v2/fact-registry.json` (Sprint 14) has no entry for a longitudinal width/thickness sample at an arbitrary angular position, and no code under `geometry/inspection/` reads `geometry/shank/` internals or re-samples the tapered solid's actual cross-section at a given `u`. What `widthSamplesMm`/`thicknessSamplesMm` report is exactly what the builder used to construct the loft — never a second, independent geometric re-measurement of the finished solid at that position. Adding a genuine per-`u` measured fact (e.g. re-slicing the actual solid at a given angle and re-deriving its cross-sectional width) is unimplemented and would require a new `FactType`, a new fact-registry entry, and a new test — it is not silently claimed here or anywhere else in this Sprint's code or specs.

## Cross-references

- `specs/geometry-inspection/v2/fact-registry.json` — the 16 generic facts this appendix's MEASURED_GEOMETRY section draws from; unmodified this Sprint.
- [`553-shank-inspection-contract.md`](../19-shank/553-shank-inspection-contract.md) — full narrative contract.
- [`inspection-type-catalog.md`](inspection-type-catalog.md) — the general Inspection module/status/intersection catalog this appendix does not duplicate.
- [`494-current-runtime-inspection-gap-analysis.md`](../16-geometry-inspection/494-current-runtime-inspection-gap-analysis.md) — the pre-existing gap-analysis document a future per-`u` Shank fact would extend.
