---
id: JM-BIBLE-ARRANGE-SPRINT-22-REPORT
title: "Sprint 22 validation report — Stone Arrangement Engine v1"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-03
source_of_truth: false
depends_on:
  - JM-BIBLE-ARRANGE-README
implementation_status: current
professional_validation: not_required
normative: false
---

# Sprint 22 validation report — Stone Arrangement Engine v1

## Test results

| Gate | Result |
| --- | --- |
| `backend/.venv/Scripts/python -m ruff check .` | clean |
| `backend/.venv/Scripts/python -m pytest -q` | **1740 passed** (1590 before this sprint), 1 pre-existing unrelated warning |
| `python -m jewelmind.geometry_quality.cli verify-all` | **All 39 goldens PASS**, **zero baseline updates** |
| `frontend/ npx tsc -b` | clean |
| `frontend/ npm run test` | **170 passed** across 25 files |

New tests: `test_arrangement.py` (104), `test_arrangement_schemas.py` (43),
`test_arrangement_no_category_dependency.py` (11),
`arrangementValidation.test.ts` (13), plus 3 new guards in
`test_capability_coverage.py`.

## What executes, and what does not

The declarative layer, its structural validation, its deterministic resolution
and its compilation boundary all execute. **Multi-stone geometry does not.** An
eight-stone halo resolves to eight real placements and produces one stone solid;
the other seven instances are reported `NOT_GENERATED`, each with a reason.

That boundary is reported through four independent channels (per instance, per
model, per validation run, per capability) and documented in
[`execution-boundary.md`](execution-boundary.md), which also records why the
line was not crossed: emitting additional stones requires a per-instance
transform on the stone builder and an instance-aware Geometry Inspection, plus
an accent setting strategy that needs an RFC. The brief warns against changing
existing geometry semantics to accommodate a new domain model, so the sprint
stopped there rather than weakening the inspection checks a second stone would
trip.

## Verified by execution, not by reading

- **Determinism.** Resolution repeated five times produces byte-identical
  canonical JSON. Reordering instances, groups, patterns and relations leaves the
  fingerprint unchanged; 370° and 10° fingerprint identically; a different
  arrangement fingerprints differently (the complement, so the equality tests
  cannot pass by measuring nothing).
- **Pattern arithmetic.** A 4-member full-circle radial run lands at exactly
  0/90/180/270°, all at the stated radius. A 3-member 180° arc lands at
  0/90/180° — a different divisor, because at a full sweep the last member would
  otherwise coincide with the first. A centred 4-member linear run at 2 mm
  spacing lands at −3/−1/1/3 mm.
- **Frame composition.** A child at +1 mm in X inside a group rotated 90° and
  offset (2, 3) resolves to (2, 4) — verified numerically, because getting the
  composition order backwards would silently mirror a group's contents.
- **Backward compatibility.** The default solitaire generates the same four
  components with `arrangement_result: None`. A design declaring a single CENTER
  instance produces the same component set and the same volumes. All 39 goldens
  pass with no baseline change.
- **Component classification.** `stone_reference.halo.3` classifies as
  `stone_reference` / `excluded_by_default`, and `is_production_component()`
  returns `False` — checked before any such geometry exists, because the
  `production_metal` default would otherwise fuse a stone into metal.

## Defects found and fixed during the sprint

1. **The resolver derived IDs its own model rejected.** `_member_id()` produced
   `halo.0`, while `ARRANGEMENT_ID_PATTERN` (inherited from gem IDs) required
   every dot-segment to start with a letter. It never surfaced during
   development because `model_copy(update=...)` does not re-run field
   validation — so a resolved arrangement existed happily in memory and would
   have failed only on serialization to JDL. Found by round-tripping a resolved
   arrangement. Fixed by allowing a digit to start a non-leading segment (a
   deliberate, documented divergence from the gem pattern: an arrangement ID is
   a user label, not a registry key) **and** by validating derived IDs
   explicitly in `_member_id()`, so the same class of gap cannot recur.

## Pre-existing defects found and closed

Each was discovered while doing this sprint's work, is a genuine misstatement or
duplication rather than a matter of taste, and was small enough to close without
expanding scope.

- **`specs/jdl/v1/jdl.schema.json` structurally rejected documents the backend
  accepts.** Its `stone.shape` enum still listed Sprint 18's seven cuts after
  Sprint 20 added fourteen more plus two pseudo-shapes, and `stone.gem`,
  `stone.source`, `stone.profile`, `stone.narrowWidth`, `stone.customOutline`,
  `stone.measurement`, `stone.importedAsset`, `setting.bezelWallThickness` and
  `setting.bezelWallHeight` were absent entirely. A JDL example exercising a
  real arrangement could not be committed without tripping over it. Every
  missing property is now generated from the live Pydantic models; existing
  hand-authored descriptions were left untouched, so the change is purely
  additive.
- **`shared/validation/engine.ts` called `bezelRules()` twice**, so every bezel
  finding was reported in duplicate to the frontend. A leftover from Sprint 21's
  patch-script mishap. Removed, with a test that pins rule-id uniqueness for a
  design that produces bezel findings.
- **`specs/forge/v1/current-rule-registry.json` was missing the new rules** —
  caught immediately by the completeness guard added in Sprint 21, which is
  exactly what it was added for.

## Derived mirrors regenerated

Adding an optional nullable field changes canonical JSON (`"arrangement": null`)
and therefore `definitionHash`. Seven generated mirrors were regenerated **by
running the real implementation**: the Alchemist normalization vectors, both JDL
canonicalization/hash vector files, the Atlas metadata vector, the Designer and
Conversation reproducible examples, the two Geometry Inspection examples, and
the Gem hash-separation vectors. No threshold was relaxed and no test weakened;
this is the same regeneration Sprint 21 performed for `stone.gem`, for the same
reason.

Golden baselines needed **no** update, which is the meaningful check: geometry
did not move.

## Boundaries held

- `jewelmind/arrangement/` imports no jewelry category, no geometry module, no
  kernel and not `JewelryDefinition` — AST-verified, along with a scan proving
  no module even names a construction verb.
- `arrangement/__init__.py` imports nothing, keeping the
  `domain/schema.py` ↔ `arrangement.models` graph acyclic.
- No new Conversation action type, no new API endpoint, and no Designer coupling:
  the arrangement is data a higher layer can propose through existing
  interfaces. Nothing in this sprint required an RFC.
- Six new Forge rules, all structural or referential. No spacing, clearance,
  proportion or density threshold exists anywhere — verified by scanning the
  real emitted messages, not the source.

## Professional validation status

Unchanged: **zero records** in the active professional-validation registry.
Nothing in this sprint is professionally reviewed, and no arrangement rule
claims to be.

## Noted, not fixed

`specs/foundry/v1/test-vectors/unit-scale-vectors.json` still contains a literal
NUL byte (it describes an STL header) and parses only with `strict=False`.
Pre-existing, untouched by this sprint, and not a regression.
