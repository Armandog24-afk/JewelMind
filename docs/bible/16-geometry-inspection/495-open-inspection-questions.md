---
id: JM-BIBLE-495
title: Open Inspection Questions
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-INSPECTION-README
  - JM-BIBLE-460
  - JM-BIBLE-494
related_documents:
  - JM-BIBLE-INSPECTION-README
normative: false
implementation_status: current
professional_validation: not_required
---

# Open Inspection Questions

These are open product and policy questions raised while building Sprint 14, not decisions. None are answered by this document — each requires either a product decision, an RFC, or an ADR per [`460-inspection-governance.md`](460-inspection-governance.md) before being acted on.

1. **What exactly should count as "connected" in OpenCascade terms?** `CONTACT_TOLERANCE_MM = 1e-6` (`version.py`) is one order of magnitude looser than OpenCascade's own `Precision::Confusion()` default of `1e-7`. Is that the right permanent value, or should it become configurable — and if configurable, at what layer (a build-time constant, a per-request parameter, a Forge-owned setting)?
2. **Should touching surfaces count as connected, the same as overlapping volume?** Today, `connectivity.py` treats any pair with `Shape.distance() <= CONTACT_TOLERANCE_MM` as connected, regardless of whether the real relationship is a genuine 3D overlap or a zero-volume surface touch. Is that the right permanent semantic, or should the two cases (overlap vs. touch) be distinguished in the connectivity graph itself rather than only in `IntersectionResult.status`'s separate `TOUCHES` value?
3. **Should connected-component analysis run on fused or original component geometry?** Today it runs on the original, pre-fuse component shapes (`band`, `prongs`, `basket_support` as separately generated solids), not on `combined_metal` after `_fuse_metal()`. Is that the right choice permanently, given that `combined_metal` is what actually gets exported?
4. **Should minimum-distance inspection run for every pair at larger scale?** Today it runs for all 6 pairs among the current solitaire's 4 named components. What is the practical pair-count ceiling before an all-pairs approach needs to change to something spatially indexed — tens of pairs, hundreds, or does it depend entirely on per-pair cost rather than pair count?
5. **Should full topology validation run for every generation, unconditionally?** Today it does, because it is cheap at the current 4-component scale (see [`491-runtime-inspection-policy.md`](491-runtime-inspection-policy.md)). Would that hold for a much larger assembly (e.g. a pavé-set piece with dozens of additional small solids), or would topology validation need its own tiering before component count grows significantly?
6. **Which specific inspection facts, if any, should eventually be folded into `compilationHash`/`definitionHash` provenance?** `GeometryInspectionReport.kernelVersion` is a first, small, unlinked step in this direction (see [`488-alchemist-inspection-integration.md`](488-alchemist-inspection-integration.md)) — should it, or any other inspection fact, become part of a future `compilationHash` per `docs/bible/08-alchemist/175-definition-hash-vs-compilation-hash.md`, and if so, does that require the fact itself to be part of provenance, or only the inspection subsystem's own version?
7. **Should inspection version become part of artifact/export provenance** — i.e. should a STEP/STL/technical-specification export record which `INSPECTION_VERSION` produced the inspection summary embedded or referenced in it, beyond the informal Markdown line `specification.py` already writes?
8. **How should topology-count/validity behavior differences across future OpenCascade version upgrades be handled or even detected?** `docs/bible/08-alchemist/174-determinism-and-version-fingerprint.md` already documented that OpenCascade's exact build is not recorded anywhere in current output beyond CadQuery's own version string; a kernel upgrade that silently changes `isValid()` or topology-count behavior for the same geometry would currently be invisible to this codebase.
9. **Should regression snapshots eventually store real intersection-volume and connectivity-edge values, not just component-level aggregates?** [`492-inspection-regression-model.md`](492-inspection-regression-model.md) documents that the current baseline captures only component counts, volumes, prong-count matching, and a single connectivity boolean — the natural next step, tentatively assigned to Sprint 15, "Geometry Quality & Golden Models v1."
10. **When, if ever, should an inspection failure actually block export?** Today, never — [`489-foundry-inspection-integration.md`](489-foundry-inspection-integration.md) documents that `export_step_file()`/`export_stl_file()` do not reference `inspection_report` at all. Is "never block" the right permanent policy, or only the right policy at the current prototype scale where a disconnected production group has never actually been observed on real geometry?
11. **Should external CAD roundtrip inspection (STEP re-import geometry comparison) become part of Foundry or stay part of Inspection?** This capability does not exist in any form today (see [`494-current-runtime-inspection-gap-analysis.md`](494-current-runtime-inspection-gap-analysis.md)); its natural home is genuinely ambiguous — Foundry already owns export integrity checking (`exporters/integrity.py`), while Inspection already owns geometric-fact reporting, and a STEP-reimport comparison is arguably both.
12. **How will pairwise inspection scale for hundreds of future pavé stones?** The current all-pairs approach (6 pairs for 4 components, reduced to 5 real intersection calls by broad-phase distance elimination — see [`491-runtime-inspection-policy.md`](491-runtime-inspection-policy.md)) is combinatorial (`O(n²)` pairs). A future pavé-set piece with, say, 200 stones would produce roughly 20,000 pairs before any elimination. Is a broad-phase/spatial-index approach (e.g. a bounding-volume hierarchy, only computing distance for pairs whose bounding boxes are already close) the eventual answer, and at what component count does today's simple all-pairs approach stop being viable even with the current distance-based broad-phase filter?

## Cross-references

- [`460-inspection-governance.md`](460-inspection-governance.md) — the governance process any answer to these questions must go through.
- [`494-current-runtime-inspection-gap-analysis.md`](494-current-runtime-inspection-gap-analysis.md) — the gaps these questions are drawn from.
- `../13-design-intent/363-open-design-intent-questions.md` — the Sprint 11 sibling this document follows in structure.

Sprint 15 — Geometry Quality & Golden Models v1 — the next sprint, explicitly cited above as a plausible home for expanding the regression model specifically (question 9). No other question in this document is committed to Sprint 15 or any other sprint.
