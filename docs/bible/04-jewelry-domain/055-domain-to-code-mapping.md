---
id: JM-BIBLE-055
title: Domain-to-Code Mapping
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on:
  - JM-BIBLE-044
related_documents:
  - JM-BIBLE-021
  - JM-BIBLE-A05
implementation_status: current
professional_validation: not_required
---

# Domain-to-Code Mapping

No refactor was performed to produce this document — it reports what
exists today and flags inconsistencies for future work, per this
Sprint's explicit instruction.

## Mapping table

| Domain concept | Frontend TS type | Backend Pydantic model | Validation module | Geometry builder | Assembly builder | API service | Exporter | Frontend UI | Tests |
|---|---|---|---|---|---|---|---|---|---|
| Project identity | `ProjectInfo` (`shared/types/jewelry-definition.ts`) | `ProjectInfo` (`domain/schema.py`) | — | — | — | — | `json_exporter.py`, `specification.py` | `ConfigurationPanel.tsx` (Name field) | `test_schema.py` |
| Jewelry category/style | `JewelryInfo` | `JewelryInfo` | — | — | `solitaire.py` (implicitly, always solitaire) | — | `json_exporter.py` | (not directly editable — fixed) | `test_schema.py` |
| Ring dimensions | `RingSpec` | `RingSpec` | `_ring_rules` (`validation/engine.py`) | `geometry/constants.py` (`inner_radius`, `outer_radius`) | `solitaire.py` | `api/routes.py::generate_model` | `specification.py` | `ConfigurationPanel.tsx` (Ring section) | `test_validation.py`, `test_geometry.py` |
| Band / Shank (Sprint 17) | `BandSpec`, `BandTaperSpec` | `BandSpec`, `BandTaperSpec` | `_band_rules` | `geometry/shank/` (`builder.py`, `profile.py`, `taper.py`, `capability.py`) via `geometry/components/band.py` re-export | `solitaire.py` | same | `step_exporter.py`, `stl_exporter.py`, `specification.py` | `ConfigurationPanel.tsx` (Band section — no taper UI control this Sprint) | `test_validation.py`, `test_geometry.py`, `test_shank.py`, `test_shank_schemas.py` |
| Stone reference / Stone System (Sprint 18) | `StoneSpec` | `StoneSpec` | `_stone_rules` (`JM-STONE-001` ROUND_ONLY, `JM-STONE-002` SHARED) | `geometry/stone/` (`builder.py`, `outline.py`, `capability.py`) + `domain/stone_dimensions.py`, via `geometry/components/stone.py` re-export | `solitaire.py` | same | Excluded by default; opt-in via `includeStoneReference` | `ConfigurationPanel.tsx` (Stone section — shape selector + conditional dimension fields) | `test_validation.py`, `test_geometry.py`, `test_stone.py`, `test_stone_schemas.py`, `test_stone_system_no_ring_dependency.py` |
| Setting / prongs | `SettingSpec` | `SettingSpec` | `_prong_rules` | `geometry/components/prongs.py` | `solitaire.py` | same | `step_exporter.py`, `stl_exporter.py` | `ConfigurationPanel.tsx` (Setting section) | `test_validation.py`, `test_geometry.py` |
| Basket support | (no dedicated schema field — derived entirely from `SettingSpec.basketHeight` and `StoneSpec`/`SettingSpec` geometry inputs) | (same — `SettingSpec.basketHeight` only) | `_setting_rules` | `geometry/components/basket.py` | `solitaire.py` | same | `step_exporter.py`, `stl_exporter.py` | (no separate UI section — `basketHeight` lives under Setting) | `test_validation.py`, `test_geometry.py` |
| Material | `MaterialSpec` | `MaterialSpec` | (no dedicated rule — see [`050-material-domain.md`](050-material-domain.md)) | — (metadata only) | — | — | `json_exporter.py`, `specification.py` | `ConfigurationPanel.tsx` (Material section), `ModelViewport.tsx` (`METAL_COLORS`) | `test_schema.py` |
| Manufacturing context | `ManufacturingSpec` | `ManufacturingSpec` | `_manufacturing_rules` | — (metadata + validation context only) | — | — | `json_exporter.py`, `specification.py` | `ConfigurationPanel.tsx` (Manufacturing section) | `test_validation.py` |
| Preview configuration | `PreviewSpec` | `PreviewSpec` | (type-level constraints only: finite, `> 0`) | `preview/mesh.py` (tessellation call) | — | `export/stl` accepts optional overrides | `stl_exporter.py` | (not directly editable in the current UI — uses schema defaults) | `test_schema_safety.py` |
| Validation results | `ValidationResult` (`shared/validation/rules.ts`) | `ValidationResult` (`validation/rules.py`) | `validate_definition()` | — | — | `/api/models/validate`, embedded in `/generate` response | — | `ValidationPanel.tsx` | `test_validation.py`, `test_api.py` |
| Generated model identity | `GenerateResponse.modelId` (`frontend/src/api/types.ts`) | `GeneratedModel.definition_hash` (`geometry/model.py`) | — | — | `solitaire.py` | `services/model_service.py::ModelRecord` | — | `useProjectStore.ts` (`generatedModel.modelId`) | `test_geometry.py::test_definition_hash_is_deterministic` |
| Generated artifacts | `PreviewComponentEntry`, export blob handling (`api/client.ts`) | — | — | — | — | `services/model_service.py` (temp file lifecycle) | `step_exporter.py`, `stl_exporter.py`, `json_exporter.py`, `specification.py` | `ModelViewport.tsx`, `ProjectActions.tsx` | `test_api.py`, `test_api_hardening.py` |

## Concepts with complete mappings

`RingSpec`, `BandSpec`, `StoneSpec`, `SettingSpec`, `MaterialSpec`,
`ManufacturingSpec`, `PreviewSpec` — each has a matching frontend type, a
matching backend model, and (where a business rule exists) a matching
validation function, geometry builder, and test coverage.

## Concepts represented only as metadata

`MaterialSpec` and `ManufacturingSpec` (beyond `JM-MANUFACTURING-001`) —
stored, validated only trivially (schema-level enum), exported, but do
not drive geometry. See [`050-material-domain.md`](050-material-domain.md)
and [`051-manufacturing-context.md`](051-manufacturing-context.md).

## Concepts duplicated across languages

Every field in `JewelryDefinition` is duplicated by hand between
`backend/jewelmind/domain/schema.py` (Pydantic) and
`shared/types/jewelry-definition.ts` (TypeScript) — see
[ADR-005](../03-decisions/ADR-005-canonical-jewelry-definition.md). All
sixteen validation rules are similarly duplicated between
`backend/jewelmind/validation/engine.py` and
`shared/validation/engine.ts` — see
[ADR-004](../03-decisions/ADR-004-backend-authoritative-validation.md).

## Concepts missing from code entirely

Per [`043-ring-anatomy.md`](043-ring-anatomy.md) and the component domain
documents: `Head` (as a named concept), `Gallery`, `Bridge`, `Shoulders`,
`Engraving`, `Internal relief`, any non-round stone shape, any setting
type other than prong, any ring style other than solitaire.

## Naming inconsistencies observed

- **"Basket" has no dedicated schema field** — it is entirely derived
  from `SettingSpec.basketHeight` plus other components' geometry. A
  reader looking for a `BasketSpec` in the schema will not find one; the
  concept exists only in `geometry/components/basket.py` and this Bible.
- **"Head"** (the informal umbrella term for setting + basket together,
  used in [`043-ring-anatomy.md`](043-ring-anatomy.md)) has no code
  representation at all — not a naming inconsistency so much as an
  absent concept, noted here so a future reader does not go looking for
  it in code.
- **`SettingSpec.type: Literal["prong"]`** names the field `type` but it
  is really "setting type" — consistent with the domain concept
  ([`047-setting-domain.md`](047-setting-domain.md)) but easy to misread
  as a more generic "type" field out of context.

## Future risk of frontend/backend schema divergence

Because both schemas and both validation engines are maintained by hand
(no codegen — [ADR-005](../03-decisions/ADR-005-canonical-jewelry-definition.md)),
every new field or rule is a manual-synchronization opportunity for
drift. This risk is already documented as a known limitation
([`02-architecture/026-known-technical-limitations.md`](../02-architecture/026-known-technical-limitations.md))
and is repeated here specifically in the context of future jewelry-domain
expansion: adding a new stone shape, setting type, or ring style (see
[`056-domain-extension-strategy.md`](056-domain-extension-strategy.md))
will need to touch both languages' schemas and both validation engines
consistently, every time.
