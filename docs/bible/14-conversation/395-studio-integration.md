---
id: JM-BIBLE-395
title: Studio Integration
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-CONVERSATION-README
  - JM-BIBLE-370
related_documents:
  - JM-BIBLE-391
  - JM-BIBLE-STUDIO-README
implementation_status: current
professional_validation: not_required
normative: true
---

# Studio Integration

`frontend/src/components/ConversationPanel.tsx`'s own module docstring is the source this document expands on:

> Conversation Engine v1's multi-turn natural-language entry point into Studio — supersedes Designer's single-turn `DesignerPanel` as the mounted "describe your design" surface (`DesignerPanel` itself remains a valid, separately-tested component; it is simply no longer the one `App.tsx` renders). `ConfigurationPanel` stays visible and authoritative at all times, before, during, and after a turn.

## `ConversationPanel` replaced `DesignerPanel` as the mounted entry point — deliberately

`frontend/src/App.tsx` imports and renders `ConversationPanel`, not `DesignerPanel`:

```
import { ConversationPanel } from './components/ConversationPanel'
...
<ConversationPanel />
```

This is a real, deliberate product decision made in this Sprint, not an accident or an incomplete migration — `docs/bible/11-studio/README.md`'s "Relationship to Sprint 12" section states it in the same terms: "Studio's natural-language entry point is `14-conversation/`'s `ConversationPanel`, which supersedes single-turn `DesignerPanel` as the component actually mounted in `frontend/src/App.tsx`." `DesignerPanel.tsx` itself is not deleted: it remains in the codebase, still exercised by its own standalone `DesignerPanel.test.tsx` (confirmed present at `frontend/src/components/DesignerPanel.test.tsx`), but no real Studio session today reaches it through `App.tsx`.

`ConfigurationPanel` (Studio's manual parameter-editing surface) is unaffected by any of this — it stays mounted, visible, and fully interactive regardless of `ConversationPanel`'s state, which is precisely what CONV-GOV-013 requires.

## The 7 conceptual UI states, mapped to the real conditional rendering

`ConversationPanel.tsx` has no single `uiState` enum variable — the 7 states from the Sprint 12 brief are real, but they are derived from several independent pieces of component state (`isLoading`, `providerUnavailable`, `error`, and fields read off `session`), not a literal state machine in code. Reading the component in full, the mapping is:

| Conceptual state | Real condition in `ConversationPanel.tsx` |
|---|---|
| `IDLE` | Default rendering when none of the conditions below hold — `session` is `null` or has no pending clarification/active proposal, `isLoading` is `false`, no error is set. The input form is always rendered in this state. |
| `INTERPRETING` | `isLoading === true`. The submit button's label becomes `"Interpreting…"`, and the `<textarea>` plus every clarification/accept/reject/cancel button gets `disabled={isLoading}`. |
| `NEEDS_CLARIFICATION` | `clarification` is non-null, computed as `session?.pendingClarification?.status === 'OPEN' ? session.pendingClarification : null`. Renders the "JewelMind needs to know" card with `ENUM_CHOICE`/`CONFIRMATION` quick-answer buttons where applicable. |
| `PROPOSAL_READY` | `proposal` is non-null, computed as `session?.activeProposal?.status === 'ACTIVE' ? session.activeProposal : null`. Renders the proposal-review card (technical field diff, design-intent statements, Accept/Reject buttons). |
| `APPLYING` | Not a separate flag. `handleAccept()` reuses the same `sendTurn()` call as every other turn, so `isLoading` is the only signal covering both "interpreting a new turn" and "applying an accepted proposal" — there is no visually distinct "applying" state in the current implementation. This is a real, minor gap between the brief's 7-state model and the shipped code, not a hidden divergence: the UI is correct (the button is disabled and shows "Interpreting…" during an accept, same as any other turn) but does not visually distinguish "waiting for interpretation" from "waiting for an accept to be confirmed." |
| `UNSUPPORTED` | `showUnsupported = lastTurn?.interpretedAction === 'REPORT_UNSUPPORTED'`, where `lastTurn = session?.turns[session.turns.length - 1] ?? null`. Renders the "Not currently supported" alert with `lastTurn.result` (the joined `reason` strings from Designer's `unsupportedFeatures`). |
| `PROVIDER_ERROR` | Two independent pieces of state cover this one conceptual UI state: `providerUnavailable` (set when the caught error is an `ApiError` with `code === 'DESIGNER_PROVIDER_UNAVAILABLE'`, rendering the "AI interpretation is unavailable in this environment" notice) and `error` (set for every other `ApiError`/network failure, including a distinct human-readable message for `CONVERSATION_STALE_CONTEXT`, rendering a `role="alert"` paragraph). |

## Accept applies to two stores, in a specific order that matters

`handleAccept()`:

```typescript
const handleAccept = async () => {
  const proposal = session?.activeProposal
  if (!proposal || proposal.status !== 'ACTIVE') return
  const toApply = proposal.designerProposal
  const result = await sendTurn('Accept')
  if (result?.turn.interpretedAction === 'ACCEPT_PROPOSAL' && result.turn.accepted === true) {
    applyDesignerProposalResult(toApply, applyDesignerProposal, applyIntent)
  }
}
```

`toApply` — the `DesignerProposal` to actually apply — is captured **before** `sendTurn('Accept')` is awaited, because the accept turn's returned `session` has already cleared `activeProposal` to `null` (`_handle_accept()` on the backend sets `session.activeProposal = None`); reading `session?.activeProposal` after the call would find nothing to apply. `sendTurn('Accept')` sends the literal text `"Accept"` as an ordinary turn — it is not a distinct API operation, just a turn whose text happens to match one of `classify_action()`'s `_ACCEPT_PHRASES` while a proposal is active. Only on a confirmed `ACCEPT_PROPOSAL` result (`interpretedAction === 'ACCEPT_PROPOSAL' && accepted === true` — guarding against the backend instead responding with a `MODIFY_DESIGN_PROPOSAL` correction, or raising a `ConversationStaleContextError`) does `applyDesignerProposalResult()` run.

`applyDesignerProposalResult()` (a module-level helper in `ConversationPanel.tsx`) applies to the same two stores `DesignerPanel.tsx` has used since Sprint 10/11, with the same `hasTechnicalChange` gate:

```typescript
const hasTechnicalChange = proposal.diff.some((d) => d.changed)
if (proposal.candidateJDL && hasTechnicalChange) {
  applyDefinition(proposal.candidateJDL)
}
...
if (hasIntentContent) {
  applyIntent(intent)
}
```

`applyDefinition` (`useProjectStore.applyDesignerProposal`) only runs when a real technical field changed, exactly the CONV-GOV-011/012 boundary — an intent-only accepted proposal never touches `currentDefinition`/`isStale`. `applyIntent` (`useDesignIntentStore.applyIntent`) runs independently whenever the accepted proposal carries any statement/relationship/unresolved-descriptor content, regardless of whether a technical field also changed.

## `useConversationStore.ts` — session state only, not persisted

`frontend/src/store/useConversationStore.ts`'s own doc comment:

> Conversation interaction state — Sprint 12 (Conversation Engine v1). Deliberately separate from `useProjectStore` (JDL/design state) and `useDesignIntentStore` (semantic intent state): a `ConversationSession` is neither of those, it only ever tracks interaction/turn history [...]. The backend is stateless per request — this store is the only place the full `ConversationSession` lives between turns; it round-trips through the API on every call. Not persisted across page reloads in v1, the same deliberate scope limit `useDesignIntentStore` already documents.

The store's real shape is minimal: `{ session: ConversationSession | null, setSession(session), resetSession() }`. `setSession` replaces the session wholesale on every `ConversationResult` (`ConversationPanel.tsx`'s `sendTurn()` calls it after every successful turn); there is no partial-update path. A page reload loses the entire conversation, exactly as `useDesignIntentStore.currentIntent` already does — this is a stated, deliberate v1 scope limit, not an oversight; see [`398-conversation-privacy.md`](398-conversation-privacy.md) for the retention implication.

## Cross-references

- `docs/bible/11-studio/README.md`'s "Relationship to Sprint 12" section — the Studio-side statement of the same `ConversationPanel`/`DesignerPanel` supersession this document details from the Conversation side.
- [`391-conversation-designer-integration.md`](391-conversation-designer-integration.md) — the backend half of what `ConversationPanel` is calling into.
- [`386-state-preservation-policy.md`](386-state-preservation-policy.md) — the `hasTechnicalChange`/`proposal.diff.some(d => d.changed)` gate's backend origin.
