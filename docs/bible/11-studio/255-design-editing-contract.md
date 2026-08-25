---
id: JM-BIBLE-255
title: Design Editing Contract
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-250
related_documents:
  - JM-BIBLE-256
implementation_status: current
professional_validation: not_required
normative: true
---

# Design Editing Contract

## The parameter groups, exactly as implemented

`ConfigurationPanel.tsx`, reorganized this Sprint:

| Group | Design fields | Advanced fields |
|---|---|---|
| Project | Name | — |
| Ring | EU size | Inner diameter |
| Band | Width, Thickness, Profile | — |
| Stone | Diameter | Depth |
| Setting | Prong count | Prong diameter, Prong height, Basket height |
| Material | Metal | — |
| Manufacturing | Method | — |
| Preview | — | Mesh tolerance, Angular tolerance (new fields exposed this Sprint — see [`256-parameter-editor-model.md`](256-parameter-editor-model.md)) |

## Fields deliberately not exposed as controls

`ring.sizeSystem` (fixed at `"EU"` — a single-value union, `RingSizeSystem = 'EU'`), `stone.shape` (fixed at `"round"`), and `setting.type` (fixed at `"prong"`) are real `JewelryDefinition` fields with exactly one possible value each today. Per this Sprint's own instruction not to invent controls, none of them got a dropdown with a single, permanently-selected option — a control with no real choice to make is not a design parameter, it is noise. If a second value for any of these three fields is ever added to the schema (a second stone shape, a second setting type), a real selector belongs here at that time, not before.

## Every edit still flows through the same validated path

Every field's `onChange` calls the same `useProjectStore.updateXxx()` actions that existed before this Sprint (`updatePreview()` is the one new action, added for the two Preview fields) — `ConfigurationPanel`'s reorganization is a presentation change, never a new data path. Every edit still runs `validateDefinition()` synchronously and marks `isStale: true` if a model already existed, exactly as before.

## No automatic derivations introduced

`ring.size` and `ring.innerDiameter` remain two independently editable fields, cross-checked only by the existing `JM-RING-003` consistency rule — this Sprint did not add any code that computes one from the other. See open question `STUDIO-OQ-002` in [`284-open-studio-questions.md`](284-open-studio-questions.md) for whether that should change later.
