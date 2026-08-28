---
id: JM-BIBLE-SPRINT19-REPORT
title: "Sprint 19 Validation Report — Setting System v1"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-27
source_of_truth: true
depends_on:
  - JM-BIBLE-SETTING-README
  - JM-BIBLE-580
related_documents:
  - JM-BIBLE-SPRINT18-REPORT
implementation_status: current
professional_validation: not_required
normative: false
---

# Sprint 19 Validation Report — Setting System v1

## Documents created

`README.md` plus 12 substantive documents and this report — 14 total in `docs/bible/21-setting/`.

## Machine-readable specifications created

7 JSON Schemas under `specs/setting/v1/`, plus a generated `setting-registry.json` (capabilities + reserved families + the 14-row Stone × Setting matrix), 5 examples, and 5 test-vector files. Plus `specs/capabilities/` — the cross-product Capability Coverage Guard (schema + 101-capability registry).

## Setting System category-neutral: yes

`backend/tests/test_setting_system_no_ring_dependency.py` (13 tests) AST-parses every module under `jewelmind/setting/` and asserts none imports `jewelmind.ring`, `jewelmind.jewelry_category`, `jewelmind.geometry.shank`, `jewelmind.geometry.connection`, `geometry/setting_adapter.py`, or `JewelryDefinition`. AST rather than `import`, so it cannot pass by accident on a cached module. It also asserts the reverse direction is real and that the permitted Stone dependency exists.

## Setting System imports Ring domain: no

Zero imports, statically verified.

## Current Setting families

`prong`, `bezel`. Both `CURRENT`, both `generatable`, both `inspectable`, both category-neutral.

Reserved (no generator, not enum members): `channel`, `flush`, `bar`, `tension`, `bead`, `pave`, `custom`.

## Current prong configurations verified

`round` + 4 prongs, `round` + 6 prongs — both byte-identical to pre-Sprint-19 (see below). Plus all 6 non-round shapes at 6 prongs.

## Non-round prong Stone shapes implemented

`oval`, `pear`, `emerald`, `cushion`, `princess`, `marquise` — all 6, via `OUTLINE_CARDINAL` placement. All `EXPERIMENTAL`.

## ROUND bezel implemented: yes · OVAL bezel implemented: yes

Both `SUPPORTED_SOFTWARE`. Real B-Rep, derived by offsetting the stone's own girdle outline.

## Other bezel-compatible shapes implemented

`pear`, `emerald`, `cushion`, `princess`, `marquise` — all generate a valid single-solid bezel, all `EXPERIMENTAL`. Real measured volumes at 0.6 mm × 2.5 mm wall:

| Shape | Volume (mm³) | STEP repair |
|---|---|---|
| round (d 6.5) | 33.458 | no |
| oval (8×6) | 35.981 | **yes** |
| emerald (8×6) | 42.929 | no |
| cushion (7×7) | 42.574 | no |
| princess (6.5×6.5) | 41.827 | no |
| marquise (10×5) | 37.601 | no |
| pear (9×6) | 37.089 | no |

## SettingAttachmentInterface implemented: yes

`attachmentPlaneZMm` / `embedMm` / `supportHeightMm`, supplied by the category integration via `geometry/setting_adapter.py`. Verified identical for both families, so the contract is genuinely generic rather than incidentally shared.

## Setting runtime inspection implemented: yes

8 new `FactType` values (registry now 30, version `1.2.0`). Prong facts emitted only for prong settings, bezel facts only for bezel — so a fact's presence is itself honest about what was built.

## Setting/Stone compatibility matrix implemented: yes

Generated from the live capability entries into `setting-registry.json` and `compatibility-vectors.json`, so it cannot drift.

## Seats capability: PLANNED · Bearings: PLANNED · Cutters: PLANNED

For **every** family, because none exists. Asserted in two independent places. Stone/metal overlap is explicitly **not** a seat and was not renamed as one.

## Forge prong rules correctly scoped: yes

All four `JM-PRONG-*` rules are now `PRONG_ONLY`; new `JM-SETTING-003`/`004` are `BEZEL_ONLY` and check only positivity (constructibility, not a domain threshold). Mirrored identically in `shared/validation/engine.ts`.

Verified: a bezel with `prongCount=99`, `prongDiameter=0.1`, `prongHeight=0.1` fires **zero** prong rules; a prong setting with `prongCount=99` still fires `JM-PRONG-001`.

**No minimum bezel wall dimension is asserted**, and `test_no_minimum_bezel_wall_dimension_is_asserted` pins that absence deliberately — no sourced professional minimum exists.

## StoneReference production exclusion verified: yes

For both families: `GEOMETRY_ROLE`/`PRODUCTION_ROLE` unchanged, `fusedIntoProductionMetal is False`, STEP export with `include_stone=False` produces a real non-empty file.

## New Setting Golden cases: 5

`SET-001-round-4-prong`, `SET-002-round-6-prong`, `SET-003-oval-prong`, `SET-004-round-bezel`, `SET-005-oval-bezel`. All complete rings. Suite is now 23 cases, all passing (10 `PASS`, 13 `PASS_WITH_KNOWN_LIMITATIONS`).

## Existing ROUND Golden baseline updates required: 0

All 12 round-stone cases (`SOL-001`–`SOL-012`) verified unchanged. `combined_metal_volume_mm3 == 341.44334316909976` and prong volume `== 29.650351464580467`, both exact equality.

## Geometry regressions discovered: 0 unintended, 6 intentional

The six non-round `SOL-013`–`SOL-018` cases changed **by design** — shape-aware placement is this Sprint's objective. Reviewed and accepted through the full sanctioned path: `verify-all` → `generate-candidate` → `diff` → independent measurement → `accept --reason` → re-verify → candidates removed → recorded in the golden update register.

The diff was confined exactly to what the change should affect: prong volume unchanged (Δ 3.55e-15), X extents unchanged, only Y extents moved. Supporting measurement on the oval: off-axis prongs moved from **0.784 mm** away from the stone outline to **0.049 mm**, with the on-axis prong unchanged at the intended 0.165 mm girdle inset.

No baseline was regenerated to obtain green CI.

## New Professional Validation records created from real human evidence: 0

## Unsupported professional claims introduced: 0

Every family is `NOT_REVIEWED`. The active professional-validation registry remains at **zero records**, verified independently by the Capability Coverage Guard.

## Capability Coverage Guard updated: yes

`specs/capabilities/jewelmind-capabilities.json`: 101 capabilities across 26 domains — 30 `CURRENT`, 1 `PARTIAL`, 66 `PLANNED`, 1 `BLOCKED`, 3 `OUT_OF_SCOPE`. `test_capability_coverage.py` (16 tests) checks it against the live Setting, Stone and category registries; `CURRENT` families must be registered generators and `PLANNED` ones must not be.

Its note-length check caught five genuinely thin justifications on first run, which were improved rather than the check being relaxed.

## Backend tests passed: 1166

Full `pytest -q`. Ruff clean.

## Frontend tests passed: 137

22 files. `tsc -b` clean.

## Setting / geometry / inspection / Golden tests passed

- `test_setting.py`: 102
- `test_setting_schemas.py`: 22
- `test_setting_system_no_ring_dependency.py`: 13
- `test_capability_coverage.py`: 16
- Golden suite: 23/23

## Frontend build: pass

## Real architectural leaks found and fixed: 5

All five were found by **exercising a bezel model**, not by reading code. A code-reading pass would plausibly have missed the last one entirely.

1. **`api/routes.py` KeyError.** `components["prongs"].metadata` was indexed unconditionally — **every bezel generation would have crashed the API**. Now `None` when absent, plus a new `metadata["setting"]`. Verified end-to-end: both families return HTTP 200.
2. **`REQUIRED_COMPONENT_NAMES` hardcoded `prongs`** → every valid bezel assembly inspected as `FAIL`.
3. **`_prong_count()` returned `FAIL`** rather than `NOT_APPLICABLE` for a bezel.
4. **`_ALL_PAIRS` was a constant over a hardcoded 4-name tuple**, so the `bezel` component was **silently excluded** from all pairwise intersection/distance inspection. Nothing failed; facts were simply missing.
5. **Technical specification** reported "Requested vs. generated prong count: 0 vs. 0" for a bezel, which reads as a defect.

## The defining geometric finding

A true geometric offset of an **ellipse** does not survive STEP export. `cq.Wire.offset2D()` on an ellipse produces edges whose `geomType()` is `OFFSET`; the extruded surface re-imports as a `Shell` with **zero solids**, which `step_roundtrip_check()` correctly flags. Every other shape offsets to `CIRCLE`/`LINE` edges and round-trips exactly.

The repair is triggered by the real **curve type**, not by a shape name — hardcoding `if shape == "oval"` would have worked and would have been wrong, re-introducing the per-shape branching the outline-agnostic design exists to prevent, and silently missing any future spline-based custom outline. Measured cost: ~0.006% volume deviation; angular shapes' crisp corners untouched.

Rejected alternatives (expanded semi-axes, blanket resampling, loft-between-copies, boolean cut) are recorded in [`bezel-setting-contract.md`](bezel-setting-contract.md).

## `definitionHash` drift: third occurrence, documented

The two additive `SettingSpec` fields changed `definition_hash()` for every document (default `e1d6dc2f2390875d` → `8def81bd12b97d38`, etc.). Same mechanism as Sprints 17 and 18 — normalization-time default-filling, **not** a Migration Requirement 4 violation. Verified again that `compare_snapshot()` never reads `definitionHash`. Nine stored fixture files regenerated by running real code, never hand-typed.

## Known limitations carried forward

- **No seat, bearing, or cutter geometry** for any family. Stone/metal overlap is not a seat.
- **Prong placement is not shape-optimized.** Marquise/pear tips and angular corners are not targeted; no `V_PRONG` geometry exists. All 6 non-round combinations are `EXPERIMENTAL`.
- **`basket_support` ownership unresolved** — genuinely both setting support and ring attachment; deliberately not force-split (`PARTIAL`).
- **Prongs remain one compound**, not individually-named components; per-prong facts are provided instead.
- **`tipDirectionY` / `isBilaterallySymmetric` are recorded but unconsumed** — present for a future tip-aware strategy.
- **The attachment interface is minimal** (three numbers) — richer attachment concepts have no consumer yet.
- **No Setting geometry is professionally validated.**
