"""Ring Architecture v2 — one jewelry category, composed from reusable
domain concepts. See docs/bible/18-ring-architecture/README.md.
"""

from jewelmind.ring.adapter import ring_definition_from_jdl
from jewelmind.ring.families import RING_FAMILY_GENERATORS, generate_ring
from jewelmind.ring.models import RingDefinition

__all__ = [
    "RING_FAMILY_GENERATORS",
    "RingDefinition",
    "generate_ring",
    "ring_definition_from_jdl",
]
