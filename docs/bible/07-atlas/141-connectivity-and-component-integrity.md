---
id: JM-BIBLE-141
title: Connectivity and Component Integrity
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-140
related_documents:
  - JM-BIBLE-A24
implementation_status: partial
professional_validation: not_required
normative: true
---

# Connectivity and Component Integrity

## Production-metal connectivity vs. assembly membership — two different questions

**Assembly membership**: is this component one of the four required parts of a `SolitaireAssembly`? All four (`band`, `stone_reference`, `prongs`, `basket_support`) always are.

**Production-metal connectivity**: do the metal components (band, prongs, basket_support) form one physically connected body? This is checked, but only indirectly and only at one point: `_fuse_metal()`'s `fused.Solids()` count. A count of 1 implies full connectivity (OCCT's fuse would not merge unconnected geometry into a single solid); a count of 3 (the fallback) means connectivity was **not** achieved, and the three solids are exported as a compound of separately-connected (or, per their construction via `EMBED_MM`, actually-overlapping-but-not-fused) bodies.

## Per-component connectivity assessment

| Component | Internally connected? | Connected to its neighbors? |
|---|---|---|
| `band` | Yes — always one solid | Embeds `EMBED_MM` into the assembly anchor region where prongs/basket attach (by construction, via shared Z-reference, not an explicit connectivity check) |
| `basket_support` | Yes — always one solid (cut, not fuse) | Embeds into the band region below it (`base_z = band_top_z - EMBED_MM`) |
| `prongs` | **No — always a compound of N independent solids**, by design (each prong is its own solid) | Each prong embeds into the band/basket region below it |
| `stone_reference` | Yes — always one solid | **Deliberately never connected to metal** (LAW-006) |

## Stone reference is expected to remain separate

This is a requirement, not an incidental fact: `stone_reference` must never appear in `combined_metal`, and the only current check enforcing physical separation is a bounding-box comparison in a test (`test_geometry.py::test_stone_reference_is_valid_and_separate_from_metal`: `stone.bounding_box.zmin >= band.bounding_box.zmax - 1e-6`) — see [`143-stone-metal-separation-contract.md`](143-stone-metal-separation-contract.md) for the full contract.

## Sprint 14 (Geometry Inspection v2): three of these are now real

[`16-geometry-inspection/470-component-connectivity-model.md`](../16-geometry-inspection/470-component-connectivity-model.md) implements, for real, at runtime, on every generation:

- **Number of disconnected metal bodies** — `AssemblyInspectionResult.productionConnectivity.disconnectedGroupCount`, computed from a real union-find over real `Shape.distance()` measurements between band/prongs/basket_support, not merely inferred from the fuse-vs-compound solid count. For the current default solitaire this independently confirms what the fuse outcome already implied: 0 disconnected groups.
- **Required intersections** — `AssemblyInspectionResult.intersections`/`distances` now independently VERIFY the `EMBED_MM` construction guarantee for every pairwise combination (band↔basket_support, basket_support↔prongs, band↔prongs all measured and confirmed to intersect with real positive volume) rather than relying on it unverified.
- **Floating components** — the same connectivity graph would report a genuinely isolated component as its own disconnected group; verified against a deliberately-broken test fixture (two components placed 100mm apart) in `backend/tests/test_geometry_inspection.py::TestDisconnectedFixture`.

**Support continuity** (an unbroken basket ring) remains PLANNED/not implemented — Sprint 14 did not add a continuity-specific check beyond the general solid/topology facts already covered above.

## Current test mapping

`test_geometry.py::test_solitaire_assembly_metal_is_single_fused_solid_by_default` (fuse outcome), `test_stone_reference_is_valid_and_separate_from_metal` (stone separation), `test_solitaire_assembly_has_all_required_components` (assembly membership, all four present with positive volume). No test currently exercises the fuse-fallback (3-solid) path itself — it has never been observed to trigger for any tested parameter combination, so its behavior is verified only by code review of `_fuse_metal()`, not by a passing/failing test that actually forces the fallback.

As of Sprint 14, add `test_geometry_inspection.py::TestProductionConnectivity` (real connectivity graph, real solitaire), `TestDisconnectedFixture`/`TestIntersectingFixture` (deliberately-broken test fixtures, never real jewelry models) — see [`16-geometry-inspection/493-current-solitaire-inspection-map.md`](../16-geometry-inspection/493-current-solitaire-inspection-map.md) for the full current coverage map.
