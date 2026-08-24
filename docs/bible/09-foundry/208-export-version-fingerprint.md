---
id: JM-BIBLE-208
title: Export Version Fingerprint
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-174
related_documents:
  - JM-BIBLE-201
implementation_status: planned
professional_validation: not_required
normative: true
---

# Export Version Fingerprint

## Addressing the Sprint 6 gap

[`08-alchemist/174-determinism-and-version-fingerprint.md`](../08-alchemist/174-determinism-and-version-fingerprint.md) found that only 2 of 8 conceptual fingerprint fields are recorded anywhere in current output. This document narrows the same question to exported artifacts specifically, and grounds every field in a real, checked value obtained during this Sprint rather than repeating the same unverified gap.

## Real values, checked during Sprint 7

| Field | Real value | Status |
|---|---|---|
| CadQuery version | `2.8.0` | PARTIAL — real and queryable (`importlib.metadata.version('cadquery')`), never recorded by any JewelMind code |
| OpenCascade version | `7.9.3.1.1` (OCP binding); STEP file headers independently show `"Open CASCADE 7.9"` | PARTIAL — empirically present in two places, never extracted as structured metadata |
| Mesh tolerance | `0.1` (default) | CURRENT — `JewelryDefinition.preview.meshTolerance`, already threaded into every STL export |
| Angular tolerance | `0.2` (default) | CURRENT — same |
| Generator version | `0.1.0` | CURRENT — `GENERATOR_VERSION`, already returned in every API response, but scoped to the geometry generator, not the exporter |
| Source compilation hash | n/a | PLANNED — depends on `compilationHash`, which does not exist |
| STEP format options | none passed anywhere | PLANNED — nothing to record; no schema variant is ever chosen |
| STL format options | binary, always | PARTIAL — real and test-verified, never recorded as structured metadata |

No code anywhere assembles these fields into a single `ExportVersionFingerprint` object today. `specs/foundry/v1/test-vectors/version-fingerprint-vectors.json` is the first place these values have been collected together, specifically to ground `export-version-fingerprint.schema.json` in checked values rather than invented ones — per FOUNDRY-GOV-014's "do not fake current version information" spirit, applied here to version metadata rather than interoperability claims.

## Why this matters for STEP specifically

[`197-step-export-contract.md`](197-step-export-contract.md) already shows that OCCT's version (`7.9`) is visible inside every STEP file's own header text, purely as an artifact of how OpenCascade writes its translator identification — not because JewelMind chose to record it. A future `ExportVersionFingerprint` implementation could extract this from the file it just wrote rather than needing a separate `importlib.metadata` call, but no code does this today.

## Do not fake current version information

Every field above is marked `CURRENT`, `PARTIAL`, or `PLANNED` based on an actual code inspection or an actual command run against the real environment during this Sprint — never assumed. Where a field's real value exists but is not assembled anywhere, that is stated explicitly as the gap, rather than the schema silently implying the field is already populated.
