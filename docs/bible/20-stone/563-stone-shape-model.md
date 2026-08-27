---
id: JM-BIBLE-563
title: Stone Shape Model
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
  - JM-BIBLE-566
  - JM-BIBLE-575
implementation_status: current
professional_validation: not_required
normative: true
---

# Stone Shape Model

## The 7 shapes

`StoneShape` (`backend/jewelmind/domain/schema.py`) is a closed enum:

```python
StoneShape = Literal["round", "oval", "pear", "emerald", "cushion", "princess", "marquise"]
```

All 7 are CURRENT and all 7 genuinely generate real CAD geometry. `round` is the pre-Sprint-18 shape, preserved byte-identically; the other 6 are new in Sprint 18.

| Shape | Symmetry class | Required dimensions | Setting compatibility |
|---|---|---|---|
| `round` | `RADIAL` | `diameter`, `depth` | `SUPPORTED` |
| `oval` | `ELONGATED_SMOOTH` | `length`, `width`, `depth` | `EXPERIMENTAL` |
| `marquise` | `ELONGATED_SMOOTH` | `length`, `width`, `depth` | `EXPERIMENTAL` |
| `emerald` | `RECTILINEAR_ANGULAR` | `length`, `width`, `depth` | `EXPERIMENTAL` |
| `princess` | `RECTILINEAR_ANGULAR` | `length`, `width`, `depth` | `EXPERIMENTAL` |
| `cushion` | `ROUNDED_RECTILINEAR` | `length`, `width`, `depth` | `EXPERIMENTAL` |
| `pear` | `ASYMMETRIC` | `length`, `width`, `depth` | `EXPERIMENTAL` |

The compatibility column is the point of STONE-GOV-009 and is not a typo: a shape that generates correct geometry is *not*, by that fact, a shape whose prong setting is valid. See [`575-stone-capability-model.md`](575-stone-capability-model.md).

## The 5 symmetry classes

`SymmetryClass` (`geometry/stone/capability.py`):

| Class | Shapes | Geometric character |
|---|---|---|
| `RADIAL` | round | Rotationally symmetric about the vertical axis; orientation is a geometric no-op. |
| `ELONGATED_SMOOTH` | oval, marquise | Bilaterally symmetric on both horizontal axes; smooth (arc/ellipse) perimeter, distinct major and minor axes. |
| `RECTILINEAR_ANGULAR` | emerald, princess | Bilaterally symmetric on both horizontal axes; straight edges with corners. |
| `ROUNDED_RECTILINEAR` | cushion | As above, but corners replaced with arcs. |
| `ASYMMETRIC` | pear | Bilaterally symmetric on **one** horizontal axis only. |

### What classification is for — and what it is not

Classification exists to make **shared geometric strategy** explicit and reviewable. Concretely it tells a future reader (or agent) which invariants a shape is expected to satisfy: an `ELONGATED_SMOOTH` shape's 90° rotation should swap its bounding-box X and Y extents; a `RADIAL` shape's rotation should be extent- and volume-equivalent; an `ASYMMETRIC` shape must not accidentally symmetrize.

It does **not** imply that shapes in the same class share an implementation. `oval` and `marquise` are both `ELONGATED_SMOOTH` yet are built from completely different primitives (`.ellipse()` vs two `threePointArc` calls). `emerald` and `princess` are both `RECTILINEAR_ANGULAR` yet one clips its corners and the other does not. Treating the class as a promise of identical construction would be a real misreading.

`ASYMMETRIC` carries the most weight of the five, because it is the class that catches a wrong assumption: any code that assumes bilateral symmetry on *both* axes is correct for 6 of 7 shapes and silently wrong for `pear`. See [`571-asymmetric-stone-contract.md`](571-asymmetric-stone-contract.md).

## Generator dispatch — a registry, not an if/elif chain

`geometry/stone/builder.py` dispatches in two steps.

First, the top-level split, which exists solely to protect round's byte-identical construction (STONE-GOV-016):

```python
def build_stone(definition):
    if definition.stone.shape == "round":
        return _build_round_stone(definition)
    return _build_non_round_stone(definition)
```

Second, within the non-round path, a real registry maps shape → outline builder:

```python
_NON_ROUND_OUTLINE_BUILDERS: dict[str, _OutlineFn] = {
    "oval": O.oval_outline,
    "marquise": O.marquise_outline,
    "pear": O.pear_outline,
    "emerald": O.emerald_outline,
    "princess": O.princess_outline,
    "cushion": O.cushion_outline,
}
```

`_build_non_round_stone()` looks the shape up once and raises `StoneShapeUnsupportedError` on a miss (STONE-GOV-007). Everything after the lookup — resolving dimensions, sampling the outline at three scales, translating to Z, lofting, validating, applying orientation, assembling metadata — is **shape-agnostic**. There is no per-shape branch in the builder body.

This is deliberate and is what makes an eighth shape a small change: add an outline function, add a registry entry, add a capability entry, add a Golden case. No dispatch surgery.

Note that the registry stores the *function objects*, which is also what lets `test_stone.py::TestPearAsymmetry::test_pear_generator_never_silently_produces_a_symmetric_fallback` assert structurally that pear's builder is not the same object as oval's or marquise's — a real guard against a silent fallback (STONE-GOV-013).

## Adding a shape

Per STONE-GOV-014/015 and the RFC requirement in [`560-stone-governance.md`](560-stone-governance.md):

1. An RFC (a new shape is a jewelry-domain extension, see [`../04-jewelry-domain/056-domain-extension-strategy.md`](../04-jewelry-domain/056-domain-extension-strategy.md)).
2. A new outline function in `outline.py` and a registry entry in `builder.py`.
3. A new enum member in `StoneShape`, plus the TypeScript mirror, `shared/validation/engine.ts`, and `specs/jdl/v1/jdl.schema.json`.
4. A `STONE_SHAPE_CAPABILITIES` entry with an honest `currentSettingCompatibility`.
5. Real generation/orientation/inspection tests, and its **own new** Golden case.

## Cross-references

- [`566-stone-outline-contract.md`](566-stone-outline-contract.md) — each outline's real construction.
- [`568-round-stone-contract.md`](568-round-stone-contract.md), [`569-elongated-stone-contract.md`](569-elongated-stone-contract.md), [`570-angular-stone-contract.md`](570-angular-stone-contract.md), [`571-asymmetric-stone-contract.md`](571-asymmetric-stone-contract.md) — per-family detail.
