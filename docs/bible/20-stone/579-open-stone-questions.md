---
id: JM-BIBLE-579
title: Open Stone Questions
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-STONE-README
  - JM-BIBLE-560
related_documents:
  - JM-BIBLE-578
  - JM-BIBLE-573
implementation_status: current
professional_validation: not_required
normative: false
---

# Open Stone Questions

Genuinely open questions, recorded rather than decided. Nothing here is a commitment, a roadmap item, or a hint about what the answer should be. Each names the process that would resolve it.

## 1. Should non-round `length`/`width` gain a Forge dimension-range rule?

`JM-STONE-001` bounds a round stone's diameter to 2–15 mm. No analogous rule exists for a non-round shape's `length` or `width`, so an `oval 0.3 × 0.2` or an `oval 400 × 300` currently produces no dimension-range error (it would still fail `JM-STONE-002` if the depth were inconsistent, but nothing bounds the horizontal extents themselves).

The open part is not *whether* a bound would be useful but *what it should be and where it comes from*. A round stone's 2–15 mm range is itself a `preliminary` software rule, not a validated professional one. Inventing separate bounds for six shapes — or reusing round's — would be a fabricated threshold with no source (STONE-GOV-010). It is also unclear whether the right rule bounds each dimension independently, bounds the smaller extent, or bounds an aspect ratio.

**Resolution path:** a Forge rule addition with a real `provenanceType`, a rule-version bump per [`../06-forge/108-rule-versioning.md`](../06-forge/108-rule-versioning.md), and registry/catalog updates. If any bound is claimed as professionally meaningful rather than `prototype_heuristic`, it needs a professional-validation register entry first.

## 2. Should prong placement become shape-aware?

Every non-round shape is `currentSettingCompatibility: EXPERIMENTAL` because `prong_center_radius()` produces a single circular layout from `resolved_width_mm`. For a 10 × 5 marquise the prongs sit on a circle far narrower than the stone, leaving both tips unsupported; for a square princess they sit mid-edge, leaving the corners exposed.

The open questions are about ownership and shape: does placement live in a new Setting System package or in the Ring head contract? Is it a per-shape strategy registry, or a general algorithm parameterised by the outline? Does a shape declare its own preferred prong positions, or does the Setting layer derive them (STONE-GOV-009 says Stone must not contain prong positions, which constrains but does not settle this)?

**Resolution path:** Sprint 19 — *"Setting System v1 — separate stone-setting geometry from ring-specific head construction and establish reusable parametric setting strategies, beginning with generalized prong placement and bezel support across compatible Stone System shapes."*

## 3. Should measured-dimension facts become orientation-aware?

`STONE_MEASURED_LENGTH` / `STONE_MEASURED_WIDTH` read the axis-aligned bounding box, so they isolate LENGTH from WIDTH exactly only at `orientation == 0`. At 45° neither extent corresponds to a real stone dimension, which makes the requested-vs-measured regression check weak at arbitrary angles.

A fix would project the solid onto the stone's own rotated local axes rather than the world axes. Open: is that worth the complexity given that non-zero orientation is not yet exposed in Studio for most workflows? Should the facts instead report an explicit `measurementValidAtOrientation` qualifier, or should a rotated stone simply emit `UNKNOWN` for these facts rather than a misleading number?

**Resolution path:** a Geometry Inspection change. Adding a fact type or changing a fact's semantics is a MINOR/MAJOR inspection-version decision per [`../16-geometry-inspection/460-inspection-governance.md`](../16-geometry-inspection/460-inspection-governance.md); replacing the measurement mechanism would need an ADR.

## 4. Should a `FACETED_GEM_MODEL` layer exist?

Today every shape is a three-level ruled loft — a reference silhouette, not faceting. A faceted layer would model real facet planes for visual fidelity and, potentially, for optical reasoning.

Open: is the driver visual (Vision presentation quality) or functional (clearance against a real facet)? If purely visual, does it belong in the backend at all, or is it a Vision-layer material/shading concern? How would it interact with Golden regression, given that facet counts would multiply topology facts? STONE-GOV-012 guarantees `StoneDefinition` would not need replacing, but says nothing about whether the layer is worth building.

**Resolution path:** an ADR, per [`560-stone-governance.md`](560-stone-governance.md).

## 5. Should `MEASURED_STONE` (supplier / scan / imported) be supported?

A jeweller setting a specific physical stone has real measured dimensions, and possibly a scan, that the parametric model cannot express. [`567-stone-reference-geometry-contract.md`](567-stone-reference-geometry-contract.md) names the future `PARAMETRIC_REFERENCE_STONE` vs `MEASURED_STONE` distinction without implementing it.

Open: does a measured stone arrive as dimensions only (which the current model could nearly express) or as imported geometry (which changes the determinism story entirely — imported geometry is not reproducible from the definition)? How would `definitionHash` and the Golden Suite treat a definition whose geometry comes from an external file? Does it need a new provenance field on the component?

The determinism question is the hard one: LAW/STONE-GOV-002 requires the same definition to produce the same geometry, which an external-file reference only satisfies if the file is content-addressed.

**Resolution path:** an ADR, and likely an RFC for the workflow around it.

## 6. Should more shapes be added, and by what process?

Named candidates: asscher, radiant, heart, trillion, baguette, cabochon, custom outlines, calibrated stones.

Deliberately **not** pre-registered as `planned` in `STONE_SHAPE_CAPABILITIES` (see [`575-stone-capability-model.md`](575-stone-capability-model.md)) — listing them would imply a commitment and a design that does not exist.

Several raise genuinely new questions rather than being more of the same:

- **cabochon** is not a faceted-silhouette shape at all — it is a domed solid with no table, so the shared three-level crown/girdle/pavilion loft does not describe it.
- **custom outlines** would mean accepting geometry data in JDL, which brushes against the rule that JDL carries no executable content and raises the same determinism question as `MEASURED_STONE`.
- **calibrated stones** are a sizing/sourcing concept more than a geometry one.
- **heart** and **trillion** would each be a second and third `ASYMMETRIC`-adjacent case, testing whether the single asymmetric precedent generalizes.

**Resolution path:** an RFC per shape, per [`../04-jewelry-domain/056-domain-extension-strategy.md`](../04-jewelry-domain/056-domain-extension-strategy.md). An ADR is additionally required for cabochon or custom outlines, since both would change the construction contract rather than add an outline.

## 7. Should the pear outline become tangent-continuous?

The current pear is a simplified non-tangent silhouette: two straight sides meeting a rounded end at a non-zero angle. A real pear has a continuous curve from tip through shoulder to belly.

Open: does the visible kink matter for a *reference* solid? A tangent-continuous version needs spline fitting, which is less predictable under extreme length/width ratios and would change the shape's volume — a Golden baseline update. Would the same treatment then be expected for marquise's tips?

**Resolution path:** a construction change, so an ADR plus a documented Golden baseline update.

## 8. Should an equivalent-size metric exist at all?

Sprint 18 refused to synthesise an equivalent diameter (brief section 44), and that refusal is load-bearing: it is what kept `JM-STONE-001` and `JM-PRONG-003` honestly round-only instead of silently evaluating a made-up number.

But the underlying need is real — "how big is this stone, roughly" is a question a rule, a UI, and a jeweller all reasonably ask. Open: is there a defensible metric (girdle area? minimum enclosing circle? spread?) with genuine domain semantics rather than a convenience average? Who validates it? Would introducing one reopen the rules currently scoped round-only?

**Resolution path:** an RFC, explicitly required by [`560-stone-governance.md`](560-stone-governance.md). This must not be introduced as a refactor.

## 9. Should multi-stone arrangements be supported?

Halo, pavé, three-stone, toi-et-moi. These are `StoneArrangement` concerns rather than `StoneDefinition` concerns — `StoneArrangementDefinition` already exists with `SINGLE_CENTER` as its only current value.

Open: does an arrangement hold N independent `StoneSpec` values, or a pattern plus one prototype stone? How do Forge rules apply per-stone versus per-arrangement? What does a Golden case for a 20-stone pavé even capture?

**Resolution path:** an RFC, and likely its own sprint. Out of Stone System's scope by design.
