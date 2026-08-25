---
id: JM-BIBLE-398
title: Conversation Privacy
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
  - JM-BIBLE-395
  - JM-BIBLE-397
implementation_status: current
professional_validation: not_required
normative: true
---

# Conversation Privacy

Grounded directly in `ConversationTurnRequest` (`backend/jewelmind/conversation/schemas.py`) — this document states exactly what one request to `POST /api/conversation/turn` carries, mirroring the discipline `docs/bible/12-designer/315-privacy-and-data-boundaries.md` already applies to Designer's own request shape.

## What one request actually carries

`ConversationTurnRequest`'s complete field list:

```python
class ConversationTurnRequest(ConversationModel):
    text: str = Field(min_length=1, max_length=2000)
    locale: SupportedLocale | None = None
    currentJDL: JewelryDefinition
    currentDesignIntent: DesignIntent
    session: ConversationSession | None = None
```

- **`text`** — whatever the user typed, verbatim, up to 2000 characters. This is the only field that could contain incidental personal information (e.g. if a user typed something unrelated to jewelry design into the box) — nothing in `backend/jewelmind/conversation/` inspects, logs, or forwards this text anywhere beyond the single `DesignerService.interpret()` call it may trigger (see [`391-conversation-designer-integration.md`](391-conversation-designer-integration.md)).
- **`locale`** — an optional language hint (`SupportedLocale`, the same type Designer already uses).
- **`currentJDL`** — the caller's full current `JewelryDefinition`. This is design data (dimensions, material, stone, setting parameters), not personal data.
- **`currentDesignIntent`** — the caller's full current `DesignIntent`. Same category: aesthetic descriptors about the design, not about the user.
- **`session`** — the entire prior `ConversationSession`, round-tripped by the caller (see "Zero server-side persistence" below).

None of these fields is, or ever contains, a file path, STEP/STL export bytes, an image, or an API key/credential. This mirrors Designer's own "what is never sent" list in `315-privacy-and-data-boundaries.md` exactly, because Conversation's request shape is a superset built from the same underlying pieces (Designer's `NaturalLanguageDesignRequest` plus the conversation-only `session` field), not a new, separately-designed surface.

## `ANTHROPIC_API_KEY` never reaches the frontend or a request body

`backend/jewelmind/api/routes.py::conversation_turn_route()` constructs `DesignerService(provider=get_designer_provider())` per-request, on the backend only; `get_designer_provider()` reads `ANTHROPIC_API_KEY` from server-side environment configuration. No conversation schema — request or response — has a field for it, and it is never interpolated into prompt text (Designer's own `prompts.py` module docstring: "Deliberately does NOT embed the Technical Bible, any secret, or any credential"). This is an unchanged inheritance from Sprint 10, not a new guarantee Conversation had to build.

## Zero server-side persistence — there is nothing to retain or delete

CONV-GOV-001 through CONV-GOV-003 establish that `ConversationSession` never stores a copy of `currentJDL`/`currentDesignIntent`, only content hashes of them, and `service.py`'s module docstring states plainly: "The backend stays stateless per request... the backend never mutates a stored design itself." No database, file, or cache anywhere in `backend/jewelmind/conversation/` or `backend/jewelmind/api/routes.py::conversation_turn_route()` writes a `ConversationSession`, a turn, or a proposal to any persistent store — the entire session lives only in the HTTP request/response cycle, constructed fresh by `state.new_session()` on the first turn and returned to the caller to round-trip on every subsequent request.

This means there is no "how long is a conversation retained on the backend" question to answer, and no persistent-deletion guarantee to make — retention and deletion apply to data that is stored somewhere; nothing here is. This document does not claim JewelMind can delete a user's conversation on request, because there is no server-side copy of it to delete in the first place. If a future change introduces server-side session persistence (explicitly named as requiring an ADR by `370-conversation-governance.md`'s "When an ADR is required" clause), this document must be revised at the same time, not left describing a now-false statelessness guarantee.

## The frontend: `useConversationStore.ts` is explicitly not persisted across reloads

`frontend/src/store/useConversationStore.ts`'s own doc comment states this directly:

> Not persisted across page reloads in v1, the same deliberate scope limit `useDesignIntentStore` already documents.

There is no `localStorage`/`sessionStorage`/IndexedDB write anywhere in the store — it is a plain in-memory Zustand store (`create<ConversationState>((set) => ({...}))`, no persistence middleware). A page reload clears the entire turn history, every clarification thread, and every proposal from the browser. This is the frontend's own retention answer, symmetric with the backend's statelessness: nothing about a conversation survives past the current browser tab's lifetime unless the user has separately accepted a proposal into `useProjectStore`/`useDesignIntentStore` (which, per [`395-studio-integration.md`](395-studio-integration.md), do persist design state, just not conversation history about how that state was reached).

## What this document does not claim

This document does not assert that a live `AnthropicDesignerProvider` (if configured) has any particular retention policy for prompt text it receives — that is a property of the external provider's own service terms, outside JewelMind's code and outside this Bible's authority to state. It only documents what JewelMind's own code sends and stores, which is exactly the scope [`391-conversation-designer-integration.md`](391-conversation-designer-integration.md) and `docs/bible/12-designer/315-privacy-and-data-boundaries.md` already establish for the underlying Designer call.

## Cross-references

- `docs/bible/12-designer/315-privacy-and-data-boundaries.md` — the Designer-layer privacy boundary this document extends, unchanged, to the conversation request shape.
- [`397-conversation-security.md`](397-conversation-security.md) — prompt-injection screening of `text`, a security rather than a privacy concern, but reusing the same field.
- [`395-studio-integration.md`](395-studio-integration.md) — `useConversationStore.ts`'s non-persistence in the context of the wider frontend store architecture.
