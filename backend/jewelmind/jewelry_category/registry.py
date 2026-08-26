"""The real jewelry category capability registry — authoritative for what
JewelMind can generate today. `ring` is the only `generationSupported`
entry; every other category is `status: planned` and
`generationSupported: false`, matching `jewelry.category`'s current
`Literal["ring"]` in `domain/schema.py` (a planned category cannot even
reach this registry through real JDL input yet — see
docs/bible/18-ring-architecture/520-jewelry-category-architecture.md).
Mirrored, not duplicated by hand, in
specs/jewelry-architecture/v1/category-registry.json.
"""

from __future__ import annotations

from jewelmind.jewelry_category.models import CategoryCapability

_SHARED_SYSTEMS = ["material", "manufacturing", "stone", "setting", "preview"]

CATEGORY_CAPABILITIES: dict[str, CategoryCapability] = {
    "ring": CategoryCapability(
        category="ring",
        status="current",
        definitionVersion="2.0.0",
        generationSupported=True,
        validationSupported=True,
        previewSupported=True,
        exportSupported=True,
        supportedFamilies=["solitaire"],
        sharedSystems=_SHARED_SYSTEMS,
        categorySpecificSystems=["sizing", "shank", "shoulders", "head"],
        message="Rings are fully supported.",
    ),
    "earring": CategoryCapability(
        category="earring",
        status="planned",
        definitionVersion="0.0.0",
        generationSupported=False,
        validationSupported=False,
        previewSupported=False,
        exportSupported=False,
        supportedFamilies=[],
        sharedSystems=_SHARED_SYSTEMS,
        categorySpecificSystems=[],
        message="Earring is a recognized future jewelry category; generation is not yet supported.",
    ),
    "pendant": CategoryCapability(
        category="pendant",
        status="planned",
        definitionVersion="0.0.0",
        generationSupported=False,
        validationSupported=False,
        previewSupported=False,
        exportSupported=False,
        supportedFamilies=[],
        sharedSystems=_SHARED_SYSTEMS,
        categorySpecificSystems=[],
        message="Pendant is a recognized future jewelry category; generation is not yet supported.",
    ),
    "bracelet": CategoryCapability(
        category="bracelet",
        status="planned",
        definitionVersion="0.0.0",
        generationSupported=False,
        validationSupported=False,
        previewSupported=False,
        exportSupported=False,
        supportedFamilies=[],
        sharedSystems=_SHARED_SYSTEMS,
        categorySpecificSystems=[],
        message="Bracelet is a recognized future jewelry category; generation is not yet supported.",
    ),
    "necklace": CategoryCapability(
        category="necklace",
        status="planned",
        definitionVersion="0.0.0",
        generationSupported=False,
        validationSupported=False,
        previewSupported=False,
        exportSupported=False,
        supportedFamilies=[],
        sharedSystems=_SHARED_SYSTEMS,
        categorySpecificSystems=[],
        message="Necklace is a recognized future jewelry category; generation is not yet supported.",
    ),
    "charm": CategoryCapability(
        category="charm",
        status="planned",
        definitionVersion="0.0.0",
        generationSupported=False,
        validationSupported=False,
        previewSupported=False,
        exportSupported=False,
        supportedFamilies=[],
        sharedSystems=_SHARED_SYSTEMS,
        categorySpecificSystems=[],
        message="Charm is a recognized future jewelry category; generation is not yet supported.",
    ),
}


def get_capability(category: str) -> CategoryCapability | None:
    return CATEGORY_CAPABILITIES.get(category)


def is_generation_supported(category: str) -> bool:
    capability = get_capability(category)
    return capability is not None and capability.generationSupported
