---
id: JM-BIBLE-067
title: Textual DSL Overview (Planned)
version: 1.0.0
status: draft
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-065
related_documents:
  - JM-BIBLE-068
  - JM-BIBLE-069
implementation_status: planned
professional_validation: not_required
normative: false
---

# Textual DSL Overview (Planned)

**Status: PLANNED, NON-NORMATIVE. No parser exists. None is built in this milestone.** This document and [`specs/jdl/v1/jdl.ebnf`](../../../specs/jdl/v1/jdl.ebnf) exist so the syntax is designed deliberately, before a parser is ever written — not so a parser can be built immediately afterward.

## Starter example (illustrative only — to be inspected and improved, not copied verbatim)

```
jdl 1.0

project "Solitaire Ring" {
  units mm
}

ring solitaire {
  size EU 16.0
  innerDiameter 17.8 mm

  band {
    width 2.4 mm
    thickness 1.8 mm
    profile comfort_fit
  }

  stone center {
    shape round
    diameter 6.5 mm
    depth 4.0 mm
  }

  setting prong {
    prongCount 6
    prongDiameter 1.1 mm
    prongHeight 4.8 mm
    basketHeight 3.5 mm
  }

  material yellow_gold_18k
  manufacturing lost_wax_casting
}
```

This maps field-for-field onto the current `JewelryDefinition` (see [`064-canonical-document-model.md`](064-canonical-document-model.md)) and introduces no new concept. The full grammar is [`specs/jdl/v1/jdl.ebnf`](../../../specs/jdl/v1/jdl.ebnf); lexical rules are [`068-lexical-conventions.md`](068-lexical-conventions.md).

## Strict requirements for any future implementation

1. **Unambiguous** — a document must have exactly one valid parse, given the grammar.
2. **No executable expressions** — no arithmetic, string concatenation, or expression evaluation of any kind inside a value position.
3. **No loops, conditionals, or functions** — a JDL document is data, never a program.
4. **No arbitrary code** — no embedded scripting language, in any block.
5. **No network imports** — no `include`/`import` of a remote URL.
6. **No hidden defaults invented by the parser** — a value omitted in text must resolve to the exact same documented default as an omitted field in Canonical JSON (see [`073-required-optional-default-and-derived-values.md`](073-required-optional-default-and-derived-values.md)), never a different, DSL-specific default.
7. **Explicit brace/block structure** — every block (`project { }`, `band { }`, `stone center { }`, ...) has an explicit opening and closing brace; no indentation-sensitive block structure.
8. **Explicit comments** — `//` line comments only, in this draft (see [`068-lexical-conventions.md`](068-lexical-conventions.md) for the final decision).
9. **Explicit quoted strings** — a project name or any free-text value is always double-quoted; a bare word is always an identifier or keyword, never ambiguous with a string.
10. **Explicit numeric literals** — see [`068-lexical-conventions.md`](068-lexical-conventions.md) for the exact number grammar.
11. **Explicit unit-bearing literals where applicable** — a dimension may carry an explicit `mm` unit suffix in this draft grammar; whether the suffix becomes *mandatory* is open question JDL-OQ-004 in [`086-open-jdl-questions.md`](086-open-jdl-questions.md).
12. **Reserved keywords are listed exhaustively** in `specs/jdl/v1/jdl.ebnf`'s trailing comment and must not double as identifiers.
13. **Case-sensitive** — `Prong` and `prong` are different tokens; the latter is the only one ever valid.
14. **Duplicate declaration behavior specified** — a block or field declared twice at the same level is a parse-time error (`JDL-PARSE-DUPLICATE-FIELD`), never last-value-wins, unlike current JSON-parsing behavior. This is a deliberate divergence from JSON's own duplicate-key handling, made because a textual DSL is human-authored and a duplicate is far more likely to be a mistake worth surfacing than a generated JSON payload's duplicate key would be.

## Explicitly not decided by this document

Whether units are mandatory on every dimension, whether a shorthand exists for the default project block, and whether nested blocks may be reordered are all open questions — see [`086-open-jdl-questions.md`](086-open-jdl-questions.md). This document does not guess.
