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
