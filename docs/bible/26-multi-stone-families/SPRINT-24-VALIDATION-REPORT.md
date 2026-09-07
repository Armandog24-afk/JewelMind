---
id: JM-BIBLE-FAMILY-SPRINT-24-REPORT
title: "Sprint 24 Validation Report — Multi-Stone Families v1"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-07
source_of_truth: false
depends_on:
  - JM-BIBLE-FAMILY-README
implementation_status: current
professional_validation: not_required
normative: false
---

# Sprint 24 Validation Report — Multi-Stone Families v1

## Test results

| Gate | Result |
| --- | --- |
| `backend/.venv/Scripts/python -m ruff check .` | clean |
| `backend/.venv/Scripts/python -m pytest -q` | **1967 passed** (1841 before this sprint), 1 pre-existing unrelated warning |
| `python -m jewelmind.geometry_quality.cli verify-all` | **All 44 goldens PASS** (39 before), **zero baseline updates** |
| `frontend/ npx tsc -b` | clean |
| `frontend/ npm run test` | **198 passed** across 27 files |

New tests: `test_multi_stone_families.py` (116), `familyValidation.test.ts` (15),
plus 3 new guards in `test_capability_coverage.py` and 3 in
`test_arrangement_schemas.py`.

## What executes

Four families — `THREE_STONE`, `TOI_ET_MOI`, `CLUSTER`,
`CENTER_WITH_ACCENTS` — each declared in JDL, each compiled by a registered
compiler into **arrangement primitives**, each resolved by the existing
arrangement resolver, and each producing **one real stone solid per member**,
placed, scaled and oriented. Mixed gems and mixed per-member scales reach the
geometry. Every stone is named `stone_reference.<instanceId>`, classified as a
reference component, and required by Geometry Inspection.

What does **not** execute, with the reason recorded in
[`execution-boundary.md`](execution-boundary.md): **a setting for a non-primary
member**. A three-stone design builds three stones and one setting. That single
limitation is why all four families are `PARTIAL` rather than `CURRENT`, and it
is reported through four independent channels — the capability registry's
`settingGeometry: false` axis, `JM-FAMILY-005` (information severity), every
test vector's `settingCoverage: "PRIMARY_ONLY"`, and each new Golden case's
`knownLimitations`.

## Verified by execution, not by reading

- **Per-member scale reaches the solid.** A 0.6-scale side stone measures
  `12.575827 mm³` against the centre's `58.221419 mm³` — 0.216 of it, which is
  0.6³ to nine digits. A pattern route that silently dropped the scale would
  have produced two equal stones and passed a component-count check.
- **The metal body is untouched by additional stones.** All five new Golden
  cases report band `250.991683`, head `83.155758`, prongs `29.650351`, three
  production components, **one** fully-connected production group, and
  `stoneReferenceIsProductionMetal: false`. Nine stone references in a cluster
  change none of it (LAW-006, ATLAS-GOV-011).
- **A symmetric pair does not collapse.** Asserted across axis angles
  0/30/45/90/135°, which is what caught the defect below.
- **Reordering `members` changes nothing** — not the compiled arrangement, not
  the canonical JSON, not the `arrangementFingerprint`. Member ids are the
  identity; array position carries no meaning (ARRANGE-GOV-003).
- **A design with no family and no arrangement is unchanged.** The default
  solitaire's fused metal volume still matches `341.44334316909976`, and the
  identity-placement path returns the builder's own solid object rather than a
  translated copy.

## Defects found and fixed during the sprint

1. **Radial compilation double-counted the anchor.** A `CLUSTER` of 8 produced 9
   ring members, because the pattern was anchored on a stone that was itself one
   of them. Restructured to anchor on the centre stone.
2. **The fix hid a worse defect: `accentScale` was silently dropped.** A pattern
   member inherits the *source instance's* overrides, and the source was now the
   centre stone — so every accent came out at full size while the parameter
   reported as applied. Resolved by placing ring members **explicitly**, always,
   using the resolver's own full-sweep-vs-arc arithmetic so a family and a
   hand-written arrangement still agree. Found by measuring volume, not by
   reading the compiler.
3. **A symmetric toi-et-moi at `axisAngleDeg=90` collapsed both stones onto one
   point.** A YZ-plane mirror maps a pair on the Y axis onto itself. Replaced
   with an explicit point reflection plus a 180° orientation flip, and covered by
   a parametrized test over five axis angles.
4. **A package-init guard passed on a docstring.** `test_family_init_imports_nothing`
   grepped for the text `import`, which the `__init__.py` docstring mentions.
   Changed to parse the module with `ast` — the same discipline the Stone, Gem
   and Arrangement no-dependency tests already use, and for the same reason:
   a text or `import`-based check can pass by accident.

## Tests updated rather than weakened

Four assertions in `test_arrangement.py` encoded Sprint 22's truth — that no
arrangement instance was generatable — and were updated to the new one. Each
became *more* specific, not looser:
`test_no_capability_claims_generation_it_does_not_have` now asserts the exact
eight-name generatable set rather than that the set is empty, so a future
capability marked `generatable` without geometry behind it still fails.

`multi_stone_geometry` stayed `PARTIAL`. Its `generatable` axis became `true`
and its note now states that a setting is generated only for the primary. That
is the honest position: the stones are real, the settings are not, and
ARRANGE-GOV's "never relabel `multi_stone_geometry` as CURRENT" holds.

## Derived mirrors regenerated

The additive `family` field changes canonical JSON and therefore
`definitionHash`, so the same generated mirrors as Sprints 22 and 23 were
regenerated **by running the real implementation**: Alchemist normalization
vectors, both JDL canonicalization/hash vector files, the Atlas metadata vector,
the Designer and Conversation reproducible examples, the Gem hash-separation
vectors, and the arrangement registry, resolved examples and boundary vectors.
Both Geometry Inspection examples were regenerated in full rather than
hash-patched, because `intersectsProductionComponents` legitimately became
sorted.

## Boundaries held

- Nothing under `jewelmind/family/` imports a jewelry category, a geometry
  module or the CAD kernel — AST-verified. `family/effective.py` is the single
  sanctioned meeting point with `JewelryDefinition`, and imports it only under
  `TYPE_CHECKING`.
- `family/__init__.py` imports nothing, for the same load-bearing reason
  `stone`, `gem` and `arrangement` do: `domain/schema.py` imports
  `family.models`.
- **No second placement engine.** A family produces an `ArrangementDefinition`
  and nothing else; the arrangement resolver does every piece of arithmetic.
  Declaring both a family and an arrangement is **refused** (`JM-FAMILY-001`),
  never merged.
- No family definition duplicates `GemDefinition`, `GemIdentity` or
  `StoneDefinition` data, and no field holds a kernel object. A member's
  `placementOverride` reuses the arrangement layer's own `InstanceTransform`
  rather than introducing a parallel transform model.
- Five new Forge rules, all structural or referential. No spacing minimum, no
  accent proportion, no stone-count limit, no settability judgment — verified by
  scanning the real emitted messages.
- No new `ConversationActionType`. No new API endpoint.

## Deliberately not done

An **accent setting strategy requires an RFC** under `SETTING-GOV`, because
holding an accent honestly means choosing between a shared prong, a miniature
head and a bezel collar — each real setter geometry with real professional
consequences. That RFC is identified explicitly in
[`execution-boundary.md`](execution-boundary.md) as the next step rather than
bypassed. Five family types are held in `RESERVED_FAMILY_TYPES` (halo, pavé,
eternity, bypass, channel row) with real reasons, refused by the model, and
never silently substituted.

## Professional validation status

Unchanged: **zero records** in the active professional-validation registry.
Every family, role rule and parameter is `NOT_REVIEWED`. No proportion, spacing
or settability rule exists anywhere in this sprint's code or documentation.
