"""JSON export: the canonical JewelryDefinition, pretty-printed."""

from __future__ import annotations

import json

from jewelmind.domain.schema import JewelryDefinition


def export_json(definition: JewelryDefinition) -> str:
    data = definition.model_dump(mode="json")
    return json.dumps(data, indent=2, sort_keys=True) + "\n"
