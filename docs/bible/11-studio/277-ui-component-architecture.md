---
id: JM-BIBLE-277
title: UI Component Architecture
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-276
related_documents:
  - JM-BIBLE-A52
implementation_status: current
professional_validation: not_required
normative: true
---

# UI Component Architecture

## The brief's conceptual names, mapped to the real repository

| Conceptual name | Real component |
|---|---|
| `StudioShell` | `App.tsx` (unchanged structure: header + 3-panel body) |
| `ProjectHeader` | `AppHeader.tsx` |
| `ParameterEditor` | `ConfigurationPanel.tsx` |
| `ParameterSection` | `FormSection.tsx` (pre-existing, reused, not renamed) |
| `ModelViewport` | `ModelViewport.tsx` (Vision, Sprint 8) |
| `ViewModeSwitcher` | `ViewModeSwitch.tsx` (Vision, Sprint 8) |
| `ViewerToolbar` | `ViewportToolbar.tsx` (Vision, Sprint 8) |
| `ComponentVisibility` | `ComponentVisibilityPanel.tsx` (Vision, Sprint 8) |
| `ValidationSummary` / `DiagnosticList` | `ValidationPanel.tsx` / `ValidationItem.tsx` (pre-existing) |
| `ModelStatus` | `ModelStatusBadge.tsx` (new this Sprint) |
| `OutputPanel` | `OutputsPanel.tsx` (new this Sprint) |
| `ArtifactAction` | `ArtifactRow.tsx` (new this Sprint) |
| `TechnicalInfo` | `ModelInformation.tsx` (pre-existing) |
| `PresentationControls` | `PresentationPanel.tsx` (Vision, Sprint 8) |

The brief's names are a useful conceptual lens; this Sprint kept the repository's own existing, already-sensible names where a component already existed, rather than renaming for naming's sake.

## No giant monolithic components introduced

`OutputsPanel.tsx` (79 lines) delegates every row's rendering to `ArtifactRow.tsx` (37 lines) — the pattern this Sprint used throughout: a small orchestrating component (reads store state, computes eligibility) plus a small, reusable presentational component (renders one row/badge), never one file doing both for every artifact.

## No unnecessary fragmentation either

`ProjectActions.tsx` remains one component (Generate + Reset) rather than being split into two single-button components — both actions are small, related, and always rendered together; splitting them would add indirection without a corresponding benefit.

## Responsibility boundaries, confirmed by inspection

`ConfigurationPanel` never reads `generatedModel`/`isStale` — it only reads/writes `currentDefinition`. `OutputsPanel` never reads `currentDefinition` directly — only `generatedModel`, `isStale`, `validationResults`, `exportStatus`. `ModelStatusBadge` is purely presentational (props in, JSX out) with zero store access of its own — every consumer (`AppHeader`, `ModelViewport`) computes the state and passes it in, keeping the badge trivially reusable and testable in isolation.
