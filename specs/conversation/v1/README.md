# Conversation v1 — Machine-Readable Specification

The machine-readable half of the Conversation Engine. The narrative, architecture, and contract half lives in [`docs/bible/14-conversation/`](../../../docs/bible/14-conversation/README.md); start there for context.

## What Conversation is

Conversation Engine is the interaction-state layer sitting above Designer (Sprint 10) and Design Intent Model (Sprint 11) — it turns a sequence of natural-language turns into a sequence of structured design transactions, never a stream of authoritative prose. Every schema here describes the real, currently-implemented pipeline in `backend/jewelmind/conversation/`: conversation state is bounded, deterministic, and never a replacement for canonical JDL or DesignIntent.

## Files

| File | Purpose |
|---|---|
| [`conversation-action.schema.json`](conversation-action.schema.json) | The 13 canonical outcomes a turn can resolve into |
| [`clarification-thread.schema.json`](clarification-thread.schema.json) | One structured, open-or-resolved clarification question |
| [`clarification-answer.schema.json`](clarification-answer.schema.json) | The validated (or rejected) outcome of one answer attempt |
| [`conversation-state.schema.json`](conversation-state.schema.json) | One observed `ConversationSession.status` transition |
| [`turn-context.schema.json`](turn-context.schema.json) | What a real provider receives when interpreting one turn — compact, bounded, never raw history |
| [`conversation-turn.schema.json`](conversation-turn.schema.json) | One structured design transaction — inlines the shapes above, matching every prior sprint's convention of not using cross-file `$ref` |
| [`conversation-summary.schema.json`](conversation-summary.schema.json) | A deterministically-rebuilt digest of turns that scrolled out of the recent window |
| [`conversation-session.schema.json`](conversation-session.schema.json) | The full client-carried session — inlines turns, the pending clarification, and the active proposal |
| [`conversation-result.schema.json`](conversation-result.schema.json) | The full response body of `POST /api/conversation/turn` |

## Files not present here, by design

There is no `conversation-proposal.schema.json` — `ConversationProposal` is inlined directly inside `conversation-session.schema.json`'s `activeProposal` property (this brings the schema count to exactly the 9 the Sprint 12 brief specifies). Its `designerProposal` field is a full `DesignerProposal` — see [`specs/designer/v1/design-proposal.schema.json`](../../designer/v1/design-proposal.schema.json) — never duplicated here, matching how `currentJDL`/`candidateJDL` fields elsewhere point at [`specs/jdl/v1/jdl.schema.json`](../../jdl/v1/README.md) instead of re-inlining it.

## Examples

7 examples in [`examples/`](examples/), one per required Sprint 12 flow: `create-and-refine.json` (CASE A), `intent-only-refinement.json` (CASE B), `clarification-flow.json` (CASE C), `preserve-unspecified-values.json` (CASE D), `unsupported-request-flow.json` (CASE E), `correction-flow.json` (CASE F), and `cancelled-proposal-flow.json` (an explicit undo/cancel path). Each file is `{"turns": [ConversationResult, ...]}` — one real `ConversationResult` per turn in the flow, captured as an isolated snapshot (see "How these files are generated" below for why that matters).

## Test vectors

7 files in [`test-vectors/`](test-vectors/):

| File | What it proves |
|---|---|
| `state-transition-vectors.json` | Real `session.status` transitions observed across a create→accept, a propose→reject, and a clarify→cancel flow |
| `reference-resolution-vectors.json` | `resolve_implicit_target()`/`find_preserve_target()` outputs for explicit targets, safe pronoun resolution, ambiguous pronouns, and material words |
| `clarification-resolution-vectors.json` | `try_resolve_answer()` outputs across all 4 `ExpectedAnswerType` values, accepted and rejected |
| `correction-vectors.json` | `classify_action()` outputs for correction/accept/reject/undo phrases against a session with an active proposal |
| `preservation-vectors.json` | Real proposal diffs showing only the requested field changes, every other field unchanged |
| `context-compaction-vectors.json` | `build_turn_context()` before and after a session crosses `MAX_RECENT_TURNS_IN_CONTEXT` |
| `stale-context-vectors.json` | `is_proposal_stale()` outputs for an unchanged base, a JDL changed since proposal creation, and an intent changed since proposal creation |

## How these files are generated

Every example and test-vector file was produced by actually running the real `ConversationEngine`, `references.py`, `clarifications.py`, `context.py`, and `state.py` modules (via a one-off `backend/generate_conversation_specs.py`, run once and not part of the shipped code or test suite) — never hand-typed. `backend/tests/test_conversation_schemas.py` re-validates all of it.

One subtlety worth documenting: `ConversationSession` is mutated in place by `process_turn()` as a conversation progresses. Naively capturing `result.session` across several chained calls and serializing them afterward would make every captured turn show the *final* session state, since they all reference the same mutable object. The generator works around this by deep-copying the session both on the way into each call and on the way out (see `_run()` in `generate_conversation_specs.py`), so each captured example turn genuinely reflects that turn's own state — the same discipline a real client integration needs to get right when displaying conversation history.

## How these files are validated

`backend/tests/test_conversation_schemas.py` validates all 9 schemas and all 7 examples using the same `jsonschema` library used for every prior sprint's specs, plus re-derives one flow live to catch pipeline drift.
