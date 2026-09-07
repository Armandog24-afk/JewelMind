---
id: JM-BIBLE-HALO-SPRINT-25-REPORT
title: "Sprint 25 Validation Report — Halo System v1"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-07
source_of_truth: false
depends_on:
  - JM-BIBLE-HALO-README
implementation_status: current
professional_validation: not_required
normative: false
---

# Sprint 25 Validation Report — Halo System v1

## Test results

| Gate | Result |
| --- | --- |
| `backend/.venv/Scripts/python -m ruff check .` | clean |
| `backend/.venv/Scripts/python -m pytest -q` | **2077 passed** (1967 before this sprint), 1 pre-existing unrelated warning |
| `python -m jewelmind.geometry_quality.cli verify-all` | **All 49 goldens PASS** (44 before), **zero pre-existing baseline updates** |
| `frontend/ npx tsc -b` | clean |
| `frontend/ npm run test` | **213 passed** across 28 files (198/27 before) |

New tests: `test_halo.py` (106), `haloValidation.test.ts` (15), plus 3 new
guards in `test_capability_coverage.py`.

## What executes

Three halo variants — `SINGLE`, `DOUBLE`, `HIDDEN` — each declared in JDL, each
compiled into **arrangement primitives**, each resolved by the existing
arrangement resolver, and each producing **one real stone solid per halo
stone**: individually identified, placed, scaled, oriented and (for a hidden
halo) vertically offset. A halo composes onto a solitaire, a multi-stone family
or an explicit arrangement. Mixed gems reach the semantics; per-ring and
per-stone scale reach the geometry.

What does **not** execute, with the reason recorded in
[`execution-boundary.md`](execution-boundary.md): **the metal that holds a
halo**. A halo design builds every halo stone and one setting, the centre
stone's. That single limitation is why all three variants are `PARTIAL` rather
than `CURRENT`, and it is reported through four independent channels — the
capability registry's `settingGeometry: false` axis, `JM-HALO-005` (information
severity), every test vector's `settingCoverage: "PRIMARY_ONLY"`, and every new
Golden case's `HALO_METAL_ABSENT` limitation.

## The architectural question this sprint had to answer

Sprint 24 **reserved** the name `halo`, on the ground that a halo is a
`CENTER_WITH_ACCENTS` family whose accents sit against the centre. That is a
contradiction with this sprint's objective, and the Bible's fundamental rule
forbids making a contradiction disappear quietly — so
[`halo-rfc.md`](halo-rfc.md) supersedes the reservation on the record.

The reservation's reasoning is **upheld, not overturned**: a fifth `FamilyType`
would indeed create two ways to say one thing, and `FamilyType` gained no
member. What the RFC establishes is that the conclusion did not follow, because
three parts of the concept are not expressible as an accent ring:

- a **hidden** halo sits below the centre's girdle plane, and the family model
  has no vertical axis at all;
- a **double** halo needs two independent counts, radii, start angles and
  scales, and one accent parameter set cannot carry two;
- a halo **composes** with a family — "three-stone with a halo around the
  centre" is one design, and a fifth family type would force a choice.

So a halo is a composable layer beside `family` and `arrangement`, not inside
either. `RESERVED_FAMILY_TYPES["halo"]` was removed and the capability
registry's `ring_family|halo` row became `OUT_OF_SCOPE` with the reason stated,
rather than deleted.

## Verified by execution, not by reading

- **A hidden halo's offset reaches the solid.** Asserted by measuring the built
  component's bounding box against the same halo at zero offset: the stone moves
  by exactly `zOffsetMm`, `1e-9` relative. A field that never reached the kernel
  would satisfy every model check and produce a flat halo.
- **Per-ring scale reaches the solid.** A double halo's rings measure
  `58.221419 × 0.22³` and `58.221419 × 0.16³` to nine digits. This is the exact
  defect class Sprint 24 found when a pattern route silently discarded
  `memberScale`, which is why halo rings are placed explicitly.
- **A halo places its stones exactly where a `RADIAL` pattern would.** Compared
  against the real resolver's own pattern expansion rather than against a
  recorded constant, so a future change to the arithmetic must move both or
  fail.
- **The metal body is untouched by halo stones.** All five new Golden cases
  report band `250.991683`, head `83.155758`, prongs `29.650351`, three
  production components and **one** fully-connected production group. Thirty-three
  additional stone references in the double-halo case change none of it
  (LAW-006, ATLAS-GOV-011).
- **A named centre a family does not have is refused.** A toi-et-moi has no
  `CENTER` member; the halo raises rather than re-anchoring on the origin.
- **Reordering rings or members changes nothing** — not the composed
  arrangement, not the canonical JSON, not the `arrangementFingerprint`.
- **A design with no halo is unchanged.** `compose_halo(base, None)` returns
  `base` — the same object — and the default solitaire's fused metal volume
  still matches `341.44334316909976`.

## The extraction, and why it needed proving

`arrangement/resolve.py` and `family/compile.py` each carried a copy of the
ring-angle arithmetic; `family/compile.py` documented the duplication in prose.
A third copy for the halo would have made drift a matter of time, so the one
function moved to `arrangement/radial.py` and all three callers now share it.

Float addition is not associative, so a re-expressed loop would have moved every
ring stone by ~1e-14 — visible as a diff on Sprint 24's five `FAM-*` baselines.
The extraction is expression-for-expression identical, and **those five
baselines reverifying unchanged is the evidence**. This is the same discipline
Sprint 23 applied to the basket bore.

## Boundaries held

- Nothing under `jewelmind/halo/` imports a jewelry category, a geometry module,
  the Setting System, the CAD kernel or `JewelryDefinition` — AST-verified, and
  `halo/__init__.py` imports nothing, checked by parsing rather than by
  importing.
- **No second placement engine.** A halo produces `StoneInstanceDef`s and
  `ArrangementRelation`s and nothing else.
- **No parallel abstraction.** Per-stone overrides reuse `FamilyMember`;
  `placementOverride` reuses `InstanceTransform`. No halo model restates a
  shape, dimension, material or visual profile, and no field holds a kernel
  object.
- Five new Forge rules, all structural or referential. No spacing minimum, no
  centre-to-halo proportion, no settability judgment — verified by scanning the
  **real emitted messages** across four deliberately extreme configurations,
  not the source.
- `HALO_COMPOSITION` is a REPORTING table; the compiler is the gate, and a test
  re-derives every row by actually composing each family with and without a
  named centre.
- No new API endpoint, no Conversation change, no new `ConversationActionType`,
  no Designer coupling, no Studio control.
- Vision required no change: a halo stone is classified by the `geometryRole`
  the preview manifest already computes, so no parallel visual-only
  representation exists.

## Pre-existing defects fixed in passing

Both were directly on the path this sprint touched, and both were left wrong by
earlier sprints rather than introduced here:

1. **The Forge rule catalog's total said 21 rules** while the registry held 43.
   Now derived from the registry (48) rather than counted by hand.
2. **Two capability rows described a halo as a reserved family name needing an
   RFC.** Both were true when written and neither is now; both were corrected
   with the reason stated, and a test asserts they no longer call a halo a
   family.

## Derived mirrors regenerated

The additive `halo` field changes canonical JSON and therefore
`definitionHash`, so the same generated mirrors as Sprints 22–24 were
regenerated **by running the real implementation**: Alchemist normalization
vectors, both JDL canonicalization/hash vector files (including their
`canonicalJsonLength` fields), the Atlas metadata vector, the Designer and
Conversation reproducible examples, both Geometry Inspection examples, the Gem
hash-separation vectors, and the family registry and vectors (which lost the
`halo` reservation).

## Deliberately not done

A **halo setting strategy requires an RFC** under `SETTING-GOV`, because holding
a halo honestly means choosing between a shared bezel rail, a row of shared
prongs and cut-down bead setting — each real setter geometry with real
professional consequences. It is the same missing capability Sprint 24 named for
accents, seen from a second direction, and
[`execution-boundary.md`](execution-boundary.md) identifies it as the next step
rather than bypassing it. Five halo variants are held in
`RESERVED_HALO_VARIANTS` (cushion, floral, compass, triple, pavé) with real
reasons, refused by the model, never silently substituted.

## Professional validation status

Unchanged: **zero records** in the active professional-validation registry.
Every halo variant, ring parameter and composition rule is `NOT_REVIEWED`. No
proportion, spacing or settability rule exists anywhere in this sprint's code or
documentation.
