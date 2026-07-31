---
id: JM-BIBLE-053
title: Domain Invariants
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on:
  - JM-BIBLE-052
related_documents:
  - JM-BIBLE-004
  - JM-BIBLE-054
implementation_status: current
professional_validation: preliminary
---

# Domain Invariants

An invariant is a statement that must always hold for the system to be
considered correct. This document classifies every current invariant
into five categories and references the
[JewelMind Constitution](../00-foundation/004-jewelmind-constitution.md)
where applicable.

## Schema invariants

| Invariant | Enforcement | Test |
|---|---|---|
| Only `schemaVersion: "0.1.0"` is accepted. | `domain/schema.py::JewelryDefinition.schemaVersion: Literal["0.1.0"]` | `test_schema_safety.py::test_unsupported_schema_version_is_rejected` |
| Only the declared enumerations are accepted (`band.profile`, `stone.shape`, `setting.type`, `material.metal`, `manufacturing.method`, `ring.sizeSystem`). | `Literal[...]` types throughout `domain/schema.py` | `test_schema.py`, `test_schema_safety.py` |
| Every numeric field must be a finite number (no `NaN`/`Infinity`), and strings are not coerced to numbers. | `Field(allow_inf_nan=False)` + `model_config = ConfigDict(strict=True)` | `test_schema_safety.py` (70 tests) |

## Geometric invariants

| Invariant | Enforcement | Test |
|---|---|---|
| Every generated component has positive volume. | Implicit in valid CadQuery solid construction; asserted in tests | `test_geometry.py` (multiple) |
| Component counts match what was requested (or the code's own documented fallback). | `build_prongs()`'s `generatedCount` reporting | `test_geometry.py::test_prongs_default_count_is_six`, `test_prongs_four_count` |
| The stone reference remains a solid entirely separate from the combined metal body. | `geometry/assemblies/solitaire.py::_fuse_metal` never receives `stone` | `test_geometry.py::test_stone_reference_is_valid_and_separate_from_metal` |
| All four required components (band, stone_reference, prongs, basket_support) are present in every generated model. | `GeneratedModel.components` always populated with all four keys | `test_geometry.py::test_solitaire_assembly_has_all_required_components` |

## Assembly invariants

| Invariant | Enforcement | Test |
|---|---|---|
| Requested prong count equals generated count for supported counts (4 or 6). | `build_prongs()` | `test_geometry.py::test_four_and_six_prong_models_visibly_differ` |
| A failed boolean fuse falls back to a multi-solid compound, never a dropped component. | `_fuse_metal`'s except branch | `test_geometry.py::test_solitaire_assembly_metal_is_single_fused_solid_by_default` (asserts the success path; the fallback path is exercised by code inspection, not a dedicated failure-injection test — see [`057-open-domain-questions.md`](057-open-domain-questions.md)) |
| Model metadata (volumes, bounding box) matches the actual generated geometry. | `GeneratedModel.component_volumes()` reads directly from each `GeneratedComponent.volume_mm3` | `test_api.py::test_model_metadata_endpoint` |

## Workflow invariants

| Invariant | Enforcement | Test |
|---|---|---|
| Invalid definitions cannot generate a model. | `services/model_service.py::generate` raises `ValidationBlockedError` before calling geometry code | `test_api.py::test_generate_invalid_definition_returns_422` |
| The same canonical definition always produces a stable hash (and therefore a stable `modelId`). | `utils/hashing.py::definition_hash` | `test_geometry.py::test_definition_hash_is_deterministic` |
| A stale model (parameters changed after generation) cannot be silently exported without regenerating. | `frontend/src/store/useProjectStore.ts`'s `isStale` flag disables export buttons | `useProjectStore.test.ts::marks the definition stale after a parameter changes post-generation` |
| Export operations always resolve an already-validated, already-generated model by `modelId` — never a raw, unchecked definition. | `api/routes.py` export endpoints all call `model_service.get_record(modelId)` | `test_api.py::test_export_with_unknown_model_id_returns_404` |

## Professional invariants

**None are currently defined as accepted.** No statement in this
repository has been reviewed and accepted by a named, qualified jewelry
professional through the process in
[`058-professional-validation-register.md`](058-professional-validation-register.md).
Candidate professional invariants — statements that *would* need
professional confirmation before being promoted out of this section —
are logged as open questions rather than asserted here:

- Whether the current prong-to-girdle overlap approximation
  (`prong_center_radius`'s `× 0.3` factor) represents an acceptable grip
  geometry for any real stone-setting practice.
- Whether the basket's wall-thickness-derived-from-prong-footprint
  approach is structurally adequate for any specific size/material
  combination.
- Whether `JM-MANUFACTURING-001`'s 0.8mm threshold is an appropriate
  minimum feature size for direct resin printing in practice.

See [`057-open-domain-questions.md`](057-open-domain-questions.md) for
the full register of these and other unresolved questions.

## Reference to the Constitution

Several invariants above directly implement Constitution laws:
[LAW-005](../00-foundation/004-jewelmind-constitution.md#LAW-005) (no
silently discarded components), 
[LAW-006](../00-foundation/004-jewelmind-constitution.md#LAW-006) (stone
separation), and
[LAW-008](../00-foundation/004-jewelmind-constitution.md#LAW-008)
(invalid definitions cannot generate/export). This document exists to
show *how* those laws are currently enforced in practice, not to restate
them.
