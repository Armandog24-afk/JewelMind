---
id: JM-BIBLE-580
title: Setting Governance
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-27
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-SETTING-README
related_documents:
  - JM-BIBLE-120
  - JM-BIBLE-090
  - JM-BIBLE-460
  - JM-BIBLE-560
implementation_status: current
professional_validation: not_required
normative: true
---

# Setting Governance

## SETTING-GOV-001 through SETTING-GOV-018

| ID | Rule |
|---|---|
| **SETTING-GOV-001** | **Setting System must be category-neutral.** No module under `backend/jewelmind/setting/` may import `jewelmind.ring`, `jewelmind.jewelry_category`, `jewelmind.geometry.shank`, `jewelmind.geometry.connection`, or `geometry/setting_adapter.py` — nor `JewelryDefinition`, which would smuggle the whole ring domain across in one import. Enforced by AST inspection in `backend/tests/test_setting_system_no_ring_dependency.py`, which also asserts the reverse direction is real. |
| **SETTING-GOV-002** | **Setting geometry must be deterministic.** No generator reads wall-clock time, randomness, or external state. Placement depends only on the `StoneSettingReference` and the prong/bezel parameters; the same inputs always produce the same solids, volumes, and bounding boxes. |
| **SETTING-GOV-003** | **Setting may consume StoneReference facts but may not redefine Stone geometry.** `setting/stone_interface.py` is the single place stone facts enter, and it calls the Stone System's own public contracts (`domain/stone_dimensions.py`, `geometry/stone/outline.py`). No file under `setting/` constructs, scales, or re-derives a stone silhouette. |
| **SETTING-GOV-004** | **StoneReference remains non-production geometry.** `GEOMETRY_ROLE["stone_reference"] == "stone_reference"` and `PRODUCTION_ROLE["stone_reference"] == "excluded_by_default"`, for every setting family. No setting generator returns the stone as one of its `productionComponents`, and STEP/STL exclude it by default (restating LAW-006). |
| **SETTING-GOV-005** | **Setting compatibility must be explicit per Stone shape.** `capability.py::compatibility_status()` returns a real `SUPPORTED_SOFTWARE`/`EXPERIMENTAL`/`UNSUPPORTED` value for every family × shape pair, and the full matrix is generated into `specs/setting/v1/setting-registry.json` rather than hand-maintained. Reserved families (`channel`, `flush`, `bar`, `tension`, `bead`, `pave`, `custom`) are deliberately NOT `SettingFamily` enum members. |
| **SETTING-GOV-006** | **A generatable Stone shape is not automatically Setting-compatible.** All 7 stone shapes generate; only `round` is `SUPPORTED_SOFTWARE` for prong, and only `round`/`oval` for bezel. Everything else is honestly `EXPERIMENTAL`. Asserted by `test_setting.py::TestSettingRegistry`. |
| **SETTING-GOV-007** | **A geometrically generated Setting is not automatically professionally validated.** `generatable` and `professionalValidationStatus` are independent fields. Every family is `generatable: true` AND `NOT_REVIEWED` simultaneously; `test_setting.py::TestNoFakeProfessionalValidation` asserts exactly that pairing so the two can never be conflated. |
| **SETTING-GOV-008** | **Prong placement must not silently assume ROUND geometry.** `placement.py::resolve_strategy()` picks `RADIAL` only for `round`; every other shape uses `OUTLINE_CARDINAL`, which samples the stone's real girdle outline. `StoneSettingReference.isBilaterallySymmetric` and `tipDirectionY` exist so a strategy can refuse to assume symmetry a shape does not have. |
| **SETTING-GOV-009** | **Prong count must remain explicit and deterministic.** Both the requested and the generated count are carried on the component metadata and on `SettingGeometryResult`, and surfaced as the `SETTING_REQUESTED_PRONG_COUNT` / `SETTING_GENERATED_PRONG_COUNT` inspection facts. A mismatch is recorded as a real warning, never smoothed over. |
| **SETTING-GOV-010** | **Setting System must not introduce unsourced professional minimum dimensions.** The only numeric constants in the package are construction parameters: `GIRDLE_INSET_PRONG_RADIUS_FRACTION` (0.3, inherited unchanged), `_OUTLINE_SAMPLES` (a search resolution), and `_RESAMPLE_POINTS` (a STEP-safety resolution). Bezel wall thickness/height defaults are PRELIMINARY SOFTWARE VALUES, and **no minimum wall dimension is enforced** because no sourced professional minimum exists. |
| **SETTING-GOV-011** | **Seat/bearing/cutter support must distinguish CURRENT, PARTIAL and PLANNED.** `seatSupport`, `bearingSupport` and `cutterSupport` are `PLANNED` for every family, because no such geometry exists. Stone/metal overlap is NOT a seat and must never be renamed as one. Asserted by `test_setting.py` and by the Capability Coverage Guard. |
| **SETTING-GOV-012** | **Unsupported Setting/Stone combinations must fail explicitly.** `SettingTypeUnsupportedError` for an unregistered family, `SettingStoneCombinationUnsupportedError` for an `UNSUPPORTED` pair. Neither is caught to produce an empty component, and no error message leaks a kernel stack trace. |
| **SETTING-GOV-013** | **Setting geometry must not silently fall back to another Setting family.** No `BEZEL → PRONG` path exists, and no `OUTLINE_CARDINAL → RADIAL` downgrade exists. The one real geometric accommodation — resampling a STEP-unsafe offset wire — is recorded as an observable `SettingFallbackEvent` on the result and as a component warning. |
| **SETTING-GOV-014** | **Category-specific integration belongs outside Setting core.** `SettingAttachmentInterface` (`attachmentPlaneZMm`/`embedMm`/`supportHeightMm`) is supplied BY the category integration. `geometry/setting_adapter.py` — deliberately outside `jewelmind/setting/` — is the sanctioned translation point from `JewelryDefinition`. |
| **SETTING-GOV-015** | **New Setting families require generation, inspection, capability metadata, and Golden coverage.** All four exist for both current families: real generators, 8 inspection facts, registry entries mirrored to `specs/`, and Golden cases `SET-001`–`SET-005`. |
| **SETTING-GOV-016** | **Setting runtime facts belong to Atlas/Inspection; professional interpretation belongs to Forge / Professional Validation.** `inspector.py::_setting_facts()` reports what was built and which recorded capability status applies. `BEZEL_WALL_CONTINUOUS` is pure topology (is it one solid), never a claim about stone coverage; `SETTING_COMPATIBILITY_STATUS` echoes the registry, never a judgement. |
| **SETTING-GOV-017** | **Existing current 4/6-prong ROUND behaviour must remain backward compatible.** `combined_metal_volume_mm3 == 341.44334316909976` exactly, prong volume `29.650351464580467` exactly, and all 12 round-stone Golden cases required zero baseline updates. The `RADIAL` strategy reproduces the original `_prong_positions()` + `prong_center_radius()` pair character-for-character. |
| **SETTING-GOV-018** | **Setting System must be extensible for future custom settings.** `SETTING_GENERATORS` is a real registry built lazily inside a cached function, not an `if/elif` chain, so a family is added by registering a generator plus a capability entry. `custom_setting` and `imported_setting_component` are recorded escape hatches in the Capability Coverage Guard, and any future custom setting must still use component roles, the attachment interface, inspection, and capability metadata. |

## Relationship to existing governance

This document sits alongside [`07-atlas/120-atlas-governance.md`](../07-atlas/120-atlas-governance.md), [`06-forge/090-forge-governance.md`](../06-forge/090-forge-governance.md), [`16-geometry-inspection/460-inspection-governance.md`](../16-geometry-inspection/460-inspection-governance.md), [`18-ring-architecture/520-jewelry-category-architecture.md`](../18-ring-architecture/520-jewelry-category-architecture.md), and [`20-stone/560-stone-governance.md`](../20-stone/560-stone-governance.md) — it supersedes none of them.

Two prior boundaries are what SETTING-GOV-001 and SETTING-GOV-016 make concrete here:

- **Sprint 16's category direction and Sprint 18's category-neutrality precedent.** Stone System proved a subsystem can be genuinely category-neutral with a real architecture test. Setting is the second such subsystem, and the first to sit *between* two others — it consumes Stone and is consumed by a category integration, so it has a boundary to defend in both directions.
- **ATLAS-GOV-002's Atlas/Forge split.** Setting reports geometric facts; only Forge interprets. This is why the prong rules were scoped in `validation/engine.py` rather than by adding a threshold to the Setting package.

## When an ADR is required

- Splitting the `prongs` compound into individually-named components (`prong_0` … `prong_n`), which would change component roles, preview manifests, export lists, and every Golden baseline.
- Replacing the outline-offset bezel construction with a different primitive.
- Moving the attachment interface, or letting a Setting compute its own attachment plane from category fields.
- Changing the girdle inset convention or the `RADIAL` placement formula (either would break SETTING-GOV-017).
- Introducing unrestricted custom-setting construction.
- Any change that violates SETTING-GOV-001 through 018 without superseding this document first.

## When an RFC is required

- A new Setting family (`channel`, `flush`, `bar`, `tension`, `bead`, `pave`) — each is a jewelry-domain extension, see [`../04-jewelry-domain/056-domain-extension-strategy.md`](../04-jewelry-domain/056-domain-extension-strategy.md).
- A new prong style (`CLAW`, `V_PRONG`, `SHARED_PRONG`). `V_PRONG` in particular is what real pear/marquise tip protection needs, and it is Sprint 23 territory.
- Introducing seat, bearing, or cutter geometry — these carry real manufacturing semantics and must not be added as a geometric side effect.
- Multi-stone settings, which are StoneArrangement concerns as much as Setting concerns.
