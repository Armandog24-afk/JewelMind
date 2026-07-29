"""Validation result schema and rule identifier constants."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

Severity = Literal["error", "warning", "information"]


class ValidationResult(BaseModel):
    ruleId: str
    severity: Severity
    message: str
    parameter: str
    suggestedValue: float | int | str | None = None


# Rule identifiers, centralized so engine.py and tests reference one source
# of truth instead of hand-typed string literals scattered across the code.
RING_INNER_DIAMETER_RANGE = "JM-RING-001"
RING_SIZE_RANGE = "JM-RING-002"
RING_SIZE_DIAMETER_CONSISTENCY = "JM-RING-003"

BAND_WIDTH_MIN = "JM-BAND-001"
BAND_THICKNESS_MIN = "JM-BAND-002"
BAND_WIDTH_MAX = "JM-BAND-003"

STONE_DIAMETER_RANGE = "JM-STONE-001"
STONE_DEPTH_RANGE = "JM-STONE-002"

PRONG_COUNT = "JM-PRONG-001"
PRONG_DIAMETER_MIN = "JM-PRONG-002"
PRONG_COUNT_VS_STONE_SIZE = "JM-PRONG-003"
PRONG_HEIGHT_VS_BASKET = "JM-PRONG-004"

SETTING_BASKET_HEIGHT_POSITIVE = "JM-SETTING-001"
SETTING_BASKET_HEIGHT_MAX = "JM-SETTING-002"

MANUFACTURING_MIN_FEATURE = "JM-MANUFACTURING-001"

GEOMETRY_OUTER_BAND_POSITIVE = "JM-GEOMETRY-001"
