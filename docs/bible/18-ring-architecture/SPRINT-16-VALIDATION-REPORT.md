---
id: JM-BIBLE-SPRINT16-REPORT
title: "Sprint 16 Validation Report — Ring Architecture v2 / Multi-Category Ready"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-RING-README
  - JM-BIBLE-520
related_documents:
  - JM-BIBLE-536
implementation_status: current
professional_validation: not_required
normative: false
---

# Sprint 16 Validation Report — Ring Architecture v2 / Multi-Category Ready

## Ring Architecture documents created

25: `README.md`, `520`–`537` (18 numbered docs), this validation report, and 5 new appendices (`A105`–`A109`).

## Machine-readable schemas created

11: 3 under `specs/jewelry-architecture/v1/` (category identity, capability, extension contract) + 8 under `specs/ring/v2/` (definition, sizing, shank, shoulder, head, stone arrangement, component graph, family).

## Jewelry category registry implemented: yes

`backend/jewelmind/jewelry_category/registry.py::CATEGORY_CAPABILITIES` — 6 real entries, mirrored at `specs/jewelry-architecture/v1/category-registry.json` and re-derived live by `test_ring_architecture_schemas.py::test_category_registry_matches_the_real_capability_registry_live`.

## Current generatable categories: ring

Verified: `test_only_ring_is_generation_supported_in_the_registry` confirms exactly one `generationSupported: true` entry.

## Planned non-generatable categories registered: 5

`earring`, `pendant`, `bracelet`, `necklace`, `charm` — each `status: "planned"`, `generationSupported: false`, `supportedFamilies: []`.

## RingDefinition v2 implemented: yes

`backend/jewelmind/ring/models.py` — `RingDefinition` composed from `RingSizing`, `ShankDefinition`, `ShoulderDefinition`, `RingHeadDefinition`, `StoneArrangementDefinition`, `SettingAttachmentDefinition` (114 lines).

## Current solitaire migrated/mapped: yes

`ring_definition_from_jdl()` runs on every real ring generation (inside `ring/families.py::generate_ring()`), not merely available as an unused function — see [`533-solitaire-migration-model.md`](533-solitaire-migration-model.md) for the full field-by-field table.

## Category dispatch implemented: yes

`jewelmind.jewelry_category.dispatch.generate_for_category()` — a generic function taking a category string, a payload, and a registry; it has never imported or referenced `jewelmind.ring` at its own module-import time.

## Ring family dispatch implemented: yes

`jewelmind.ring.families.generate_ring()` — dispatches on `definition.jewelry.style` through `RING_FAMILY_GENERATORS`, currently `{"solitaire": build_solitaire_ring}`; 7 reserved PLANNED family names exist in `RingFamilyId` with no generator, proving the dispatch mechanism is not solitaire-specific.

## Shared/category-specific domain boundaries formalized: yes

[`521-shared-vs-category-specific-domain.md`](521-shared-vs-category-specific-domain.md) — the real audit backing `ring/models.py`'s field ownership and `jewelry_category/forge_scope.py`'s rule-scope classification.

## Test-only non-ring category implemented: yes

`backend/tests/test_jewelry_category_extension.py::TestNonRingCategoryExtension` — a `DummyPendantDefinition` (unrelated to `JewelryDefinition`/`RingDefinition`) dispatches through the exact same `generate_for_category()` function `ring` uses.

## Production exposure of dummy category: no

Verified structurally: `test_dummy_category_is_absent_from_the_real_production_registry` and `test_dummy_category_cannot_be_reached_through_generate_jewelry` both assert `"dummy_pendant"` is absent from `CATEGORY_CAPABILITIES` and the real category-generator registry.

## Ring-specific leaks discovered: 3

1. `ModelService.generate()` called `build_solitaire_ring()` directly — the one monolithic call site the brief's architecture goal targeted.
2. `geometry_quality/snapshot.py`'s Golden fixture builder had the identical direct call.
3. `designer/capability.py`'s `KNOWN_UNSUPPORTED_CONCEPTS` hardcoded 4 category-unsupported message strings independently of any capability source of truth.

## Ring-specific leaks removed: 3

All 3 fixed this Sprint: (1) and (2) now dispatch through `generate_jewelry()`; (3) now sources its 4 messages from `jewelry_category.registry.get_capability(category).message`. See [`536-current-code-mapping-and-gaps.md`](536-current-code-mapping-and-gaps.md) for the real diff-level detail.

## Current JDL backward compatible: yes

`backend/jewelmind/domain/schema.py` was not modified. `ring_definition_from_jdl()` is a pure, additive adapter over the unmodified schema — never a competing input format (JEWELRY-ARCH-GOV-008).

## Golden solitaire cases passed unchanged: 9

All 9 real cases in `goldens/solitaire-v1/` verify `PASS`/`PASS_WITH_KNOWN_LIMITATIONS` through the new dispatch path, with their accepted `snapshot.json` files byte-for-byte unchanged on disk.

## Golden baseline updates required: 0

Confirmed by `git status` showing no modifications under `goldens/` after this Sprint's full implementation and test run.

## Geometry changes introduced intentionally: 0

This Sprint changed architecture (what calls geometry code and how), never geometry itself. `build_solitaire_ring()` was not modified.

## Professional validation statuses altered: no

Sprint 13's active validation registry (`specs/professional-validation/v1/current-validation-registry.json`) remains untouched — still zero records.

## Backend tests passed

**808/808** (`pytest -q`), including 44 new tests across `test_jewelry_category_extension.py` (16), `test_ring_architecture.py` (20), and `test_ring_architecture_schemas.py` (8), plus 1 pre-existing test in `test_api_hardening.py` fixed (not newly added) after the dispatch rewiring changed its correct monkeypatch target.

## Frontend tests passed

**137/137** — unaffected; this Sprint made no frontend changes.

## Architecture/geometry/Golden tests passed

44 new architecture tests + the full pre-existing Geometry Inspection (40), Geometry Quality (49), and Professional Validation suites, all verified green as part of the same full `pytest -q` run.

## Frontend build: pass

`npm run build` succeeds unchanged (pre-existing >500kB single-chunk warning, unrelated to this Sprint).

## GitHub Actions: result

See the top-level Sprint 16 delivery message for the final run link and status.

## Two real, non-obvious bugs found and fixed during this Sprint's own implementation

1. **A genuine circular import**, found empirically (not merely reasoned about) by running `python -c "import jewelmind.ring"` on a fresh interpreter: `jewelmind.ring.adapter` imports `jewelmind.jewelry_category.errors`, which triggers `jewelry_category/__init__.py`, which (at the time) eagerly built its category-generator registry by importing `jewelmind.ring.families` — which in turn imports `jewelmind.ring.adapter`, still mid-import. Fixed by deferring that cross-package import inside a cached, lazily-evaluated function (`_category_generators()`), called only on the first real dispatch, well after both packages have finished loading. Verified fixed from both import orders (`import jewelmind.ring` first, and `import jewelmind.jewelry_category` first) plus an end-to-end dispatch call.
2. **A monkeypatch-target break in a pre-existing test**: `test_api_hardening.py::test_generation_failure_maps_to_model_generation_failed` patched `jewelmind.services.model_service.build_solitaire_ring`, a name that no longer exists in that module after the dispatch rewiring. The first fix attempt (patching `jewelmind.ring.families.build_solitaire_ring`, the new "correct-looking" location) still failed, because `RING_FAMILY_GENERATORS = {"solitaire": build_solitaire_ring}` captures the function reference at dict-construction time — patching the module attribute afterward does not change the dict's stored reference. Fixed by patching the dict entry itself (`monkeypatch.setitem(ring_families.RING_FAMILY_GENERATORS, "solitaire", _boom)`).

Both were found and fixed before this Sprint's commit — neither shipped as a latent bug.

---

**Sprint 17 — Band & Shank System v1** — replace the current uniform band implementation with a reusable parametric shank subsystem supporting controlled profiles, width/thickness variation, tapering and connection interfaces while preserving Golden regression safety.
