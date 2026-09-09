---
id: JM-BIBLE-A25
title: "Appendix: Atlas Fallback Register"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-135
related_documents:
  - JM-BIBLE-134
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Atlas Fallback Register

**These are the only two fallback paths that exist anywhere in the current geometry codebase.** Sprint 28 added no third one; it widened the TRIGGER of `ATLAS-FALLBACK-002`, which matters more than a new entry would — see "Why the trigger was widened" below.

## `ATLAS-FALLBACK-001` — Band outer-rim fillet

| Field | Value |
|---|---|
| Operation | `.fillet(fillet_radius)` on the band's outer-rim edges |
| Trigger | The fillet call raises an exception, or succeeds but yields zero solids |
| Primary behavior | A band with a rounded outer rim (radius up to 0.25mm) |
| Fallback behavior | The pre-fillet, sharp-edged solid |
| Affected component | `band` |
| User-visible warning | `"Outer rim fillet could not be applied ({exc}); falling back to sharp edges."` |
| Regression tests | **None** — no test forces this fallback to trigger; it is verified only by code review |
| Risk | Low — purely cosmetic difference; band dimensions (inner/outer radius, width) are unaffected either way |

## `ATLAS-FALLBACK-002` — Combined-metal boolean fuse

| Field | Value |
|---|---|
| Operation | `band.fuse(basket).fuse(prongs)` and every further production-metal component |
| Trigger | The fuse raises an exception; **or** succeeds but `fused.Solids()` is empty; **or (Sprint 28)** succeeds and returns a volume SMALLER THAN ITS LARGEST INPUT |
| Primary behavior | A single fused solid (`combined_metal.Solids()` has length 1) |
| Fallback behavior | `cq.Compound.makeCompound([...])` — every original solid, unfused |
| Affected component | `combined_metal` (assembly-level, not a single named component) |
| User-visible warning | `"Combined metal union failed ({exc}); exporting {names} as a multi-solid compound instead of a single fused solid."` — where `{exc}` now includes the measured volumes when the invariant is what tripped |
| Regression tests | **Yes, since Sprint 28** — `test_ring_families.py::test_a_degenerate_fuse_is_reported_rather_than_shipped` forces the fallback with a real design and asserts the warning, and `test_the_fuse_invariant_leaves_every_sound_family_alone` asserts it does NOT fire on any of the 13 ring-family variants |
| Risk | Low for correctness (no component is dropped — LAW-005), but STEP/STL consumers receive a multi-solid file instead of 1, which some downstream CAD/manufacturing tools may treat differently |

### Why the trigger was widened (Sprint 28)

The original trigger assumed a bad fuse either raises or returns nothing. It can
do neither. A bypass shank whose two passes clear each other by ~0.07 mm
produced a fuse that **raised nothing, reported `isValid() == True`, and returned
six solids of NEGATIVE volume** — the six prongs, inverted, with the band and the
basket gone entirely. `combined_metal_volume_mm3` was −60.904 and **no warning
was emitted**, so a caller had no way to know the ring had disappeared.

The invariant now checked is the strongest one available without redoing the
boolean: **a union is never smaller than its largest input.** That is arithmetic
about unions — not a tolerance, not a jewelry threshold — so it needed no
invented number. A result that fails it takes this same honest fallback.

## Not hidden

Both fallbacks are stated plainly in `docs/known-limitations.md`, `docs/geometry-conventions.md`, and now formally in [`07-atlas/135-fillets-rounding-and-fallbacks.md`](../07-atlas/135-fillets-rounding-and-fallbacks.md) / [`134-boolean-operation-strategy.md`](../07-atlas/134-boolean-operation-strategy.md) — neither is a newly-discovered secret; this Sprint's contribution is formalizing them into one comparable register with the three previously-undocumented magic numbers involved in the fillet fallback.
