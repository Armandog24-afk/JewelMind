---
id: JM-BIBLE-ARRANGE-BOUNDARY
title: "Stone Arrangement execution boundary"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-03
source_of_truth: true
depends_on:
  - JM-BIBLE-ARRANGE-README
implementation_status: partial
professional_validation: not_required
normative: true
---

# Stone Arrangement execution boundary

Exactly what executes today, what does not, and why the line was drawn here
rather than further along.

## The line

| Stage | Status | Evidence |
| --- | --- | --- |
| Declare an arrangement in JDL | **CURRENT** | round-trips through `JewelryDefinition`, validates against `specs/jdl/v1/jdl.schema.json` |
| Validate it structurally | **CURRENT** | `JM-ARRANGE-001`…`006` |
| Resolve it to explicit placements | **CURRENT** | `resolve.py`; every instance gets real coordinates |
| Fingerprint it deterministically | **CURRENT** | `arrangement_fingerprint()` |
| Report per-instance generation status | **CURRENT** | `compile.py`; travels on `GeneratedModel.arrangement_result` |
| Build geometry for the primary instance | **CURRENT** | the existing `stone_reference` component |
| Build geometry for additional instances | **NOT IMPLEMENTED** | reported `NOT_GENERATED` with a reason |

So an eight-stone halo is fully expressible, fully validated, fully resolved to
eight real positions, and produces **one** stone solid. The other seven
instances are reported, each with an explanation. Nothing is silently dropped
and no placeholder solid is invented.

## Why the line is here

Emitting additional stone solids is not a matter of calling the stone builder in
a loop. It requires changes across four subsystems that currently assume exactly
one stone, and each change alters semantics that existing behaviour depends on:

1. **`geometry/stone/builder.py`** places one stone on the design axis at a
   girdle Z. It takes no XY offset and no per-instance transform, so an
   additional instance has nowhere to go.
2. **`geometry/inspection/assembly.py`** hardcodes
   `REQUIRED_COMPONENT_NAMES = ("band", "stone_reference", "basket_support")`
   and keys the stone/metal separation check on the literal name
   `"stone_reference"`. A second stone would be inspected as production metal
   and generate spurious intersection findings against the first.
3. **The Setting System** receives one `StoneSettingReference` and produces one
   setting. A halo needs either one setting per accent or a genuinely new
   setting family (pavé, shared prong), which is RFC territory under
   `SETTING-GOV`.
4. **Foundry and Vision** classify components by name. That part IS now handled
   — `geometry/roles.py` recognizes the `stone_reference.` prefix — but it was
   the one piece that had to land early, because getting it wrong would break
   LAW-006 the first time a second stone appeared.

Crossing the line properly means changing (2) and (3), which the brief
explicitly warns against doing "simply to accommodate the new domain model", and
(3) requires an RFC. So the sprint implemented the domain and compilation
contracts, integrated what genuinely works, and stopped.

## What was deliberately NOT done

- **No loop over the stone builder.** It would place every instance at the same
  point, producing coincident solids — geometry that looks like a feature and is
  not one.
- **No empty component per ungenerated instance.** An empty
  `GeneratedComponent` would make a component count match while representing
  nothing, which is worse than an honest absence.
- **No relaxation of the inspection checks** to stop a second stone tripping
  them. Weakening a real check to make new geometry pass is the failure mode
  `INSPECT-GOV` exists to prevent.
- **No `arrangement` exclusion from `geometryHash`.** Tempting, because it would
  let a halo edit reuse the single-stone geometry — and wrong, because the
  arrangement will drive geometry the moment (1) lands, and a stale-geometry
  cache hit is worse than a rebuild.

## How the boundary is reported, not hidden

Four separate channels, so it cannot be missed:

- **Per instance.** `ResolvedInstance.generationStatus` is `NOT_GENERATED` with a
  `generationNote`. The model REQUIRES the note when the status says so, and a
  `GENERATED` instance must name its component — enforced by a validator, so no
  code path can omit either.
- **Per model.** `ResolvedArrangement.generatedCount` versus `instanceCount`,
  plus `notes`.
- **Per validation run.** `JM-ARRANGE-006`, severity `information`: "This
  arrangement resolves N stone instances. Multi-stone geometry generation is not
  yet implemented…". An `information` result, because the design is not faulty.
- **Per capability.** `multi_stone_geometry` is `PARTIAL` with
  `generatable: false` in `arrangement/capability.py`,
  `specs/arrangement/v1/arrangement-registry.json`, and
  `specs/capabilities/jewelmind-capabilities.json`.

## What lands next

In dependency order:

1. A per-instance transform on the stone builder — the smallest change that
   makes a second stone placeable at all.
2. Instance-aware Geometry Inspection: `REQUIRED_COMPONENT_NAMES` and the
   stone/metal separation check generalized to a set of stone components.
3. A setting strategy for accents (RFC required under `SETTING-GOV`).
4. Instance overrides applied to geometry (`scale`, `orientationDeg`), which are
   representable and resolved today but affect nothing built.

Only after (1) and (2) can `multi_stone_geometry` become `CURRENT`, and it must
not be relabelled before then.
