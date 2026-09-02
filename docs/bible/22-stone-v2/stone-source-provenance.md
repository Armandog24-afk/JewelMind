---
id: JM-BIBLE-612
title: "Stone Source Provenance"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-02
source_of_truth: true
depends_on:
  - JM-BIBLE-601
related_documents:
  - JM-BIBLE-609
  - JM-BIBLE-611
implementation_status: current
professional_validation: not_required
normative: true
---

# Stone Source Provenance

`StoneSourceProvenance` records where a stone's geometry came from. It travels
into the technical specification, into Geometry Inspection facts, and into the
professional review package.

## The record

| Field | Populated for |
|---|---|
| `sourceMode` | always |
| `sourceAssetHash` | imported |
| `sourceAssetName` | imported, custom (as the outline label) |
| `originalUnit` | imported, custom |
| `normalizationOperations` | always (possibly empty) |
| `generatorVersion` | parametric, custom, measured |
| `importerVersion` | imported |
| `measurementSource` | measured |
| `measurementDate` | measured |
| `operatorNote` | measured |

## Two rules that shape the whole model

### 1. Provenance must be TRUE

`normalizationOperations` records every operation **actually applied**.

An entry claiming an operation the geometry did not receive is a worse defect
than a missing entry — a missing entry prompts a question, a false entry answers
it wrongly. Sprint 20 shipped exactly that bug briefly: mesh imports recorded
`UNIT_CONVERSION:cm->mm` while the triangulation had not moved at all, because
neither `Shape.scale()` nor `BRepBuilderAPI_Transform` transforms a mesh. See
[`import-normalization.md`](import-normalization.md).

The regression test that guards it asserts **correspondence**, not presence: a
claimed unit conversion must coincide with a real size change, for both
representations.

### 2. Provenance must be STABLE

**No wall-clock timestamp.** No `createdAt`, no import time, no generation time.

This record participates in `definitionHash` and appears in Golden snapshots, so
a clock reading would make identical geometry hash differently on every run —
breaking determinism (ATLAS-GOV-003) and making every Golden comparison fail.
Brief section 34 asked for this directly: *"Do not include volatile metadata in
Golden geometry equality unless necessary."*

A caller-supplied `measurementDate` **is** allowed, because it is a stable data
value describing when a physical measurement was taken, not a reading of the
current clock.

**Verified:** two builds of the same measured stone produce byte-identical
provenance, and no `createdAt` key exists.

## Asset identity is a content hash, never a path

`sourceAssetHash` is a SHA-256 content hash. A filesystem path in a design
document would leak an internal server location into every export, every
technical specification and every review package (FOUNDRY-GOV-011).

Content addressing also gives the property the brief asked for in section 55:
**changing the imported asset invalidates the geometry.** A different file has a
different hash, which changes `stone.importedAsset.assetHash`, which changes
`definitionHash`, which marks the model stale. No separate cache-invalidation
mechanism is needed.

`sourceAssetName` carries the caller-facing filename for traceability in a
review package — a reviewer needs to know which file they are looking at — and
is never used to resolve anything.

## Version fingerprints

`generatorVersion` records the reference-geometry construction version;
`importerVersion` records the normalization pipeline version. Both let a Golden
diff be traced to a deliberate version bump rather than an unexplained drift.

Stone v1's round fast path reports `1.0.0` and the v2 pipeline reports `2.0.0`,
which is how a test can tell — and does tell — that round has not been rerouted.

## What provenance is not

- **Not a chain of custody.** It records what JewelMind did, not who owns the
  stone or where it was bought.
- **Not a certification.** No field asserts a grading report, a lab, or a
  gemological property.
- **Not professional validation.** Recording that a caliper was used says
  nothing about whether the resulting geometry was reviewed by a qualified
  professional. Every source remains `NOT_REVIEWED`.

## Cross-references

- [`measured-stone-contract.md`](measured-stone-contract.md)
- [`import-normalization.md`](import-normalization.md)
- [`../08-alchemist/174-determinism-and-version-fingerprint.md`](../08-alchemist/174-determinism-and-version-fingerprint.md)
