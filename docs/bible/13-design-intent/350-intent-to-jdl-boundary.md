---
id: JM-BIBLE-350
title: Intent To JDL Boundary
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-349
related_documents:
  - JM-BIBLE-351
implementation_status: current
professional_validation: not_required
normative: true
---

# Intent To JDL Boundary

## Three conceptually possible paths — none of them exist yet

`DesignIntent` may only ever influence JDL through one of three conceptual paths:

1. **`DETERMINISTIC_MAPPING`** — a registered `IntentProfile` mapping fires automatically because it satisfies all seven conditions in [`349-deterministic-resolution-policy.md`](349-deterministic-resolution-policy.md).
2. **`USER_CONFIRMATION`** — a proposed numeric resolution is shown to the user, who explicitly approves it before it becomes part of `candidateJDL`.
3. **`ACCEPTED_PROFILE`** — a profile that has itself already been through some acceptance process (e.g. a designer-approved house style) resolves the statement.

None of these three paths currently exist or fire anywhere in the real codebase. This is verifiable directly: `backend/jewelmind/design_intent/` has zero imports of, or references to, `backend/jewelmind/domain/schema.py`'s `JewelryDefinition`. A grep across the package for `JewelryDefinition`, `domain.schema`, or `domain/schema` returns exactly one hit, and it is a docstring comment in `design_intent/__init__.py` describing the *boundary itself* ("...the deterministic `JewelryDefinition` that Forge/Alchemist/Atlas consume") — not an import, not a reference to an actual object.

## What this means concretely

- No function in `design_intent/` constructs, mutates, or even reads a `JewelryDefinition` instance.
- `IntentStatement.relatedJDLPaths` is declared in `schemas.py` but is always an empty list in practice — no code ever populates it (INTENT-GOV-001).
- The one place `DesignIntent` and JDL exist side by side is `designer/service.py::_build_proposal()`, which constructs `DesignerProposal.designIntent` and `DesignerProposal.candidateJDL` from the same request but through two structurally separate pipelines — `build_design_intent()` for the former, `normalizer.py`'s technical-field logic for the latter. Neither pipeline's output feeds the other's input.

## The LLM never mutates JDL directly through intent reasoning

Every raw statement a Designer provider emits (`RawIntentStatement`) passes through `normalize_target()` and `normalize_descriptor()` — `design_intent/normalizer.py`'s deterministic, hand-authored vocabulary check — before it can become part of a `DesignIntent` at all. A value the vocabulary does not recognize is never guessed at or coerced; it becomes an `unresolvedDescriptors` entry with an `INTENT_UNKNOWN_DESCRIPTOR` diagnostic (see [`352-unresolved-intent-lifecycle.md`](352-unresolved-intent-lifecycle.md)). There is no code path where the LLM's raw reasoning about what a descriptor "should" numerically mean ever reaches JDL — the normalization step is a hard, deterministic gate in both directions: into `DesignIntent`, and from there, nowhere near JDL at all in v1.

## Why this boundary is currently absolute, not merely typical

Compare this to Designer's own technical channel: `proposedFields` values do reach `candidateJDL`, after passing through `validate_definition()`. Design Intent has no equivalent downstream step yet, because there is nothing on the other side of that step to receive a value — no deterministic mapping, no confirmation UI for a proposed resolution, no accepted profile. The boundary is not merely respected by discipline; there is currently no code path that could cross it even if a future implementer wanted a shortcut, since `resolver.py` never emits anything shaped like a JDL field path.

## Cross-references

- [`330-intent-governance.md`](330-intent-governance.md) — INTENT-GOV-001, INTENT-GOV-004, INTENT-GOV-016.
- [`349-deterministic-resolution-policy.md`](349-deterministic-resolution-policy.md) — the policy this boundary enforces.
- [`351-intent-to-forge-boundary.md`](351-intent-to-forge-boundary.md) — the equivalent boundary on the Forge side.
- [`356-designer-intent-extraction.md`](356-designer-intent-extraction.md) — how the two channels stay structurally disjoint inside `designer/service.py`.
