---
id: JM-BIBLE-485
title: Inspection Versioning
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-INSPECTION-README
  - JM-BIBLE-460
related_documents:
  - JM-BIBLE-481
  - JM-BIBLE-486
implementation_status: current
professional_validation: not_required
normative: true
---

# Inspection Versioning

## `INSPECTION_VERSION` is a separate axis from `GENERATOR_VERSION`

```python
INSPECTION_VERSION = "1.0.0"
```

(`backend/jewelmind/geometry/inspection/version.py`.) This is independent of `GENERATOR_VERSION = "0.1.0"` (`backend/jewelmind/geometry/constants.py`). The two version fields answer two different questions about the same generated model:

- `geometryGeneratorVersion` (on `GeneratedModel`, carried through unchanged into `GeometryInspectionReport.geometryGeneratorVersion`) — what code path *generated* this geometry.
- `inspectionVersion` (on `GeometryInspectionReport`, stamped on every `GeometricFact` too) — what code, and what definition of each fact, *measured* the geometry that was generated.

A change to what inspection measures — e.g. redefining connectivity, adding a new fact type, changing a diagnostic's wording — is a different kind of change than a change to what geometry gets built, and the two version numbers can and will diverge independently over time. Both are currently recorded on every `GeometryInspectionReport` (see [`481-inspection-result-model.md`](481-inspection-result-model.md)), so a caller can always tell which axis moved.

## Change classification (`specs/geometry-inspection/v2/inspection-version.schema.json`)

```json
"changeLevel": {
  "enum": ["PATCH", "MINOR", "MAJOR"],
  "description": "PATCH: diagnostic wording only. MINOR: a new optional fact. MAJOR: a changed definition of an existing fact (e.g. connectivity/intersection semantics)."
}
```

| Level | Real example (hypothetical, not yet done) |
|---|---|
| `PATCH` | Rewording an `InspectionDiagnostic.message` string without changing its `code`, `severity`, or the condition that triggers it. |
| `MINOR` | Adding a new `FactType` (e.g. a future local-thickness fact) alongside the existing 16, without changing how any existing fact is computed or what it means. |
| `MAJOR` | Redefining `CONTACT_TOLERANCE_MM`'s role in connectivity (e.g. switching the connectivity basis from `DISTANCE` to `INTERSECTION`, see [`480-assembly-graph-model.md`](480-assembly-graph-model.md)), or changing what `INTERSECTS` vs. `TOUCHES` means for `IntersectionStatus`. |

The `inspectionVersion` field this schema classifies changes against is the same `"1.0.0"` string every `GeometryInspectionReport` and every `GeometricFact` carries — a version bump would apply uniformly across the whole report, not per-fact.

## No bump has occurred yet

This Sprint ships `INSPECTION_VERSION = "1.0.0"` as the first real version — there is no prior inspection version to compare against, and no historical `GeometryInspectionReport` from before this Sprint exists to be affected by a classification decision. `1.0.0` is the baseline, not a bump from something earlier.

## Not yet part of Alchemist's compilation-provenance/fingerprint model

[`08-alchemist/174-determinism-and-version-fingerprint.md`](../08-alchemist/174-determinism-and-version-fingerprint.md) documents the real, current gap in Alchemist's conceptual `CompilationEnvironmentFingerprint`: "Only 2 of 8 conceptual fingerprint fields are recorded anywhere in current output" (JDL schema version and Atlas generator version). `inspectionVersion` is not one of the fields that document tracks at all — it predates this Sprint. As of Sprint 14, `inspectionVersion` is recorded on `GeometryInspectionReport`, but it does not participate in `definitionHash` (which stays purely a JDL-input hash — see [`08-alchemist/175-definition-hash-vs-compilation-hash.md`](../08-alchemist/175-definition-hash-vs-compilation-hash.md)), and no `compilationHash` exists yet for it to participate in either. This is a real, honest, deferred integration point: a future `compilationHash` that folds in compiler/kernel/Forge-rule-set versions (per `174-determinism-and-version-fingerprint.md`) would be the natural place to also fold in `inspectionVersion`, but that work has not been done, and this document does not claim otherwise.

`kernelVersion` (`cadquery.__version__`, see [`481-inspection-result-model.md`](481-inspection-result-model.md)) is, incidentally, the first place any generated-model artifact records an actual CadQuery build identifier — `174-determinism-and-version-fingerprint.md`'s own table lists "CadQuery version ... Recorded anywhere today? **No**" as of Sprint 8/13; this Sprint's `GeometryInspectionReport.kernelVersion` is new, real, per-generation evidence toward that fingerprint gap, even though it is not yet wired into the fingerprint concept itself.

## Cross-references

- [`481-inspection-result-model.md`](481-inspection-result-model.md) — where `inspectionVersion`/`kernelVersion` are actually stamped.
- [`486-inspection-determinism.md`](486-inspection-determinism.md) — determinism is about identical geometry under the *same* inspection version; a version bump is a separate, explicit event this document classifies.
- [`08-alchemist/174-determinism-and-version-fingerprint.md`](../08-alchemist/174-determinism-and-version-fingerprint.md) / [`175-definition-hash-vs-compilation-hash.md`](../08-alchemist/175-definition-hash-vs-compilation-hash.md) — the compiler-level fingerprint gap this document explains inspection's real, current non-participation in.
