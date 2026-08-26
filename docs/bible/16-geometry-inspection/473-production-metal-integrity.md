---
id: JM-BIBLE-473
title: Production Metal Integrity
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
  - JM-BIBLE-465
  - JM-BIBLE-467
  - JM-BIBLE-470
implementation_status: current
professional_validation: not_required
normative: true
---

# Production Metal Integrity

## What "production metal" means

`jewelmind.geometry.roles.GEOMETRY_ROLE` (`backend/jewelmind/geometry/roles.py`) is the single source of truth: `band`, `prongs`, and `basket_support` are `"production_metal"`; `stone_reference` is `"stone_reference"`. This module was extracted this Sprint from a private mapping that previously lived only inside `preview/mesh.py` — Sprint 14's own code audit found the same production-vs-reference classification duplicated in more than one place, and `roles.py` is the deduplication: both `geometry/inspection/assembly.py` and `preview/mesh.py` now import `is_production_component()`/`production_component_names()`/`reference_component_names()` from this one module, so there is exactly one place a future component's role is declared, not two that could silently drift apart.

## How integrity is assessed — three real signals, never a fusion re-check

Inspection never fuses geometry itself — that remains exclusively `solitaire.py::_fuse_metal()`'s job, called once during generation, before inspection ever runs. Inspection is purely read-only observation of whatever connectivity and solid-count the already-built geometry has. Three real facts, all already computed elsewhere in the pipeline, together describe production-metal integrity:

1. **Required-component presence.** `AssemblyInspectionResult.missingComponentIds` — every one of `REQUIRED_COMPONENT_NAMES` not present or not `exists` in `component_results`.
2. **Production connectivity.** `AssemblyInspectionResult.productionConnectivity.disconnectedGroupCount` — built from real pairwise `Shape.distance()` measurements over exactly the production-role components (see [`470-component-connectivity-model.md`](470-component-connectivity-model.md)). A count of `0` means every production component is one connected body (band, prongs, basket touching or overlapping each other); a nonzero count means the production metal has genuinely separate, unconnected groups.
3. **Aggregate production solid count.** Surfaced in the API metadata summary, not on `AssemblyInspectionResult` itself: `backend/jewelmind/api/routes.py::_inspection_summary()` computes `productionSolidCount = sum(r.solidCount or 0 for r in report.componentResults if r.componentId in production_ids)` — the sum of each production component's own `solidCount` (e.g. `band: 1 + prongs: 6 + basket_support: 1 = 8` for the default definition, counting each independent prong solid), which is a different number from `combined_metal`'s own solid count (`1`, the fused result) and is not meant to be compared against it directly — it answers "how many independent solids exist across the production components before fusing," while `combined_metal`'s solid count (from `assembly.py::_boolean_operations()`, see [`467-solid-count-inspection.md`](467-solid-count-inspection.md)) answers "did the fuse actually succeed."

## Real current finding, default solitaire

Production metal is exactly **1 connected group** (`disconnectedGroupCount = 0`) — `band`, `basket_support`, and `prongs` all touch or overlap each other by real measured distance. The `combined_metal` shape is exactly **1 solid** — the boolean fuse (`_fuse_metal()`) succeeded on its first attempt, with no fallback to a multi-solid compound. These are two independently-computed facts that happen to agree for the default definition: connectivity is measured from the pre-fuse component shapes via `Shape.distance()`, while the solid count is measured from the post-fuse `combined_metal` shape via `Shape.Solids()` — a disagreement between them (e.g. a fully connected production graph whose fuse still fell back to a compound, or vice versa) is possible in principle and would itself be a reportable, interesting fact, not something either check would paper over.

## A structural fact, not a professional judgment

Whether a multi-body production structure would be professionally appropriate — for example, whether prongs remaining geometrically separate solids (rather than fused into one body with the band) matters for a specific casting process — is explicitly a separate, deferred question this document does not answer. `inspect_assembly()` and `_inspection_summary()` report the structural fact (connected or not, fused or not, how many solids); interpreting that fact against a manufacturing profile is Forge's job, and no Forge rule currently consumes `productionSolidCount` or `disconnectedGroupCount` (see [`487-forge-fact-contract.md`](487-forge-fact-contract.md)).

## Cross-references

[`465-assembly-inspection-contract.md`](465-assembly-inspection-contract.md) for the full assembly orchestration this document's three signals are drawn from; [`467-solid-count-inspection.md`](467-solid-count-inspection.md) for the per-component and `combined_metal` solid-count mechanics; [`470-component-connectivity-model.md`](470-component-connectivity-model.md) for the connectivity-graph algorithm itself. `backend/tests/test_geometry_inspection.py::TestProductionConnectivity` and `TestFallbackInspection::test_combined_metal_multi_solid_is_detectable_as_a_fallback_signal` exercise the two independent signals this document combines.
