---
id: JM-BIBLE-254
title: Project Session Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-251
related_documents:
  - JM-BIBLE-274
implementation_status: current
professional_validation: not_required
normative: true
---

# Project Session Model

## One project, one session — the current, honest scope

JewelMind today has exactly one active "project" at a time: the single `JewelryDefinition` held in `useProjectStore.currentDefinition`, persisted to one `localStorage` key. There is no project list, no named/saved multiple designs, and no server-side project record — restating CLAUDE.md's explicit out-of-scope list (no accounts, no cloud projects) at the Studio layer. `project.name` is a field *within* the design definition (shown in the DESIGN zone), not a separate project-management concept.

## What a "session" consists of, concretely

| Element | Persisted? | Where |
|---|---|---|
| `JewelryDefinition` (the design) | Yes | `localStorage`, `jewelmind:project-definition:v1` |
| `viewMode` (Technical/Presentation) | Yes, as of this Sprint | `localStorage`, `jewelmind:vision-view-mode:v1` |
| `generatedModel` / `lastSuccessfulPreview` | No | In-memory only — the backend's per-process model cache is also not persisted across a backend restart |
| `componentVisibility`, `selectedComponent`, camera position | No | In-memory only, reset on reload |
| Validation results | No (recomputed) | Derived instantly from the restored definition on load |

## Relationship to `specs/studio/v1/project-session.schema.json`

That schema documents the *conceptual* session shape (design + view preference + a summary of generation/output state) as a single composed object — useful for reasoning and for a future server-side session concept, but no runtime code assembles one today; see [`278-frontend-state-architecture.md`](278-frontend-state-architecture.md) for why design state, generated-model state, and Vision state are kept in genuinely separate stores rather than one combined object.

## Named projects, multiple designs, autosave

All PLANNED, not CURRENT — see [`283-studio-gap-analysis.md`](283-studio-gap-analysis.md).
