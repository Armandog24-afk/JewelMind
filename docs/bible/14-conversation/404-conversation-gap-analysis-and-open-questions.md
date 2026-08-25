---
id: JM-BIBLE-404
title: Conversation Gap Analysis and Open Questions
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-CONVERSATION-README
  - JM-BIBLE-370
  - JM-BIBLE-403
related_documents:
  - JM-BIBLE-CONVERSATION-README
implementation_status: current
professional_validation: not_required
normative: false
---

# Conversation Gap Analysis and Open Questions

This document catalogues gaps and open questions observed while building Sprint 12, without implementing any of them. Per Bible governance ([`000-bible-governance.md`](../00-foundation/000-bible-governance.md)'s CURRENT/PARTIAL/PLANNED/VISION rule), none of these are CURRENT or PARTIAL functionality — they are candidate future work, gated by the RFC/ADR process named in [`370-conversation-governance.md`](370-conversation-governance.md). Every entry below was verified against the real code, not assumed.

## Schema-complete but currently unreachable values

These are real, correctly-typed fields that no current code path ever sets — a deliberate, honest pattern this codebase uses throughout (the same pattern appears in several Designer/Design-Intent codes from Sprints 10-11).

| Value | Where declared | Why it's unreachable today |
|---|---|---|
| `SessionStatus.WAITING_FOR_ACCEPTANCE` | `schemas.py` | `service.py` only ever assigns `IDLE`, `ACTIVE`, `WAITING_FOR_CLARIFICATION`, `PROPOSAL_READY` — a proposal being reviewed is `PROPOSAL_READY`, not a separate awaiting-acceptance state. |
| `SessionStatus.CLOSED` | `schemas.py` | No code path ever closes a session — a session simply stops being sent by the caller. |
| `SessionStatus.FAILED` | `schemas.py` | Failures raise an `AppError`/HTTP error instead of returning a session with this status; the caller's last-known-good session is left untouched. |
| `ConversationActionType.ADD_INTENT` | `schemas.py` | `classify_action()` never returns it; an intent-only technical result is relabeled `MODIFY_INTENT` in `_resolve_designer_proposal()` regardless of whether the intent is new or a modification. |
| `ConversationActionType.REMOVE_INTENT` | `schemas.py` | Same as above — no code path constructs a "remove an intent statement" turn; that is a `useDesignIntentStore.removeStatement()` UI action, entirely outside Conversation. |
| `ProposalStatus.REJECTED` | `schemas.py` | `_handle_reject()` clears `session.activeProposal` to `None` rather than relabeling it `REJECTED` — a rejected proposal simply stops existing in session state. |
| `ProposalStatus.STALE` | `schemas.py` | Staleness is detected at accept-time and raises `ConversationStaleContextError` immediately; the proposal object is never mutated to carry this status. |
| `clarifications.cancel()` / `clarifications.supersede()` | `clarifications.py` | Both are real, correct, `model_copy`-based functions with zero call sites anywhere in `service.py` — `_handle_cancel()` clears `pendingClarification` to `None` directly instead of calling `cancel()` on it, and nothing currently supersedes an open clarification thread the way `_handle_designer_routed()` supersedes an active proposal. |
| `ConversationTurn.role = "system"` | `schemas.py` | `_make_turn()` hardcodes `role="user"` unconditionally — every turn's structured fields (`result`, `interpretedAction`, diff/intent lists) already carry "JewelMind's side" of the exchange, so a separate system-authored message was never needed. |
| `CONVERSATION_PROPOSAL_SUPERSEDED`, `CONVERSATION_CONTEXT_TOO_LARGE`, `CONVERSATION_ACTION_UNSUPPORTED`, `CONVERSATION_STATE_SYNC_FAILED` | `errors.py` / `schemas.py` | Verified by direct grep: none of the four is instantiated or raised anywhere in `service.py` or `routes.py`. Proposal supersession happens silently via a status field change, not an error; context size, action support, and state-sync all currently succeed unconditionally given the bounded `MAX_RECENT_TURNS_IN_CONTEXT` and the fixed 13-action classifier. |

## Behavioral gaps

| Gap | Business value | Complexity | Architecture dependency | Professional-validation need | Target sprint |
|---|---|---|---|---|---|
| `REVERT_LAST_ACCEPTED_CHANGE` not implemented | Medium — users may want to undo an already-applied change, not just an unaccepted proposal | Medium | Would need to reconstruct a prior JDL state; today only `session.acceptedChangeHistory` (a list of dotted paths, not values) is tracked, which is insufficient to revert | No | Unscheduled |
| `TurnContext` built and tested (`build_turn_context()`) but never actually threaded into the real `NaturalLanguageDesignRequest` sent to `DesignerService.interpret()` | Low today — Designer already receives `currentJDL`/`currentDesignIntent` directly, which is what actually matters for correctness; `TurnContext`'s value would be giving a provider *conversational* context (recent changes, open clarification) that Designer's prompt-building doesn't currently use | Low-Medium — `NaturalLanguageDesignRequest` would need a new optional field, and `designer/prompts.py` would need to build a block from it | Touches `designer/schemas.py` and `designer/prompts.py`, not `conversation/` | No | Unscheduled — worth confirming this is intentional simplicity for v1 rather than an oversight |
| Italian clitic-attached pronouns ("rendilo" = "make" + "-lo") not detected by `references.py`'s space-delimited bare-pronoun check | Low-Medium — affects a specific Italian phrasing style | Medium — requires real morphological handling, not a word-list addition | None architecturally, but genuinely non-trivial NLP | No | Unscheduled |
| No real observability instrumentation | Medium — needed before production usage metrics are trustworthy | Low-Medium | Structured logging infrastructure beyond current generic middleware (mirrors the same gap noted for Designer/Design-Intent in earlier sprints) | No | Unscheduled |
| No dedicated JDL operation-vocabulary layer (`SET_FIELD`/`PRESERVE_FIELD`/`RESET_FIELD_TO_SYSTEM_DEFAULT`/`REMOVE_OPTIONAL_FIELD`, as sketched in the original Sprint 12 brief) | Low today — Designer's existing `interactionMode` (`CREATE`/`MODIFY`) split already provides the preserve-unless-explicitly-changed guarantee this vocabulary would have formalized | Medium if ever built as a real intermediate layer | Would sit inside `designer/`, not `conversation/`, if built | No | Unscheduled — deliberate simplification, not a missing safety property (see [`386-state-preservation-policy.md`](386-state-preservation-policy.md)) |
| No merge/rebase logic for a stale proposal | Low — conservative rejection was the brief's own explicit preference ("prefer conservative stale-proposal rejection where merge certainty is insufficient") | High if ever attempted — automatic merging of two independently-edited JDL states is a genuinely hard correctness problem | Would need a real 3-way-merge concept for `JewelryDefinition` | Yes, if ever built — a wrong automatic merge could silently produce an invalid or unintended design | Not planned — deliberately simplified, see [`402-stale-context-and-concurrent-editing.md`](402-stale-context-and-concurrent-editing.md) |
| `docs/bible/00-foundation/005-current-product-status.md` and `docs/bible/appendices/implementation-inventory.md` had not been updated for Sprints 8-11 before this Sprint's cross-cutting pass added a Sprint 12 row | Low — a documentation debt, not a code gap | Low | None | No | A dedicated documentation-catch-up pass, unscheduled |

## Larger future-facing gaps (multi-session, richer capabilities)

| Gap | Business value | Complexity | Architecture dependency | Professional-validation need | Target sprint |
|---|---|---|---|---|---|
| Server-side session persistence | Medium — a session currently only exists as long as the caller keeps sending it | Medium | A real database, currently absent from the whole product | No | Unscheduled — explicitly out of scope per CONV-GOV-001 unless a future ADR changes this |
| Multi-session / multi-user conversation | Medium | High | No auth/accounts exist yet anywhere in JewelMind | Possibly | Unscheduled |
| Voice or image input to Conversation | Low-Medium | High | New multimodal provider capability, new privacy boundary | Yes | Unscheduled |
| Long-term personal memory across sessions | Low-Medium | High | Persistent per-user storage — out of scope (no auth/accounts) | Possibly | Unscheduled |
| A 14th+ `ConversationActionType` beyond the current 13 | Depends on the capability | Depends | Requires an RFC per [`370-conversation-governance.md`](370-conversation-governance.md) | Depends | Unscheduled |

## Open questions

1. **Should `TurnContext` actually be threaded into Designer's provider call, or is Designer's existing `currentJDL`/`currentDesignIntent`-only context sufficient?** The class exists, is tested, and is schema-validated, but nothing currently constructs a `DesignerContext`/prompt block from it. Is this an intentional v1 boundary (Conversation-level context is a UI/session concern only) or an integration step that was simply not reached this Sprint?
2. **Should the 4 currently-unreachable `CONVERSATION_*` diagnostic codes be pruned, or is keeping them schema-reserved for a near-future capability (real supersession errors, context-size limits, action-support gating, state-sync failures) the right call?**
3. **Should `REVERT_LAST_ACCEPTED_CHANGE` be built, and if so, does it require JewelMind to first build a real undo/version-history mechanism at the Studio/Project level** — i.e. is this fundamentally a Conversation-layer feature at all, or does it belong to a future Project/Version sprint that Conversation would then integrate with?
4. **Should Conversation ever gain its own observability event emission**, or should JewelMind instead build one shared structured-logging layer that Designer, Design Intent, and Conversation all adopt together, avoiding three separate ad hoc implementations?
5. **Is conservative stale-proposal rejection (no merge) the permanent policy, or a v1 simplification** that a future sprint might revisit once there's real usage data on how often concurrent manual edits actually happen in practice?
6. **Should Italian clitic pronoun handling be added**, and if so, is a word-list/regex approach ever going to be sufficient, or does correct handling require a real morphological analyzer — a materially larger dependency than anything else in `references.py`?
7. **Should `ConversationSession` ever be persisted server-side**, and if that happens, does it remain a pure interaction-state cache (CONV-GOV-001 preserved) or does it become the seed of a future Project-persistence concept — and if the latter, does that require superseding CONV-GOV-001 via an ADR rather than merely extending it?

## Next scheduled sprint

Sprint 13 — **Professional Validation Framework v1** — controlled review of JewelMind geometry, rules and manufacturing assumptions by qualified jewelry CAD designers, goldsmiths, setters and manufacturing professionals, converting preliminary software assumptions into traceable evidence-backed knowledge. None of the gaps above are committed to that Sprint's scope by this document.

## Cross-references

- [`370-conversation-governance.md`](370-conversation-governance.md) — when an RFC or ADR is required before any of these can be built.
- [`403-current-code-mapping.md`](403-current-code-mapping.md) — the real-file inventory these gaps were found while writing.
- `../13-design-intent/362-design-intent-gap-analysis.md` and `363-open-design-intent-questions.md` — the Sprint 11 siblings this document follows in structure.
