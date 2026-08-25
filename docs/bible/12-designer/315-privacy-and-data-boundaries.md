---
id: JM-BIBLE-315
title: Privacy and Data Boundaries
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-314
related_documents:
  - JM-BIBLE-316
implementation_status: current
professional_validation: not_required
normative: true
---

# Privacy and Data Boundaries

Grounded directly in `prompts.py`'s actual construction (see [`306-prompt-architecture.md`](306-prompt-architecture.md)) — this document states what a real provider call would send versus what is structurally never sent, so the boundary is verifiable against real code rather than asserted.

## What a real provider call would send

`build_system_prompt()` and `build_user_message()` together would transmit, to whichever endpoint `AnthropicDesignerProvider` is configured against:

- **The request text itself** (`request.text`) — whatever the user typed, verbatim, plus an optional locale hint.
- **The current JDL, only on `MODIFY`** — `current.model_dump_json()`, the full canonical `JewelryDefinition` for the design being edited, so the model can propose changes relative to it. Never sent on `CREATE`, where there is nothing to modify.
- **The capability subset** — `current_capabilities()`'s JSON dict and the 19 known JDL field paths, so the model knows what it may propose. This is schema metadata, not user data.

## What is never sent

- **No local filesystem path.** Nothing in `prompts.py` interpolates a file path, working directory, or any other environment-specific string.
- **No secret or credential.** The `ANTHROPIC_API_KEY` used to authenticate the call is passed to the SDK client constructor, never into prompt text; `prompts.py`'s own module docstring states this explicitly: "Deliberately does NOT embed the Technical Bible, any secret, or any credential."
- **No unrelated project data.** Only the single `JewelryDefinition` under interpretation is ever included — never other users' designs, never project history, never anything outside the one request's own `currentJDL`.
- **No application logs.** The generic request/timing log line described in [`316-designer-observability.md`](316-designer-observability.md) is written by FastAPI middleware after the response, never fed back into a prompt.
- **No Technical Bible content.** None of `docs/bible/` is embedded — the model receives only the schema-shape and capability facts it needs to do its one job, not JewelMind's architectural reasoning.

## Why this boundary is drawn where it is

The JDL for the design being modified is genuinely necessary for a `MODIFY` request to make sense — a model asked to "change it to platinum" cannot do so without knowing what "it" currently is. Everything else on the "never sent" side is either irrelevant to interpreting one request's text, or actively dangerous to include (credentials, other users' data). No exception to this list exists in current code; a future capability that would require sending something not already on the "would send" list (e.g. a rendered image, a reference sketch) is out of scope for Sprint 10 and would need its own RFC — see [`321-designer-gap-analysis.md`](321-designer-gap-analysis.md).
