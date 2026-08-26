---
id: JM-BIBLE-421
title: Manufacturing Validation Process
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-PROVAL-README
  - JM-BIBLE-410
related_documents:
  - JM-BIBLE-419
  - JM-BIBLE-420
  - JM-BIBLE-422
implementation_status: current
professional_validation: not_required
normative: false
---

# Manufacturing Validation Process

## Two different questions, never conflated

**GEOMETRY VALIDITY** ("is this a well-formed, plausible solid?") and **MANUFACTURING SUITABILITY** ("can this solid actually be cast or printed successfully, and finished into a wearable piece?") are different questions, reviewed differently, and a `ValidationRecord` about one never implies anything about the other. A geometry component can be `VALIDATED` for construction plausibility while remaining entirely unreviewed for manufacturing — see [`412-validation-object-model.md`](412-validation-object-model.md)'s distinct `GEOMETRY_COMPONENT` vs. `MANUFACTURING_PROFILE` object types.

## Only two manufacturing processes exist in JewelMind today

`backend/jewelmind/domain/schema.py::ManufacturingMethod = Literal["lost_wax_casting", "direct_resin_printing"]` — verified directly in the schema. There is exactly one Forge rule that is manufacturing-context-specific: `JM-MANUFACTURING-001` (`backend/jewelmind/validation/engine.py::_manufacturing_rules`), which only fires `if d.manufacturing.method != "direct_resin_printing"` is false — i.e. it only applies context to the resin-printing case. No other rule branches on `manufacturing.method` anywhere in `backend/jewelmind/validation/engine.py` (verified by reading the file), and no geometry builder in `backend/jewelmind/geometry/components/` branches on it either (verified: `grep -rn "manufacturing" backend/jewelmind/geometry/` finds nothing). Manufacturing method today is closer to declared *context* than a geometry- or rule-driving input.

## Future review areas (none reviewed yet)

Per the original Sprint 13 brief, a future manufacturing review would look at:

- casting preparation (sprue placement, investment considerations);
- printability (resin-specific geometry constraints, support requirements);
- spruing implications;
- cleanup (post-cast or post-print finishing effort);
- finishing (polishing access, surface quality expectations);
- shrinkage allowances;
- accessibility (can a caster/printer's own tooling actually reach the geometry);
- support considerations (for resin printing specifically).

None of these has been reviewed. None of them has a JewelMind-side numeric parameter today.

## Do not invent process numbers

A grep across the entire `backend/jewelmind/` tree for `shrinkage` and `wall_thickness` (or `wall thickness`) returns zero matches — no shrinkage percentage, no minimum wall-thickness constant, no cast-specific tolerance exists anywhere in the codebase. This document does not invent one either. If a future casting specialist supplies a real, sourced value during a real review, it becomes a `ValidationRecord` (scoped explicitly to `manufacturingMethod: lost_wax_casting`, per [`415-validation-scope-model.md`](415-validation-scope-model.md)) before it may influence anything — never a value added directly to code from documentation alone.

## Reviewer role

`CASTING_SPECIALIST` for lost-wax casting concerns; `RESIN_PRINTING_SPECIALIST` for direct resin printing concerns. These are two of the 8 real `ReviewerRole` values (`413-reviewer-role-model.md`) — a casting specialist is not assumed automatically qualified to review resin-printing suitability, and vice versa (PROVAL-GOV-004).

## Cross-references

- [`420-geometry-validation-process.md`](420-geometry-validation-process.md) — the geometry-side counterpart this document is explicitly distinguished from.
- [`415-validation-scope-model.md`](415-validation-scope-model.md) — how a manufacturing-specific finding stays scoped to the manufacturing method it was actually reviewed under (PROVAL-GOV-016).
- [`441-review-sampling-strategy.md`](441-review-sampling-strategy.md) — sampling both manufacturing contexts.
