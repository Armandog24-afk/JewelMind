---
id: JM-BIBLE-SPRINT-14-VALIDATION-REPORT
title: "Sprint 14 Validation Report — Geometry Inspection v2"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-INSPECTION-README
  - JM-BIBLE-460
related_documents:
  - JM-BIBLE-494
implementation_status: current
professional_validation: not_required
normative: false
---

# Sprint 14 Validation Report — Geometry Inspection v2

## Inspection documents created

39 files under `docs/bible/16-geometry-inspection/`: `README.md`, `460-inspection-governance.md`, `461`–`495` (35 narrative docs), and this validation report. Plus 8 new appendices (`A92`–`A99`) and 11 cross-cutting files updated across Forge, Atlas, Alchemist, Professional Validation, `README.md`, `documentation-index.md`, `008-glossary.md`, and `CLAUDE.md`.

## Schemas created

9 JSON Schemas under `specs/geometry-inspection/v2/`: `geometric-fact`, `component-inspection`, `assembly-inspection`, `connectivity-result`, `intersection-result`, `distance-result`, `inspection-report`, `inspection-diagnostic`, `inspection-version`. Plus a hand-authored `fact-registry.json` (16 fact-type definitions), 5 real generated examples, and 8 real generated test-vector files.

## Runtime inspectors implemented

Yes — 12 real Python modules under `backend/jewelmind/geometry/inspection/` (1,168 lines total), invoked unconditionally by `ModelService.generate()`, not test-only scaffolding. See [`inspection-code-mapping.md`](../appendices/inspection-code-mapping.md).

## Geometric fact types implemented

16 `FactType` values defined; **11 of 16 are actually constructed** by the current pipeline (`COMPONENT_PRESENT`, `SOLID_COUNT`, `VOLUME`, `SHAPE_VALID`, `BOUNDING_BOX`, `COMPONENT_COUNT`, `PRONG_COUNT`, `STONE_METAL_SEPARATE`, `INTERSECTION_VOLUME`, `MIN_DISTANCE`, `CONNECTED`). Not currently emitted into `geometricFacts`: `INTERSECTION_EXISTS`, `DISCONNECTED` (never true for the real solitaire), `COMPONENT_PRESENT` at assembly scope for a missing required component, `BOOLEAN_RESULT_VALID`, `FALLBACK_USED` as a standalone flattened fact (fallback state is present in `ComponentInspectionResult.fallbackUsed`/`BooleanOperationResult.fallbackUsed` but not separately flattened into `geometricFacts`). See [`geometry-fact-catalog.md`](../appendices/geometry-fact-catalog.md).

## Current components inspected

4 — `band`, `stone_reference`, `prongs`, `basket_support` (the full current solitaire component set; no new component family was added).

## Component relationship pairs inspected

6 pairwise relationships per inspection run — all C(4,2) combinations of the 4 real components, each carrying both a distance fact and an intersection fact.

## Runtime connectivity/intersection/distance implemented: yes

All three are real, running, kernel-backed computations (`Shape.distance()`, `Shape.intersect()`, and a DFS-based connectivity graph built from real distance measurements), not placeholders.

## Kernel topology validity implemented: yes

`Shape.isValid()` (OCP `BRepCheck_Analyzer`) and `Shape.Solids()/Shells()/Faces()/Edges()/Vertices()` topology counts are both real and wired into every component inspection.

## Current production connectivity groups discovered

1 — the real default and four-prong solitaires are both fully connected production assemblies (`band`, `prongs`, `basket_support`), `disconnectedGroupCount: 0`.

## Current unexpected disconnected components

0 — no real solitaire configuration currently produces a disconnected production component. (A synthetic two-cube fixture, never a real jewelry model, is used in `TestDisconnectedFixture` to prove the detection logic itself works.)

## Current unexpected intersections

0 — every intersecting pair observed in the real solitaire (band↔prongs, band↔basket_support, stone_reference↔prongs, stone_reference↔basket_support, prongs↔basket_support) is an expected, by-design overlap (`EMBED_MM`-driven fusion overlap for production pairs; deliberate grip realism for the stone). No pair intersects that the domain model did not already anticipate.

## StoneReference separation verified: yes

Verified structurally, not geometrically — the stone's shape is confirmed (by code inspection and by `TestStoneExportSeparation`) never to be an argument to `_fuse_metal()`, in both the default and four-prong configurations. A positive stone↔production intersection volume (2.10mm³ / 3.62mm³ in the default solitaire) is correctly *not* treated as a separation failure — see [`474-stone-metal-separation-inspection.md`](474-stone-metal-separation-inspection.md).

## Real solitaire models inspected

2 configurations captured as baseline: the default six-prong solitaire and the four-prong variant. Both produced `status: PASS` inspection reports with zero diagnostics.

## Regression baselines created: yes

`specs/geometry-inspection/v2/examples/default-solitaire-inspection.json`, `four-prong-inspection.json`, and `specs/geometry-inspection/v2/test-vectors/regression-vectors.json`, checked by `TestInspectionRegression`. Full per-component/per-pair values are tabulated in [`solitaire-inspection-baseline.md`](../appendices/solitaire-inspection-baseline.md) (A99).

## Inspection files added to review packages: yes

`professional_validation/review_package.py` now bundles `geometry-inspection.json` (the full real `GeometryInspectionReport`) in every generated review package.

## Geometry issues newly discovered

None that indicate a defect. Sprint 14 discovered and corrected a **documentation framing error**, not a geometry bug: the pre-existing `143-stone-metal-separation-contract.md` implied "zero intersection volume" was the correct StoneReference separation invariant. Real measurement showed the stone genuinely and intentionally intersects `prongs`/`basket_support` with positive volume. The correct invariant — structural non-fusion, not geometric non-intersection — is now the one implemented and documented (see [`474-stone-metal-separation-inspection.md`](474-stone-metal-separation-inspection.md)).

## Professional thresholds introduced: 0

Zero. Every new field is a geometric fact (a volume, a distance, a solid count, a boolean) — Inspection reports facts, and per INSPECT-GOV, never interprets a fact as a jewelry-domain or manufacturing rule violation. `fact-registry.json`'s `forgeConsumptionStatus` is `"not_consumed"` for all 16 facts.

## Tests passed

- Backend: **715/715** (`pytest -q`), including 34 new tests in `test_geometry_inspection.py` and 6 new tests in `test_geometry_inspection_schemas.py`.
- Frontend: **137/137** (`vitest run`).
- `ruff check .`: clean.
- `npx tsc -b`: clean.
- `npx oxlint`: clean.
- `npm run build`: succeeds (pre-existing >500kB single-chunk warning, unrelated to this Sprint).

## CI result

Pending — verified locally prior to push; GitHub Actions run to be monitored after commit/push (see the top-level Sprint 14 delivery message for the final run status).

## Honest gaps carried forward (not defects, documented plainly)

- Only 4 of 11 `InspectionDiagnosticCode` values are reachable by current code (`INSPECTION_COMPONENT_MISSING`, `INSPECTION_VOLUME_FAILED`, `INSPECTION_BOUNDING_BOX_FAILED`, `INSPECTION_TOPOLOGY_FAILED`). `distance.py`/`intersection.py` report kernel failures via `status` (`ERROR`/`UNKNOWN`) but never construct an `InspectionDiagnostic` entry — see [`inspection-diagnostic-catalog.md`](../appendices/inspection-diagnostic-catalog.md).
- `ConnectivityEdge.basis` only ever takes the value `"DISTANCE"` in current code; `"INTERSECTION"` is a real, schema-valid, currently-unreachable alternative.
- Individual prong identity (tracking which specific prong is which across regeneration) is investigated but not implemented — see [`475-prong-count-and-identity-inspection.md`](475-prong-count-and-identity-inspection.md).
- No frontend component currently calls `fetchInspectionReport()` — the API contract (`GET /api/models/{model_id}/inspection`) is real and complete, but Vision/Studio UI consumption is deliberately out of scope for this Sprint — see [`490-vision-inspection-integration.md`](490-vision-inspection-integration.md).
- Forge does not yet consume any geometric fact — `487-forge-fact-contract.md` establishes the contract only, per the brief's explicit "groundwork, not full wiring" instruction.

---

**Sprint 15 — Geometry Quality & Golden Models v1** — establish authoritative geometric regression fixtures, quality baselines, reproducible reference models, output comparison tools and controlled acceptance criteria before JewelMind expands beyond the solitaire.
