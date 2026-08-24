---
id: JM-BIBLE-081
title: Schema Versioning and Migrations
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-060
related_documents:
  - JM-BIBLE-A12
implementation_status: current
professional_validation: not_required
normative: true
---

# Schema Versioning and Migrations

## Version axes that actually exist today, and their current values

| Axis | Current value | Source | Independent of the others? |
|---|---|---|---|
| Backend package version | `0.1.0` | `backend/pyproject.toml` | Yes |
| Frontend package version | `0.0.0` | `frontend/package.json` | Yes — **not currently synchronized with the backend package version**, a real, already-existing fact, not a Sprint 3 change |
| JDL schema version | `"0.1.0"` | `SCHEMA_VERSION` / `schemaVersion` field, `backend/jewelmind/domain/schema.py` | Yes |
| Geometry generator version | `"0.1.0"` | `GENERATOR_VERSION`, `backend/jewelmind/geometry/constants.py` | Yes — currently equal to the schema version by coincidence, not by any code linking them together |
| Rule-set version | Not versioned separately today — `validation/engine.py`'s sixteen rules have no version identifier of their own | n/a | n/a |
| Artifact version | Not versioned separately today — STEP/STL/JSON/specification exports carry no format-version marker beyond the definition's own `schemaVersion` (embedded in the JSON/specification exports) | n/a | n/a |

Only **one JDL schema version has ever been released: `0.1.0`.** Every compatibility statement below is therefore about what happens today with a single-version system, not a demonstrated multi-version migration.

## PATCH / MINOR / MAJOR definitions for JDL schema changes

| Level | Definition | Example (hypothetical, not implemented) |
|---|---|---|
| PATCH | A change that does not alter accepted documents or their meaning — a documentation fix, a test addition, a code comment | Fixing this document's own prose |
| MINOR | An additive, backward-compatible change: a new optional field with a default, a new enum member appended to an existing list, a new semantic rule that only adds diagnostics (never changes acceptance of a previously-valid document from valid to invalid) | Adding a `flat_court` band profile alongside `comfort_fit`/`flat` |
| MAJOR | A breaking change: removing or renaming a field, changing a field's type, removing an enum member, tightening a previously-permissive structural constraint so a previously-valid document becomes invalid, or changing the canonicalization/hashing algorithm (see [`076-canonicalization-and-definition-hashing.md`](076-canonicalization-and-definition-hashing.md)) | Removing `ring.sizeSystem` or changing `angularTolerance`'s unit from radians to degrees |

## Migration requirements

1. A MAJOR change requires bumping `schemaVersion` to a new literal and updating `Literal["0.1.0"]` in `backend/jewelmind/domain/schema.py` to accept both the new and (temporarily, if a migration path is offered) the old version.
2. A migration path, if offered, must be an explicit, tested transform function — never an implicit "best guess" interpretation of an old document under new rules.
3. Every MAJOR/MINOR change updates [`jdl-version-compatibility-matrix.md`](../appendices/jdl-version-compatibility-matrix.md) and `specs/jdl/v1/test-vectors/compatibility-vectors.json` in the same change, per JDL-GOV-002.
4. No migration may silently alter a `definitionHash` for a document whose `schemaVersion` field value is unchanged (see [`076-canonicalization-and-definition-hashing.md`](076-canonicalization-and-definition-hashing.md)'s proposed hash-versioning scheme for how a hash-algorithm change would be introduced instead).

## Compatibility matrix (current)

See [`specs/jdl/v1/test-vectors/compatibility-vectors.json`](../../../specs/jdl/v1/test-vectors/compatibility-vectors.json) for the generated, tested vectors and [`jdl-version-compatibility-matrix.md`](../appendices/jdl-version-compatibility-matrix.md) for the narrative table. Today: `schemaVersion: "0.1.0"` is accepted; every other value, of any type, is rejected. No migration path has ever been implemented, because no second version has ever existed.
