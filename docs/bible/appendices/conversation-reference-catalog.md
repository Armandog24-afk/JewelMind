---
id: JM-BIBLE-A75
title: "Appendix: Conversation Reference Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-CONVERSATION-README
  - JM-BIBLE-370
related_documents:
  - JM-BIBLE-CONVERSATION-README
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Conversation Reference Catalog

Every resolvable reference target and trigger word/phrase from `backend/jewelmind/conversation/references.py`, plus the target vocabulary it reuses rather than duplicates: `backend/jewelmind/design_intent/vocabulary.py::TARGET_SYNONYMS`. See `docs/bible/14-conversation/379-reference-resolution.md` and `380-pronoun-and-implicit-target-resolution.md`.

## Explicit target words (`TARGET_SYNONYMS`, `design_intent/vocabulary.py`)

Reused verbatim by `references.py::find_explicit_target()` — never a second, conversation-only word list. Longer phrases are checked before single words (`find_explicit_target()` sorts by phrase length, descending).

| Phrase | Canonical target |
|---|---|
| `ring`, `anello`, `whole ring`, `overall` | `RING` |
| `band`, `fascia` | `BAND` |
| `stone`, `pietra`, `diamond`, `diamante` | `STONE` |
| `setting`, `castone` | `SETTING` |
| `prongs`, `griffe` | `PRONGS` |
| `basket` | `BASKET` |
| `jewelry`, `gioiello`, `product` | `JEWELRY_PRODUCT` |

## Preserve markers (`_PRESERVE_MARKERS`, `references.py`)

Phrases meaning "don't change this — keep it exactly as it is now." A preserve marker **without** an explicit target word is *not* resolved to a guess — `find_preserve_target()` returns `None` in that case, per the "safe vs. unsafe implicit resolution" distinction in `380-pronoun-and-implicit-target-resolution.md`.

```
"leave", "keep", "lascia", "lasciala", "lascialo", "lasciate"
```

## Bare pronouns (`_BARE_PRONOUNS`, `references.py`)

Never safely resolved from the pronoun text alone — only via `session.lastReferencedTarget` (an established topic) or reported as ambiguous.

```
"it", "that", "quello", "quella", "lo", "la"
```

## Comparative/dimensional markers (`_COMPARATIVE_MARKERS`, `references.py`)

The specific case where a missing target is genuinely ambiguous (which field would grow?). A bare pronoun *without* one of these markers (e.g. "make it delicate") is treated as a legitimate whole-ring aesthetic statement, not ambiguous.

```
"wider", "narrower", "bigger", "smaller", "larger", "thicker", "thinner",
"più largo", "più larga", "più stretto", "più grande", "più piccolo",
"più spesso", "più sottile", "wide", "narrow"
```

## Material words (`_MATERIAL_WORDS`, `references.py`)

A safe exception: naming a metal/color directly always resolves to `MATERIAL_APPEARANCE`, regardless of pronoun wording, because no other target has a "material" sense.

```
"gold", "oro", "platinum", "platino", "silver", "argento",
"rose gold", "oro rosa", "white gold", "oro bianco", "yellow gold", "oro giallo"
```

## Resolution outcomes (`resolve_implicit_target()`, `references.py`)

| Input shape | Resolution | `is_ambiguous` |
|---|---|---|
| Text contains an explicit target word | That target | `False` |
| Text contains a material word (no explicit target) | `MATERIAL_APPEARANCE` | `False` |
| Bare pronoun, `session.lastReferencedTarget` is set | The last-referenced target | `False` |
| Bare pronoun, no established topic, no comparative marker (e.g. "make it delicate") | `None` (treated as a whole-ring aesthetic statement, resolved downstream by Design Intent's own RING default) | `False` |
| Bare pronoun, no established topic, comparative marker present (e.g. "make it wider") | `None` | `True` — triggers `REQUEST_CLARIFICATION` per CONV-GOV-010 |
| No target word, no material word, no bare pronoun | `None` | `False` |

## Known targets offered on ambiguous-reference clarification (`_KNOWN_TARGETS`, `service.py`)

When `resolve_implicit_target()` reports `is_ambiguous=True`, `ConversationEngine._handle_designer_routed()` opens an `ENUM_CHOICE` clarification listing:

```
"RING", "BAND", "STONE", "SETTING", "PRONGS", "BASKET",
"MATERIAL_APPEARANCE", "OVERALL_PROPORTION", "VISUAL_HIERARCHY", "JEWELRY_PRODUCT"
```

Note that `OVERALL_PROPORTION` and `VISUAL_HIERARCHY` are offered as clarification choices here even though neither appears in `TARGET_SYNONYMS` as a resolvable word/phrase target — they exist only as Design Intent's own `IntentTarget` values, included in this list for completeness of choice, not as something `find_explicit_target()`/`resolve_implicit_target()` can ever return directly from raw text.
