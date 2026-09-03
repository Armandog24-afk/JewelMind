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
# Sprint 19, BEZEL_ONLY, both ENGINEERING_INVARIANT (constructibility, not
# a jewelry threshold). No minimum bezel wall dimension is asserted — no
# sourced professional value exists and inventing one is forbidden
# (SETTING-GOV-010).
BEZEL_WALL_THICKNESS_POSITIVE = "JM-SETTING-003"
BEZEL_WALL_HEIGHT_POSITIVE = "JM-SETTING-004"

# Sprint 23 — SETTING_V2. Structural and referential checks on the advanced
# head/prong fields: does the requested architecture have the parameters it
# needs, is a field meaningful for the family that was chosen, can the
# requested operation actually run against this stone.
#
# NONE is a professional or manufacturing threshold. There is deliberately no
# rule about minimum prong thickness for a given stone size, minimum head wall
# for a given metal, or whether a seat is deep enough to hold a stone — each
# needs sourced professional evidence this project does not have.
SETTING_HEAD_PARAMETERS_COMPLETE = "JM-SETTING-005"
SETTING_FIELD_APPLICABLE = "JM-SETTING-006"
SETTING_SEAT_FEASIBLE = "JM-SETTING-007"

MANUFACTURING_MIN_FEATURE = "JM-MANUFACTURING-001"

GEOMETRY_OUTER_BAND_POSITIVE = "JM-GEOMETRY-001"

# Sprint 21 — GEM_IDENTITY_ONLY. Every one is a REFERENTIAL or COHERENCE
# invariant: does the referenced entry exist, is the declared state
# self-consistent, does the profile resolve.
#
# NONE is a gemological or manufacturing claim. There is deliberately no rule
# about hardness, durability, heat sensitivity, setting suitability or treatment
# safety, because every one of those needs evidence this project does not have
# (GEM-GOV-006, brief section 26).
GEM_REFERENCE_EXISTS = "JM-GEM-001"
GEM_ORIGIN_APPLICABLE = "JM-GEM-002"
GEM_CUSTOM_COHERENT = "JM-GEM-003"
GEM_VISUAL_PROFILE_RESOLVES = "JM-GEM-004"
GEM_TREATMENT_COHERENT = "JM-GEM-005"
GEM_ENTRY_DEPRECATED = "JM-GEM-006"

# Sprint 22 — ARRANGEMENT_ONLY. Every one is a STRUCTURAL or REFERENTIAL
# invariant of the declarative arrangement: do the referenced things exist, are
# the authoritative IDs unique, does the declared structure resolve.
#
# NONE is a jewelry or manufacturing claim. There is deliberately no rule about
# minimum stone spacing, accent-to-centre proportion, pave density or setting
# suitability, because each needs sourced professional evidence this project
# does not have. Whether two placed stones physically overlap is a GEOMETRIC
# fact, answerable only by Geometry Inspection once multi-stone geometry
# exists — not a threshold to invent here.
ARRANGEMENT_INSTANCE_IDS_UNIQUE = "JM-ARRANGE-001"
ARRANGEMENT_REFERENCES_RESOLVE = "JM-ARRANGE-002"
ARRANGEMENT_STONE_REFERENCE_RESOLVES = "JM-ARRANGE-003"
ARRANGEMENT_STRUCTURE_RESOLVES = "JM-ARRANGE-004"
ARRANGEMENT_ROLE_COHERENT = "JM-ARRANGE-005"
ARRANGEMENT_GENERATION_PARTIAL = "JM-ARRANGE-006"
