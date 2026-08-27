---
id: JM-BIBLE-560
title: Stone Governance
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-STONE-README
related_documents:
  - JM-BIBLE-120
  - JM-BIBLE-090
  - JM-BIBLE-460
  - JM-BIBLE-540
implementation_status: current
professional_validation: not_required
normative: true
---

# Stone Governance

## STONE-GOV-001 through STONE-GOV-016

| ID | Rule |
|---|---|
| **STONE-GOV-001** | **Stone System is category-neutral.** Nothing under `backend/jewelmind/geometry/stone/` or in `backend/jewelmind/domain/stone_dimensions.py` may import `jewelmind.ring` (or any other jewelry-category package). Ring depends on Stone; Stone never depends on Ring. Enforced by `backend/tests/test_stone_system_no_ring_dependency.py`, which AST-parses every Stone System file rather than importing it — an `import`-based check could pass by accident on an already-cached module. |
| **STONE-GOV-002** | **StoneReference geometry must be deterministic.** `geometry/stone/builder.py::build_stone()` and every function in `outline.py` read only the passed `JewelryDefinition` — no wall-clock time, randomness, or external state. The same `StoneSpec` always produces the same solid, the same volume, and the same bounding box (restating LAW/ATLAS-GOV-003 for this subsystem). |
| **STONE-GOV-003** | **StoneReference must remain separate from production metal.** The stone solid is never an argument to a production-metal fuse, and STEP/STL exports exclude it unless the caller explicitly opts in. This holds for all 7 shapes, not only `round` — verified by `test_stone.py::TestStoneProductionExportExclusion` and `TestStoneMeasuredDimensions::test_stone_reference_never_reported_as_production_metal` (restating LAW-006). |
| **STONE-GOV-004** | **Stone geometry must never silently become production geometry.** There is no code path in `geometry/stone/` that returns a shape into a metal-union call, and the component's identity stays the literal name `"stone_reference"`. `assembly.py::_stone_metal_separation()` reports separation structurally by component identity, never by inferring a role from a geometric coincidence (restating INSPECT-GOV-008). |
| **STONE-GOV-005** | **Stone shape and stone dimensions are separate concepts.** `stone.shape` selects a construction strategy; `diameter`/`length`/`width`/`depth` are independent quantities. `domain/stone_dimensions.py` is the single place the two are reconciled, normalizing `round` to `length == width == diameter` so no downstream module needs a shape special case to read a dimension. |
| **STONE-GOV-006** | **Shape-specific dimensions must be explicit.** `StoneSpec`'s own `@model_validator(mode="after")` requires `diameter` when `shape == "round"`, and requires **both** `length` and `width` for every other shape. A shape's `requiredDimensions` are also declared in `geometry/stone/capability.py`. No dimension is ever inferred from a shape name (see also STONE-GOV-012's Designer boundary). |
| **STONE-GOV-007** | **Unsupported shapes must fail explicitly.** `StoneShape` is a closed Pydantic enum, so an unknown value is rejected at validation. Beyond that, `geometry/stone/errors.py::StoneShapeUnsupportedError` is raised if a shape ever reaches `_build_non_round_stone()` with no registered outline builder — a real explicit guard rather than an implicit `KeyError`. Verified by `test_stone.py::TestStoneDimensionValidation::test_unknown_shape_is_rejected`. |
| **STONE-GOV-008** | **Stone orientation must be explicit and deterministic.** `stone.orientation` is a real JDL field (degrees, default `0.0`), applied by `builder.py::_apply_orientation()` as a rotation around the stone's own local vertical axis at its own bounding-box center. It early-returns unchanged at `0.0`, and is applied uniformly for every shape rather than special-cased away for `round`. No arbitrary 3D transform is ever exposed. Verified by `test_stone.py::TestStoneOrientation`. |
| **STONE-GOV-009** | **Setting geometry may consume Stone facts but may not redefine Stone geometry.** Stone exposes resolved dimensions, an outline, a girdle-plane Z, a bounding box, and an orientation; the Setting layer decides prong placement *from* those facts. `StoneDefinition` contains no prong positions. Correspondingly, `generationSupported` and `currentSettingCompatibility` are independent axes in the capability registry: only `round` is `SUPPORTED`, all 6 new shapes are honestly `EXPERIMENTAL`. |
| **STONE-GOV-010** | **Stone System must not contain professional setting thresholds.** No file under `geometry/stone/` imports `jewelmind.validation` or references a Forge rule ID. The only numeric constants in the package are construction/sampling parameters (`_CROWN_FRACTION`, `_PAVILION_FRACTION`, `_TABLE_TO_GIRDLE_RATIO`, `_CULET_SCALE_RATIO`, `_EMERALD_CORNER_CLIP_RATIO`, `_CUSHION_CORNER_RATIO`) — never jewelry-domain thresholds (restating FORGE-GOV-005/ATLAS-GOV-002). |
| **STONE-GOV-011** | **Stone reference geometry must not claim gemological accuracy.** Every generated component sets `isGemologicalReproduction: false`, for every shape. A `StoneReference` never guarantees an exact facet pattern, optical behaviour, commercial cutting proportions, gemological certification, or vendor dimensions. Every construction constant carries `provenance: software_reference_profile` in `specs/stone/v1/stone-reference-profile.schema.json` — a deliberate, deterministic software choice verified only to produce robust CAD geometry, never a sourced industry standard. |
| **STONE-GOV-012** | **Future faceting must not require replacing the StoneDefinition contract.** `StoneSpec` describes *what stone is wanted* (shape, dimensions, orientation), never *how it is tessellated*. A future `FACETED_GEM_MODEL` or `MEASURED_STONE` layer is therefore additive: it would change which builder runs, not the definition a caller writes. See [`567-stone-reference-geometry-contract.md`](567-stone-reference-geometry-contract.md). |
| **STONE-GOV-013** | **Stone generation failures must not silently fall back to another shape.** `_build_non_round_stone()` raises `StoneGenerationError` when a loft throws, or when the result has no solids or fails `isValid()`. Nothing catches it to substitute a different shape or a simpler solid. Structurally reinforced by `test_stone.py::TestPearAsymmetry::test_pear_generator_never_silently_produces_a_symmetric_fallback`, which asserts pear's outline builder is not the same object as oval's or marquise's. |
| **STONE-GOV-014** | **Every current shape must have capability metadata.** `geometry/stone/capability.py::STONE_SHAPE_CAPABILITIES` is the single source of truth for CURRENT vs PLANNED and carries `generationSupported`/`jdlSupported`/`inspectionSupported`/`visionSupported`/`currentSettingCompatibility`/`requiredDimensions`/`symmetryClass`/`referenceGeometryVersion` per shape. It is mirrored — never hand-duplicated — at `specs/stone/v1/shape-registry.json`, re-derived live by `test_stone_schemas.py::test_shape_registry_matches_the_real_capability_registry_live`. |
| **STONE-GOV-015** | **Every new shape requires inspection and Golden regression coverage.** A new shape must produce real inspection facts (the 6 `STONE_*` dimension facts plus the generic component facts) and must get its **own new** Golden case — never a retrofit of an existing one. Sprint 18 added `SOL-013` through `SOL-018` for exactly this reason; `SOL-001` through `SOL-012` were left untouched. |
| **STONE-GOV-016** | **Existing ROUND behaviour remains backward compatible.** Every `round` request routes to `_build_round_stone()`, which is the byte-identical pre-Sprint-18 construction. Proven two ways: `test_stone.py::TestRoundStoneBackwardCompatibility` asserts the exact recorded volume `58.22141924499569 mm³`, and all 12 pre-existing Golden cases required **zero** baseline updates. A `round` request must never be routed through the non-round loft path "for consistency". |

## Relationship to Atlas, Ring Architecture, Shank, and Forge governance

This document sits alongside [`07-atlas/120-atlas-governance.md`](../07-atlas/120-atlas-governance.md) (Sprint 5), [`18-ring-architecture/520-jewelry-category-architecture.md`](../18-ring-architecture/520-jewelry-category-architecture.md) (Sprint 16), [`19-shank/540-shank-governance.md`](../19-shank/540-shank-governance.md) (Sprint 17), [`06-forge/090-forge-governance.md`](../06-forge/090-forge-governance.md) (Sprint 4), and [`16-geometry-inspection/460-inspection-governance.md`](../16-geometry-inspection/460-inspection-governance.md) (Sprint 14) — it supersedes none of them.

Two existing boundaries are what STONE-GOV-001 and STONE-GOV-010 make concrete here:

- **Sprint 16's category direction.** Ring is one jewelry category, not the platform root. Shank (Sprint 17) is genuinely ring-specific and lives in the Atlas layer for layering reasons; Stone is genuinely *category-neutral* and is the first subsystem to prove that distinction with a real architecture test.
- **ATLAS-GOV-002's Atlas/Forge split.** Stone reports geometric facts (a resolved dimension, a measured extent, a bounding box); only Forge interprets a fact as a jewelry-domain violation. This is why the round-only scoping of `JM-STONE-001`/`JM-PRONG-003` happened in `validation/engine.py` and not in `geometry/stone/` — see [`578-current-code-mapping-and-gaps.md`](578-current-code-mapping-and-gaps.md).

One layering nuance is specific to this Sprint: `domain/stone_dimensions.py` deliberately lives in `domain/` rather than `geometry/` or `validation/`, because both Atlas geometry and Forge validation need the same LENGTH/WIDTH/DEPTH resolution. Putting it in either consumer's package would have created a new Forge↔Atlas coupling that did not previously exist; `domain/` is the one layer both already depended on.

## When an ADR is required

- Replacing the 3-level crown/girdle/pavilion loft with a different construction primitive.
- Changing the LENGTH→Y / WIDTH→X / DEPTH→Z axis mapping, or the orientation convention (own-bbox-center rotation around local vertical).
- Moving `stone_dimensions` out of `domain/`, or otherwise changing which layer owns dimension resolution.
- Introducing a `FACETED_GEM_MODEL` or `MEASURED_STONE` layer.
- Any change that violates STONE-GOV-001 through 016 without superseding this document first.

## When an RFC is required

- A new stone shape (asscher, radiant, heart, trillion, baguette, cabochon, custom outlines, calibrated stones) — see [`../04-jewelry-domain/056-domain-extension-strategy.md`](../04-jewelry-domain/056-domain-extension-strategy.md).
- Multi-stone arrangements (halo, pavé, three-stone) — these are StoneArrangement concerns, not StoneDefinition concerns.
- Introducing an equivalent-size metric for non-round stones. This needs explicit domain semantics of its own; it is not a refactor. See [`578-current-code-mapping-and-gaps.md`](578-current-code-mapping-and-gaps.md) on why no such metric exists today.
