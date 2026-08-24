---
id: JM-BIBLE-198
title: STL Export Contract
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-146
related_documents:
  - JM-BIBLE-211
implementation_status: current
professional_validation: not_required
normative: true
---

# STL Export Contract

[`07-atlas/146-stl-export-geometry-contract.md`](../07-atlas/146-stl-export-geometry-contract.md) is authoritative for *what geometry* gets tessellated and at what tolerance. This document is authoritative for *what the resulting file is and is not*.

## What JewelMind's STL export IS

- A real binary STL file, produced by OpenCascade 7.9 via CadQuery's `Shape.exportStl(tolerance=..., angularTolerance=...)`. Binary format confirmed directly by parsing a real exported file's header during this Sprint: 80-byte banner (`"STL Exported by Open CASCADE Technology [dev.opencascade.org]"`, zero-padded), a 4-byte little-endian triangle count, then 50 bytes per triangle. ASCII STL is never produced anywhere in this codebase.
- Byte-for-byte deterministic across repeated exports of the same design: two exports of the identical `GeneratedModel` produce identical SHA-256 checksums, confirmed during this Sprint. This is the opposite of STEP's behavior — see [`197-step-export-contract.md`](197-step-export-contract.md).
- Structurally self-validating: `binary_stl_triangle_count()` (added this Sprint) confirms the file's declared triangle count matches its actual byte length via `84 + triangleCount * 50 == fileSize`, exactly as observed on the default solitaire (10454 triangles, 522784 bytes).

## What JewelMind's STL export is NOT, and must never be claimed to be

- **Not a source of JDL parametric information.** No dimension, material, or design-intent field survives tessellation — an STL file cannot be used to reconstruct a `JewelryDefinition`.
- **Not a B-Rep.** STL is a lossy triangle-mesh approximation of the true surface, controlled entirely by `meshTolerance`/`angularTolerance` — restates ATLAS-GOV-013/FOUNDRY-GOV-013: STL must never become the canonical source geometry for anything downstream in this system.
- **Not unit-labeled.** See [`212-unit-and-scale-contract.md`](212-unit-and-scale-contract.md) — the binary STL format has no field for declaring length units anywhere in its specification; a consumer only knows the numbers are millimetres because JewelMind's documentation says so, never because the file itself says so.

## Roundtrip validation performed this Sprint

`backend/tests/test_export_integrity.py::test_stl_export_roundtrip_via_binary_header_parse` confirms, for the default solitaire, that the exported file's declared triangle count (10454) exactly reconciles with its byte size via the format's own size formula — a dependency-free structural check, not a full mesh-quality re-import (CadQuery has no STL importer suited for this; see [`214-export-roundtrip-validation.md`](214-export-roundtrip-validation.md) for why a deeper mesh-level roundtrip was judged impractical this Sprint, per FOUNDRY-GOV-014's "do not introduce fragile dependencies" spirit).
