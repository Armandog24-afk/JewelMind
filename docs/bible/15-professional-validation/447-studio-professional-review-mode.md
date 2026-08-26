---
id: JM-BIBLE-447
title: Studio Professional Review Mode
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-PROVAL-README
  - JM-BIBLE-410
related_documents:
  - JM-BIBLE-446
  - JM-BIBLE-STUDIO-README
implementation_status: current
professional_validation: not_required
normative: false
---

# Studio Professional Review Mode

This document describes an **already-implemented** Studio feature, not a
future intention: the "Review" tab that lets a user generate a
Professional Review Package directly from the running application. Every
name below (`ProfessionalReviewPanel`, `generateReviewPackage`,
`computeOutputEligibility`) was verified by reading the real source files.

## Where it lives

- `frontend/src/components/ProfessionalReviewPanel.tsx` — the component.
- `frontend/src/components/ProfessionalReviewPanel.test.tsx` — 6 real
  `it(...)` test cases.
- `frontend/src/api/client.ts::generateReviewPackage()` — the fetch
  wrapper that calls `POST /api/professional-validation/review-package`.
- `frontend/src/components/RightPanelTabs.tsx` — where the tab is
  registered and mounted.

## Integration into `RightPanelTabs`

`RightPanelTabs.tsx` defines a `TabKey` union that now includes `'review'`
alongside the five pre-existing tabs (`'validation' | 'outputs' |
'specification' | 'json' | 'model-info'`), with a `TABS` entry `{ key:
'review', label: 'Review' }`, and renders `<ProfessionalReviewPanel />`
when `active === 'review'` — exactly the same pattern every other tab
uses, with no special-cased routing or wrapper.

## Component state and props

`ProfessionalReviewPanel` takes no props; it reads directly from
`useProjectStore`:

- `generatedModel` — the current generated model, or `null`.
- `isStale` — whether the design has changed since the last generation.
- `validationResults` — used to compute `hasBlockingValidationErrors =
  validationResults.some((r) => r.severity === 'error')`.

Local component state: `caseId` (string, user-entered, defaults to
`` `JMCASE-${generatedModel.definitionHash}` `` when left blank), `phase`
(`'idle' | 'exporting' | 'success' | 'error'`), and `error` (string or
`null`, populated from `ApiError.message` on failure).

## Gating: the same eligibility rule as every other export, never reimplemented

```ts
const eligibility: OutputEligibilityKey = computeOutputEligibility({
  hasModel: generatedModel !== null,
  isStale,
  hasBlockingValidationErrors,
  phase,
})
```

`computeOutputEligibility()` (`frontend/src/studio/outputEligibility.ts`)
is the single pure function every artifact button in Studio — STEP, STL,
JSON, technical specification, and now the Professional Review Package —
calls to decide whether "now" is a safe time to export. Its precedence is
fixed and shared: `EXPORTING` if mid-export, `UNAVAILABLE` if no model,
`STALE_BLOCKED` if the design changed or a blocking validation error
exists, `FAILED` if the last attempt errored, otherwise `AVAILABLE`. The
`ProfessionalReviewPanel` component does not define its own staleness or
error-blocking logic anywhere — it constructs the same
`OutputEligibilityInput` shape every other artifact constructs and passes
it through the same function, and renders the result through the same
`ArtifactRow` component the Outputs tab uses. This is the mandatory rule
this feature follows, restated directly: **the review package can never
become eligible for generation through a code path independent of the one
every other export already uses.**
`frontend/src/components/ProfessionalReviewPanel.test.tsx` verifies this
behaviorally rather than by inspection alone — `'shows "generate a model
first" when no model has been generated'`, `'is blocked when the model is
stale'`, and `'is blocked when there are blocking validation errors'` all
assert the same `'Design changed — regenerate first'` /
`'Generate a model first'` labels the Outputs tab's own artifacts use
(`OUTPUT_ELIGIBILITY_LABELS`).

## The generate action

```ts
const handleGenerate = async () => {
  if (!generatedModel) return
  const trimmedCaseId = caseId.trim() || `JMCASE-${generatedModel.definitionHash}`
  setPhase('exporting')
  setError(null)
  try {
    const { blob, filename } = await generateReviewPackage(generatedModel.modelId, trimmedCaseId, true)
    triggerBrowserDownload(blob, filename)
    setPhase('success')
  } catch (err) {
    setError(err instanceof ApiError ? err.message : 'Review package generation failed unexpectedly.')
    setPhase('error')
  }
}
```

`generateReviewPackage(modelId, caseId, includeStoneReference)` in
`client.ts` POSTs `{ modelId, caseId, includeStoneReference }` to
`/api/professional-validation/review-package` via the shared
`downloadPost()` helper (the same helper `exportStep`/`exportStl`/
`exportJson` use) and returns `{ blob, filename }`. The panel always
passes `includeStoneReference: true` — the stone reference solid is
included by default in a review package specifically so a reviewer can
assess the setting, in explicit contrast to FOUNDRY-GOV-004's rule that
production STEP/STL export must never default to including the stone; a
review package is not a production artifact and this document treats
that distinction as deliberate, not an oversight.
`triggerBrowserDownload()` (also in `client.ts`) is the same
`URL.createObjectURL` / anchor-click / `URL.revokeObjectURL` pattern used
for every other downloadable artifact — no separate download mechanism
exists for this feature.

## Terminology in primary Studio UI copy

`ProfessionalReviewPanel.tsx`'s own rendered text (the intro paragraph,
the case-ID label, and the `ArtifactRow` name/purpose strings) was read in
full: it uses only product-facing language — "review case ID," "Generate
review package," "STEP, STL, the design definition, technical
specification, geometry data" — and never the words "Forge," "Atlas,"
"Alchemist," or "Foundry." This satisfies STUDIO-GOV-011 for the
component's own UI copy.

**One nuance worth flagging honestly, not glossed over:** the ZIP's
generated `README.md` — produced server-side by
`review_package.py::_readme_text()`, not by this component — does contain
the literal phrase *"Forge diagnostics"* when describing
`forge-report.json`'s contents. That text is never rendered inside the
Studio application itself; it only appears inside the downloaded package,
addressed to an external professional reviewer who has never read the
Technical Bible and has no other name to call the automated-check report
by. Whether STUDIO-GOV-011 ("never put ... these architecture-internal
names in user-facing UI copy") is meant to reach a backend-generated
document bundled for an off-platform audience, versus strictly the
Studio React UI, is not settled by the rule's own text. This document
takes no position on whether that phrasing should change; it is recorded
here as a real, verified fact for
[`451-validation-gap-analysis.md`](451-validation-gap-analysis.md) to
track rather than silently omitted.

## Cross-references

- [`446-review-package-generation.md`](446-review-package-generation.md) — the backend generation mechanics this panel triggers.
- [`11-studio/261-export-experience.md`](../11-studio/261-export-experience.md) — `computeOutputEligibility()`'s home document.
- [`11-studio/280-product-copy-and-terminology.md`](../11-studio/280-product-copy-and-terminology.md) — STUDIO-GOV-011's source.
