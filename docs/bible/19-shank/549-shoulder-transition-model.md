---
id: JM-BIBLE-549
title: Shoulder Transition Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-SHANK-README
  - JM-BIBLE-540
  - JM-BIBLE-542
related_documents:
  - JM-BIBLE-527
  - JM-BIBLE-548
implementation_status: current
professional_validation: not_required
normative: true
---

# Shoulder Transition Model

## There is no shoulder-transition component in v1

Sprint 17 did not add a shoulder as an independently modeled piece of geometry. `jewelmind.ring.models.ShoulderDefinition` (Sprint 16) remains exactly what it was before this Sprint:

```python
class ShoulderDefinition(RingModel):
    modeled: Literal[False] = False
```

`ring_definition_from_jdl()` still constructs it as `ShoulderDefinition()` with no data flowing in from the JDL, because no shoulder-related field exists anywhere in `domain/schema.py`. This is documented in full at [`18-ring-architecture/527-shoulder-contract.md`](../18-ring-architecture/527-shoulder-contract.md); this document does not restate that contract's reasoning, only records how it interacts with taper.

In the real geometry builders (`geometry/components/`), the shank flows directly into the head with no distinct transition solid, no separate component name, and no dedicated section of `builder.py`. "Shoulder" is a domain-anatomy term (see [`04-jewelry-domain/043-ring-anatomy.md`](../04-jewelry-domain/043-ring-anatomy.md)) describing a region of the same single `band` solid that `build_shank()` produces — it is not a boundary the code draws.

## Why taper does not need one either

A dedicated shoulder-transition component would typically exist to handle a geometric discontinuity — a change in cross-section, width, or thickness that needs its own blending geometry between two regions built differently. Sprint 17's taper model was deliberately designed to avoid creating that discontinuity in the first place:

- `taper.py::taper_ratio(u, taper)` is a pure function of `u`, the longitudinal position around the ring, and is continuous over `u ∈ [0, 1)` (SHANK-GOV-005).
- `mode="TOWARD_BOTTOM"` anchors the full base width/thickness exactly at `u=0` (the head) and interpolates linearly to `bottomRatio * base` at `u=0.5` (the bottom), using `distance_from_head = min(u, 1.0 - u) * 2.0` — see [`548-taper-model.md`](548-taper-model.md).
- Because `distance_from_head` is symmetric around `u=0`, the two shoulder regions (`u` increasing from 0, and `u` decreasing toward 1 from the other side) receive identical taper behavior automatically, computed by the same single call path. No code anywhere in `geometry/shank/` special-cases "left shoulder" vs "right shoulder" with separately duplicated parameters (SHANK-GOV-005's explicit prohibition).

The practical consequence: both shoulders taper (or don't) identically and symmetrically without any shoulder-specific code existing to make that true. It falls out of `taper_ratio()`'s definition, not out of a shoulder-transition builder.

## No invented shoulder geometry parameter

SHANK-GOV-012 forbids inventing a professional threshold or subjective descriptor for taper — no code path in `geometry/shank/` or `design_intent/` may map a word like "more delicate" or "elegant" to an arbitrary `bottomRatio`. This applies directly to the shoulder region: there is no separate "shoulder taper amount" concept anywhere in the schema or the builder distinct from the single `bottomRatio` already documented in [`548-taper-model.md`](548-taper-model.md). A caller cannot request a shoulder that behaves differently from the rest of the taper curve; the only knob is the one `BandTaperSpec` already exposes, applied uniformly by `taper_ratio(u, taper)` regardless of where along the ring `u` falls.

## Golden coverage of the shoulder region

None of SOL-010/011/012 (see [`555-shank-golden-strategy.md`](555-shank-golden-strategy.md)) isolates the shoulder region as a distinct measurement — Golden comparison works at the level of the whole `band` component's volume, bounding box, and connectivity facts, not a per-region breakdown. A defect specific to the shoulder transition (as opposed to the taper curve generally) would only be caught by these cases if it changed the component's overall volume or bounding box enough to exceed comparison tolerance; nothing in the current Golden Suite specifically targets the shoulder as its own region of interest, consistent with there being no shoulder-specific code to target.

## What this means for the tapered loft

`_build_tapered_shank()` samples `SECTION_COUNT + 1` (49) profile wires at `i / SECTION_COUNT` for `i in range(49)` and lofts them into one solid with `cq.Solid.makeLoft(wires, ruled=True)`. There is no seam, join, or blend feature at either shoulder position — the shoulder region is simply a contiguous range of sampled sections like any other range of `u`. See [`551-shank-generation-pipeline.md`](551-shank-generation-pipeline.md) and [`552-shank-continuity-model.md`](552-shank-continuity-model.md) for how the loft itself is constructed and what continuity guarantee it actually provides.

## Honest limitation

Because there is no explicit shoulder component or transition model, there is nothing in v1 that could express a shoulder-specific geometric feature distinct from a plain taper — for example, a shoulder that flares, steps, or blends into a cathedral-style head mount. The `cathedral_shank` capability entry in `geometry/shank/capability.py::SHANK_CAPABILITIES` (`status: "planned"`) is explicitly described as belonging "primarily to shoulder/head integration, not a profile type" — the capability registry itself records that a real shoulder/head integration model does not exist yet, rather than implying it does. See [`557-shank-capability-model.md`](557-shank-capability-model.md) for the full capability list, and [`559-open-shank-questions.md`](559-open-shank-questions.md) for whether a dedicated shoulder-transition model should be built in a future Sprint.
