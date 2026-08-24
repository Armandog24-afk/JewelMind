---
id: JM-BIBLE-084
title: Current Implementation Mapping
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-064
related_documents:
  - JM-BIBLE-A09
  - JM-BIBLE-055
implementation_status: current
professional_validation: not_required
normative: true
---

# Current Implementation Mapping

Every JDL v1 field, mapped to its exact current representation across the stack. This is not a refactor plan — gaps found here are reported, not fixed, per the Sprint 3 brief.

| JSON path | TS type | Frontend control (`ConfigurationPanel.tsx`) | Frontend runtime guard | Pydantic field | Backend semantic rule(s) | Geometry dependency | Preview dependency | Export dependency |
|---|---|---|---|---|---|---|---|---|
| `schemaVersion` | `string` (loose) | none — not user-editable | exact-match check | `Literal["0.1.0"]` | none (structural only) | none | none | embedded verbatim in JSON/spec exports |
| `project.name` | `string` | `#project-name` text input | `typeof === 'string'` (no length check) | `str, min_length=1, max_length=200` | none | none | none | filename basis (via `sanitize_filename()`), spec title |
| `project.units` | `'mm'` | none — fixed | exact-match `'mm'` | `Literal["mm"]` | none | implicit (all geometry is mm) | implicit | implicit |
| `jewelry.category` | `'ring'` | none — fixed | exact-match `'ring'` | `Literal["ring"]` | none | none | none | metadata in exports |
| `jewelry.style` | `'solitaire'` | none — fixed | exact-match `'solitaire'` | `Literal["solitaire"]` | none | selects `build_solitaire_ring()` (only style that exists) | none | metadata |
| `ring.sizeSystem` | `'EU'` | none — fixed | exact-match `'EU'` | `Literal["EU"]` | none | none | none | metadata |
| `ring.size` | `number` | `#ring-size` numeric input | `isFiniteNumber` (no range check) | `float, allow_inf_nan=False` | `JM-RING-002`, `JM-RING-003` | not directly consumed by geometry builders (only `innerDiameter` is) | none | metadata |
| `ring.innerDiameter` | `number` | `#ring-inner-diameter` numeric input | `isFiniteNumber` | `float, allow_inf_nan=False` | `JM-RING-001`, `JM-RING-003`, `JM-GEOMETRY-001` | `inner_radius()`, `outer_radius()` | indirect (affects generated mesh) | STEP/STL geometry |
| `band.width` | `number` | `#band-width` numeric input | `isFiniteNumber` | `float, allow_inf_nan=False` | `JM-BAND-001`, `JM-BAND-003`, `JM-GEOMETRY-001` | `build_ring_band()` | indirect | STEP/STL geometry |
| `band.thickness` | `number` | `#band-thickness` numeric input | `isFiniteNumber` | `float, allow_inf_nan=False` | `JM-BAND-002`, `JM-GEOMETRY-001` | `outer_radius()`, `build_ring_band()` | indirect | STEP/STL geometry |
| `band.profile` | `BandProfile` | `#band-profile` select | `BAND_PROFILES.includes(...)` | `Literal["comfort_fit", "flat"]` | none | selects band cross-section shape | indirect | STEP/STL geometry |
| `stone.shape` | `'round'` | none — fixed | exact-match `'round'` | `Literal["round"]` | none | `build_stone_reference()` | reference-only preview material | excluded by default (LAW-006) |
| `stone.diameter` | `number` | `#stone-diameter` numeric input | `isFiniteNumber` | `float, allow_inf_nan=False` | `JM-STONE-001`, `JM-STONE-002`, `JM-PRONG-003` | `build_stone_reference()`, `prong_center_radius()` | indirect | reference-only |
| `stone.depth` | `number` | `#stone-depth` numeric input | `isFiniteNumber` | `float, allow_inf_nan=False` | `JM-STONE-002` | `build_stone_reference()` | indirect | reference-only |
| `setting.type` | `'prong'` | none — fixed | exact-match `'prong'` | `Literal["prong"]` | none | selects `build_prongs()`/`build_basket_support()` | indirect | STEP/STL geometry |
| `setting.prongCount` | `number` (loosely typed) | `#prong-count` numeric input | `isFiniteNumber` (does not check integer-ness or the `{4,6}` set) | `int` (strict; a non-integer float is rejected at the Pydantic layer, not caught by the looser frontend guard) | `JM-PRONG-001`, `JM-PRONG-003` | `build_prongs()`, `build_basket_support()` | indirect | STEP/STL geometry |
| `setting.prongDiameter` | `number` | `#prong-diameter` numeric input | `isFiniteNumber` | `float, allow_inf_nan=False` | `JM-PRONG-002` | `build_prongs()`, `build_basket_support()`, `prong_center_radius()` | indirect | STEP/STL geometry |
| `setting.prongHeight` | `number` | `#prong-height` numeric input | `isFiniteNumber` | `float, allow_inf_nan=False` | `JM-PRONG-004` | `build_prongs()` | indirect | STEP/STL geometry |
| `setting.basketHeight` | `number` | `#basket-height` numeric input | `isFiniteNumber` | `float, allow_inf_nan=False` | `JM-SETTING-001`, `JM-SETTING-002`, `JM-PRONG-004` | `build_basket_support()`, `build_stone_reference()` (via `band_top_z + basketHeight`) | indirect | STEP/STL geometry |
| `material.metal` | `MetalType` | `#metal` select | `METAL_TYPES.includes(...)` | `Literal[...5 values...]` | none | **none today** — metadata only | none | specification text, JSON export |
| `manufacturing.method` | `ManufacturingMethod` | `#manufacturing-method` select | `MANUFACTURING_METHODS.includes(...)` | `Literal["lost_wax_casting", "direct_resin_printing"]` | `JM-MANUFACTURING-001` | none | none | specification text, JSON export |
| `preview.meshTolerance` | `number` | none — no UI control; fixed default used unless an export request overrides it | `isFiniteNumber && > 0` | `float, gt=0, allow_inf_nan=False` | none (structural `gt=0` only) | none | tessellation only | tessellation only |
| `preview.angularTolerance` | `number` | none — no UI control | `isFiniteNumber && > 0` | `float, gt=0, allow_inf_nan=False` | none | none | tessellation only | tessellation only |

## Findings from this mapping (reported, not fixed)

1. **Complete mappings**: every geometry-driving dimension field (ring, band, stone, setting) has a working frontend control, a Pydantic field, a semantic rule (where applicable), and a geometry dependency. No field is fully disconnected from the pipeline.
2. **Metadata-only fields confirmed by inspection, not assumption**: `material.metal` and `manufacturing.method` have zero geometry dependency today — confirmed by reading every `geometry/components/*.py` file, none of which reference `definition.material` or (for shape purposes) `definition.manufacturing`. This matches [`04-jewelry-domain/052-parametric-dependency-model.md`](../04-jewelry-domain/052-parametric-dependency-model.md).
3. **Frontend/backend constraint mismatch**: the frontend's `isValidJewelryDefinition()` runtime guard checks `isFiniteNumber(setting.prongCount)` but not integer-ness or `{4, 6}` membership; the backend's Pydantic `int` type is stricter about integer-ness (a JSON float like `4.5` is rejected in strict mode) but the `{4, 6}` set is enforced only by semantic rule `JM-PRONG-001`, not either type system. Net effect: `4.5` is caught by the backend but not by the frontend guard; `5` is caught by neither type layer, only by `JM-PRONG-001` at validation time. This is intentional per `schema.py`'s own comment, not a bug — recorded here for completeness.
4. **UI-absent fields**: `preview.meshTolerance`/`angularTolerance` have no configuration-panel control; they use their schema defaults unless an export request explicitly overrides them via `mesh_tolerance`/`angular_tolerance` request parameters (see `api/schemas.py`). This is a genuine current limitation (a user cannot tune preview quality from the UI) — not addressed in this documentation-only Sprint.
5. **No undocumented derived values found**: every value used by a geometry builder that isn't a direct field read traces to one of the four named functions in `geometry/constants.py` (`inner_radius`, `outer_radius`, `band_top_z`, `prong_center_radius`) plus the fixed `EMBED_MM` constant — none of these were previously undocumented; all are now cross-referenced in [`078-geometry-generation-contract.md`](078-geometry-generation-contract.md).
6. **No schema divergence found** between `backend/jewelmind/domain/schema.py` and `shared/types/jewelry-definition.ts` — every field, type, and enum member matches exactly as of this Sprint's inspection.

These findings do not require code changes; items 3 and 4 are candidates for a future hardening or UX sprint, not this one.
