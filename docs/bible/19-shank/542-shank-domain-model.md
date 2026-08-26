---
id: JM-BIBLE-542
title: Shank Domain Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-SHANK-README
  - JM-BIBLE-540
  - JM-BIBLE-541
related_documents:
  - JM-BIBLE-526
  - JM-BIBLE-RING-README
implementation_status: current
professional_validation: not_required
normative: true
---

# Shank Domain Model

## What a Shank is

A Shank is the metal body of a ring's band: one closed solid, produced by revolving or lofting a 2D cross-section around the ring's circumference. It is ring-specific geometry — the concept has no meaning outside the Ring jewelry category — and it is exactly one component on the generated assembly, named `"band"` (SHANK-GOV-002, `geometry/shank/builder.py::build_shank()`'s `GeneratedComponent(name="band", ...)`). "Shank" is JewelMind's internal architectural name for this geometry subsystem; nothing about the concept is new to Sprint 17 — a single-file uniform-only version of the same solid existed since Sprint 5's Atlas foundation (`geometry/components/band.py`). What Sprint 17 changed is how that solid is built and what shapes it can now take, not what it represents.

## Relationship to `BandSpec` / `BandTaperSpec`

`domain/schema.py::BandSpec` is the JDL-facing input a Shank is built from:

```python
class BandSpec(StrictModel):
    width: float = Field(default=2.4, allow_inf_nan=False)
    thickness: float = Field(default=1.8, allow_inf_nan=False)
    profile: BandProfile = "comfort_fit"
    widthTaper: BandTaperSpec = Field(default_factory=BandTaperSpec)
    thicknessTaper: BandTaperSpec = Field(default_factory=BandTaperSpec)
```

`width`/`thickness`/`profile` are unchanged from before this Sprint. `widthTaper`/`thicknessTaper` are new, each a `BandTaperSpec`:

```python
class BandTaperSpec(StrictModel):
    mode: BandTaperMode = "NONE"          # Literal["NONE", "TOWARD_BOTTOM"]
    bottomRatio: float = Field(default=1.0, gt=0, le=1, allow_inf_nan=False)
```

`build_shank()` reads exactly these five `BandSpec` fields, plus `ring.innerDiameter` (via `geometry/constants.py::inner_radius()`/`outer_radius()`) for the metal's radial extent. No other JDL field feeds Shank construction. This is documented in full detail in [`546-width-function-model.md`](546-width-function-model.md), [`547-thickness-function-model.md`](547-thickness-function-model.md), and [`548-taper-model.md`](548-taper-model.md).

## The two real metadata shapes

`build_shank()` dispatches deterministically (SHANK-GOV-001) on whether either taper is requested, and returns a `GeneratedComponent` whose `metadata` dict takes one of two distinct, non-overlapping shapes — both documented exactly in [`specs/shank/v1/shank-definition.schema.json`](../../../specs/shank/v1/shank-definition.schema.json):

**`UNIFORM`** (`widthTaper.mode == "NONE" and thicknessTaper.mode == "NONE"`): `profile`, `innerRadiusMm`, `outerRadiusMm`, `filletApplied`, `variation: "UNIFORM"`, `widthTaperMode: "NONE"`, `thicknessTaperMode: "NONE"`, `sectionCount: 1`, `connectionInterface`.

**`TAPERED`** (either taper mode is not `"NONE"`): the same base fields, plus `filletApplied: false` with a `filletSkippedReason` string, `widthTaperMode`/`widthTaperBottomRatio`, `thicknessTaperMode`/`thicknessTaperBottomRatio`, `sectionCount: 48`, and `widthSamplesMm`/`thicknessSamplesMm` (each `{headMm, bottomMm}`).

Both shapes carry `connectionInterface` (`topZMm`/`embedMm`/`headCenterRadiusMm`, read from `shank_connection_interface(definition)` — see [`550-head-connection-interface.md`](550-head-connection-interface.md)), because that handoff is identical regardless of construction path (SHANK-GOV-010/011). Which shape a given `GeneratedComponent` carries is fully determined by `variation`; nothing about the component's name, identity, or place in the assembly changes between the two.

The `widthSamplesMm`/`thicknessSamplesMm` values are computed from the same `taper_ratio()` calls the loft itself used to build each section wire — they are CONSTRUCTION_PARAMETER facts, not an independent re-measurement of the resulting solid's actual geometry (SHANK-GOV-013). Any downstream reader (Forge, Inspection, a future Studio panel) that needs a measured width/thickness fact rather than a construction input must derive it from the solid itself, not read these fields as if they were.

## How this differs from Ring Architecture v2's `ShankDefinition`

`jewelmind.ring.models.ShankDefinition` (Sprint 16, see [`18-ring-architecture/526-shank-contract.md`](../18-ring-architecture/526-shank-contract.md)) is a different kind of object with a name that deliberately overlaps: it is a thin, 1:1 data-mapping model — `profile`, `widthMm`, `thicknessMm`, `widthTaper`, `thicknessTaper` — produced by `ring_definition_from_jdl()` directly from `JewelryDefinition.band`. It does not build geometry, does not call CadQuery, and does not know about `SECTION_COUNT`, loft, revolve, or any of the two metadata shapes above. It exists so Ring-domain code can read band parameters through a Ring-typed model instead of the raw JDL schema, one layer above where any geometry actually happens.

The geometry subsystem documented in this Sprint 17 section (`geometry/shank/`, `build_shank()`, the two `GeneratedComponent` metadata shapes) is the authoritative source of the real solid, its volume, its bounding box, and its construction metadata. `526-shank-contract.md` was updated this Sprint to point here rather than be rewritten to restate this content — it now records only how `ring.models.ShankDefinition`'s fields map from `BandSpec`, not how geometry is actually built.

## What a Shank is not

A Shank is not the stone, not the prong/basket assembly, and not the whole ring. It is exactly the band's metal body — one `GeneratedComponent` named `"band"` among the assembly's other components (`stone_reference`, `prongs`, `basket_support`). Nothing in this Sprint changed which components exist or how they combine; see [`07-atlas/131-assembly-contract.md`](../07-atlas/131-assembly-contract.md) for the unchanged assembly-level contract.
