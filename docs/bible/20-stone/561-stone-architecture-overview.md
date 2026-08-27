---
id: JM-BIBLE-561
title: Stone Architecture Overview
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
  - JM-BIBLE-562
  - JM-BIBLE-541
implementation_status: current
professional_validation: not_required
normative: true
---

# Stone Architecture Overview

## The layers

```
domain/                                  ← the shared contract layer
  schema.py::StoneSpec                     public JDL input (shape + dimensions + orientation)
  stone_dimensions.py                      resolved LENGTH / WIDTH / DEPTH — the ONE reconciliation point

geometry/                                ← Atlas layer (Sprint 5), generic
  stone/
    __init__.py                            deliberately NON-EAGER (see below)
    outline.py                             7 pure 2D outline primitives -> closed cq.Wire
    builder.py                             dispatch + 3-level loft + orientation
    capability.py                          CURRENT vs PLANNED registry, setting-compatibility axis
    errors.py                              StoneShapeUnsupportedError, StoneGenerationError
  components/stone.py                      thin re-export: build_stone_reference = build_stone
  constants.py::prong_center_radius()       consumes resolved_width_mm() (placement, not a threshold)

validation/                              ← Forge layer (Sprint 4)
  engine.py::_stone_rules()                consumes resolved dimensions; owns every threshold
```

`domain/stone_dimensions.py` is the keystone. Its placement is a real architectural decision, not a convenience: **both** Atlas geometry (`geometry/stone/builder.py`, `geometry/constants.py::prong_center_radius()`) and Forge validation (`validation/engine.py::_stone_rules()`) need the same LENGTH/WIDTH/DEPTH resolution. Putting it inside either consumer would have created a Forge→Atlas or Atlas→Forge import that did not previously exist. `domain/` is the one layer both packages already depended on, so it is the only placement that adds no new coupling.

## Why Stone is category-neutral, not Ring-owned

Sprint 16 established that Ring is one jewelry category rather than JewelMind's architectural root. Sprint 17's Shank subsystem is genuinely ring-specific — a shank *is* a ring part — and lives in the Atlas layer purely for layering reasons.

A stone is different in kind. The same `StoneDefinition` is meaningful in an earring, a pendant, a necklace, a bracelet, or a charm; none of those categories exists yet, but nothing in Stone System assumes a ring either. This is why STONE-GOV-001 is enforced by a real architecture test rather than left as an intention: `backend/tests/test_stone_system_no_ring_dependency.py` AST-parses every file under `geometry/stone/` plus `domain/stone_dimensions.py` and asserts none of them imports `jewelmind.ring`. It uses AST parsing rather than `import` deliberately — an import-based check can pass by accident when the module is already cached from an earlier test in the same session. The same test asserts the *reverse* direction is real, so the dependency arrow is documented in both directions.

The one place Stone touches a ring-shaped concern is `geometry/constants.py::prong_center_radius()`, and that is the ring side reaching *into* Stone's resolved-dimension contract, not Stone reaching out. See [`573-stone-setting-interface.md`](573-stone-setting-interface.md).

## The thin re-export

`geometry/components/stone.py` is now three lines: it re-exports `build_stone` as `build_stone_reference`. This preserves the pre-Sprint-18 import path (`from jewelmind.geometry.components.stone import build_stone_reference`) that the assembly, tests, and preview pipeline already used, so no caller had to change. It mirrors exactly what Sprint 17 did for `geometry/components/band.py`.

## Case study: a real circular import, and why the layering rule earns its keep

The dependency graph above contains a genuine cycle risk, and the first implementation hit it:

```
geometry/constants.py          needs  resolved_width_mm   (for prong_center_radius)
  -> domain/stone_dimensions.py                                    ... fine

geometry/stone/builder.py      needs  band_top_z          (for the girdle plane Z)
  -> geometry/constants.py                                         ... fine

geometry/stone/__init__.py     had    from ...builder import build_stone   ← the mistake
```

With that eager re-export in the package `__init__.py`, importing `geometry.constants` triggered `geometry.stone` (the package), which triggered `builder.py`, which imported `geometry.constants` — still mid-initialization. The real failure was:

```
ImportError: cannot import name 'band_top_z' from partially initialized module
jewelmind.geometry.constants (most likely due to a circular import)
```

**The fix was to make `geometry/stone/__init__.py` deliberately non-eager.** It imports nothing; callers import `jewelmind.geometry.stone.builder` directly. The file's own docstring records why, so a future agent does not "tidy up" the missing convenience re-export and reintroduce the cycle.

This is the *same class* of bug as Sprint 17's finding (where `connection.py` had been placed in `jewelmind/ring/` instead of the Atlas layer) but a different specific cause: Sprint 17's was a **layer** violation, this one is an **eager-package-init** violation with the layers already correct. Both were diagnosed the same way — running `python -c "import X"` from several independent entry points in fresh processes rather than reasoning about import order abstractly. The verification set used here was:

```
import jewelmind.geometry.stone
import jewelmind.geometry.constants
import jewelmind.ring
import jewelmind.jewelry_category
import jewelmind.geometry.components.stone
import jewelmind.api.app
```

All six succeed. The generalizable lesson, worth carrying forward: **when a low-level module needs a value from a package that itself depends on that module, the package's `__init__.py` must not eagerly import its own submodules.** Convenience re-exports are exactly where this bites.

## What Stone does not do

- It does not construct, position, or reason about setting geometry (STONE-GOV-009).
- It does not evaluate any jewelry-domain threshold (STONE-GOV-010).
- It does not know what a ring, prong, or basket is.
- It does not claim gemological accuracy for anything it builds (STONE-GOV-011).

## Cross-references

- [`562-stone-domain-model.md`](562-stone-domain-model.md) — what a StoneDefinition/StoneReference *is*.
- [`572-stone-generation-pipeline.md`](572-stone-generation-pipeline.md) — the real construction stages.
- [`578-current-code-mapping-and-gaps.md`](578-current-code-mapping-and-gaps.md) — the file-by-file map and the honest gaps.
