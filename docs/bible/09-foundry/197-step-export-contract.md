---
id: JM-BIBLE-197
title: STEP Export Contract
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-145
related_documents:
  - JM-BIBLE-210
implementation_status: current
professional_validation: not_required
normative: true
---

# STEP Export Contract

[`07-atlas/145-step-export-geometry-contract.md`](../07-atlas/145-step-export-geometry-contract.md) is authoritative for *what geometry* gets selected and serialized. This document is authoritative for *what the resulting file is and is not*, and for facts discovered this Sprint by directly inspecting a real exported file's own bytes.

## What JewelMind's STEP export IS

- Real ISO-10303 (STEP) B-Rep data, produced by OpenCascade 7.9 via CadQuery 2.8.0's `Shape.exportStep()`.
- Explicitly declares its own length unit: `SI_UNIT(.MILLI.,.METRE.)`, confirmed by inspecting a real exported file's `GLOBAL_UNIT_ASSIGNED_CONTEXT` entity during this Sprint — see [`212-unit-and-scale-contract.md`](212-unit-and-scale-contract.md). This was not previously verified in any prior Sprint's documentation.
- Re-importable: confirmed by `backend/tests/test_export_integrity.py::test_step_export_roundtrip_via_reimport`, which re-imports a real exported STEP file via `cadquery.importers.importStep()` and confirms the recovered volume matches the original within a `1e-3` relative tolerance (measured: `3.96e-7`, see [`214-export-roundtrip-validation.md`](214-export-roundtrip-validation.md)).

## What JewelMind's STEP export is NOT, and must never be claimed to be

- **Not a parametric history.** No feature tree, sketch, or construction-step sequence is preserved — only the final B-Rep. Re-opening the STEP file in any CAD tool shows solids, never the band/prong/basket construction steps that produced them.
- **Not equivalent to a native MatrixGold or Rhino project file.** Restates FOUNDRY-GOV-006. STEP is a neutral exchange format; opening it in MatrixGold or Rhino produces imported geometry, not an editable native design.
- **Not guaranteed to import at a given quality in every CAD application.** Only the specific tools and versions actually tested belong in a "tested" interoperability claim — see [`210-step-interoperability-boundaries.md`](210-step-interoperability-boundaries.md). No blanket "works in any CAD software" claim is made.

## Not byte-for-byte deterministic — discovered this Sprint

Two exports of the identical `GeneratedModel` differ in exactly 2 of ~4315 lines: an embedded wall-clock `FILE_NAME` timestamp, and an incrementing `PRODUCT` entity translator-instance counter (`'Open CASCADE STEP translator 7.9 N'`). All actual B-Rep geometry data is byte-identical between the two exports. **Consequence: a STEP file's SHA-256 checksum is not stable across repeated exports of the same design**, even though the geometry it encodes is. This is the opposite of STL's behavior — see [`198-stl-export-contract.md`](198-stl-export-contract.md) — and is documented honestly rather than assumed away; see [`208-export-version-fingerprint.md`](208-export-version-fingerprint.md) for why checksums alone cannot serve as a stable content-identity proxy for STEP.

## Incidental discovery: an embedded OCCT uncertainty value

Every exported STEP file also carries `UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(5.E-06), ...)` next to its unit declaration — 5 nanometres in the file's own millimetre unit context. This is OCCT's own default STEP-translator uncertainty value, not a JewelMind-chosen tolerance; JewelMind's own code never reads, sets, or relies on it. See [`07-atlas/136-tolerance-model.md`](../07-atlas/136-tolerance-model.md) for why no other kernel tolerance number could previously be asserted, and do not read this value as a statement about the accuracy of any upstream boolean or fillet operation.
