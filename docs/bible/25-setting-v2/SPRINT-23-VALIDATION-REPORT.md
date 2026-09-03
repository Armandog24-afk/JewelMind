---
id: JM-BIBLE-SETTINGV2-SPRINT-23-REPORT
title: "Sprint 23 validation report — Setting System v2"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-03
source_of_truth: false
depends_on:
  - JM-BIBLE-SETTINGV2-README
implementation_status: current
professional_validation: not_required
normative: false
---

# Sprint 23 validation report — Setting System v2

## Test results

| Gate | Result |
| --- | --- |
| `backend/.venv/Scripts/python -m ruff check .` | clean |
| `backend/.venv/Scripts/python -m pytest -q` | **1841 passed** (1740 before this sprint), 1 pre-existing unrelated warning |
| `python -m jewelmind.geometry_quality.cli verify-all` | **All 39 goldens PASS**, **zero baseline updates** |
| `frontend/ npx tsc -b` | clean |
| `frontend/ npm run test` | **183 passed** across 26 files |

New tests: `test_setting_v2.py` (96), `settingV2Validation.test.ts` (13), plus
2 new guards in `test_capability_coverage.py`.

## What executes

Four prong styles and four head architectures, each a registered builder
producing a real valid solid; explicit prong layouts with per-group style
overrides; a deterministic setting→stone-instance mapping; opt-in reference
seat relief. Head construction became category-neutral, with
`geometry/components/basket.py` reduced to a thin re-export.

What does **not** execute, with recorded reasons in
[`head-execution-boundary.md`](head-execution-boundary.md): `TRELLIS` and three
other reserved architectures, support rails, shared prong geometry against two
stones, bearing and cutter geometry.

## Verified by execution, not by reading

- **Every style and architecture** builds one valid solid, spans the requested
  height, and is deterministic across repeated construction.
- **Head volume ordering** (basket > martini > tulip) is asserted, which is a
  cheap check that the three are genuinely different shapes rather than one
  shape with different labels.
- **V notch orientation** — a prong on +X and one on +Y remove the same volume,
  because each notch follows its own radius. A notch pointing the wrong way is
  not a V prong.
- **Legacy preservation** — the default solitaire's fused metal volume is
  unchanged, `ROUND_PRONG` matches a freshly-built legacy cylinder exactly, and
  a document with all seven new fields stripped generates identically.
- **Seat relief** removes real material from both head and prongs, keeps the
  metal one connected solid, and leaves the stone reference excluded from
  production.

## Defects found and fixed during the sprint

1. **`PEG_HEAD` produced two disconnected solids.** A peg narrower than the
   wall's bore never touches it, so stacking them shipped a floating basket
   above an unattached peg. Fixed with a conical flare from the peg's radius out
   to the wall's outer radius, occupying the lowest 45% of the wall height so it
   genuinely intersects the wall's material — plus a check in the builder that
   raises if a head is ever not one connected body.
2. **The V notch cut the whole prong tip off.** The half-width was derived from
   a fraction of the prong's *height*, making the wedge several times wider than
   the prong; the cut removed the entire top face and produced a shortened
   cylinder that reported `V_PRONG`. Fixed by deriving the notch from the prong
   *radius* and its own opening angle, with the width factor strictly below 1 so
   two horns survive — which is what makes the tip a V. Found by asserting the
   solid still spans its full height, not by inspection.
3. **The basket bore drifted ~1e-11 mm.** Deriving it as
   `outerRadius − wallThickness` re-associates the original
   `centre − prongRadius` as `(c + p) − 2p`. Harmless numerically and still an
   avoidable change to shipped geometry, so `HeadSettingDefinition` gained an
   explicit `innerRadiusMm` and the Ring adapter passes the original expression.
   The default metal volume is now bit-identical again.

## Tests updated rather than weakened

Three existing assertions encoded the pre-Sprint-23 truth and were updated to
the new one, each with the reason recorded in the test itself:

- `seatSupport` moved `PLANNED` → `PARTIAL` in both registries, because relief
  is real. `bearingSupport`/`cutterSupport` stay `PLANNED`, and the assertions
  became *more* specific rather than looser.
- A setting built through the Ring adapter now reports its family component
  **and** the head, so `generatedComponents` gained `basket_support`.

No threshold was relaxed and no check removed.

## Derived mirrors regenerated

Seven additive JDL fields change canonical JSON and therefore
`definitionHash`. The same generated mirrors Sprint 22 regenerated were
regenerated again **by running the real implementation**: Alchemist
normalization vectors, both JDL canonicalization/hash vector files, the Atlas
metadata vector, the Designer and Conversation reproducible examples, the two
Geometry Inspection examples, and the Gem hash-separation vectors. The
inspection examples also legitimately gained new prong metadata keys
(`prongStyle`, `positionSource`, `stylesUsed`, `tipRatio`,
`sharedProngCount`), so they were regenerated in full rather than hash-patched.

Golden baselines needed **no** update, which is the meaningful check.

## Boundaries held

- Nothing under `jewelmind/setting/` imports a jewelry category or the
  arrangement layer — AST-verified.
- `SettingDefinition` stays kernel-neutral: the stone shape reaches seat relief
  as a function **argument**, never as a model field.
- `seat.py` calls `.cut()` and never `.fuse()`, asserted by parsing its own
  source. LAW-006 holds unchanged.
- Three new Forge rules, all structural. No professional threshold anywhere —
  verified by scanning the real emitted messages, not the source.
- No new API endpoint, no Conversation change, no Designer coupling. Nothing in
  this sprint required an RFC.

## Professional validation status

Unchanged: **zero records** in the active professional-validation registry.
Every prong style, head architecture and seat mode is `NOT_REVIEWED`.

## Noted, not fixed

`specs/foundry/v1/test-vectors/unit-scale-vectors.json` still contains a literal
NUL byte (it describes an STL header) and parses only with `strict=False`.
Pre-existing, untouched by this sprint, and not a regression.
