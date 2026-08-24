---
id: JM-BIBLE-210
title: STEP Interoperability Boundaries
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-209
related_documents:
  - JM-BIBLE-197
implementation_status: current
professional_validation: not_required
normative: true
---

# STEP Interoperability Boundaries

## Current status by target application

| Application | Level | Basis |
|---|---|---|
| CadQuery / OpenCascade (self) | `IMPORT_TESTED` (self-consistency only, see [`209-cad-interoperability-philosophy.md`](209-cad-interoperability-philosophy.md)) | `cadquery.importers.importStep()` round-trip, this Sprint |
| FreeCAD | `EXPORT_SUPPORTED` only | FreeCAD is itself built on OpenCascade and reads ISO-10303 STEP natively; not independently installed or tested this Sprint |
| Rhino | `EXPORT_SUPPORTED` only | A commercial application; CLAUDE.md and FOUNDRY-GOV-014 both prohibit requiring its purchase to complete this Sprint |
| MatrixGold (via Rhino) | `EXPORT_SUPPORTED` only | Depends on Rhino; same reasoning |
| Autodesk Fusion | `EXPORT_SUPPORTED` only | Same reasoning — no license available in this environment |

**None of these external applications has been actually launched against a real JewelMind STEP file.** Every one of them remains at `EXPORT_SUPPORTED` — a reasonable expectation based on STEP being a standard, widely-implemented exchange format, never an observed result.

## Future testing plan (not yet executed)

If and when a license or trial becomes available for any of the above, the test to run is: export the default solitaire's STEP file, open it in the target application, confirm (a) it opens without error, (b) the solid count and rough bounding box match what JewelMind itself reports, and (c) record the application name/version and outcome in this document and in `specs/foundry/v1/test-vectors/`. Until that happens, this table's `EXPORT_SUPPORTED`-only status stands as the honest, current answer — not a placeholder for an assumed future pass.

## What is safe to claim today

STEP is a real, ISO-standardized format; software that correctly implements the standard should be able to open it. That is a statement about the standard, not a JewelMind-specific interoperability guarantee — see [`197-step-export-contract.md`](197-step-export-contract.md) for the exact boundary between the two kinds of claim.
