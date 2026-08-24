---
id: JM-BIBLE-068
title: Lexical Conventions (Planned DSL)
version: 1.0.0
status: draft
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-067
related_documents:
  - JM-BIBLE-069
implementation_status: planned
professional_validation: not_required
normative: false
---

# Lexical Conventions (Planned DSL)

**Status: PLANNED, NON-NORMATIVE.** Lexical rules for the future textual JDL DSL, referenced by [`specs/jdl/v1/jdl.ebnf`](../../../specs/jdl/v1/jdl.ebnf).

| Aspect | Rule |
|---|---|
| Character encoding | UTF-8 |
| Comments | `//` to end of line only, in this draft. Block comments are not yet decided (open question JDL-OQ-005) |
| Whitespace | Insignificant between tokens; used only to separate them |
| Identifiers | `letter , { letter \| digit \| "_" }` — must not collide with a reserved keyword |
| Reserved keywords | `jdl`, `project`, `units`, `ring`, `band`, `stone`, `setting`, `material`, `manufacturing`, `preview`, `mm`, `EU`, `comfort_fit`, `flat`, `round`, `prong`, `center`, `yellow_gold_18k`, `white_gold_18k`, `rose_gold_18k`, `platinum`, `silver`, `lost_wax_casting`, `direct_resin_printing` — exactly the current enum members and section names, no more |
| Case sensitivity | Case-sensitive throughout; keywords are always lowercase/snake_case exactly as listed |
| String literals | Double-quoted, no multi-line strings, backslash-escaped `\"` and `\\` only |
| Numeric literals | Optional leading `-`, digit sequence, optional `.` + digit sequence — no exponent notation, no leading `+`, no underscores-as-digit-separators, no hexadecimal |
| Unit-bearing literals | A numeric literal optionally followed directly by `mm` (no space) for dimension fields; `angularTolerance`/`meshTolerance` never take a unit suffix (see [`071-units-and-numeric-model.md`](071-units-and-numeric-model.md)) |
| Duplicate declarations | A field or block repeated at the same nesting level is a parse error, never last-value-wins (see [`067-textual-dsl-overview.md`](067-textual-dsl-overview.md)) |
| Non-finite numbers | `inf`, `-inf`, `nan` (in any casing) are not numeric literals in this grammar at all — they simply don't parse as `number-literal`, so there is no separate rejection rule needed the way JSON's `Infinity` token requires one |

## What is intentionally still open

Whether block comments exist, whether a trailing comma is permitted in future array-typed fields (none exist today), and whether unit suffixes become mandatory are all recorded as open questions in [`086-open-jdl-questions.md`](086-open-jdl-questions.md) rather than decided here by default.
