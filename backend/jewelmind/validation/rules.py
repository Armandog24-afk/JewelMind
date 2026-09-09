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

# Sprint 24 — FAMILY_ONLY. Structural and referential checks on a multi-stone
# family: does the document declare one authority or two, do the roles match
# the family's own rules, does the family compile, and do its references
# resolve.
#
# NONE is a professional or jewelry claim. There is deliberately no rule about
# centre-to-accent proportion, minimum stone spacing, whether a cluster is
# settable, or how many stones a design should carry — each needs sourced
# professional evidence this project does not have. Whether two placed stones
# overlap is a GEOMETRIC fact for Geometry Inspection.
FAMILY_SINGLE_PLACEMENT_AUTHORITY = "JM-FAMILY-001"
FAMILY_ROLES_VALID = "JM-FAMILY-002"
FAMILY_COMPILES = "JM-FAMILY-003"
FAMILY_REFERENCES_RESOLVE = "JM-FAMILY-004"
FAMILY_SETTING_COVERAGE = "JM-FAMILY-005"

# Sprint 25 — HALO_ONLY. Structural and referential checks on a halo: does the
# centre it names exist, does it compose, is the family/halo combination one the
# real compiler supports, do its stone and setting references resolve, and what
# does a composed halo NOT get.
#
# NONE is a professional or jewelry claim. There is deliberately no rule about
# minimum halo stone spacing, a centre-to-halo proportion, a settable radius, or
# whether a hidden halo clears the centre stone's pavilion — each needs sourced
# professional evidence this project does not have. Whether two placed stones
# overlap is a GEOMETRIC fact for Geometry Inspection.
HALO_CENTER_RESOLVES = "JM-HALO-001"
HALO_COMPOSES = "JM-HALO-002"
HALO_COMPOSITION_SUPPORTED = "JM-HALO-003"
HALO_REFERENCES_RESOLVE = "JM-HALO-004"
HALO_SETTING_COVERAGE = "JM-HALO-005"

# Sprint 26 — PAVE_ONLY. Structural, referential and MATHEMATICAL checks on a
# pavé or microsetting field: does its host surface resolve for this design,
# does the field compile, did it lose cells to the surface edge, do its
# references resolve, is the requested pitch geometrically consistent with the
# stones it must carry, and what does a compiled field NOT include.
#
# JM-PAVE-006 is the only numeric one, and it is a MATHEMATICAL CONSTRAINT
# rather than a professional threshold: two stones whose footprints are wider
# than the pitch between them overlap as a matter of arithmetic, whatever a
# setter would say about it. There is deliberately NO minimum pavé spacing, no
# minimum bead diameter, no maximum density and no settable seat depth — each
# needs sourced professional evidence this project does not have, and the
# Sprint 26 brief prohibits inventing them.
PAVE_HOST_RESOLVES = "JM-PAVE-001"
PAVE_COMPILES = "JM-PAVE-002"
PAVE_FIELD_CONTAINMENT = "JM-PAVE-003"
PAVE_REFERENCES_RESOLVE = "JM-PAVE-004"
PAVE_EXECUTION_BOUNDARY = "JM-PAVE-005"
PAVE_PITCH_CONSISTENCY = "JM-PAVE-006"

# Sprint 27 — EXTENDED_SETTING_MODES. Structural, referential and MATHEMATICAL
# checks on a declared setting mode: does the mode belong to the family the
# document chose, are the parameters it needs present, are the ones it does not
# read reported, is the request geometrically possible, and does the mode carry
# an honest status or a review requirement.
#
# NOT ONE OF THEM IS A PROFESSIONAL JUDGMENT. There is deliberately no rule
# about whether a channel wall is thick enough, whether a bar spacing is
# settable, whether a flush collar leaves enough metal, or whether a tension
# setting would hold. Each of those needs sourced professional evidence this
# project does not have (SETTING-GOV-010).
#
# JM-SETTING-011 is the only numeric one and it is a MATHEMATICAL CONSTRAINT: a
# collar rim taller than the whole stone buries it, and two supports reaching
# further inward than the stone's half-extent meet through its middle. Both are
# arithmetic, whatever a setter would say. It is a NECESSARY condition checked
# against the document's own requested dimensions; the SUFFICIENT check runs at
# generation time against the real measured stone, because only the built solid
# knows its own crown height.
#
# JM-SETTING-012 carries the brief's PROFESSIONAL REVIEW category. It is emitted
# as a `warning` rather than a fourth severity: the three severities are a
# published contract, and the rule's own registry entry records
# `professionalValidationStatus: required`, which is where that distinction
# already lives.
SETTING_MODE_FAMILY_MATCHES = "JM-SETTING-008"
SETTING_MODE_PARAMETER_APPLICABLE = "JM-SETTING-009"
SETTING_MODE_REQUIREMENTS_MET = "JM-SETTING-010"
SETTING_MODE_GEOMETRY_FEASIBLE = "JM-SETTING-011"
SETTING_MODE_PROFESSIONAL_REVIEW = "JM-SETTING-012"
SETTING_MODE_STATUS = "JM-SETTING-013"
