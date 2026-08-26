---
id: JM-BIBLE-A12
title: "Appendix: JDL Version Compatibility Matrix"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-081
related_documents:
  - JM-BIBLE-A09
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: JDL Version Compatibility Matrix

Reflects only versions that actually exist. See [`081-schema-versioning-and-migrations.md`](../05-jdl/081-schema-versioning-and-migrations.md) for PATCH/MINOR/MAJOR definitions and [`specs/jdl/v1/test-vectors/compatibility-vectors.json`](../../../specs/jdl/v1/test-vectors/compatibility-vectors.json) for the machine-checked vectors this table is generated from.

## `schemaVersion` compatibility

| Input `schemaVersion` | Accepted | Reason |
|---|---|---|
| `"0.1.0"` | Yes | The only released JDL schema version |
| `"0.2.0"` | No | Does not exist |
| `"0.0.9"` | No | Does not exist |
| `"0.1"` | No | Not a byte-exact match for the literal; no semver parsing/coercion |
| `0.1` (JSON number) | No | Wrong type — rejected by strict-mode type checking before any literal comparison |

## Version-axis snapshot (current, single point in time)

| Axis | Current value |
|---|---|
| Backend package version | `0.1.0` |
| Frontend package version | `0.0.0` |
| JDL schema version | `0.1.0` |
| Geometry generator version | `0.1.0` |

## Migration paths implemented

**None.** Only one schema version has ever existed, so no migration has ever been necessary or built. This row will be updated the day a second schema version ships, per [`081-schema-versioning-and-migrations.md`](../05-jdl/081-schema-versioning-and-migrations.md) rule 3.

## MINOR change history (per JDL-GOV-002)

| Sprint | Change | `schemaVersion` | Notes |
|---|---|---|---|
| 17 | Added `band.widthTaper`/`band.thicknessTaper` (`BandTaperSpec`: `mode`, `bottomRatio`), both optional with a `mode: "NONE"` default | `0.1.0` (unchanged) | An additive, backward-compatible MINOR change per [`081`](../05-jdl/081-schema-versioning-and-migrations.md)'s own definition and worked example. A real, discovered side effect: `definitionHash` changes for any previously-recorded document once regenerated under the new schema, because `canonical_json()` includes every field's default value — this is not a "migration silently altering a hash" (rule 4), since no transform is offered or applied to old documents; it is normalization-time default-filling producing a different (still deterministic, still correct) canonical form, the same mechanism rule 4 was written before this case existed. See [`docs/bible/19-shank/556-current-band-migration.md`](../19-shank/556-current-band-migration.md) for the full account and every spec/test-vector file updated because of it. |
