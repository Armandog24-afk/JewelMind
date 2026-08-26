---
id: JM-BIBLE-494
title: Current Runtime Inspection Gap Analysis
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-INSPECTION-README
  - JM-BIBLE-460
  - JM-BIBLE-493
related_documents:
  - JM-BIBLE-495
  - JM-BIBLE-460
normative: false
implementation_status: current
professional_validation: not_required
---

# Current Runtime Inspection Gap Analysis

This document catalogues future gaps observed while building Sprint 14, without implementing any of them. Per Bible governance, none of these are CURRENT or PARTIAL functionality — they are candidate future work, gated by the RFC/ADR process named in [`460-inspection-governance.md`](460-inspection-governance.md).

## Gaps identified while building the real Sprint 14 code

| Gap | Business value | Complexity | Architecture dependency | Professional-validation need | Target sprint |
|---|---|---|---|---|---|
| Forge does not yet consume any `GeometricFact` (all 16 fact types `forgeConsumptionStatus: "not_consumed"`) | High — this is the whole point of reporting facts, unconsumed value is latent | Medium — the contract exists (see [`487-forge-fact-contract.md`](487-forge-fact-contract.md)); a first rule needs a provenance declaration and registry entries, not new plumbing | A specific fact + threshold + provenance decision, per `docs/bible/06-forge/090-forge-governance.md` | Yes, for any threshold beyond `unknown`/`prototype_heuristic` provenance | Unscheduled |
| No frontend UI renders inspection data anywhere in Studio | Medium — the backend contract is real and callable, but invisible to a user today | Low — `fetchInspectionReport()` and `InspectionSummary` already exist; `ProfessionalReviewPanel.tsx` is a specific, natural home (see [`490-vision-inspection-integration.md`](490-vision-inspection-integration.md)) | None beyond a component change; no new backend work needed for a summary view | No | Unscheduled |
| Individual prong identity (`prong_0`/`prong_1`/...) not implemented | Low-Medium — useful once per-prong quality questions matter | Low — the ordered `_prong_positions()` list in `prongs.py` already makes this structurally easy | None — additive to `ComponentInspectionResult`/`GeometricFact` metadata | No, until a per-prong Forge rule is proposed | Unscheduled |
| `ConnectivityEdge.basis = "INTERSECTION"` is schema-complete but never assigned — connectivity is decided purely by distance | Low today — distance-only connectivity matches the current solitaire's real behavior | Low-Medium — would require wiring intersection results into `build_connectivity_graph()`, currently fed only by `pairwise_distances()` | None architectural — `connectivity.py`'s own function signature would need to accept intersection results too | No | Unscheduled |
| No inspection-version participation in Alchemist's compilation-provenance/fingerprint model | Medium — `kernelVersion` is now recorded per-report (a real partial improvement, see [`488-alchemist-inspection-integration.md`](488-alchemist-inspection-integration.md)) but not tied to `definitionHash`/any future `compilationHash` | Medium — depends on `compilationHash` existing first, per `docs/bible/08-alchemist/175-definition-hash-vs-compilation-hash.md` | Blocked on `compilationHash` implementation (ALCHEMIST-GOV-009) | No | Unscheduled — blocked on Alchemist work, not Inspection work |
| Shape-validity check is binary valid/invalid only, no deeper defect classification | Medium — a jeweler/engineer would want to know *what* is invalid, not just that it is | High — would require enumerating and classifying `BRepCheck_Analyzer` defect categories, a real OpenCascade-API investigation this Sprint did not undertake | New Atlas-level inspection primitive under `shape.py` | Possibly, to interpret defect severity | Unscheduled |
| Regression baseline doesn't yet snapshot connectivity edges/intersection volumes/topology counts as automated assertions | Medium — the raw data already exists in test-vector JSON, only the automated comparison is missing | Low — the data capture already works, this is purely more assertions in `test_geometry_inspection.py` | None | No | **Sprint 15 — "Geometry Quality & Golden Models v1"** (the one gap in this table with a specific, non-"Unscheduled" target; see [`492-inspection-regression-model.md`](492-inspection-regression-model.md)) |

## The brief's explicit gap list — inspection families that do not exist in any form

Every item below is confirmed absent from `backend/jewelmind/geometry/inspection/` by reading the package in full for this Sprint. None has any code, test, or partial implementation. Each is classified as a future geometric-fact type (something Inspection could eventually compute) vs. something that would additionally require professional jewelry/manufacturing input to interpret (a future Forge concern, or both).

| Gap | Classification | Architecture owner | Complexity | Target sprint |
|---|---|---|---|---|
| Local-thickness inspection | Geometric-fact-type (future) | Atlas (new inspection primitive) | High — no existing kernel wrapper in this codebase attempts this | Unscheduled |
| Curvature inspection | Geometric-fact-type (future) | Atlas | High | Unscheduled |
| Sharp-feature detection | Geometric-fact-type (future), would also require professional input to set any threshold | Atlas + Forge (threshold) | High | Unscheduled |
| Enclosed-volume (trapped-volume) detection | Geometric-fact-type (future) | Atlas | Medium-High — `docs/bible/07-atlas/140-geometry-inspection-framework.md` already lists this as PLANNED from Sprint 5 | Unscheduled |
| Manufacturable-opening inspection | Would require professional input to define "manufacturable" | Atlas (fact) + Forge (interpretation) | High | Unscheduled |
| Stone-seat inspection | Would require professional input (setting-specific geometry expertise) | Atlas (fact) + Forge (interpretation) | High | Unscheduled |
| Prong-contact-region inspection | Geometric-fact-type (future) — related to, but more precise than, the aggregate `IntersectionResult` this Sprint already computes for `prongs`↔`stone_reference` | Atlas | Medium | Unscheduled |
| Polishing-access inspection | Would require professional input | Atlas (fact) + Forge (interpretation) | High | Unscheduled |
| Surface-continuity inspection | Geometric-fact-type (future) | Atlas | High | Unscheduled |
| Wall-thickness inspection | Would require professional input to define acceptable minimums per manufacturing method | Atlas (fact) + Forge (interpretation) | Medium-High | Unscheduled |
| Mesh-manifold inspection | Geometric-fact-type (future) — distinct from the current B-Rep `isValid()` check; would apply to tessellated STL output specifically (ATLAS-GOV-009 still requires STL to never become a source of truth even if inspected) | Atlas/Foundry boundary | Medium | Unscheduled |
| STEP-reimport-comparison inspection | Geometric-fact-type (future) — see [`495-open-inspection-questions.md`](495-open-inspection-questions.md) for whether this belongs to Foundry or Inspection | Foundry or Atlas (undecided — open question) | High | Unscheduled |
| Collision-acceleration structures (for pairwise checks at scale) | Infrastructure, not a fact type itself | Atlas (Inspection performance layer) | Medium — the current broad-phase distance-based elimination (`should_skip_intersection()`) is a first, small step in this direction | Unscheduled |
| Large-assembly-performance inspection (e.g. hundreds of pavé stones) | Infrastructure/policy, not a fact type itself | Atlas (Inspection performance layer) — see [`491-runtime-inspection-policy.md`](491-runtime-inspection-policy.md) | High | Unscheduled |

None of the fourteen items above is committed to any sprint; per `docs/bible/16-geometry-inspection/460-inspection-governance.md`'s "When an RFC is required," any of them beyond the current component/assembly/connectivity/intersection/distance/topology families would need its own RFC before implementation, and several would separately need a named professional's input before any resulting Forge rule could be marked `validated` (PROVAL-GOV-006/007).

## Next scheduled sprint

**Sprint 15 — "Geometry Quality & Golden Models v1"** — cited above as the specific home for expanding the regression baseline (connectivity/intersection/topology snapshot assertions). No other gap in this document is committed to Sprint 15; every other row is genuinely "Unscheduled."

## Cross-references

- [`460-inspection-governance.md`](460-inspection-governance.md) — when an RFC or ADR is required before any of these can be built.
- [`495-open-inspection-questions.md`](495-open-inspection-questions.md) — the open product/policy questions these gaps raise.
- [`487-forge-fact-contract.md`](487-forge-fact-contract.md), [`488-alchemist-inspection-integration.md`](488-alchemist-inspection-integration.md), [`489-foundry-inspection-integration.md`](489-foundry-inspection-integration.md), [`490-vision-inspection-integration.md`](490-vision-inspection-integration.md) — the four integration documents this gap table draws from.
- `../13-design-intent/362-design-intent-gap-analysis.md` — the Sprint 11 sibling this table follows in structure.
