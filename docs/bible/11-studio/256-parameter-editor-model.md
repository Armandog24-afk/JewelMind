---
id: JM-BIBLE-256
title: Parameter Editor Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-255
related_documents:
  - JM-BIBLE-A52
implementation_status: current
professional_validation: not_required
normative: true
---

# Parameter Editor Model

## Why each Advanced field is Advanced, specifically

| Field | Why it's Advanced, not Design |
|---|---|
| Ring inner diameter | `ring.size` (EU size) is the design-intent field a jeweler normally thinks in; inner diameter is the exact millimeter equivalent, cross-validated against size by `JM-RING-003` — most designs only need to set one of the two |
| Stone depth | Diameter is the dimension that visually communicates stone size; depth is a secondary, more technical dimension |
| Prong diameter / height, basket height | All three are real geometry-driving dimensions, but none is a first decision a jeweler makes when starting a design — prong count is the meaningful design choice; the exact prong/basket dimensions refine an already-chosen setting |
| Mesh / angular tolerance | These control preview *tessellation quality*, not the design itself — see [`07-atlas/136-tolerance-model.md`](../07-atlas/136-tolerance-model.md); a user changing these is tuning rendering fidelity, not the ring |

## Nothing required to understand current geometry is hidden

Every Advanced field remains fully visible once the disclosure is expanded — restating this Sprint's own constraint ("Do not hide parameters required to understand current geometry"). The disclosure defaults to collapsed (see `useVisionStore`-adjacent reasoning in [`284-open-studio-questions.md`](284-open-studio-questions.md) `STUDIO-OQ-001` for whether that default should ever change), never removed from the DOM or made unreachable.

## Real, not assumed, dependency check

Before moving a field to Advanced, each one was checked against `backend/jewelmind/geometry/` to confirm it genuinely drives geometry (all five moved fields do — `prongDiameter`/`prongHeight`/`basketHeight` feed `geometry/components/{prongs,basket}.py` directly; `innerDiameter` feeds `band.py`; `stone.depth` feeds `stone.py`) and against `backend/jewelmind/validation/` to confirm no rule assumes it is always visible in a "basic" editing context. None does.

## Input quality, per field

Every `NumericField` (Design or Advanced) has: a `<label>` associated via `htmlFor`/`id`, a unit suffix where relevant, `type="number"` with real `min`/`max`/`step`, and — new this Sprint — an `aria-invalid` + visible error message when the typed value falls outside its declared range, without ever silently clamping or discarding the user's input (the raw value is always passed to `onChange`; JDL/Forge remain the authoritative validators, per STUDIO-GOV-001). See [`A52`](../appendices/studio-ui-component-catalog.md).

## Real test coverage

`ConfigurationPanel.test.tsx` (7 tests) confirms: Design fields render with correct default values; Advanced parameters are collapsed by default; expanding the disclosure reveals all Advanced fields including the new Preview-tolerance controls; edits to both Design and Advanced fields correctly update `JewelryDefinition`; every visible field has an accessible label.
