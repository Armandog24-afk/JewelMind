---
id: JM-BIBLE-261
title: Export Experience
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-260
related_documents:
  - JM-BIBLE-A50
implementation_status: current
professional_validation: not_required
normative: true
---

# Export Experience

## The 5-state eligibility model

`frontend/src/studio/outputEligibility.ts::computeOutputEligibility()` — one function, one precedence order, shared by every artifact:

| State | Meaning | Button behavior |
|---|---|---|
| `AVAILABLE` | Ready to export now | Enabled, label "Download"/"Save render" |
| `UNAVAILABLE` | No model exists yet | Disabled, "Generate a model first" |
| `EXPORTING` | In flight | Disabled, "Preparing…" |
| `FAILED` | Last attempt errored, not currently stale | Enabled (retry), "Last attempt failed — try again" |
| `STALE_BLOCKED` | Model is stale or has blocking validation errors | Disabled, "Design changed — regenerate first" |

Precedence: `EXPORTING` > `UNAVAILABLE` > `STALE_BLOCKED` > `FAILED` > `AVAILABLE` — confirmed by 8 tests in `outputEligibility.test.ts`, including the edge case where a design changes again after a failed export (correctly reported as `STALE_BLOCKED`, not `FAILED`, for the same reasoning as the model-state precedence in [`259-model-state-experience.md`](259-model-state-experience.md)).

## Consistent pattern, not scattered buttons

Every artifact renders through the same `ArtifactRow` component — there is exactly one place in the codebase that decides how an export button looks in each state, eliminating the risk of STEP and STL ever disagreeing about what "stale" should look like (a real risk before this Sprint, when each button's disabled logic was written independently inline in `ProjectActions.tsx`).

## No ZIP bundling

Per this Sprint's explicit instruction, artifacts are not bundled into a single downloadable package. Each `ArtifactRow` triggers exactly one download. A future "Download package" is recorded as PLANNED — see the bundled-downloads entry in [`283-studio-gap-analysis.md`](283-studio-gap-analysis.md).

## Error state, per artifact

`exportError` (a single string in `useProjectStore`, unchanged from before this Sprint) is threaded into every download-type `ArtifactRow` and rendered inline in that row when its eligibility is `FAILED` — restating this Sprint's "error state per artifact" requirement. This is a known, honest limitation: `exportError` is a single shared field, not one per artifact type, so if two exports fail in quick succession only the most recent message is shown against both rows until a fresh attempt succeeds. Recorded as a real, minor gap rather than silently accepted as perfect — see [`283-studio-gap-analysis.md`](283-studio-gap-analysis.md).

## Stale model protection, verified live

During this Sprint's browser verification, editing a field after a successful STEP export immediately flipped all 5 output rows to `STALE_BLOCKED` ("Design changed — regenerate first"), confirmed via direct page-text inspection — no output remained silently available for the old, no-longer-current model.
