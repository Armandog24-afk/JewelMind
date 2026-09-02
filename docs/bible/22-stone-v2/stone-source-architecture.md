---
id: JM-BIBLE-601
title: "Stone Source Architecture"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-02
source_of_truth: true
depends_on:
  - JM-BIBLE-600
related_documents:
  - JM-BIBLE-602
  - JM-BIBLE-607
implementation_status: current
professional_validation: not_required
normative: true
---

# Stone Source Architecture

## The problem this solves

Stone v1 had one way to obtain stone geometry: name a cut from an enum and give
its dimensions. That is fine until a user has a stone the enum does not
describe — which is most real stones.

Stone v2 introduces `StoneSourceMode`, and with it the architectural claim that
**JewelMind can work with a stone even when that stone corresponds to no
built-in named cut** (STONEV2-GOV-002).

## The four modes

```
StoneSourceMode
├── PARAMETRIC_REFERENCE   a named cut + explicit dimensions        CURRENT
├── CUSTOM_OUTLINE         a validated closed outline + depth       CURRENT
├── MEASURED               real measurements of a real stone        CURRENT
└── IMPORTED_CAD           an external STEP / BREP / STL asset      PARTIAL
```

### Why there is no `SCANNED_MESH`

A scan arrives as a mesh or as a converted CAD file. `IMPORTED_CAD` already
normalizes both. A fifth mode would duplicate that pipeline without adding
meaning, and would invite the false impression that JewelMind performs
scan-specific processing (decimation, hole filling, point-cloud
reconstruction) — which it does not.

Scan-specific processing is tracked as the `STONE_SCAN` capability, status
`PLANNED`. The architecture does not prevent it; `ImportedStoneSource` is where
it would attach.

## The canonicalization boundary

Everything funnels through one function:

```
StoneSpec  ──►  canonicalize_stone()  ──►  NormalizedStoneDefinition
                (jewelmind/stone/normalize.py)
```

**Why this exists.** Without it, every downstream system — Atlas, Forge,
Setting, Vision, Studio, Foundry, the technical specification, the review
package — would need its own `if source == ...` ladder.

Sprint 19 showed exactly how that goes. The moment `prong` stopped being the
only setting family, five separate architectural leaks appeared in five
different modules, every one a hardcoded assumption about the old single case.
The subtlest produced *missing facts* rather than an error. Normalizing once,
here, is what stops the same thing happening for stone sources.

**The consumer contract:** read `sourceMode` to learn where geometry came from.
Never pattern-match `shape`, which carries `"custom"` or `"imported"` for
stones with no named cut.

## Dispatch is a registry, not a conditional

```python
STONE_SOURCE_HANDLERS = {
    "PARAMETRIC_REFERENCE": ...,
    "CUSTOM_OUTLINE": ...,
    "MEASURED": ...,
    "IMPORTED_CAD": ...,
}
```

`jewelmind/stone/dispatch.py` builds this lazily inside a cached function
rather than as a module-level constant, for the same reason
`jewelry_category/dispatch.py` does: the handler lives in `normalize.py`, which
imports this package's other modules, and a module-level constant would force
that import at package-init time. Deferring it keeps the import graph acyclic.

All four currently route to the same canonicalizer, which branches internally.
They are registered separately anyway, so a future mode needing genuinely
different handling is a new registration rather than another branch inside one
function. Nothing is registered as a placeholder.

## The non-eager `__init__.py`, and why it is load-bearing

`backend/jewelmind/stone/__init__.py` imports **nothing**.

This is not tidiness. `domain/schema.py` imports `jewelmind.stone.models` for
the canonical stone vocabulary, while `jewelmind.stone.normalize` imports
`domain/schema.py` for `StoneSpec`. That is only acyclic because importing the
package itself pulls in no submodule.

Sprint 18 hit this exact cycle in `geometry/stone/__init__.py` and fixed it the
same way. Adding a convenience re-export here reintroduces it.

**Enforced by** `test_stone_v2_no_category_dependency.py::test_stone_package_init_is_non_eager`.

## Layering

```
domain/schema.py          ──►  jewelmind/stone/models.py     (vocabulary only)
jewelmind/stone/*         ──►  domain/schema.py              (StoneSpec only)
                          ──►  geometry/stone/outline.py     (kernel primitives)
geometry/stone/builder.py ──►  jewelmind/stone/*             (the placement adapter)
jewelmind/setting/*       ──►  jewelmind/stone/*             (consumes outlines)
```

`geometry/stone/builder.py` is the only module that sees a whole
`JewelryDefinition`, and only to compute where the girdle plane sits. Its
category-neutral counterpart, `build_stone_geometry(stone, girdle_z_mm)`, takes
a stone and a plane — which is what lets a test, or a future jewelry category,
build a stone without fabricating a ring around it.

## Cross-references

- [`custom-outline-contract.md`](custom-outline-contract.md)
- [`measured-stone-contract.md`](measured-stone-contract.md)
- [`imported-stone-contract.md`](imported-stone-contract.md)
- [`../21-setting/setting-architecture.md`](../21-setting/setting-architecture.md)
  — the same two-boundary pattern, one sprint earlier.
