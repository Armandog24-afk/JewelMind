---
id: JM-BIBLE-611
title: "Import Normalization"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-02
source_of_truth: true
depends_on:
  - JM-BIBLE-610
related_documents:
  - JM-BIBLE-612
implementation_status: current
professional_validation: not_required
normative: true
---

# Import Normalization

`backend/jewelmind/stone/importing.py`.

## The pipeline

```
content hash  ──►  resolve  ──►  format detect  ──►  parse
                                                       │
                     ┌─────────────────────────────────┴──────────┐
                     ▼                                            ▼
              BREP_SOLID path                              MESH path
              scale → validate → recentre → rotate         ONE node pass:
              (shape-level transforms)                     scale + rotate + recentre
                     └─────────────────────┬──────────────────────┘
                                           ▼
                     ImportedStoneGeometry + recorded provenance
```

## The mesh bug, and why it mattered more than a wrong size

**A mesh must be transformed node by node.** Neither
`cadquery.Shape.scale()` nor `BRepBuilderAPI_Transform` moves a triangulation
attached to an otherwise-empty face.

Measured on a real 6 × 8 × 4mm STL with a requested 10× scale:

| Method | Resulting bounding box |
|---|---|
| `Shape.scale(10)` | 6 × 8 × 4 — **unchanged** |
| `BRepBuilderAPI_Transform` | 6 × 8 × 4 — **unchanged** |
| Direct node scaling | 60 × 80 × 40 — correct |

So an STL declared in centimetres came back at its original millimetre size.
That was the visible half of the bug.

**The worse half:** `normalizationOperations` still recorded
`UNIT_CONVERSION:cm->mm`. The provenance record asserted a conversion that had
never happened. A false provenance entry is more damaging than a missing one —
a missing entry prompts a question, a false entry answers it wrongly
(STONEV2-GOV-015).

The same failure applied to recentring: mesh imports were reporting
`ORIGIN_RECENTERED` while the geometry stayed where it was.

`_transform_triangulation()` now applies scale, then rotation about Z, then
translation to the triangulation's own nodes, in **one pass**. The centre is
measured in the scaled frame and rotated with the geometry, so subtracting the
rotated centre lands the mesh on the origin.

**Regression coverage:** `TestMeshTransformRegression` asserts that an STL
declared in centimetres really is ten times larger, that a claimed
`UNIT_CONVERSION` corresponds to a real size change **for both
representations**, that a mesh is really recentred, and that mesh orientation
really swaps length and width.

## Normalization operations, and the honesty rule

| Operation | Recorded as |
|---|---|
| Unit conversion | `UNIT_CONVERSION:cm->mm` |
| Origin recentring | `ORIGIN_RECENTERED:bbox_center(x,y,z)` |
| Orientation | `ORIENTATION_APPLIED:90deg` |

An operation is recorded **if and only if** it was applied. An empty list means
none was needed — never that normalization was skipped.

Recentring uses the **bounding-box centre**, matching the canonical stone frame
every native shape uses, so an imported stone lands in the same frame as a
parametric one.

## Security — assets are untrusted input

| Safeguard | Mechanism |
|---|---|
| Path traversal | Assets are addressed by CONTENT HASH, validated against `[0-9a-f]{8,128}` before touching a path. Structurally impossible, not filtered. |
| File size | `MAX_ASSET_BYTES` = 32 MiB, checked at store time and again at import time |
| Mesh complexity | `MAX_MESH_TRIANGLES` = 2,000,000, checked **after parsing** |
| B-Rep complexity | `MAX_BREP_FACES` = 100,000, checked after parsing |
| Format | Refused at store time with the real per-format reason |
| Parser failures | Caught and re-raised as structured errors |
| Code execution | None. Only geometry is read. |

**Complexity is checked after parsing** on purpose: a small compressed file can
expand into a very large mesh, so a pre-parse size check alone is not a bound on
work.

The store's filename is `<hash><ext>`, so resolving never uses any
caller-supplied string other than the validated hash. That is what makes
traversal structurally impossible.

## Error messages leak nothing

```python
raise StoneImportFailedError(
    "The stone asset could not be read as B-Rep geometry. It may be "
    "corrupt, truncated, or not the format its extension claims."
) from exc
```

The underlying exception is **chained** (`from exc`) so it remains available in
server logs, and deliberately **not interpolated** into the message: importer
output can contain absolute server paths and library internals
(FOUNDRY-GOV-011).

**Verified:** a malformed STEP produces a message containing no traceback, no
asset-store path, and not even the asset hash.

One thing outside JewelMind's control: OCCT writes its own parse diagnostics
(`**** ERR StepFile : ...`) to the process's stderr. That is kernel console
output, never part of an API response, and it is noted here so a future reader
does not mistake it for a leak.

## Resource limits are safeguards, not judgements

None of these limits is a geometric or quality judgement. A real gemstone asset
is orders of magnitude below every one of them. They exist because the input is
untrusted, and they are recorded in
`specs/stone/v2/stone-source-registry.json` so a caller can see them.

## Cross-references

- [`imported-stone-contract.md`](imported-stone-contract.md)
- [`stone-source-provenance.md`](stone-source-provenance.md)
- [`../09-foundry/190-foundry-governance.md`](../09-foundry/190-foundry-governance.md)
