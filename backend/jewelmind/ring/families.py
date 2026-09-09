"""Ring family dispatch — a second, narrower dispatch boundary nested
inside the `ring` category (JDL `jewelry.style` currently means "ring
family"; see docs/bible/18-ring-architecture/524-ring-family-model.md and
540-category-vs-family-vs-style question in 537-open-ring-architecture-questions.md).

`generate_ring()` is registered as the `ring` category's generator in
`jewelmind.jewelry_category.dispatch.CATEGORY_GENERATORS`. It calls the
real `ring_definition_from_jdl()` adapter (proving every real solitaire
definition maps cleanly into RingDefinition v2) and then dispatches to
the real, UNCHANGED `build_solitaire_ring()` — geometry output is
guaranteed identical to before this Sprint (QUALITY-GOV-016/017 apply
here too: this refactor must not itself cause a Golden regression).
"""

from __future__ import annotations

from collections.abc import Callable

from jewelmind.domain.schema import JewelryDefinition
from jewelmind.geometry.assemblies.solitaire import build_solitaire_ring
from jewelmind.geometry.model import GeneratedModel
from jewelmind.jewelry_category.errors import RingFamilyUnsupportedError
from jewelmind.ring.adapter import ring_definition_from_jdl

#: Real generators only — a family present in `RingFamilyId` (models.py) but
#: absent here is a recognized, PLANNED family with no implementation, never a
#: fake one. Mirrors the category-level current/planned pattern in
#: `jewelmind.jewelry_category.registry`.
#:
#: EVERY FAMILY MAPS TO THE SAME ASSEMBLY, and that is the point rather than an
#: oversight (Sprint 28). A ring family is a PARAMETRIC COMPOSITION of the one
#: ring assembly, not a second assembly: the family resolves into the blocks the
#: existing systems own — the shank's architecture, the head's height, the stone
#: family, the halo, the pavé field — and `build_solitaire_ring()` applies the
#: resolution through `geometry/ring_family_adapter.py::effective_definition()`
#: before building anything.
#:
#: A generator per family would have meant a class per combination, which is
#: exactly the catalogue the sprint brief forbids: "cathedral + oval diamond +
#: four prongs + pavé shoulders" is one variant with four parameters.
#:
#: The function's NAME is historical — it predates ring families and is
#: referenced from the Golden suite, the specs and every test — so it is kept
#: rather than renamed (SETTINGV2-GOV-002's discipline for `basket_support`,
#: applied to a function).
RING_FAMILY_GENERATORS: dict[str, Callable[[JewelryDefinition], GeneratedModel]] = {
    "solitaire": build_solitaire_ring,
    "three_stone": build_solitaire_ring,
    "halo": build_solitaire_ring,
    "split_shank": build_solitaire_ring,
    "bypass": build_solitaire_ring,
    "signet": build_solitaire_ring,
}

#: Reserved, PLANNED ring families — metadata only, with the real technical
#: reason for each in `ring_family/models.py::RESERVED_RING_FAMILIES`.
#:
#: Sprint 28 REMOVED `three_stone`, `halo` and `signet` from this tuple because
#: each now has a real generator and at least one executable variant, and added
#: none: `split_shank` and `bypass` were never reserved names, they are new.
RESERVED_PLANNED_RING_FAMILIES: tuple[str, ...] = (
    "toi_et_moi",
    "eternity",
    "plain_band",
    "cluster",
)


def generate_ring(definition: JewelryDefinition) -> GeneratedModel:
    ring_definition_from_jdl(definition)  # validates the real RingDefinition v2 mapping on every generation

    family = definition.jewelry.style
    generator = RING_FAMILY_GENERATORS.get(family)
    if generator is None:
        raise RingFamilyUnsupportedError(f"Ring family '{family}' is not supported.")
    return generator(definition)
