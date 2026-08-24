---
id: JM-BIBLE-086
title: Open JDL Questions
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-076
related_documents:
  - JM-BIBLE-JDL-README
implementation_status: current
professional_validation: not_required
normative: false
---

# Open JDL Questions

Each question below is genuinely unresolved. This document records the current provisional behavior — it does not guess an answer and does not treat the provisional behavior as a decision.

| ID | Question | Impact | Current provisional behavior | Affected documents | Blocking? | Decision mechanism | Recommended owner |
|---|---|---|---|---|---|---|---|
| JDL-OQ-001 | Should preview parameters (`meshTolerance`, `angularTolerance`) participate in the definition hash? | Changes `definitionHash` for every document if resolved "no"; affects cache-key stability | Included today (proven by test vectors) | [`076`](076-canonicalization-and-definition-hashing.md) | No — current behavior is stable and tested, just possibly not ideal | ADR (would be a MAJOR hashing-contract change) | Backend maintainer |
| JDL-OQ-002 | Should the JSON Schema structural layer duplicate any semantic-layer positivity/range constraints for defense-in-depth, or stay strictly minimal as it is today? | Affects how much a generic JSON-Schema validator alone can catch before reaching Pydantic/the rule engine | Minimal — structural layer mirrors only what Pydantic itself enforces structurally | [`075`](075-validation-pipeline.md), `specs/jdl/v1/jdl.schema.json` | No | Team discussion + doc update | Backend maintainer |
| JDL-OQ-003 | Should canonicalization define an explicit normalization rule for `-0.0`? | Currently unreachable by any valid field range; matters only if a future field's range includes zero-crossing values | Undefined; `json.dumps(-0.0)` would emit `-0.0` if ever produced | [`065`](065-canonical-json-serialization.md), [`076`](076-canonicalization-and-definition-hashing.md) | No | Small spec addendum once/if a relevant field is added | Backend maintainer |
| JDL-OQ-004 | Should the textual DSL require an explicit `mm` unit suffix on every dimension literal, or allow a bare number with the unit always implied? | Affects DSL ergonomics and whether a future non-mm unit could ever be introduced without ambiguity | Optional suffix, in the draft grammar | [`067`](067-textual-dsl-overview.md), [`068`](068-lexical-conventions.md), `specs/jdl/v1/jdl.ebnf` | Yes, for building a real DSL parser | Language design decision | Whoever implements the DSL parser |
| JDL-OQ-005 | Should the textual DSL support block comments in addition to `//` line comments? | Minor authoring ergonomics | Line comments only, in this draft | [`068`](068-lexical-conventions.md) | Yes, for building a real DSL parser | Language design decision | Whoever implements the DSL parser |
| JDL-OQ-006 | Should `setting.prongCount` become a true `Literal[4, 6]` at the schema/structural layer instead of a semantic rule (`JM-PRONG-001`)? | Trades a less-informative raw type error for a stronger structural guarantee; current design deliberately chose the informative-diagnostic path | Plain `int`, validated semantically | [`060`](060-jdl-governance.md) (JDL-GOV-004), [`075`](075-validation-pipeline.md) | No | Code change + ADR if changed (moves validation authority — see JDL-GOV-004) | Backend maintainer |
| JDL-OQ-007 | Should `material.metal` or `manufacturing.method` ever be allowed to affect geometry (e.g. minimum structural wall thickness enforced per metal, or resin-specific clearances)? | Would move these fields from METADATA to geometry-driving, a parametric-dependency-model change | Metadata/validation-context only, confirmed by inspection | [`064`](064-canonical-document-model.md), [`04-jewelry-domain/052-parametric-dependency-model.md`](../04-jewelry-domain/052-parametric-dependency-model.md) | No | RFC (new geometric relationship) | Jewelry-domain + backend maintainers jointly |
| JDL-OQ-008 | Should a request-body size limit and/or a geometry-generation timeout be introduced as a JDL-level requirement? | Directly addresses the two "NOT MITIGATED" rows in [`083`](083-security-and-resource-limits.md) | No limit exists today | [`083`](083-security-and-resource-limits.md) | No (not currently exploited, but a known gap) | Engineering decision, not a jewelry-domain one | Backend maintainer |
| JDL-OQ-009 | Should the frontend's `isValidJewelryDefinition()` runtime guard be tightened to match backend strictness (integer-ness of `prongCount`, `{4,6}` set membership), or intentionally stay a looser, fast preliminary check? | Affects how early a malformed `localStorage` definition is caught on the frontend | Looser than the backend, by current design (see [`084`](084-current-implementation-mapping.md) finding 3) | [`084`](084-current-implementation-mapping.md) | No | Frontend code change if decided | Frontend maintainer |
| JDL-OQ-010 | When a second ring style or stone shape is eventually added, should `category`/`style`/`shape` become a tagged union with per-variant field sets, or stay flat fields shared across all variants? | A foundational schema-shape decision that would be very disruptive to change after a second variant already exists | Flat fields; only one variant of each exists, so the question hasn't yet been forced | [`064`](064-canonical-document-model.md), [`070`](070-type-system.md), [`04-jewelry-domain/056-domain-extension-strategy.md`](../04-jewelry-domain/056-domain-extension-strategy.md) | Yes, before a second ring style RFC is accepted | RFC + ADR (schema-shape decision) | Whoever authors the first new-ring-style RFC |

## What this document is not

It is not a backlog and not a set of recommendations disguised as questions. Each provisional behavior is exactly what the code does today, stated so a future decision-maker starts from the true current state rather than from an assumption.
