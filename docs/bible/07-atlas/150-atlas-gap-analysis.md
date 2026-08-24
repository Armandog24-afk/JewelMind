---
id: JM-BIBLE-150
title: Atlas Gap Analysis
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-140
related_documents:
  - JM-BIBLE-111
implementation_status: current
professional_validation: not_required
normative: false
---

# Atlas Gap Analysis

No solution is proposed for any gap below beyond what would be needed to close it responsibly — per this Sprint's instruction not to invent solutions merely to fill the document.

| Gap ID | Current state | Impact | Priority | Affected modules | Prerequisite | Requires jewelry expertise? | Atlas or Forge? |
|---|---|---|---|---|---|---|---|
| `ATLAS-GAP-001` Runtime topology validation | No `BRepCheck_Analyzer`-equivalent check runs anywhere | A malformed solid could pass generation and export undetected | High | `geometry/model.py`, all builders | None — a library-level addition | No | Atlas |
| `ATLAS-GAP-002` Runtime connectivity inspection | Only the fuse-solid-count check exists (1 vs. 3) | Cannot distinguish "correctly fused" from "coincidentally 1 solid but poorly connected" | Medium | `solitaire.py` | GAP-001 | No | Atlas |
| `ATLAS-GAP-003` Systematic boolean diagnostics | Only the metal fuse is diagnosed; the basket's cut operation has no diagnostic wrapper at all | A future cut failure (unobserved to date) would propagate as an unhandled `MODEL_GENERATION_FAILED` rather than a documented fallback | Low | `basket.py` | None | No | Atlas |
| `ATLAS-GAP-004` Local-thickness analysis | Does not exist — see also Sprint 4's `FORGE-GAP-005` | The single largest unaddressed manufacturability-adjacent gap in the whole system | High | New capability, likely `geometry/` + a new Forge rule | A mesh/solid distance-field or offset-based library capability | Yes, to interpret results | Both — Atlas measures, Forge interprets |
| `ATLAS-GAP-005` Intersection analysis (general, any two components) | Only stone-vs-metal separation is checked, via bounding box, not true intersection volume | Cannot detect an unexpected overlap between, e.g., prongs and basket beyond the `EMBED_MM`-guaranteed one | Medium | `geometry/model.py` | None | No | Atlas |
| `ATLAS-GAP-006` Stone-metal clearance analysis (beyond bounding-box separation) | Bounding-box Z-separation only (see [`143-stone-metal-separation-contract.md`](143-stone-metal-separation-contract.md)) | A true clearance/intersection check would be more exhaustive | Medium | `geometry/model.py` | GAP-005 | No (structural), yes (to set a clearance threshold — that part is Forge's) | Atlas measures; Forge would judge |
| `ATLAS-GAP-007` Support continuity verification | `basket_support`'s ring-shape continuity is structurally guaranteed by its cut-cylinder construction, but never explicitly verified | Low risk today (construction guarantees it), but would matter for a future non-cylindrical basket | Low | `basket.py` | None | No | Atlas |
| `ATLAS-GAP-008` Geometry plan abstraction | No `GeometryPlan` object exists between validated JDL and construction (same finding as [`05-jdl/077-compiler-contract.md`](../05-jdl/077-compiler-contract.md)) | Harder to inspect/test "what will be built" independent of actually building it | Medium | `solitaire.py` | None | No | Atlas |
| `ATLAS-GAP-009` Component graph | No explicit dependency graph between components (e.g. "prongs depend on stone.diameter") exists as data — it is only knowable by reading builder source | Harder to reason about blast radius of a JDL field change | Low | New capability | GAP-008 | No | Atlas |
| `ATLAS-GAP-010` Kernel-version recording | `GeneratedModel` never records which OCCT/CadQuery version produced it | Cannot retroactively distinguish "this model differs because of an intentional change" from "this model differs because the kernel version changed" | Medium | `geometry/model.py` | None | No | Atlas |
| `ATLAS-GAP-011` Deterministic component identity (per-prong) | No `prong_0`/`prong_1`/... identity exists (see [`138-component-naming-and-identity.md`](138-component-naming-and-identity.md)) | Cannot address or inspect one specific prong individually | Low | `prongs.py` | None | No | Atlas |
| `ATLAS-GAP-012` Robust, general fallback policy | Only two fallbacks exist (fillet, fuse); every other operation (loft, extrude, revolve, cut) has no fallback at all | An unobserved failure in any of these would be an unhandled `MODEL_GENERATION_FAILED`, not a graceful degradation | Medium | All builders | GAP-001 (to know what "robust" means) | No | Atlas |
| `ATLAS-GAP-013` Geometry regression fixtures | `test_geometry.py` tests only the default definition plus a few explicit variants (flat/comfort, 4/6 prong) — no broader fixture set (e.g. boundary-value definitions) exists | A future refactor could silently change geometry for an untested parameter combination | Medium | `backend/tests/` | None | No | Atlas |
| `ATLAS-GAP-014` STEP re-import validation | No test re-imports an exported STEP file to confirm it round-trips correctly | A STEP export could in principle be malformed in a way that only a re-import would catch | Low | `backend/tests/` | None | No | Atlas |
| `ATLAS-GAP-015` STL mesh validation | No test checks the exported STL mesh for manifoldness/watertightness | A tessellation defect (e.g. from an unusual angular tolerance) could go undetected | Low | `backend/tests/` | None | No | Atlas |
| `ATLAS-GAP-016` Performance benchmarks | No benchmark exists at all — see [`148-performance-and-resource-model.md`](148-performance-and-resource-model.md) | Cannot detect a performance regression from a future change | Low | `backend/tests/` | None | No | Atlas |

## Summary

16 gaps identified. **Zero require jewelry expertise on the Atlas side** — every gap is a geometry-engineering capability gap; where a gap's *result* would need domain interpretation (local thickness, clearance), that interpretation step correctly belongs to Forge, consistent with this Sprint's fundamental architectural boundary. The highest-priority gaps (`ATLAS-GAP-001`, `ATLAS-GAP-004`) are both about detecting geometric facts Atlas currently cannot see at all — not about redesigning any existing component.
