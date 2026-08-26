---
id: JM-BIBLE-467
title: Solid Count Inspection
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-INSPECTION-README
  - JM-BIBLE-460
related_documents:
  - JM-BIBLE-464
  - JM-BIBLE-466
  - JM-BIBLE-473
implementation_status: current
professional_validation: not_required
normative: true
---

# Solid Count Inspection

## The functions

`shape.py::solid_count(shape: cq.Shape) -> int` is `len(shape.Solids())`. `shape.py::topology_counts(shape: cq.Shape) -> TopologyCounts` computes the same solid count alongside shells/faces/edges/vertices in one call, and is what `inspect_component()` actually uses (via `inspect_topology()`) — `solid_count()` exists as the standalone single-purpose primitive other callers (e.g. `assembly.py::_boolean_operations()`'s `combined_metal.Solids()` check) can use without paying for the other four counts. `TopologyCounts.solids` is the field `ComponentInspectionResult.solidCount` is populated from.

## Real per-component solid counts, default definition

| Component | Solid count |
|---|---|
| `band` | 1 |
| `stone_reference` | 1 |
| `prongs` (default, 6-prong) | 6 — one independent solid per prong, by design (`prongs.py` builds each prong as a separate `cq.Workplane` extrusion and combines them with `cq.Compound.makeCompound()`, never a `.fuse()` chain) |
| `prongs` (4-prong variant) | 4 |
| `basket_support` | 1 |

Assembly level: `combined_metal` (band + prongs + basket, fused via `_fuse_metal()`) is **1** solid for the default definition — the boolean fuse succeeded on its first attempt, with no fallback to a multi-solid compound.

## Multi-solid is a fact, never automatically a failure

`prongs` being reported as a 6-solid (or 4-solid) compound is expected, real, and reported plainly — `inspect_component()` assigns `status="PASS"` to `prongs` under normal conditions regardless of its solid count being greater than 1, because nothing in `inspect_component()`'s own logic treats solid count as a pass/fail criterion at all (only existence, bounding-box success, topology success, and volume finiteness/non-negativity do — see [`464-component-inspection-contract.md`](464-component-inspection-contract.md)). `combined_metal` reporting more than 1 solid (the fallback case) is likewise never itself a `FAIL` at the inspection layer — `assembly.py::_boolean_operations()` reports it as `fallbackUsed=True` with an explanatory note, a structural fact, not a verdict.

Whether a given solid count matters for a specific component in a specific manufacturing context is exactly the kind of question this Sprint's architecture reserves for Forge (restating INSPECT-GOV-001/002 and ATLAS-GOV-001/002): Atlas/Inspection reports "6 solids"; only a Forge rule, if one existed and consumed this fact (none currently does — see [`487-forge-fact-contract.md`](487-forge-fact-contract.md)), could decide "6 disconnected prong solids is/isn't acceptable for lost-wax casting."

## Cross-references

[`464-component-inspection-contract.md`](464-component-inspection-contract.md) for how `solidCount` fits into the full per-component result; [`466-shape-validity-inspection.md`](466-shape-validity-inspection.md) for the sibling check computed in the same `inspect_topology()` call; [`473-production-metal-integrity.md`](473-production-metal-integrity.md) for how the assembly-level `combined_metal` solid count feeds into the production-metal integrity picture. `backend/tests/test_geometry_inspection.py::TestSolidCount` (`test_prongs_solid_count_matches_generated_count`, `test_band_is_a_single_solid`) exercises this directly.
