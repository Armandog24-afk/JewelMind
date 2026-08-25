---
id: JM-BIBLE-306
title: Prompt Architecture
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-305
related_documents:
  - JM-BIBLE-307
implementation_status: current
professional_validation: not_required
normative: true
---

# Prompt Architecture

`backend/jewelmind/designer/prompts.py::build_system_prompt()` assembles a real, layered system prompt from five blocks, joined with blank lines. Nothing here is hypothetical — this is the literal text a live `AnthropicDesignerProvider` call would send.

## The five layers

1. **`SYSTEM_CONTRACT`** — a fixed instruction block establishing role and hard rules. A real excerpt:

   > "You are JewelMind Designer, a natural-language interpretation layer for a parametric jewelry CAD system. You do not design jewelry and you do not decide what is manufacturable... Never propose an enum value that is not listed in CURRENT CAPABILITIES for that field."

2. **`build_jdl_fields_block()`** — the literal 19 dotted JDL paths Designer may reference (`project.name`, `ring.size`, ... `jewelry.style`), matching `capability.KNOWN_JDL_FIELD_PATHS` exactly.
3. **`build_capabilities_block()`** — `json.dumps(current_capabilities())`, the same live, schema-derived dict described in [`296-capability-awareness.md`](296-capability-awareness.md).
4. **`build_current_design_block()`** — for `CREATE`, a plain note that unspecified fields keep system defaults; for `MODIFY`, the full current `JewelryDefinition` as canonical JSON (`current.model_dump_json()`), so the model can see what already exists rather than guessing.
5. **`build_output_schema_block()`** — a prose restatement of the `RawDesignerResponse` shape, reinforcing the same contract already mechanically enforced by `_TOOL_INPUT_SCHEMA` (see [`304-ai-output-constraining.md`](304-ai-output-constraining.md)).

`build_user_message()` is a separate, minimal wrapper: the raw request text plus an optional locale hint, nothing else.

## What is deliberately excluded

The module's own docstring states it plainly: this prompt "deliberately does NOT embed the Technical Bible, any secret, or any credential — only the current JDL schema shape, current capabilities, and the current design state (when modifying)." No file path, no API key, no unrelated project data, and no governance document text is ever concatenated into a prompt. See [`315-privacy-and-data-boundaries.md`](315-privacy-and-data-boundaries.md) for the full inbound/outbound data-boundary treatment.

## Why layering, not one blob

Separating the fixed contract from the two data blocks (capabilities, current design) means a schema change or a capability change automatically produces a correct prompt on the next call — `build_capabilities_block()` re-reads `current_capabilities()` fresh every time, so there is no stale, hand-copied capability list to fall out of sync with `domain/schema.py`. Only `SYSTEM_CONTRACT` and the fields list require a manual edit if the JDL's field set changes.

See [`307-provider-abstraction.md`](307-provider-abstraction.md) for the provider that actually sends this prompt, and the honest statement that it has never been sent to a live endpoint in this environment.
