---
id: JM-BIBLE-501
title: Golden Model Contract
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
  - JM-BIBLE-502
  - JM-BIBLE-510
implementation_status: current
professional_validation: not_required
normative: true
---

# Golden Model Contract

`GoldenModel` (`backend/jewelmind/geometry_quality/models.py`) is the accepted, on-disk software regression reference for one golden case. Every field below is read directly from that class.

## Fields

| Field | Type | Meaning |
|---|---|---|
| `goldenId` | `str` | Stable case identifier, e.g. `SOL-001-default-solitaire`. Never renamed once published (mirrors FORGE-GOV-001's "stable ID" discipline at this layer). |
| `description` | `str` | Human-readable summary of the case. |
| `sourceJDLPath` | `str` | Path to the case's `design.json`, relative to the repository root, e.g. `goldens/solitaire-v1/SOL-001-default-solitaire/design.json`. |
| `definitionHash` | `str` | The real `JewelryDefinition`'s `definitionHash`, taken from `model.definition_hash` after generation — never computed independently by this subsystem. |
| `versionFingerprint` | `VersionFingerprint` | See [`510-version-fingerprint-policy.md`](510-version-fingerprint-policy.md). |
| `expectedComponents` | `list[str]` | Sorted component IDs present in the snapshot at creation/acceptance time. |
| `geometrySnapshot` | `GeometrySnapshot` | The accepted geometric facts — see below. |
| `artifactExpectations` | `list[ArtifactExpectation]` | Defaults to `DEFAULT_ARTIFACT_EXPECTATIONS` (`harness.py`) unless a prior accepted golden already carried its own. |
| `baselineStatus` | `BaselineStatus` | `INITIAL \| STABLE \| CANDIDATE \| KNOWN_LIMITATION`. |
| `knownLimitations` | `list[str]` | Free-text notes about expected, non-regression conditions (e.g. an expected Forge warning). Never a place to silence a real regression. |
| `createdAt` | `str` | ISO-8601 timestamp of candidate/initial generation. |
| `acceptedAt` | `str \| None` | ISO-8601 timestamp set only by `accept_candidate_baseline()`. `None` for a candidate that has never been accepted. |
| `notes` | `str` | Free text; `accept`'s `--reason` is appended here (see [`507-golden-update-policy.md`](507-golden-update-policy.md)). |

`ArtifactExpectation` (embedded, one per requested export format):

| Field | Type | Meaning |
|---|---|---|
| `artifactType` | `Literal["STEP","STL","JSON","SPECIFICATION"]` | Which Foundry export format this expectation covers. |
| `nonEmpty` | `bool` | Defaults `True`. |
| `minSolidCount` | `int \| None` | Optional minimum solid count for the exported production-metal shape. |

## `baselineStatus` in practice

Only two of the four `BaselineStatus` values are ever actually assigned by the real code: `generate_candidate_baseline()` always sets `"CANDIDATE"`, and `accept_candidate_baseline()` always sets `"STABLE"` (`harness.py`). `"INITIAL"` and `"KNOWN_LIMITATION"` are declared as valid enum members but are not written by any current code path — the real Golden Suite's `generate_golden_fixtures.py` sets `baselineStatus="STABLE"` directly at initial creation, not `"INITIAL"`, and a case with expected warnings (e.g. `SOL-009-warning-only-large-stone-four-prong`) still carries `baselineStatus="STABLE"` with a non-empty `knownLimitations` list, not `"KNOWN_LIMITATION"`. This is recorded here as an accurate description of current behavior, not a defect to silently paper over.

## No timestamp field is regression-sensitive

`createdAt` and `acceptedAt` are informational only. `compare_snapshot()` never reads either field, and neither appears anywhere in `GeometrySnapshot` (see [`503-quality-signal-model.md`](503-quality-signal-model.md)'s discussion of volatile-field exclusion by construction). A Golden Model accepted a year apart from another, with everything else identical, compares as `PASS`.

## Relationship to `GeometrySnapshot`

`GoldenModel.geometrySnapshot` is a `GeometrySnapshot` (`AssemblySnapshot` + `list[ComponentSnapshot]` + `list[RelationshipSnapshot]` + `DesignConsistencySnapshot`, each field built in `snapshot.py::build_snapshot_from_report()` from a real `GeometryInspectionReport`). This document defines the container; [`503-quality-signal-model.md`](503-quality-signal-model.md) defines what each embedded fact means for regression purposes, and [`../16-geometry-inspection/README.md`](../16-geometry-inspection/README.md) is the authoritative source for what Sprint 14 measured to produce that report in the first place — this document does not repeat that.
