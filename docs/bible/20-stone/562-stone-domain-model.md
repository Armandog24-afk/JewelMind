---
id: JM-BIBLE-562
title: Stone Domain Model
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
  - JM-BIBLE-563
  - JM-BIBLE-529
implementation_status: current
professional_validation: not_required
normative: true
---

# Stone Domain Model

## StoneDefinition — the public input

Conceptually a `StoneDefinition` answers four questions and nothing else:

| Concept | Real field(s) | Notes |
|---|---|---|
| **Shape** | `stone.shape` | One of 7 closed enum values; selects a construction strategy. |
| **Dimensions** | `stone.diameter` (round) or `stone.length` + `stone.width` (every other shape), plus `stone.depth` | Independent quantities, never derived from the shape name. |
| **Orientation** | `stone.orientation` | Degrees around the stone's own local vertical axis. Default `0.0`. |
| **ReferenceGeometryProfile** | *not a JDL field* | The fixed software construction parameters (crown/pavilion/table ratios, corner ratios) — see [`567-stone-reference-geometry-contract.md`](567-stone-reference-geometry-contract.md). Documented, not user-supplied. |

The real Pydantic model (`backend/jewelmind/domain/schema.py::StoneSpec`):

```python
shape: StoneShape = "round"
diameter: float | None = Field(default=6.5, allow_inf_nan=False)
length: float | None = Field(default=None, allow_inf_nan=False)
width: float | None = Field(default=None, allow_inf_nan=False)
depth: float = Field(default=4.0, allow_inf_nan=False)
orientation: float = Field(default=0.0, allow_inf_nan=False)
```

with a real `@model_validator(mode="after")` that requires `diameter` for `round` and **both** `length` and `width` for every other shape (STONE-GOV-006). Note what is *not* here: no material, no setting, no ring dimension, no prong count, no placement in world space. Placement belongs to StoneArrangement / category integration; setting belongs to the Setting layer.

## StoneReference — the generated output

A `StoneReference` is the real `GeneratedComponent` named `"stone_reference"` that `geometry/stone/builder.py::build_stone()` returns. It is **deterministic geometric reference geometry** suitable for layout, setting construction, component relationships, clearance/intersection analysis, Vision, and technical communication.

It is not a gemstone model. It never guarantees an exact facet pattern, optical behaviour, commercial cutting proportions, gemological certification, or vendor dimensions (STONE-GOV-011). Every component it produces carries `isGemologicalReproduction: false`, for every shape, unconditionally.

## The `generatedMetadata` contract

Both construction paths report a common core; `round` adds two fields the non-round loft has no single equivalent for.

**Common to every shape:**

| Field | Meaning |
|---|---|
| `shape` | The real shape that was built. |
| `girdleZMm` | Z height of the girdle plane — the assembly's stone-placement anchor. |
| `crownHeightMm` / `pavilionHeightMm` | The depth split, from the shared reference proportions. |
| `lengthMm` / `widthMm` / `depthMm` | The **resolved** dimensions used to build the geometry. CONSTRUCTION_PARAMETER — see below. |
| `orientationDeg` | The applied orientation. |
| `isGemologicalReproduction` | Always `false`. |
| `referenceGeometryVersion` | `"1.0.0"` — bumped on any MAJOR change to how outlines/lofts are built. |

**`round` only:** `girdleRadiusMm`, `tableRadiusMm`. These exist because a radially symmetric outline *has* a single girdle radius and a single table radius. A non-round outline does not: an oval's girdle has two distinct semi-axes, an emerald's has clipped corners. Rather than invent a misleading "equivalent radius" for those shapes, the fields are simply absent — the same discipline as refusing a fake equivalent diameter (see [`578-current-code-mapping-and-gaps.md`](578-current-code-mapping-and-gaps.md)).

### CONSTRUCTION_PARAMETER vs MEASURED_GEOMETRY

`lengthMm`/`widthMm`/`depthMm` in this metadata are **CONSTRUCTION_PARAMETER**: they are the values that were fed into the builder, echoed back. They are not an independent re-measurement of the finished solid. The independently measured counterparts are Geometry Inspection's `STONE_MEASURED_LENGTH`/`WIDTH`/`DEPTH` facts, computed from the real bounding box. Keeping the two separate is what lets a regression show up as a *divergence between them* — see [`574-stone-inspection-contract.md`](574-stone-inspection-contract.md). This mirrors Sprint 17's `widthSamplesMm` convention for the Shank.

## Relationship to Ring Architecture v2's `StoneArrangementDefinition`

Ring Architecture v2 (Sprint 16) has a `StoneArrangementDefinition` in `backend/jewelmind/ring/models.py`:

```python
arrangement: StoneArrangementType   # "SINGLE_CENTER" — the only CURRENT value
stone: StoneSpec
```

It **wraps** `StoneSpec` — it does not redefine or extend it. That is the correct relationship and must stay that way: the arrangement layer owns *how many stones and where*, the Stone System owns *what a stone is*. `StoneArrangementDefinition` gaining a `MULTI_STONE`/`HALO`/`PAVE_ARRAY` value in a future sprint would not require any change to `StoneSpec`.

See [`../18-ring-architecture/529-stone-arrangement-contract.md`](../18-ring-architecture/529-stone-arrangement-contract.md) for that layer's own authority; this document does not restate it.

## What is deliberately absent from StoneDefinition

- **Prong positions.** These are derived by the Setting layer *from* stone facts (STONE-GOV-009).
- **World placement.** The stone's girdle Z is computed at build time from the ring's own anchor (`band_top_z + basketHeight`); the definition itself carries no coordinates.
- **Material / colour.** Vision's material presentation is separate visual state (VISION-GOV-014); the stone's optical appearance is not a StoneDefinition concern.
- **Carat weight or any commercial descriptor.** No such field exists, and none may be inferred from dimensions.

## Cross-references

- [`563-stone-shape-model.md`](563-stone-shape-model.md) — the 7 shapes and 5 symmetry classes.
- [`564-stone-dimension-model.md`](564-stone-dimension-model.md) — the public-vs-resolved dimension split.
- [`576-current-round-migration.md`](576-current-round-migration.md) — how the pre-Sprint-18 round-only model maps onto this one.
