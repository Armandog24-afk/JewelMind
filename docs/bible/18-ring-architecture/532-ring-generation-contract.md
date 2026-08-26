---
id: JM-BIBLE-532
title: Ring Generation Contract
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-RING-README
  - JM-BIBLE-520
related_documents:
  - JM-BIBLE-521
implementation_status: current
professional_validation: not_required
normative: true
---

# Ring Generation Contract

The real, in-production dispatch chain from an HTTP generation request
down to CadQuery geometry, as it exists after this Sprint.

## The chain

```
ModelService.generate(definition)
  -> jewelmind.jewelry_category.dispatch.generate_jewelry(definition)
       -> generate_for_category(
            definition.jewelry.category,   # currently always "ring"
            definition,
            registry=_category_generators(),   # lazily built, cached dict
          )
            -> jewelmind.ring.families.generate_ring(definition)
                 -> ring_definition_from_jdl(definition)   # validates the mapping; result discarded
                 -> RING_FAMILY_GENERATORS[definition.jewelry.style](definition)
                      -> build_solitaire_ring(definition)   # UNCHANGED since Sprint 5
```

Each arrow is a real function call, verified by reading:
[`services/model_service.py`](../../../backend/jewelmind/services/model_service.py)
(`generate_jewelry` imported and called at the point that previously
called `build_solitaire_ring` directly),
[`jewelry_category/dispatch.py`](../../../backend/jewelmind/jewelry_category/dispatch.py),
[`ring/families.py`](../../../backend/jewelmind/ring/families.py), and
[`ring/adapter.py`](../../../backend/jewelmind/ring/adapter.py).

## The real call-site comment in `model_service.py`

```python
# Dispatched by jewelry.category (currently always "ring") rather
# than calling a geometry builder directly — see
# docs/bible/18-ring-architecture/532-ring-generation-contract.md.
generated_model = generate_jewelry(definition)
```

A second, identical call site exists in
[`geometry_quality/snapshot.py`](../../../backend/jewelmind/geometry_quality/snapshot.py)
(Sprint 15's Golden Suite fixture builder), with the matching comment
citing this same document. Both call sites prove the dispatch path
carries production and Golden-fixture generation identically — there is
no separate "fast path" that bypasses category dispatch.

## `ring_definition_from_jdl()` runs on every generation, and its result is discarded

`generate_ring()` ([`ring/families.py`](../../../backend/jewelmind/ring/families.py))
calls `ring_definition_from_jdl(definition)` before dispatching to the
family generator, but never uses the returned `RingDefinition` for
anything — the actual geometry call still receives the original
`JewelryDefinition`:

```python
def generate_ring(definition: JewelryDefinition) -> GeneratedModel:
    ring_definition_from_jdl(definition)  # validates the real RingDefinition v2 mapping on every generation
    family = definition.jewelry.style
    generator = RING_FAMILY_GENERATORS.get(family)
    ...
    return generator(definition)
```

This means every real generation proves the JDL -> `RingDefinition` v2
mapping still succeeds (raising `CategoryAdapterFailedError` if it ever
would not), without `RingDefinition` v2 itself driving geometry —
`build_solitaire_ring()` still consumes the original `JewelryDefinition`
directly, unchanged from Sprint 5.

## Why composition/registry, not inheritance

The brief for this Sprint states explicitly: *"Do not add unnecessary
inheritance. Composition/registry-based architecture may be superior."*
Both dispatch layers follow this literally:

- `jewelmind.jewelry_category.dispatch._category_generators()` returns a
  plain `dict[str, Callable[[Any], Any]]` — currently `{"ring":
  generate_ring}`.
- `jewelmind.ring.families.RING_FAMILY_GENERATORS` is a plain
  `dict[str, Callable[[JewelryDefinition], GeneratedModel]]` — currently
  `{"solitaire": build_solitaire_ring}`.

Neither introduces a base class, an abstract generator interface, or a
class hierarchy. Extending either registry (a new category, a new ring
family) is adding one dict entry — see
[`534-multi-category-readiness-contract.md`](534-multi-category-readiness-contract.md).
This directly satisfies JEWELRY-ARCH-GOV-002/003/010
([`520-jewelry-category-architecture.md`](520-jewelry-category-architecture.md)):
the dispatch boundary stays generic, a planned category/family is never
silently generatable, and an unregistered-but-recognized value raises a
clean, typed error (`JewelryCategoryNotGeneratableError` /
`RingFamilyUnsupportedError`) rather than a fallback.

## Atlas's `build_solitaire_ring()` was not modified

This Sprint changed **only** what calls `build_solitaire_ring()` and how
— never the function itself. `ring/families.py` imports it unchanged:

```python
from jewelmind.geometry.assemblies.solitaire import build_solitaire_ring
...
RING_FAMILY_GENERATORS: dict[str, Callable[[JewelryDefinition], GeneratedModel]] = {
    "solitaire": build_solitaire_ring,
}
```

This is JEWELRY-ARCH-GOV-009 by construction: the same `JewelryDefinition`
in, the same `GeneratedModel` out. `backend/tests/test_ring_architecture.py::TestBackwardCompatibleJdl::test_generate_jewelry_and_generate_ring_produce_identical_geometry`
proves `generate_jewelry()` and a direct `generate_ring()` call produce
the identical `definition_hash` and `combined_metal_volume_mm3` for the
same input. The Golden Suite (Sprint 15) required zero baseline updates
— see the README's validation report reference and
[`536-current-code-mapping-and-gaps.md`](536-current-code-mapping-and-gaps.md).

## The real circular-import bug, and its fix

`jewelmind.jewelry_category.dispatch._category_generators()` carries
this real docstring, explaining a bug found and fixed during this
Sprint's own implementation:

> "Built lazily, on first real dispatch rather than at module-import
> time: `jewelmind.ring` imports `jewelmind.jewelry_category.errors`, so
> importing `jewelmind.ring.families` here eagerly (at this module's own
> import time) is a genuine circular import whenever `jewelmind.ring` is
> the first of the two packages to be imported. Deferring the import
> until this function is actually called (well after both packages have
> finished loading) avoids it entirely."

Concretely: `jewelmind.ring.adapter` imports
`jewelmind.jewelry_category.errors.CategoryAdapterFailedError`, and
(before the fix) `jewelmind.jewelry_category.dispatch` imported
`jewelmind.ring.families` at its own module top. If Python happened to
import `jewelmind.ring` first, loading `jewelmind.ring.families` would
trigger loading `jewelmind.jewelry_category.dispatch`, which would in
turn try to import `jewelmind.ring.families` again — a module still
mid-initialization, so the name would not yet be bound.

**The fix**: the cross-package import (`from jewelmind.ring.families
import generate_ring`) was moved inside `_category_generators()`, a
function evaluated lazily and cached via the module-level
`_category_generators_cache` variable, called only on the first real
dispatch (i.e. the first `generate_jewelry()` call) — by which point both
packages have finished loading regardless of import order. This is
JEWELRY-ARCH-GOV-002's textual requirement: `generate_for_category()`
itself never imports or references `jewelmind.ring` at its own
module-import time.

This was verified empirically from both import orders during
implementation, not merely reasoned about — see the README's "What was
investigated, not invented" section.
