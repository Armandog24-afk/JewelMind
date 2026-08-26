---
id: JM-BIBLE-424
title: CAD Workflow Validation Process
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
  - JM-BIBLE-426
implementation_status: current
professional_validation: not_required
normative: false
---

# CAD Workflow Validation Process

## The future workflow this formalizes

```
JewelMind STEP export
  → external CAD import
  → inspect solids
  → measure geometry
  → continue professional editing
```

This is the workflow a `CAD_INTEROPERABILITY_SPECIALIST` reviewer would actually exercise, and the review-package's `model.step` file (see [`426-review-package-contract.md`](426-review-package-contract.md)) is what makes it possible.

## Candidate target applications — planned, not tested

Per the original brief and per CLAUDE.md's own constraint ("Never require Rhino, MatrixGold, JewelCAD, a desktop FreeCAD instance, or any other paid/interactive CAD software"), JewelMind cannot itself install or drive these applications. Candidate applications for a *human* reviewer to test STEP import in: Rhino, a MatrixGold/Rhino-based workflow, FreeCAD, Fusion, or any other CAD tool a reviewer already has access to. None of these are PLANNED targets in the sense of a JewelMind roadmap commitment — they are simply the realistic set a professional reviewer might use.

## Current real status: zero external CAD workflows tested

`docs/bible/09-foundry/209-cad-interoperability-philosophy.md` (Sprint 7) already states this precisely and remains accurate as of this Sprint — quoted directly from that document:

> "The only real `IMPORT_TESTED`-equivalent check performed this Sprint is `cadquery.importers.importStep()` re-importing JewelMind's own STEP output — this proves the file is well-formed STEP, but CadQuery is not an independent third-party CAD application; it is the same library that wrote the file. This is documented as a self-consistency check, not an external interoperability test."

A repo-wide search for `IMPORT_TESTED` and `WORKFLOW_VALIDATED` (verified directly) finds these terms only inside `docs/bible/09-foundry/209-cad-interoperability-philosophy.md` itself, as defined vocabulary — never as a claimed, completed status anywhere in the codebase. This Sprint changes nothing about that state; it only builds the mechanism (`docs/professional-review/cad-interoperability-review-form.md`, the real fillable form) that would eventually let a reviewer produce a real one.

## The real reviewer vocabulary

`backend/jewelmind/professional_validation/schemas.py::ImportOutcome` defines exactly 6 values, verified directly:

- `IMPORT_SUCCESS`
- `IMPORT_WITH_WARNINGS`
- `IMPORT_FAILURE`
- `EDITABLE_WITHOUT_REBUILD`
- `EDITABLE_WITH_REWORK`
- `REQUIRES_SUBSTANTIAL_REBUILD`

## Never interpreted as universal compatibility

A single `ImportOutcome` value from a single reviewer testing a single application version proves exactly one thing: that JewelMind's STEP output behaved that way, in that application, on that day. It is never generalized to "JewelMind is compatible with [application]" as a blanket claim — the same discipline `209-cad-interoperability-philosophy.md` already established for Foundry's own export layer, restated here for the professional-review layer.

## Cross-references

- [`426-review-package-contract.md`](426-review-package-contract.md) — the `model.step` file and its real SHA-256 checksum, which a CAD-interoperability review would actually use.
- `docs/professional-review/cad-interoperability-review-form.md` — the real fillable form.
- [`441-review-sampling-strategy.md`](441-review-sampling-strategy.md) — this is Priority 4 in the review order.
