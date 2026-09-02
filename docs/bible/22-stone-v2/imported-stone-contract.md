---
id: JM-BIBLE-610
title: "Imported Stone Contract"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-02
source_of_truth: true
depends_on:
  - JM-BIBLE-601
related_documents:
  - JM-BIBLE-611
implementation_status: partial
professional_validation: not_required
normative: true
---

# Imported Stone Contract

`IMPORTED_CAD` is **PARTIAL**, and the reason is precise: B-Rep and mesh import,
unit normalization, inspection and Vision all work; **setting compatibility is
decided per asset from real geometry rather than granted.**

## Formats — declared from what the kernel actually does

Every entry below was established by **running the installed CadQuery 2.8.0 /
OCP build**, not by reading documentation (brief section 30's "do not claim
support for formats the current importer cannot actually parse").

| Format | Result | Mechanism |
|---|---|---|
| `.step`, `.stp` | `BREP_SOLID` | `cadquery.importers.importStep` |
| `.brep` | `BREP_SOLID` | `cadquery.importers.importBrep` |
| `.stl` | `MESH` | `OCP.RWStl` directly |

Not claimed, each with its real reason:

| Format | Why not |
|---|---|
| `.obj` | `OCP.RWObj` is not present in this build |
| `.gltf`, `.glb` | No XCAF document pipeline is wired up to read it |
| `.iges`, `.igs` | No IGES reader is available in this build |
| `.3dm` | Rhino format; JewelMind never requires Rhino |

STL is read through OCP directly because CadQuery's own importer registry
(`ImportTypes`: BIN, BREP, DXF, STEP) has **no STL entry** — verified, not
assumed.

An unsupported format is refused at **store** time, not merely at import time,
so a caller learns immediately rather than after apparently-successful upload.

## B-Rep versus mesh is never papered over

| | `BREP_SOLID` | `MESH` |
|---|---|---|
| Solids | ≥ 1 | **0** |
| Reliable volume | yes | **no** (`null`) |
| Triangle count | — | real |
| B-Rep operations | yes | **no** |
| `supportsBrepOperations` | `true` | `false` |

`supportsBrepOperations` is computed from the **real parsed result**
(`representation == "BREP_SOLID" and bool(solids)`), never from the file
extension. A STEP file containing only surfaces reports `false`, correctly.

Reporting `solidCount: 0` and `volumeMm3: null` for a mesh is the honest answer,
not a failure. A mesh genuinely has no watertight solid to measure
(STONEV2-GOV-014).

## Units are declared, never guessed

`declaredUnit` is **required**. No format JewelMind reads carries a reliable,
universally-populated unit, and guessing one silently rescales a real physical
object by a factor of ten or twenty-five (FOUNDRY-GOV-012).

If a caller cannot state the unit, the honest outcome is
`STONE_IMPORT_UNITS_UNKNOWN`, not a default.

## Dimensions come from the asset, never from the document

`resolved_length_mm()`, `resolved_width_mm()` and `resolved_depth_mm()`
deliberately **raise** `StoneDimensionsUnavailableError` for an imported stone.

This is not an oversight. An imported stone's size is a property of the asset;
answering from the document would let a design place components around a size
the stone does not have. Callers read the normalized definition, whose
dimensions are labelled `IMPORTED_GEOMETRY_MEASUREMENT`.

That refusal caught a real bug: Forge's `STONE_DEPTH_RANGE` called
`resolved_length_mm()` unconditionally and **crashed validation** for every
imported stone. The rule is now scoped away from `IMPORTED_CAD` (STONEV2-GOV-011).

## The asset IS the stone

An imported asset is **placed**, never rebuilt. The builder translates it to the
girdle plane and applies orientation; it never substitutes a native
approximation. Doing so would discard the exact geometry the user supplied,
which is the entire reason they imported it (STONEV2-GOV-010).

## Why setting compatibility is UNSUPPORTED

The `imported` pseudo-shape carries `prongCompatibility: UNSUPPORTED` and
`bezelCompatibility: UNSUPPORTED`.

Not because imported stones can never be set, but because both current families
are **outline-driven**, and deriving a girdle outline by projecting arbitrary
imported geometry is not implemented. Reporting no outline is honest; fabricating
one would place metal against a silhouette the stone does not have
(brief section 44).

`STONE_IMPORT_OUTLINE_UNAVAILABLE` exists for that case. Outline projection is
the `STONE_OUTLINE_EXTRACTION` capability, status `PLANNED`, and it is the one
change that would move imported stones from `UNSUPPORTED` to at least
`EXPERIMENTAL`.

This is also why there is **no imported-stone Golden ring case**: a ring cannot
be assembled around a stone no setting will grip. Imported geometry is covered
by unit tests and by real import vectors instead — see
[`stone-v2-golden-strategy.md`](stone-v2-golden-strategy.md).

## Assets are untrusted input

See [`import-normalization.md`](import-normalization.md) for the full set of
safeguards. In summary: content-addressed storage with a validated hexadecimal
hash (so path traversal is structurally impossible rather than filtered), size
and complexity bounds checked after parsing as well as before, sanitized error
messages carrying no stack trace or server path, and no execution of anything in
the file.

## Cross-references

- [`import-normalization.md`](import-normalization.md)
- [`stone-setting-compatibility-v2.md`](stone-setting-compatibility-v2.md)
- [`../09-foundry/212-unit-and-scale-contract.md`](../09-foundry/212-unit-and-scale-contract.md)
