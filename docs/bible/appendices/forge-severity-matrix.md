---
id: JM-BIBLE-A16
title: "Appendix: Forge Severity Matrix"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-099
related_documents: []
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Forge Severity Matrix

From `specs/forge/v1/test-vectors/severity-vectors.json`, cross-checked against a live run of `validate_definition()` in `backend/tests/test_forge_registry.py`.

| Rule ID | Severity | Blocking | Conceptual blocking scope |
|---|---|---|---|
| `JM-RING-001` | error | Yes | GENERATION, ALL_EXPORTS |
| `JM-RING-002` | error | Yes | GENERATION, ALL_EXPORTS |
| `JM-RING-003` | information / warning (value-dependent) | No | NONE |
| `JM-BAND-001` | error | Yes | GENERATION, ALL_EXPORTS |
| `JM-BAND-002` | error / warning (value-dependent, two branches) | Conditional | GENERATION, ALL_EXPORTS (error branch only) |
| `JM-BAND-003` | warning | No | NONE |
| `JM-STONE-001` | error | Yes | GENERATION, ALL_EXPORTS |
| `JM-STONE-002` | error | Yes | GENERATION, ALL_EXPORTS |
| `JM-PRONG-001` | error | Yes | GENERATION, ALL_EXPORTS |
| `JM-PRONG-002` | error / warning (value-dependent, two branches) | Conditional | GENERATION, ALL_EXPORTS (error branch only) |
| `JM-PRONG-003` | warning | No | NONE |
| `JM-PRONG-004` | error | Yes | GENERATION, ALL_EXPORTS |
| `JM-SETTING-001` | error | Yes | GENERATION, ALL_EXPORTS |
| `JM-SETTING-002` | warning | No | NONE |
| `JM-MANUFACTURING-001` | warning | No | NONE |
| `JM-GEOMETRY-001` | error | Yes | GENERATION, ALL_EXPORTS |
| `FORGE-SCHEMA-001` | fatal (structural) | Yes | GENERATION, ALL_EXPORTS |
| `FORGE-SAFETY-001` | fatal (structural) | Yes | GENERATION, ALL_EXPORTS |
| `FORGE-SAFETY-002` | fatal (structural) | Yes | GENERATION, ALL_EXPORTS |
| `FORGE-GEOM-001` | warning | No | NONE |
| `FORGE-EXPORT-001` | error-equivalent | Yes | STEP_EXPORT, STL_EXPORT |

## Severity distribution

| Severity | Count |
|---|---|
| error (fixed) | 10 |
| error/warning (value-dependent) | 2 |
| warning (fixed) | 5 |
| information (as one branch of a value-dependent rule) | 1 (part of `JM-RING-003`) |
| fatal (structural, pre-`ValidationResult`) | 3 |

**No rule currently uses `FATAL` as a `ValidationResult.severity` value** — `FATAL` is reserved in the conceptual model for FORGE-0 structural rejections, which never produce a `ValidationResult` at all (see [`06-forge/099-severity-and-blocking-semantics.md`](../06-forge/099-severity-and-blocking-semantics.md)).
