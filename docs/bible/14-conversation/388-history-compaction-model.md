---
id: JM-BIBLE-388
title: History Compaction Model
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
  - JM-BIBLE-387
  - JM-BIBLE-389
implementation_status: current
professional_validation: not_required
normative: true
---

# History Compaction Model

## What triggers compaction

`context.py::compact_summary(session)` is only asked to do real work once a session's turn history exceeds the recent window:

```python
has_older_turns = len(session.turns) > MAX_RECENT_TURNS_IN_CONTEXT
older_turns = session.turns[:-MAX_RECENT_TURNS_IN_CONTEXT] if has_older_turns else []
```

With 6 or fewer turns, `older_turns` is empty and `compact_summary()` simply returns the session's existing `summary` fields unchanged (copied, not mutated). Only turns at index `0` through `len(turns) - MAX_RECENT_TURNS_IN_CONTEXT - 1` — the ones that have scrolled *out* of the 6-turn recent window — are ever folded into the summary.

## Field-by-field mapping

For each `turn` in `older_turns`, `compact_summary()` applies exactly these rules:

| Turn field(s) | Condition | Feeds summary field |
|---|---|---|
| `turn.technicalChanges` | `turn.accepted and turn.technicalChanges` | `acceptedDecisions` (each change path appended if not already present) |
| `turn.intentChanges` | `turn.intentChanges` non-empty | `intentThemes` (each `target.concept` string appended if not already present) |
| `turn.sourceText` | `turn.interpretedAction == "REJECT_PROPOSAL"` | `rejectedDirections` (the raw rejection turn's text, appended if not already present) |
| `turn.unsupportedFeatures` | non-empty | `unsupportedDiscussed` (each feature name appended if not already present) |
| `turn.clarification.question` | `turn.clarification is not None and turn.clarification.status == "OPEN"` | `unresolvedQuestions` (appended if not already present) |

Every list uses simple membership dedup (`if x not in list`) — no ordering guarantee beyond first-seen-first-kept, and no cap on how large any of the five lists can grow across a very long session (see the gap analysis).

## What is never summarized away

Structured, exact state is never passed through this compaction logic at all:

- The accepted JDL/DesignIntent themselves — `ConversationSession` never carries a copy of either (CONV-GOV-001/003).
- `session.pendingClarification` (the currently open thread, if any) — read directly by `build_turn_context()`, never derived from the summary.
- `session.activeProposal` — same: read directly, never summarized.

Only turns that have already scrolled out of the 6-turn recent window are compacted; the 6 most recent turns remain available in full to any caller that wants `recent_turns(session)` directly, alongside the summary.

## Real generated evidence: `context-compaction-vectors.json`

`specs/conversation/v1/test-vectors/context-compaction-vectors.json` was produced by actually running `build_turn_context()` against two real sessions, sampled at 4 and 9 total turns against the `MAX_RECENT_TURNS_IN_CONTEXT = 6` boundary:

```json
{
  "maxRecentTurnsInContext": 6,
  "totalTurnsAtSample": [4, 9],
  "contextNeedsSummary": [false, true],
  "sampledContexts": [
    {"...": "...", "compactConversationSummary": null, "modelCurrentOrStale": "CURRENT"},
    {"...": "...", "compactConversationSummary": {"acceptedDecisions": [], "...": "..."}, "modelCurrentOrStale": "CURRENT"}
  ]
}
```

At 4 turns (below the 6-turn threshold), `contextNeedsSummary` is `false` and `compactConversationSummary` is `null`. At 9 turns (above the threshold), `contextNeedsSummary` is `true` and a (in this sample, empty-valued) `ConversationSummary` object is present — proving the boundary condition is `>`, not `>=`, and matches `needs_summary = len(session.turns) > MAX_RECENT_TURNS_IN_CONTEXT` exactly.

`backend/tests/test_conversation.py::TestContext::test_compact_summary_preserves_accepted_decisions_from_older_turns` additionally proves the field-mapping table above directly: a 9-turn session where every turn is an accepted `material.metal` change produces `"material.metal" in summary.acceptedDecisions` after compaction.

## Cross-references

- [`387-context-window-policy.md`](387-context-window-policy.md) — the `MAX_RECENT_TURNS_IN_CONTEXT` bound itself.
- [`389-conversation-summary-model.md`](389-conversation-summary-model.md) — the `ConversationSummary` shape this function produces.
- CONV-GOV-004, CONV-GOV-015, CONV-GOV-016 in [`370-conversation-governance.md`](370-conversation-governance.md).
