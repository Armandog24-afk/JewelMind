---
id: JM-BIBLE-380
title: Pronoun and Implicit Target Resolution
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-CONVERSATION-README
  - JM-BIBLE-370
  - JM-BIBLE-379
related_documents:
  - JM-BIBLE-335
  - JM-BIBLE-334
implementation_status: current
professional_validation: not_required
normative: true
---

# Pronoun and Implicit Target Resolution

## The core design tension

A bare pronoun ("it", "that", "quello") is structurally ambiguous on its own — it could mean the band, the stone, the whole ring, or nothing at all. `resolve_implicit_target()` (`backend/jewelmind/conversation/references.py`) resolves this tension with one governing distinction: **whether the request is comparative/dimensional or purely aesthetic.**

- **"make it wider"** — a comparative marker (`wider`, one of `_COMPARATIVE_MARKERS`) attached to a bare pronoun with no established topic. This is genuinely ambiguous: "wider" implies a numeric field must grow, and *which* field (`band.width`? `stone.diameter`? something else?) is exactly the information missing. `resolve_implicit_target()` returns `(None, True)` here — CONV-GOV-010 requires this to trigger a clarification, never a guess.
- **"make it more classic" / "make it delicate"** — no comparative marker. This is a legitimate whole-ring aesthetic statement with no missing information at all: there is nothing dimensional to scope, so there is no ambiguity to resolve. `resolve_implicit_target()` returns `(None, False)` — not ambiguous, and correctly so, because a target of `None` here doesn't mean "unknown"; it means "this statement doesn't need a structural target at all, Design Intent will classify it on its own."

## Why an unscoped aesthetic descriptor is safe

This mirrors how Design Intent Model already treats an unscoped aesthetic descriptor. `backend/jewelmind/design_intent/vocabulary.py`'s `TARGET_SYNONYMS` table includes `"ring"`, `"anello"`, `"whole ring"`, and `"overall"` mapping to the canonical target `RING` — a real, ordinary member of the same target vocabulary as `BAND`/`STONE`/`SETTING`, not a fallback or default value manufactured for this purpose. When a provider (an LLM, per [`335-aesthetic-descriptor-model.md`](../13-design-intent/335-aesthetic-descriptor-model.md)) reads "make it more classic" in context and reports `target="ring"` alongside `concept="STYLE_CONTINUUM", value="classic"`, that is an entirely ordinary `IntentStatement` — Design Intent has no special-case "default to RING" branch to invoke, because treating the whole product as the subject of an unscoped style word is simply what `RING` already means in its vocabulary. `resolve_implicit_target()`'s job in Conversation is narrower and upstream of that: it only decides whether Conversation itself needs to interrupt with a clarification before handing the turn to Designer at all — and for a non-comparative aesthetic statement, it correctly decides no interruption is warranted, leaving Design Intent free to do its own, already-correct target classification downstream.

## `_BARE_PRONOUNS` and `_COMPARATIVE_MARKERS`

```python
_BARE_PRONOUNS: tuple[str, ...] = ("it", "that", "quello", "quella", "lo", "la")
_COMPARATIVE_MARKERS: tuple[str, ...] = (
    "wider", "narrower", "bigger", "smaller", "larger", "thicker", "thinner",
    "più largo", "più larga", "più stretto", "più grande", "più piccolo",
    "più spesso", "più sottile", "wide", "narrow",
)
```

`resolve_implicit_target()`'s branch order:

1. `find_explicit_target(text)` — an explicit component word always wins, regardless of any pronoun present.
2. `mentions_material_word(text)` — a material word resolves to `MATERIAL_APPEARANCE` even though "it" alone would not; see `references.py`'s own comment: "make it rose gold" is safe because no other target has a "material" sense, so the material word alone disambiguates.
3. A bare pronoun check (`f" {p} " in f" {lowered} "` for each of `_BARE_PRONOUNS`, padded with spaces so `"it"` doesn't match inside `"width"`). If none is present, returns `(None, False)` — not a pronoun sentence at all, nothing to resolve.
4. If `last_referenced_target is not None`, the pronoun resolves to it (the established topic) — never a guess from the pronoun text alone (CONV-GOV-009).
5. Otherwise: `(None, True)` if `mentions_comparative_marker(text)`, else `(None, False)` — the tension described above, resolved.

## Acknowledged limitation: Italian clitic pronouns are not detected

`_BARE_PRONOUNS`'s space-delimited matching (`f" {p} " in f" {lowered} "`) only finds a pronoun that appears as its own whitespace-delimited token. Italian frequently attaches an object clitic directly to an imperative verb — "rendilo più largo" ("make it wider"), where `-lo` ("it") is fused onto `rendi` ("make") rather than appearing as a separate word. No regex or tokenization step in `references.py` splits `rendilo` into `rendi` + `lo`; the bare-pronoun check simply never fires for this sentence, so it falls through to `find_explicit_target()`/`mentions_material_word()` finding nothing, and the whole function returns `(None, False)` — not ambiguous, just resolved to nothing, silently missing the fact that a real pronoun reference was present.

This is an honest, out-of-scope NLP limitation, not a silently-ignored one: `references.py` is deliberately simple, whitespace-token matching, consistent with every other deterministic-matching module in this codebase (compare `designer/normalizer.py`'s own denylist-based, non-exhaustive prompt-injection screen, `docs/bible/12-designer/314-prompt-injection-and-untrusted-input.md`). Building real Italian morphological analysis (clitic detection, verb-pronoun segmentation) is a distinct, much larger capability than anything Sprint 12 scopes — see [`404-conversation-gap-analysis-and-open-questions.md`](404-conversation-gap-analysis-and-open-questions.md).
