---
id: JM-BIBLE-250
title: Studio Governance
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-220
related_documents:
  - JM-BIBLE-STUDIO-README
implementation_status: current
professional_validation: not_required
normative: true
---

# Studio Governance

## STUDIO-GOV-001 through STUDIO-GOV-015

| ID | Rule |
|---|---|
| **STUDIO-GOV-001** | Studio must never duplicate authoritative backend jewelry rules. `NumericField`'s `min`/`max` are UI hints for immediate feedback, never a second copy of a Forge rule's threshold — the backend's `validate_definition()` remains the single source of truth for what is actually blocking. |
| **STUDIO-GOV-002** | Frontend validation is advisory until backend validation confirms it — restates Product Principle 6 at the Studio layer; `shared/validation/engine.ts` runs the identical 16+ rules as the backend for instant feedback, but every `generate()` call re-validates server-side regardless. |
| **STUDIO-GOV-003** | Visual-only changes must not regenerate geometry — view mode, camera preset, component visibility, and material presentation live in `useVisionStore`, which has zero coupling to `useProjectStore.generate()` (verified by `useVisionStore.test.ts`). |
| **STUDIO-GOV-004** | Geometry-driving changes must mark the current model stale — every `updateXxx()` action in `useProjectStore` sets `isStale: true` via `withUpdatedDefinition()`, unchanged since before this Sprint. |
| **STUDIO-GOV-005** | A stale model must never be presented as current — `computeModelState()` (`frontend/src/studio/modelState.ts`) is the single function computing this distinction, consumed identically by the header badge, the in-viewport banner, and output eligibility. |
| **STUDIO-GOV-006** | The last successful model may remain visible after parameter changes or failed regeneration — restates VISION-GOV-006/007 at the Studio layer; `lastSuccessfulPreview` is untouched by a failed `generate()` call. |
| **STUDIO-GOV-007** | Export eligibility must correspond to the correct generated model — `computeOutputEligibility()` gates every artifact (including the Presentation PNG) on the same `isStale`/`hasBlockingValidationErrors` facts the model-status badge uses, so an output can never claim availability for a model that no longer matches the current parameters. |
| **STUDIO-GOV-008** | Users must always be able to distinguish editable design parameters from generated outputs — the left panel (`ConfigurationPanel`) only ever contains editable JDL fields; the right panel (`RightPanelTabs`) only ever contains read-only/generated information (validation, outputs, specification, JSON, model info). |
| **STUDIO-GOV-009** | Warnings and errors must be visually distinct — `ValidationItem`'s severity-keyed class names and `ModelStatusBadge`'s tone system both encode severity via label text plus color, never color alone. |
| **STUDIO-GOV-010** | Studio must not hide important Forge diagnostics — every `ValidationResult` the backend returns is still rendered in the Validation tab; Studio reorganizes presentation, it never filters out a diagnostic. |
| **STUDIO-GOV-011** | Technical terminology must use the controlled JewelMind glossary — see [`280-product-copy-and-terminology.md`](280-product-copy-and-terminology.md). |
| **STUDIO-GOV-012** | User-facing language must avoid unsupported manufacturing claims — restates LAW-010; every output description in the Outputs panel was written to avoid implying manufacturing readiness. |
| **STUDIO-GOV-013** | Studio state must not become a second JDL schema — `useVisionStore`/`frontend/src/studio/*.ts` never define a field that duplicates a `JewelryDefinition` field; Studio state describes UI/workflow facts (view mode, model state, output eligibility), never design intent. |
| **STUDIO-GOV-014** | Core workflows must remain usable without a mouse where practical — see [`273-keyboard-and-input-model.md`](273-keyboard-and-input-model.md); every control is a native, keyboard-focusable element, and a small shortcut set covers generate/fit/camera presets. |
| **STUDIO-GOV-015** | User actions must have visible state feedback — every button that triggers an async action (`Generate`, `Download`, `Save render`) changes its own label/disabled state while in flight; see [`267-status-and-feedback-system.md`](267-status-and-feedback-system.md). |

## When an ADR is required

Moving Studio-owned state (view mode, model status, output eligibility) into `useProjectStore`, introducing a second design-definition schema at the Studio layer, or any change that violates STUDIO-GOV-001 through STUDIO-GOV-015 without superseding this document first.

## When an RFC is required

A new major product workflow — a project dashboard, multiple open designs, undo/redo, or autosave — see [`283-studio-gap-analysis.md`](283-studio-gap-analysis.md). A reorganization of existing controls within the current single-workspace model does not require an RFC.
