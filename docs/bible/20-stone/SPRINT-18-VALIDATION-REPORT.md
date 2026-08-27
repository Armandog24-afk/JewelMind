---
id: JM-BIBLE-SPRINT18-REPORT
title: "Sprint 18 Validation Report — Stone System v1"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-STONE-README
  - JM-BIBLE-560
related_documents:
  - JM-BIBLE-SPRINT17-REPORT
implementation_status: current
professional_validation: not_required
normative: false
---

# Sprint 18 Validation Report — Stone System v1

## Stone documents created

`README.md`, the full `560`–`579` numbered set (20 docs, matching the README's reading order exactly), this validation report, and 3 new appendices (`A114`–`A116`) — 25 documentation files in total.

## Machine-readable schemas created

5 under `specs/stone/v1/`: `stone-definition.schema.json`, `stone-dimensions.schema.json`, `stone-orientation.schema.json`, `stone-shape-capability.schema.json`, `stone-reference-profile.schema.json` — plus a real generated `shape-registry.json`, 7 examples (one per shape), and 5 test-vector files, all produced by running the real `build_stone()` / `stone_dimensions` / `capability` code.

## Stone System is category-neutral: yes

`backend/tests/test_stone_system_no_ring_dependency.py` (8 tests) AST-parses every file under `geometry/stone/` plus `domain/stone_dimensions.py` and asserts none imports `jewelmind.ring`. AST parsing rather than `import` is deliberate — an import-based check can pass by accident on an already-cached module. The test also asserts the reverse direction is real, documenting the dependency arrow both ways, and includes a guard against the glob silently matching zero files.

## Stone System imports Ring domain: no

Zero imports, statically verified as above.

## All 7 target shapes generate: yes

`round`, `oval`, `pear`, `emerald`, `cushion`, `princess`, `marquise` — all `status: current`, all `generationSupported: true`. The Sprint's strong target was fully met; no shape was marked `NOT_GENERATABLE` or `EXPERIMENTAL` for instability.

Real generated volumes at `depth = 4.0`, each producing exactly one valid solid:

| Shape | Dimensions | Volume (mm³) |
|---|---|---|
| `round` | d 6.5 | 58.221419 |
| `oval` | 8 × 6 | 67.350 |
| `pear` | 9 × 6 | 57.413477 |
| `emerald` | 8 × 6 | 84.711 |
| `cushion` | 7 × 7 | 86.365 |
| `princess` | 6.5 × 6.5 | 75.480 |
| `marquise` | 10 × 5 | 62.430 |

## Round backward compatibility: yes

Two independent proofs. `test_stone.py::TestRoundStoneBackwardCompatibility::test_default_definition_produces_the_pre_sprint18_recorded_volume` asserts the exact pre-Sprint-18 volume `58.22141924499569 mm³` at `rel=1e-9`. And all 12 pre-existing Golden cases verified with zero baseline changes — 9 of which contain round stones across several real dimension combinations, including `SOL-007-stone-dimension-variation`.

`_build_round_stone()` retains the exact fluent `Workplane.loft()` chain rather than being routed through the shared `cq.Solid.makeLoft()` path. That was a deliberate decision, not an oversight: the two constructions are not provably bit-identical, and round's absolute `_CULET_RADIUS_MM = 0.05` differs in kind from the non-round proportional `_CULET_SCALE_RATIO = 0.05`.

## Existing round Golden baseline updates required: 0

No baseline was regenerated. Per QUALITY-GOV-003/004 the only path to changing an accepted `snapshot.json` is the explicit `geometry-quality accept --reason "..."` command, which was not used.

## Non-round dimension model: yes

`stone.length` / `stone.width` (both `float | None`) added; `domain/stone_dimensions.py` resolves the per-shape public fields into one canonical LENGTH (local Y) / WIDTH (local X) / DEPTH (local Z) contract. Round normalizes internally to `length == width == diameter` while keeping `diameter` as its public field for backward compatibility.

The resolution layer lives in `domain/` rather than `geometry/` or `validation/` specifically so both Atlas geometry and Forge validation can consume it without creating a new cross-layer coupling. Verified by `test_stone.py::TestStoneDimensionValidation` (26 collected) and `specs/stone/v1/test-vectors/dimension-vectors.json`.

## Stone orientation: yes

`stone.orientation` (degrees, default `0.0`), applied by `_apply_orientation()` as a rotation around the stone's own local vertical axis at its own bounding-box centre. Early-returns unchanged at `0.0`, so the default path is bit-identical to no orientation code at all. Applied uniformly to every shape rather than special-cased away for round.

Verified: round at 45° is volume- and extent-equivalent; `oval` and `marquise` at 90° swap their measured Y/X extents and preserve volume. Real bounding boxes and volumes at 0°/90°/180° recorded in `specs/stone/v1/test-vectors/orientation-vectors.json`.

## PEAR asymmetric orientation verified: yes

The discriminating signal is the **centroid offset along Y** — the signed distance from the bounding-box centre to the real centre of mass. Volume and extents alone are insufficient, since two different shapes can differ in volume while both being symmetric.

Real measured values at 9 × 6 × 4:

| Shape | centroid Y offset |
|---|---|
| `pear` | **−0.737306 mm** |
| `oval` | +0.000002 mm |
| `marquise` | +0.000000 mm |

Pear's mass sits toward the rounded end (−Y), matching the tip-at-+Y convention; the two symmetric `ELONGATED_SMOOTH` controls sit at zero within floating-point noise. Under a 180° rotation the offset flips to **+0.737306** — a real directional flip, with volume and extents preserved (a rigid motion).

An earlier draft of this test compared pear against oval with an `or` between a centre check and a volume check. It passed — but via the volume clause, proving only "pear is not oval" rather than "pear is asymmetric". It was replaced with the centroid assertions above plus a symmetric-shape control, precisely because the weaker form could pass for the wrong reason. `TestPearAsymmetry` is now 5 tests (6 collected).

## Stone runtime inspection: yes

6 new `FactType` values — `STONE_REQUESTED_LENGTH`/`MEASURED_LENGTH`/`REQUESTED_WIDTH`/`MEASURED_WIDTH`/`REQUESTED_DEPTH`/`MEASURED_DEPTH` — emitted by `inspector.py::_stone_dimension_facts()` for the `stone_reference` component only. Registered in `specs/geometry-inspection/v2/fact-registry.json` (now 22 fact types, registry version `1.1.0`) and catalogued in `geometry-fact-catalog.md` (A92).

The registry's count assertion was replaced with `test_fact_registry_covers_exactly_the_live_fact_type_values`, which derives the expected set from the live `FactType` via `get_args()` — so the registry can no longer silently drift when a fact type is added. Both stored inspection examples were regenerated and now contain 42 facts each (up from 36).

## Requested/measured dimension comparison: yes

Real measured example (default round): requested length 6.5 vs measured 6.5000002; requested depth 4.0 vs measured 4.000000199999999. The ~2e-7 mm residual is OpenCascade bounding-box padding.

Compared with a **software geometry tolerance** (`abs=1e-3` for round, `abs=0.05` for non-round), never a professional or manufacturing tolerance. Parametrized over all 6 non-round shapes at 9 × 5 × 3.5.

**Honest limitation:** `STONE_MEASURED_LENGTH`/`WIDTH` read an axis-aligned bounding box, so they isolate LENGTH from WIDTH exactly only at `orientation == 0`. At an arbitrary angle neither extent corresponds to a real stone dimension. Documented in [`574-stone-inspection-contract.md`](574-stone-inspection-contract.md) and recorded as an open question.

## New Stone Golden cases: 6

`SOL-013-oval-solitaire` (8 × 6), `SOL-014-pear-solitaire` (9 × 6), `SOL-015-emerald-solitaire` (8 × 6), `SOL-016-cushion-solitaire` (7 × 7), `SOL-017-princess-solitaire` (6.5 × 6.5), `SOL-018-marquise-solitaire` (10 × 5).

All `baselineStatus: STABLE`, appended to `fullSuite` only — `fastSuite` unchanged (`SOL-001`/`002`/`003`). Each records the honest `EXPERIMENTAL` setting-compatibility caveat in `knownLimitations`, which is why all six verify as `PASS_WITH_KNOWN_LIMITATIONS`. Every case is a **complete solitaire**, not an isolated stone solid.

Full suite verification, run as a separate pass from the pass that generated the baselines:

```
SOL-001 … SOL-008: PASS
SOL-009 … SOL-018: PASS_WITH_KNOWN_LIMITATIONS
All 18 golden(s) PASS.
```

Recorded in [`../appendices/golden-update-register.md`](../appendices/golden-update-register.md) as `INITIAL_BASELINE`, per QUALITY-GOV-018.

## Complete-ring non-round cases generated: 4

`TestNonRoundAssembly::test_shape_generates_a_fully_connected_solitaire_assembly` covers `oval`, `emerald`, `cushion`, and `princess` — each builds a complete solitaire with `fullAssemblyConnectivity.isFullyConnected is True` and a matching generated prong count. This exceeds the required minimum (round + oval + one angular shape). Counting the 6 Golden cases, all 6 non-round shapes assemble into complete rings.

## StoneReference production exclusion verified for all shapes: yes

`TestStoneProductionExportExclusion::test_step_export_excludes_stone_by_default` is parametrized over all 6 non-round shapes; `TestNonRoundShapeGeneration::test_shape_reference_stays_separate_from_metal` asserts the stone sits at or above the band top for each; and `TestStoneMeasuredDimensions::test_stone_reference_never_reported_as_production_metal` asserts `stoneMetalSeparation.fusedIntoProductionMetal is False`.

No code under `geometry/stone/` constructs or touches metal. The separation check remains **structural** (by component identity), never "zero intersection volume" — the stone legitimately intersects prongs and basket by design (INSPECT-GOV-008).

## Vision verified for shapes: 7 (no frontend rendering changes needed)

No Vision code changed. `ModelViewport.tsx` and `useComponentGeometries.ts` parse whatever STL the backend generates and have no shape-specific path (VISION-GOV-001/002) — a shape that generates therefore renders automatically. `visionSupported: true` in the capability registry reflects that structural fact rather than a per-shape frontend feature.

The only frontend change was Studio's parameter editor (shape selector + conditional dimension fields), not the renderer.

## STEP/STL verified for shapes: 7

- STEP roundtrip (`step_roundtrip_check()` → zero findings): `oval`, `emerald`, `cushion`, `princess`.
- STEP export non-empty with `include_stone=False`: all 6 non-round shapes.
- STL structure (`stl_structure_check()` → zero findings): `oval`, `pear`, `marquise`.
- STL export non-empty: verified.
- Round: covered by the unchanged pre-existing export tests and all 12 pre-existing Golden cases' artifact expectations.

No exporter needed shape-specific logic.

## Forge round-only rules correctly scoped: yes

| Rule | Classification |
|---|---|
| `JM-STONE-001` (`STONE_DIAMETER_RANGE`) | **ROUND_ONLY** — guarded by `if d.stone.shape == "round"` |
| `JM-PRONG-003` (`PRONG_COUNT_VS_STONE_SIZE`) | **ROUND_ONLY** — same guard; REQUIRES_RULE_EVOLUTION |
| `JM-STONE-002` (`STONE_DEPTH_RANGE`) | **SHARED** — genuinely generalized to `min(resolved_length, resolved_width)` |

`shared/validation/engine.ts` was updated identically (FORGE-GOV-004). Verified by `TestForgeRoundRuleScope` (4 tests), including an oval at 100 × 100 producing no `JM-STONE-001` and an oval at 20 × 20 with 4 prongs producing no `JM-PRONG-003`.

`JM-STONE-002`'s generalization is not a disguised equivalent diameter: the old form compared depth against `diameter`, which for a circle *is* the minimum horizontal extent, so round's behaviour is bit-identical and the rule now expresses the geometric invariant it always meant.

## Fake equivalent-diameter mappings introduced: 0

No `length × width` is ever collapsed into a synthetic diameter. The one generalization — `prong_center_radius()` now reading `resolved_width_mm()` instead of `stone.diameter` — is **placement geometry, not a threshold evaluation**: it produces a radius at which to place prong solids, feeds no Forge rule, and is precisely why every non-round shape's setting compatibility is honestly `EXPERIMENTAL`.

## Designer shape normalization: yes

`STONE_SHAPE_SYNONYMS` covers all 7 shapes in IT and EN: round/rotondo/rotonda/tondo/tonda, oval/ovale, pear/pera/goccia, emerald/smeraldo/"taglio smeraldo", cushion/cuscino, princess/principessa, marquise/navette. `KNOWN_JDL_FIELD_PATHS` and `_NUMERIC_FIELDS` gained `stone.length`/`stone.width`/`stone.orientation`. Designer never infers dimensions from a shape name.

The 6 stale `KNOWN_UNSUPPORTED_CONCEPTS` entries claiming *"Only round stones are currently supported"* were **removed** — leaving them would have made Designer actively misreport a real capability.

One pre-existing test asserted `oval` was rejected as unsupported. That assertion encoded the old reality, so it was retargeted to `asscher` (a shape genuinely still unsupported), preserving the test's actual intent — that an out-of-capability enum value is rejected deterministically and never smuggled into the candidate JDL. A **new complement test** was added asserting the opposite for all 6 newly-supported shapes: they must not be reported unsupported, and must actually reach `candidateJDL.stone.shape`.

## Conversation shape modification: yes

Unchanged mechanism — Conversation routes every modification through `DesignerService.interpret()`, so it inherited the widened capability automatically. The existing conversation corpora pass unchanged.

## Shapes falsely professionally validated: 0

`specs/professional-validation/v1/current-validation-registry.json` remains at **zero records**. Every new shape is software reference geometry with `isGemologicalReproduction: false`. `baselineStatus: STABLE` and `currentSettingCompatibility: EXPERIMENTAL` coexist deliberately on all six new shapes and are not in conflict — the first says the geometry is reproducible, the second says the setting around it is provisional.

## Backend tests passed: 1013

Full `pytest -q`: **1013 passed**, 1 pre-existing unrelated warning. Includes 118 new tests: `test_stone.py` (92), `test_stone_schemas.py` (18), `test_stone_system_no_ring_dependency.py` (8). Ruff clean across `jewelmind/` and `tests/`.

## Frontend tests passed: 137/137

`tsc -b` clean, 22 test files / 137 tests passing, production build succeeds.

## Stone / geometry / inspection / Golden tests passed

- `test_stone*.py`: 118
- `test_geometry_quality_*.py`: 49 (with the expanded 18-case Golden Suite)
- `test_geometry_inspection*.py`: 41
- Golden CLI `verify-all`: 18/18

## Technical specification verified

Round prints Shape + Diameter + Depth; non-round prints Shape + Length + Width + Orientation + Depth. Confirmed by real output:

```
--- pear ---
- Shape: pear
- Length: 9.000 mm
- Width: 6.000 mm
- Orientation: 30 deg
- Depth: 4.000 mm
```

**No fake diameter is printed for a non-round stone.** The professional-review disclaimer is present in both cases.

## Real bugs and near-misses found during this Sprint: 3

1. **A genuine circular import.** `geometry/constants.py` needs `resolved_width_mm` (for `prong_center_radius`), while `geometry/stone/builder.py` needs `band_top_z` from `geometry/constants.py`. An eager re-export in `geometry/stone/__init__.py` closed the loop, producing `ImportError: cannot import name 'band_top_z' from partially initialized module`. Fixed by making that `__init__.py` deliberately non-eager; verified from 6 independent fresh-process entry points. Same *class* as Sprint 17's finding but a different cause — Sprint 17's was a layer violation, this was an eager-package-init violation with layers already correct.

2. **An architectural leak in `prong_center_radius()`.** It read `stone.diameter / 2` unconditionally, which would have raised `TypeError: unsupported operand type(s) for /: 'NoneType' and 'int'` for every non-round stone. This was the single genuine leak — a supposedly shape-agnostic construction helper assuming round.

3. **A pear asymmetry test that could pass for the wrong reason.** See the PEAR section above; replaced with centroid-offset assertions plus a symmetric-shape control.

Three further OpenCascade/CadQuery API traps were found during the pre-implementation construction investigation and are recorded in [`572-stone-generation-pipeline.md`](572-stone-generation-pipeline.md): `Workplane.val()` returning an `Edge` rather than a `Wire` without `.close()` (and `isValid()` returning `True` for it, so a validity check would not have caught it); a fillet on a near-zero-thickness extrusion failing with `BRep_API: command not done`; and a `threePointArc` through non-co-circular points failing with a bare `StdFail_NotDone`.

## The assumption that proved unnecessary

The brief pre-authorized a microscopic tip stabilization for pointed shapes. It turned out to be **unnecessary and was not implemented** — marquise and pear both build valid single solids, survive a STEP roundtrip, and rotate cleanly with the sharp construction as written. Stated explicitly in [`569-elongated-stone-contract.md`](569-elongated-stone-contract.md) because a future reader might reasonably expect stabilization to exist and "restore" it.

## `definitionHash` drift: investigated, harmless to Golden regression, documented

The additive `StoneSpec` fields changed `definition_hash()` for every document once regenerated (default `867175e206c8ba1f` → `e1d6dc2f2390875d`; four-prong → `76cd86b9ac469105`; flat-band → `613e1b7451247e6f`; direct-resin → `276ac91816f0fd6a`, plus 3 invalid examples).

This is **not** a violation of `081`'s Migration Requirement 4 — that rule concerns migrating an already-stored document, whereas this is normalization-time default-filling on a freshly re-validated one. Same symptom, different mechanism. Verified that `compare_snapshot()` never reads `definitionHash`, so Golden regression detection was unaffected.

12 stored fixture files were regenerated by running the real code, never hand-typed. This is now the **second consecutive sprint** with this finding, so it is recorded as a recurring structural tension in [`../appendices/jdl-version-compatibility-matrix.md`](../appendices/jdl-version-compatibility-matrix.md) rather than re-derived each time.

## Downstream ripple: 8 failing tests, all stale fixtures, no logic bugs

Notably smaller than Sprint 17's 266. Directly attributable to Sprint 17's recursive `_flatten_into()` fix having already generalized Designer's flattener to arbitrary nesting depth — evidence that the earlier fix was a real structural improvement rather than a local patch.

## Geometry changes introduced intentionally: 1 (additive)

A new shared loft-based construction path for 6 non-round shapes. Round's path was not modified. Confirmed by zero baseline updates across the 12 pre-existing Golden cases.

## Known limitations carried forward

- **Setting compatibility is `EXPERIMENTAL` for all 6 new shapes.** The current prong layout is a generic circular placement that leaves marquise/pear tips and angular-stone corners unsupported. Sprint 19's Setting System.
- **No dimension-range Forge rule for non-round `length`/`width`.** REQUIRES_RULE_EVOLUTION; inventing bounds would be a fabricated threshold.
- **`JM-PRONG-003` not generalized.** No defensible non-round analogue without an equivalent-size metric.
- **Measured dimensions are not orientation-aware.** Axis-aligned bounding box isolates LENGTH from WIDTH exactly only at `orientation == 0`.
- **Golden snapshots do not capture centroid offset.** A silently symmetrized shape preserving volume and extents would pass Golden verification; covered instead by `TestPearAsymmetry`.
- **No faceting.** `FACETED_GEM_MODEL` and `MEASURED_STONE` are documented future layers, not implemented; both require an ADR.
- **Pear's outline is a simplified non-tangent silhouette.** Robust and deterministic, not a smooth commercial pear.
- **No Studio orientation control for round.** Deliberate — orientation is geometrically inert for a `RADIAL` shape.
