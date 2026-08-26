---
id: JM-BIBLE-516
title: Current Code Mapping and Gaps
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-QUALITY-README
  - JM-BIBLE-500
related_documents:
  - JM-BIBLE-160
  - JM-BIBLE-120
  - JM-BIBLE-460
  - JM-BIBLE-190
implementation_status: current
professional_validation: not_required
normative: true
---

# Current Code Mapping and Gaps

## Existing layers Geometry Quality builds on (unchanged this Sprint)

- **Geometry builders** (Sprint 5) — `backend/jewelmind/geometry/components/*.py` (band, stone, prongs, basket) + `backend/jewelmind/geometry/assemblies/solitaire.py::build_solitaire_ring()`. Unchanged; `generate_snapshot()` calls this directly.
- **ModelService orchestration** (Sprint 8/Alchemist) — `backend/jewelmind/services/model_service.py`. Unchanged; Geometry Quality does not go through `ModelService`, it calls `build_solitaire_ring()`/`inspect_model()` directly, same as `ModelService` itself does.
- **Sprint 14 inspector** — `backend/jewelmind/geometry/inspection/inspector.py::inspect_model()` and the rest of `geometry/inspection/`. Unchanged; `snapshot.py::generate_snapshot()` runs it and normalizes its `GeometryInspectionReport` into a `GeometrySnapshot`.
- **Foundry exporters** (Sprint 9) — `backend/jewelmind/exporters/step_exporter.py::export_step()`, `stl_exporter.py::export_stl()`, `integrity.py::binary_stl_triangle_count()`. Unchanged; reused as-is by `artifact_regression.py`'s `step_roundtrip_check()`/`stl_structure_check()`.
- **`definitionHash`** (Sprint 1/2) — `backend/jewelmind/utils/hashing.py::definition_hash()`. Unchanged; every `GoldenModel.definitionHash` and `GeometrySnapshot.definitionHash` is this exact value, never a new hash.

## The new `backend/jewelmind/geometry_quality/` module

10 files, 1,121 real lines total (`wc -l` run directly against the module):

| File | Lines | Purpose |
|---|---|---|
| `__init__.py` | 20 | Public entry points: `generate_candidate_baseline`, `generate_snapshot`, `verify_all_goldens`, `verify_golden`. |
| `artifact_regression.py` | 173 | `step_roundtrip_check()`, `stl_structure_check()` — STEP/STL regression, never byte-for-byte. |
| `cli.py` | 118 | `verify-all` / `verify` / `generate-candidate` / `diff` / `accept` developer/CI commands. |
| `compare.py` | 205 | `compare_snapshot()` — the structured comparison engine and severity classification. |
| `fingerprint.py` | 55 | `collect_fingerprint()` — real version identifiers (see [`510-version-fingerprint-policy.md`](510-version-fingerprint-policy.md)). |
| `harness.py` | 126 | `verify_golden()`, `verify_all_goldens()`, `generate_candidate_baseline()`, `accept_candidate_baseline()`. |
| `models.py` | 217 | All Pydantic types: `VersionFingerprint`, `GeometrySnapshot`, `GoldenModel`, `GeometryDiff`, `QualityResult`, etc. |
| `registry.py` | 63 | `load_golden()`/`save_golden()`/`load_design()`/`list_golden_ids()` — the only disk I/O boundary for `goldens/`. |
| `snapshot.py` | 116 | `generate_snapshot()` — runs the real pipeline and builds a normalized `GeometrySnapshot`. |
| `version.py` | 28 | `QUALITY_VERSION`, `ABSOLUTE_COMPARISON_TOLERANCE_MM`, `RELATIVE_COMPARISON_TOLERANCE`. |

## New test fixtures

4 new test files under `backend/tests/`, 47 new tests total, collected and verified directly (`pytest --collect-only`):

- `test_geometry_quality_snapshot.py` — 16 tests (`TestComponentPresence`, `TestSolidCount`, `TestConnectivity`, `TestIntersectionRelations`, `TestProngCount`, `TestStoneRole`, `TestVolatileFieldNormalization`, `TestMetadataOnlyEquivalence`).
- `test_geometry_quality_harness.py` — 15 tests (`TestRealGeneration`, `TestHumanReadableDiff`, `TestIntentionalFailureDetection`, `TestRepeatability`, `TestNoAutoUpdate`, `TestVersionFingerprint`).
- `test_geometry_quality_artifacts.py` — 6 tests (`TestStepRoundtrip`, `TestStlStructure`, `TestNoBinaryStepDeterminismClaim`).
- `test_geometry_quality_schemas.py` — 10 tests (8 module-level functions + `TestNoProfessionalClaim`).

## The new Golden Suite

`goldens/solitaire-v1/` — 9 real cases (`design.json` + `snapshot.json` each) + `manifest.json`. See [`511-current-solitaire-golden-suite.md`](511-current-solitaire-golden-suite.md) for the full inventory.

## The new version information

`VersionFingerprint` — see [`510-version-fingerprint-policy.md`](510-version-fingerprint-policy.md) for its 7 fields and their real sources.

## Gaps — stated honestly, none solved this Sprint

a. **`GeometryPlan` still does not exist as a materialized object.** Carried forward unchanged from Sprint 6/Alchemist ([`08-alchemist/README.md`](../08-alchemist/README.md), ALCHEMIST-GOV-004). Geometry Quality calls `build_solitaire_ring()` directly, the same as `ModelService` does — it does not introduce or require a `GeometryPlan`.

b. **`compilationHash` still does not exist, only `definitionHash`.** Carried forward unchanged from [`08-alchemist/175-definition-hash-vs-compilation-hash.md`](../08-alchemist/175-definition-hash-vs-compilation-hash.md). `VersionFingerprint` records overlapping information (compiler/rule-set/kernel versions) but is attached to `GoldenModel`/`GeometryDiff`, not folded into any hash on `GeneratedModel` (see [`510-version-fingerprint-policy.md`](510-version-fingerprint-policy.md)).

c. **No kernel-neutral model identity beyond `definitionHash` + `VersionFingerprint`.** There is no single identifier that answers "would this design compile to the same output today as it did when this baseline was accepted" other than comparing the two fingerprints field-by-field plus running a full `compare_snapshot()`. That is a workflow, not an identity.

d. **Topology variability across kernel versions is now VISIBLE, not auto-resolved.** `VERSION_REVIEW_REQUIRED` (QUALITY-GOV-010) surfaces a kernel-driven topology difference for human review — it does not attempt to auto-classify it as safe or unsafe. This is intentional, restated explicitly here so it is never mistaken for an oversight: automatically trusting a kernel-driven topology change would be exactly the kind of silent regression this Sprint exists to prevent.

e. **No external CAD-application regression testing exists.** `step_roundtrip_check()` re-imports JewelMind's own STEP export using `cadquery.importers.importStep()` — the same library that wrote the file, not an independent third-party CAD application. This is the same honest limitation [`09-foundry/209-cad-interoperability-philosophy.md`](../09-foundry/209-cad-interoperability-philosophy.md) already documents at the export layer (`EXPORT_SUPPORTED` achieved; `IMPORT_TESTED`/`WORKFLOW_VALIDATED` not attempted) — this Sprint does not change that finding, and does not claim otherwise anywhere in `artifact_regression.py`'s docstrings or this Bible section.

f. **No professional geometry approval exists.** By design — Sprint 13's active `ValidationRecord` registry stays at zero. See [`514-professional-validation-boundary.md`](514-professional-validation-boundary.md).

g. **No physical manufacturing baseline exists.** No physical prototype of any Golden case, or any other JewelMind geometry, has ever been made. Nothing in `goldens/solitaire-v1/` claims otherwise (enforced by `TestNoProfessionalClaim`).

None of these seven gaps is attempted or partially solved by this Sprint — each is either an unchanged carry-forward from an earlier Sprint's own documented gap, or a deliberate, permanent boundary this subsystem is designed to respect, not erode.

## Cross-references

- [`08-alchemist/174-determinism-and-version-fingerprint.md`](../08-alchemist/174-determinism-and-version-fingerprint.md), [`175-definition-hash-vs-compilation-hash.md`](../08-alchemist/175-definition-hash-vs-compilation-hash.md) — gaps (a)/(b)/(c).
- [`09-foundry/209-cad-interoperability-philosophy.md`](../09-foundry/209-cad-interoperability-philosophy.md) — gap (e), in full.
- [`514-professional-validation-boundary.md`](514-professional-validation-boundary.md) — gap (f), in full.
- [`517-open-geometry-quality-questions.md`](517-open-geometry-quality-questions.md) — open questions arising from these gaps.
