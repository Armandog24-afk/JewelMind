---
id: JM-BIBLE-211
title: STL Interoperability Boundaries
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-209
related_documents:
  - JM-BIBLE-198
implementation_status: current
professional_validation: not_required
normative: true
---

# STL Interoperability Boundaries

## Current status by use case

| Use case | Level | Basis |
|---|---|---|
| Structural self-validation (this codebase) | `IMPORT_TESTED`-equivalent | `binary_stl_triangle_count()`, a dependency-free binary-header parse confirming `84 + triangleCount * 50 == fileSize`, this Sprint |
| 3D-printing slicers (e.g. PrusaSlicer, Cura) | `EXPORT_SUPPORTED` only | Binary STL is the de facto universal slicer input format; no specific slicer was launched against a real JewelMind file this Sprint |
| General mesh-inspection tools (e.g. MeshLab) | `EXPORT_SUPPORTED` only | Same reasoning |
| Physical prototyping services | `EXPORT_SUPPORTED` only | No print was actually ordered or produced this Sprint; a real physical print is out of scope for a documentation/hardening sprint |

## Why STL's interoperability risk profile differs from STEP's

STL carries no unit metadata at all (see [`212-unit-and-scale-contract.md`](212-unit-and-scale-contract.md)) — a slicer that assumes inches instead of millimetres would silently produce a print roughly 25.4× too large, with no error from the file format itself. This is a real, documented interoperability risk specific to STL, worth stating plainly rather than implying STL export is risk-free simply because the format is universally supported.

## What is safe to claim today

Binary STL is real, well-formed, and structurally self-consistent, confirmed by this Sprint's header-and-size check. Whether any specific external tool renders or slices it exactly as intended has not been independently tested, and is not claimed as `WORKFLOW_VALIDATED` per [`209-cad-interoperability-philosophy.md`](209-cad-interoperability-philosophy.md).
