"""Deterministic hashing of a canonical JewelryDefinition.

The hash is used as a stable model identity: the same input definition must
always produce the same hash, and (barring a generator version change) the
same geometry.
"""

from __future__ import annotations

import hashlib
import json

from jewelmind.domain.schema import JewelryDefinition


def canonical_json(definition: JewelryDefinition) -> str:
    """Serialize a definition to a canonical (sorted-key, stable) JSON string."""

    data = definition.model_dump(mode="json")
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def definition_hash(definition: JewelryDefinition) -> str:
    """Return a short deterministic hex digest identifying this definition."""

    payload = canonical_json(definition).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]
