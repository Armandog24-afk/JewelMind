"""Platform-level jewelry category architecture.

Ring is one jewelry category, not JewelMind's architectural root — see
docs/bible/18-ring-architecture/README.md. This package owns category
identity, capability, and generic dispatch; it must never import from
`jewelmind.ring` or know anything about ring-specific fields.
"""

from jewelmind.jewelry_category.dispatch import generate_for_category, generate_jewelry
from jewelmind.jewelry_category.forge_scope import rule_scope
from jewelmind.jewelry_category.registry import (
    CATEGORY_CAPABILITIES,
    get_capability,
    is_generation_supported,
)

__all__ = [
    "CATEGORY_CAPABILITIES",
    "generate_for_category",
    "generate_jewelry",
    "get_capability",
    "is_generation_supported",
    "rule_scope",
]
