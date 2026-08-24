---
id: JM-BIBLE-136
title: Tolerance Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-133
related_documents:
  - JM-BIBLE-071
implementation_status: current
professional_validation: not_required
normative: true
---

# Tolerance Model

Six distinct kinds of "tolerance" appear in or near this codebase. They are not interchangeable, and this document is the single place that distinguishes them.

| Kind | Real current value(s) | Units | Where | Interchangeable with the others? |
|---|---|---|---|---|
| CAD-kernel tolerance | OpenCascade's own internal geometric tolerance | mm — **JewelMind never sets, reads, or overrides this value anywhere in the codebase**, so no specific number is asserted here; whatever OCCT's own internal default is applies, unexamined by this Sprint | Implicit, inside every OCCT operation | No |
| Geometric-comparison tolerance | `FlatCircleAtRadius.tol = 1e-3` (edge-selection tolerance for the fillet selector) | mm | `geometry/primitives/selectors.py` | No |
| Preview mesh tolerance | `preview.meshTolerance`, default `0.1` | mm | `domain/schema.py::PreviewSpec`, used by `.tessellate()`/`.exportStl()` | No |
| Angular mesh tolerance | `preview.angularTolerance`, default `0.2` | **radians** (confirmed by inspecting CadQuery's source, Sprint 3) | Same | No |
| Validation threshold | e.g. `JM-BAND-001`'s 1.5mm minimum width | mm | `backend/jewelmind/validation/engine.py` | No — this is a Forge domain rule, not a geometric tolerance at all |
| Manufacturing tolerance | **None exists anywhere in this codebase** | n/a | n/a | No — and none is invented here |

## Undocumented kernel default, flagged

**JewelMind never explicitly sets an OCCT B-Rep comparison tolerance.** Every boolean/fillet/loft/revolve operation runs with whatever default OCCT applies internally. This was not previously documented anywhere in the Bible or in `docs/`. It is flagged here as a real, previously-undocumented fact — not invented, not assumed to be a specific number, since this codebase never queries or overrides it. If OCCT's default tolerance ever needs to be tuned for a specific geometric edge case, that would be a deliberate future engineering decision (an ADR, per [`120-atlas-governance.md`](120-atlas-governance.md)), not something already decided.

## No invented tolerances

Per this Sprint's explicit instruction, no OpenCascade internal tolerance value and no manufacturing tolerance (shrinkage, wall-thickness minimums for a specific casting house or printer) is stated as a specific number anywhere in this document, because none is present in the actual code. `docs/known-limitations.md` already states this for manufacturing tolerances ("No manufacturing-grade tolerancing"); this document extends the same discipline to CAD-kernel tolerances specifically.
