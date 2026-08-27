---
id: JM-BIBLE-576
title: Current Round Migration
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-STONE-README
  - JM-BIBLE-560
  - JM-BIBLE-081
related_documents:
  - JM-BIBLE-568
  - JM-BIBLE-564
  - JM-BIBLE-577
implementation_status: current
professional_validation: not_required
normative: true
---

# Current Round Migration

## The classification: MINOR, additive

`domain/schema.py::StoneSpec` changed in four ways this Sprint:

- `shape` gained 6 new enum members (`oval`, `pear`, `emerald`, `cushion`, `princess`, `marquise`).
- `length` and `width` were added, both `float | None`, defaulting to `None`.
- `orientation` was added, `float`, defaulting to `0.0`.
- `diameter` widened from `float` to `float | None` (default unchanged at `6.5`).

Per [`../05-jdl/081-schema-versioning-and-migrations.md`](../05-jdl/081-schema-versioning-and-migrations.md)'s own PATCH/MINOR/MAJOR table, MINOR is:

> An additive, backward-compatible change: a new optional field with a default, a new enum member appended to an existing list, a new semantic rule that only adds diagnostics (never changes acceptance of a previously-valid document from valid to invalid)

Every one of the four changes fits. The new fields are optional with defaults; the enum only gained members; and `diameter` widening its type **relaxes** rather than tightens the constraint, so no previously-valid document becomes invalid. `schemaVersion` correctly stays `"0.1.0"` — that same document reserves a `schemaVersion` bump for MAJOR changes only (Migration Requirement 1).

The one added semantic rule — `StoneSpec`'s `@model_validator` requiring `diameter` for round and `length`+`width` otherwise — cannot reject a previously-valid document either: every pre-Sprint-18 document has `shape: "round"` and a real `diameter`.

## The full round → Stone System mapping

| Layer | Before Sprint 18 | After |
|---|---|---|
| Pydantic model | `StoneSpec(shape, diameter, depth)` | `StoneSpec(shape, diameter, length, width, depth, orientation)` + a `@model_validator` |
| JDL schema | `specs/jdl/v1/jdl.schema.json` stone block: `shape` as `const: "round"`, `diameter`/`depth` as `number` | `shape` as a 7-member `enum`; `diameter`/`length`/`width` as `["number","null"]`; `orientation` added. The conditional requirement is deliberately left to the semantic layer per [`../05-jdl/075-validation-pipeline.md`](../05-jdl/075-validation-pipeline.md) |
| Geometry builder | `geometry/components/stone.py::build_stone_reference()` — the real builder | Thin re-export of `geometry/stone/builder.py::build_stone()`; round's construction preserved byte-identically in `_build_round_stone()` |
| Dimension access | `stone.diameter` read directly in geometry and Forge | `domain/stone_dimensions.py::resolved_length_mm()`/`resolved_width_mm()`/`resolved_depth_mm()` |
| Forge (`validation/engine.py`) | `JM-STONE-001`, `JM-STONE-002`, `JM-PRONG-003` all read `stone.diameter` | `JM-STONE-001` and `JM-PRONG-003` scoped `ROUND_ONLY`; `JM-STONE-002` generalized to `min(resolved_length, resolved_width)` |
| Forge mirror | `shared/validation/engine.ts` matched the above | Updated identically (FORGE-GOV-004) |
| TypeScript types | `StoneShape = 'round'`; `StoneSpec` with `diameter`/`depth` | 7-member union; nullable `diameter`/`length`/`width`; `orientation`; new `isValidStone()` mirroring the Pydantic validator |
| Studio | A single "Diameter" numeric field | Capability-driven `STONE_SHAPE_OPTIONS` selector; Diameter for round, Length + Width otherwise; Orientation in Advanced for non-round |
| Designer | `STONE_SHAPE_SYNONYMS` had 5 round-only entries; 6 shapes listed in `KNOWN_UNSUPPORTED_CONCEPTS` | IT/EN synonyms for all 7 shapes; the 6 stale "only round supported" entries **removed**; `stone.length`/`width`/`orientation` added to `KNOWN_JDL_FIELD_PATHS` and `_NUMERIC_FIELDS` |
| Conversation | Routed shape changes through Designer | Unchanged mechanism — it inherits the widened Designer capability automatically |
| Vision | Parsed backend STL generically | **Unchanged.** No shape-specific frontend code exists or was added (VISION-GOV-001/002) |
| Inspection | Generic component facts only | Plus 6 `STONE_*` requested/measured dimension facts |
| Technical specification | Shape + Diameter + Depth | Round: Shape + Diameter + Depth. Non-round: Shape + Length + Width + Orientation + Depth. Never a fake diameter |
| Ring Architecture v2 | `StoneArrangementDefinition.stone: StoneSpec` | Unchanged — it wraps `StoneSpec`, so it inherited the new fields automatically |
| Goldens | 12 cases, all round | 18 cases; the 12 pre-existing untouched; 6 new per-shape cases |

## What round-only logic was, and was not, removed

**Removed** — because it had become factually false:

- The 6 entries in `designer/capability.py::KNOWN_UNSUPPORTED_CONCEPTS` claiming *"Only round stones are currently supported (stone.shape)"* for oval, emerald_cut, princess_cut, pear, marquise, and cushion. Leaving them would have made Designer actively lie about a real capability.

**Deliberately kept:**

- `_build_round_stone()` as a separate code path. Not dead code and not duplication to be tidied away — it is the mechanism of the byte-identical guarantee. See [`568-round-stone-contract.md`](568-round-stone-contract.md) for why routing round through the shared loft would have changed its geometry (different culet semantics) and could not be proven bit-identical.
- `stone.diameter` as a public field. Removing it would be a MAJOR breaking change for zero benefit.
- `girdleRadiusMm` / `tableRadiusMm` in round's metadata. A radially symmetric outline genuinely has these; other shapes genuinely do not.
- `JM-STONE-001` and `JM-PRONG-003` as round-only rules, rather than generalized against a substituted dimension.

Per the brief's own instruction — *"Remove duplicate round-only logic only after compatibility is verified"* — nothing was removed on the strength of an assumption. The two proofs (exact recorded volume, zero Golden updates) came first.

## The `definitionHash` drift

Adding fields to `StoneSpec` changed `definition_hash()` for every document once regenerated. Real values:

| Example | Before | After |
|---|---|---|
| `default-solitaire.json` | `867175e206c8ba1f` | `e1d6dc2f2390875d` |
| `four-prong-solitaire.json` | `1af3aa14ea3537e0` | `76cd86b9ac469105` |
| `flat-band-solitaire.json` | `23c9d0937ca91045` | `613e1b7451247e6f` |
| `direct-resin-printing-solitaire.json` | `2be05db42097fd4d` | `276ac91816f0fd6a` |

(plus the three `examples/invalid/` documents.)

The cause: `definitionHash` is a SHA-256 of `canonical_json()`, which is `model_dump(mode="json")` — **every** field including newly-added defaults. A document that previously canonicalized `{"depth":4.0,"diameter":6.5,"shape":"round"}` now canonicalizes with `length`, `width`, and `orientation` present at their defaults, so the hash differs even though the geometry is identical.

### This is not a violation of Migration Requirement 4

That requirement states:

> No migration may silently alter a `definitionHash` for a document whose `schemaVersion` field value is unchanged.

The distinction is real and is recorded rather than glossed over. That rule concerns **migrating an already-stored old document** — taking a saved document and transforming it, without changing its declared `schemaVersion`, into something that hashes differently. No code path in this Sprint does that; no migration function was written, and no stored document was rewritten in place.

What actually happened is **normalization-time default-filling on a freshly re-validated document**: any document run through `JewelryDefinition.model_validate()` today gains the new fields at their defaults as part of ordinary validation, exactly as it always has for every other defaulted field. The practical symptom is identical to what Migration Requirement 4 forbids — a changed hash for logically-unchanged content — but the mechanism is different.

This is the *same finding as Sprint 17's*, for the same structural reason (see [`../19-shank/556-current-band-migration.md`](../19-shank/556-current-band-migration.md)). Recording it twice rather than treating it as settled is deliberate: it will recur on **every** future additive `StoneSpec`/`BandSpec`-style change, and it is a real, unresolved tension in the hashing contract rather than a one-off.

### Verified: Golden regression detection was unaffected

`geometry_quality.snapshot.compare_snapshot()` — the real Golden Suite comparator — was checked directly and never reads `definitionHash` anywhere in its comparison logic. Independent practical confirmation: all 12 pre-existing Golden cases remained `STABLE` with zero baseline updates.

### What needed regeneration

Only stored fixtures with hardcoded hash values or serialized stone blocks. **All regenerated by running the real code, never hand-typed**, per every prior Sprint's discipline:

- `specs/jdl/v1/test-vectors/definition-hash-vectors.json`
- `specs/jdl/v1/test-vectors/canonicalization-vectors.json`
- `specs/alchemist/v1/test-vectors/normalization-vectors.json`
- `specs/alchemist/v1/test-vectors/capability-vectors.json` (`supportedStoneShapes` widened to all 7)
- `specs/atlas/v1/test-vectors/metadata-vectors.json`
- `specs/conversation/v1/examples/create-and-refine.json`
- `specs/designer/v1/examples/complete-solitaire-request.json` (`candidateJDL` + `diff`, which grew from 26 to 29 entries)
- `specs/geometry-inspection/v2/examples/default-solitaire-inspection.json` and `four-prong-inspection.json`
- `specs/ring/v2/examples/current-default-solitaire.json`, `flat-band-solitaire.json`, `four-prong-solitaire.json`

## A real downstream ripple

Unlike Sprint 17 — where the same class of additive change broke 260 tests via Designer's one-level-deep `flatten_definition()` — Sprint 18's ripple was small: 8 failing tests, all stale stored fixtures, no logic bugs.

The reason is directly attributable: Sprint 17's recursive `_flatten_into()` fix had already generalized the flattener to arbitrary nesting depth. `StoneSpec` gaining scalar fields needed nothing further. This is worth noting as evidence that the earlier fix was a real structural improvement rather than a local patch.

The one non-fixture adjustment was `specs/alchemist/v1/test-vectors/capability-vectors.json`, whose `supportedStoneShapes` list was genuinely wrong after the enum widened — caught by a test that compares it against the live `StoneShape` args.
