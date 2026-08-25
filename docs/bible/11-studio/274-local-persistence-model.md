---
id: JM-BIBLE-274
title: Local Persistence Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-254
related_documents:
  - JM-BIBLE-275
implementation_status: current
professional_validation: not_required
normative: true
---

# Local Persistence Model

## What is persisted, exactly, and where

| Data | Storage key | Added this Sprint? |
|---|---|---|
| `JewelryDefinition` (the design) | `jewelmind:project-definition:v1` | No — pre-existing, `persistence.ts` |
| `viewMode` (Technical/Presentation) | `jewelmind:vision-view-mode:v1` | Yes |

Both audited this Sprint and confirmed to follow the identical safety pattern: every read and write is wrapped in `try`/`catch` (private browsing, disabled storage, or quota errors degrade to "nothing persisted" rather than throwing), and `viewMode`'s reader (`loadStoredViewMode()`) validates the stored value against the literal `'presentation'` string, falling back to `'technical'` for anything else (corrupted or unrecognized data) — mirroring `persistence.ts`'s `isValidJewelryDefinition()` structural check for the design itself.

## What is deliberately NOT persisted

| Data | Why not |
|---|---|
| `generatedModel` / `lastSuccessfulPreview` | These reference a backend model cache that itself doesn't survive a backend restart — persisting a stale reference across a reload would risk exactly the "pretend previous backend-generated model still exists" failure mode this Sprint's own instructions warn against; see [`275-session-recovery.md`](275-session-recovery.md) |
| `componentVisibility`, `selectedComponent`, camera position | Ephemeral viewing state, cheap to re-derive, and camera position specifically is tied to a `THREE.Vector3` object that must never be serialized (VISION-GOV-010-adjacent reasoning) |
| Any Object URL | None is ever created in this codebase — `triggerBrowserDownload()` creates and revokes its object URL synchronously within one function call, never storing it |
| `exportStatus`, `exportError` | Transient, per-session network-operation state |

## Corruption recovery, confirmed unchanged and re-verified

`loadDefinition()`'s existing three-layer defense (unavailable storage → null; invalid JSON → null; structurally invalid definition → null) was not modified this Sprint — `useProjectStore.ts`'s `initialDefinition = loadDefinition() ?? createDefaultDefinition()` still falls back safely in every failure case. This Sprint's own `loadStoredViewMode()` was written to the identical standard.
