---
id: JM-BIBLE-283
title: Studio Gap Analysis
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-282
related_documents:
  - JM-BIBLE-284
implementation_status: current
professional_validation: not_required
normative: false
---

# Studio Gap Analysis

No solution is proposed beyond what's needed to name each gap responsibly — per this Sprint's own instruction not to implement all of these now.

| Gap ID | Current state | Business value | Complexity | Priority | Target sprint |
|---|---|---|---|---|---|
| `STUDIO-GAP-001` Named projects | One unnamed active design (`project.name` is a design field, not a project record) | High for any real multi-design workflow | Medium | High | A dedicated project-workflow sprint |
| `STUDIO-GAP-002` Multiple designs | Single active design only | High | Medium-High | High | Same sprint as `GAP-001` |
| `STUDIO-GAP-003` Autosave | Every edit already writes to `localStorage` synchronously — "autosave" already exists locally; server-side autosave does not | Low locally, high once cloud projects exist | Low (local) / High (cloud) | Low | Deferred until cloud projects are in scope |
| `STUDIO-GAP-004` Project dashboard | Does not exist — single workspace only | High once multiple projects exist | Medium | Medium | Same sprint as `GAP-001`/`002` |
| `STUDIO-GAP-005` Undo/redo | Does not exist — only the single most-recent design is held in state | Medium-High | Medium | Medium | A future sprint, likely before cloud projects (per `STUDIO-OQ-008`) |
| `STUDIO-GAP-006` Design history | Does not exist | Medium | Medium | Medium | Same sprint as `GAP-005` |
| `STUDIO-GAP-007` Compare versions | Does not exist | Medium | Medium-High | Low | Not before design history exists |
| `STUDIO-GAP-008` Duplicate design | Does not exist | Medium | Low | Medium | Same sprint as `GAP-001`/`002` |
| `STUDIO-GAP-009` Presets | Does not exist beyond the single hardcoded default definition | Medium | Low-Medium | Medium | Any near-term sprint |
| `STUDIO-GAP-010` User preferences (beyond `viewMode`) | Only `viewMode` persists; no theme/unit/shortcut-customization preferences exist | Low | Low | Low | Not scheduled |
| `STUDIO-GAP-011` Cloud save | Does not exist — explicitly out of scope per CLAUDE.md | High long-term | High | Low (this stage) | Not before a deliberate product decision to add accounts |
| `STUDIO-GAP-012` Collaboration | Does not exist — explicitly out of scope | Unknown | High | Low | Not scheduled |
| `STUDIO-GAP-013` Comments | Does not exist | Low at this stage | Medium | Low | Not scheduled |
| `STUDIO-GAP-014` Permissions | Does not exist — no accounts exist to attach permissions to | N/A | N/A | Low | Not before accounts exist |
| `STUDIO-GAP-015` Real asynchronous compilation | Generation remains one synchronous request; no job queue | Low today (generation is fast) | High | Low | Only if generation time becomes a real problem |
| `STUDIO-GAP-016` Job queue | Same as above | Low today | High | Low | Same as above |
| `STUDIO-GAP-017` Richer notifications (toast/snackbar system) | Only inline banners/badges exist — see [`267-status-and-feedback-system.md`](267-status-and-feedback-system.md) | Low-Medium | Low-Medium | Medium | Any near-term UI-polish sprint |
| `STUDIO-GAP-018` Command palette | Does not exist | Low at current feature scale | Medium | Low | Not scheduled |
| `STUDIO-GAP-019` Guided beginner mode | Does not exist beyond short inline copy | Unknown — no user research exists | Medium | Low | Not scheduled |
| `STUDIO-GAP-020` No AbortController for generate/export requests | A stale in-flight request cannot be cancelled, only prevented from double-submission | Low today (requests are fast) | Low | Low | Any future hardening sprint |
| `STUDIO-GAP-021` Bundled ("download package") export | Each artifact downloads individually | Low-Medium | Low | Low | Any near-term Outputs-polish sprint |
| `STUDIO-GAP-022` Per-artifact export error messages | `exportError` is a single shared field, not one per artifact | Low | Low | Low | Same sprint as `GAP-017` |

## Architecture debt carried forward from prior sprints, re-confirmed

- `ModelService.generate()` remains mixed-responsibility (Sprint 6 finding, backend, out of Studio's scope).
- No explicit `GeometryPlan` runtime exists (Sprint 6 finding, still true).
- Export-version-fingerprint gaps remain partial (Sprint 7 finding, still true).
- The cache-identity risk (`definitionHash` alone as cache key, no version fingerprint) remains (Sprint 6 finding, still true).
- STEP export remains geometrically but not byte-for-byte deterministic (Sprint 7 finding, still true — unaffected by any frontend change).
- External CAD interoperability remains unvalidated beyond CadQuery's own self-consistency (Sprint 7/8 finding, still true — no new evidence this Sprint).

None of these were addressed this Sprint, per its own explicit instruction not to solve unrelated backend architecture debt merely because Studio touches the API.

## Summary

22 new/updated Studio-specific gaps identified, plus 6 pre-existing architecture-debt items re-confirmed unchanged. **None requires jewelry expertise.** The highest-priority cluster is project/design management (`GAP-001`/`002`/`004`/`008`), because every other gap in that cluster depends on it existing first.
