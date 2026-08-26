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

#: Real generators only — a family present in `RingFamilyId`
#: (models.py) but absent here is a recognized, PLANNED family with no
#: implementation, never a fake one. Mirrors the category-level
#: current/planned pattern in `jewelmind.jewelry_category.registry`.
RING_FAMILY_GENERATORS: dict[str, Callable[[JewelryDefinition], GeneratedModel]] = {
    "solitaire": build_solitaire_ring,
}

#: Reserved, PLANNED ring families — metadata only, proving the family
#: dispatch boundary is not solitaire-specific without implementing any
#: of them (brief section 10/23).
RESERVED_PLANNED_RING_FAMILIES: tuple[str, ...] = (
    "three_stone",
    "toi_et_moi",
    "halo",
    "eternity",
    "signet",
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
