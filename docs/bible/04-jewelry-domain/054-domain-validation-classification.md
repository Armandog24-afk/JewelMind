---
id: JM-BIBLE-054
title: Domain Validation Classification
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-040
related_documents:
  - JM-BIBLE-053
  - JM-BIBLE-058
  - JM-BIBLE-093
implementation_status: current
professional_validation: preliminary
---

# Domain Validation Classification

**Relationship to Forge (Sprint 4):** [`06-forge/093-rule-classification-model.md`](../06-forge/093-rule-classification-model.md) reclassifies these same sixteen rules (plus five newly-named cross-cutting rules) into Forge's eleven-category system (`SCHEMA_INTEGRITY`, `SEMANTIC_COMPATIBILITY`, `DOMAIN_INVARIANT`, `PROTOTYPE_HEURISTIC`, etc.) and adds a formal provenance, lifecycle, and evaluation-stage model around them. This document remains authoritative for the schema-integrity/geometry-feasibility/prototype-safety/professional-validation classification below; Forge is authoritative for the rule *system's* architecture built on top of it.

> **Implemented validation is not equivalent to professional
> manufacturability certification.** Every rule below is, at most, a
> PRELIMINARY SOFTWARE RULE (see
> [`040-domain-governance.md`](040-domain-governance.md)) unless its
> "Professional-validation status" column says otherwise — and as of
> this Sprint, none do.

Every one of the sixteen rules currently in
`backend/jewelmind/validation/engine.py` is classified below, using the
categories from this Sprint's instructions: **schema integrity**,
**geometry feasibility**, **prototype safety heuristic**,
**user-consistency check**, **manufacturing-context heuristic**,
**professional rule candidate**.

| Rule ID | Behavior | Severity | Parameter | Code | Test | Classification | Provenance | Professional-validation status | Risk if wrong | Future action |
|---|---|---|---|---|---|---|---|---|---|---|
| `JM-RING-001` | Inner diameter must be strictly between 10mm and 30mm. | error | `ring.innerDiameter` | `validation/engine.py::_ring_rules` | `test_validation.py::test_ring_inner_diameter_out_of_range_is_error` | geometry feasibility | Engineering guess at a plausible human-finger range | preliminary | Degenerate/implausible ring geometry at the extremes; low real-world harm, mostly a sanity bound | Confirm bounds with a professional; consider whether bounds should vary by intended wearer population |
| `JM-RING-002` | EU size must be strictly between 1 and 50. | error | `ring.size` | `validation/engine.py::_ring_rules` | `test_validation.py::test_ring_size_out_of_range_is_error` | schema integrity | Range matching the EU/French sizing formula's plausible domain | preliminary | Labeling/cosmetic only — size is metadata about diameter, not itself geometry-driving | Confirm real-world EU size range in use |
| `JM-RING-003` | Size and inner diameter are cross-checked for consistency (`size = π·diameter − 40`); mismatch beyond a threshold is flagged, never auto-corrected. | information/warning | `ring.innerDiameter` | `validation/engine.py::_ring_rules`, `validation/sizing.py` | `test_validation.py::test_ring_size_diameter_inconsistency_flagged` | user-consistency check | EU/French civil sizing convention, threshold values chosen for this prototype | preliminary | If ignored, a ring could be produced at the wrong actual size while the label looks fine | Confirm the EU/French formula and thresholds with a professional; document other sizing systems (see [`057-open-domain-questions.md`](057-open-domain-questions.md)) |
| `JM-BAND-001` | Band width below 1.5mm is an error. | error | `band.width` | `validation/engine.py::_band_rules` | `test_validation.py::test_band_width_below_min_is_error` | prototype safety heuristic | Engineering guess at a minimum plausible width | preliminary | Structurally fragile or unmanufacturable band if the real minimum is different | Seek a professionally validated minimum band width |
| `JM-BAND-002` | Band thickness below 1.4mm is an error; 1.4–1.6mm is a warning. | error/warning | `band.thickness` | `validation/engine.py::_band_rules` | `test_validation.py::test_band_thickness_below_min_is_error`, `test_band_thickness_warning_band` | prototype safety heuristic | Engineering guess at minimum structural thickness | preliminary | Same as JM-BAND-001 | Same as JM-BAND-001 |
| `JM-BAND-003` | Band width above 12mm is a warning. | warning | `band.width` | `validation/engine.py::_band_rules` | `test_validation.py::test_band_width_above_max_is_warning_not_error` | user-consistency check | Guess at an unusually wide band for a solitaire | preliminary | Cosmetic only — never blocks | Confirm whether 12mm is a meaningful boundary for any real solitaire convention |
| `JM-STONE-001` | Stone diameter must be between 2mm and 15mm. | error | `stone.diameter` | `validation/engine.py::_stone_rules` | `test_validation.py::test_stone_diameter_out_of_range_is_error` | geometry feasibility | Engineering guess at a plausible reference-stone size range | preliminary | Degenerate stone-reference geometry outside range | Confirm range against real solitaire stone size distributions |
| `JM-STONE-002` | Stone depth must be greater than 0.5mm and less than the diameter. | error | `stone.depth` | `validation/engine.py::_stone_rules` | `test_validation.py::test_stone_depth_must_be_less_than_diameter` | geometry feasibility | Geometric plausibility bound (a depth ≥ diameter would not resemble a brilliant-style proportion at all) | preliminary | Degenerate stone-reference loft | Confirm proportion bound against real depth/diameter ratios |
| `JM-PRONG-001` | Prong count must be exactly 4 or 6. | error | `setting.prongCount` | `validation/engine.py::_prong_rules` | `test_validation.py::test_prong_count_invalid_is_error` | geometry feasibility | `build_prongs()` only supports 4 or 6 by construction | preliminary (as a jewelry rule); IMPLEMENTED FACT (as a code constraint) | Unsupported geometry request if bypassed | None — this matches current code capability exactly; revisit only if more counts are implemented |
| `JM-PRONG-002` | Prong diameter below 0.8mm is an error; 0.8–1.0mm is a warning. | error/warning | `setting.prongDiameter` | `validation/engine.py::_prong_rules` | `test_validation.py::test_prong_diameter_below_min_is_error`, `test_prong_diameter_warning_band` | prototype safety heuristic | Engineering guess at minimum structural prong diameter | preliminary | Fragile prongs if the real minimum differs | Seek a professionally validated minimum prong diameter |
| `JM-PRONG-003` | Stone diameter above 8mm with 4 prongs produces a warning recommending 6. | warning | `setting.prongCount` | `validation/engine.py::_prong_rules` | `test_validation.py::test_large_stone_with_four_prongs_warns` | professional rule candidate | General jewelry-setting tendency (larger stones often set with more prongs), not a validated threshold | preliminary | If ignored, a large stone on 4 prongs may be less secure — a genuine real-world concern behind an unvalidated number | High priority for professional review — see [`058-professional-validation-register.md`](058-professional-validation-register.md) |
| `JM-PRONG-004` | Prong height must exceed basket height. | error | `setting.prongHeight` | `validation/engine.py::_prong_rules` | `test_validation.py::test_prong_height_must_exceed_basket_height` | geometry feasibility | Pure geometric plausibility (a prong shorter than the basket it rises from would not visually clear it) | preliminary | Geometrically implausible assembly | None — this is closer to an IMPLEMENTED FACT about the current geometry's requirements than a jewelry-domain rule |
| `JM-SETTING-001` | Basket height must be positive. | error | `setting.basketHeight` | `validation/engine.py::_setting_rules` | `test_validation.py::test_basket_height_must_be_positive` | geometry feasibility | A non-positive extrusion height is geometrically invalid | preliminary | Degenerate/invalid basket geometry if bypassed | None — this is an IMPLEMENTED FACT about CadQuery extrusion requirements |
| `JM-SETTING-002` | Basket height above 8mm is a warning. | warning | `setting.basketHeight` | `validation/engine.py::_setting_rules` | `test_validation.py::test_basket_height_above_max_warns` | user-consistency check | Guess at an unusually tall basket | preliminary | Cosmetic only | Confirm 8mm against real basket height conventions |
| `JM-MANUFACTURING-001` | For direct resin printing, band thickness/width below 0.8mm produce a warning. | warning | `band.thickness`, `band.width` | `validation/engine.py::_manufacturing_rules` | `test_validation.py::test_direct_resin_printing_thin_feature_warns` | manufacturing-context heuristic | Generic minimum-feature-size guess for resin printing, not tied to a specific printer/resin | preliminary | If ignored, a print attempt may fail to resolve the feature | High priority for professional/process-specific review |
| `JM-GEOMETRY-001` | Rejects any combination producing a non-positive outer band dimension. | error | `band.thickness`, `band.width` | `validation/engine.py::_geometry_rules` | `test_validation.py::test_geometry_rejects_non_positive_outer_band` | geometry feasibility | Defense-in-depth: a non-positive outer dimension cannot produce a valid solid regardless of other rules | preliminary (though effectively an IMPLEMENTED FACT about CadQuery's requirements) | Crash or degenerate geometry if bypassed | None — this is a computational safety net, not a jewelry-domain claim |

## Summary counts

- **16** total current rules.
- **0** professionally validated rules.
- **2** flagged as high-priority professional-review candidates:
  `JM-PRONG-003` and `JM-MANUFACTURING-001` — both encode genuine
  real-world jewelry/manufacturing concerns behind numbers that have
  never been reviewed by an identified professional.
- The remaining 14 are either geometric-feasibility guards (protecting
  CadQuery from degenerate input) or cosmetic/consistency checks with low
  real-world risk if the specific threshold turns out to be imprecise.

See [`058-professional-validation-register.md`](058-professional-validation-register.md)
for the (currently empty) register these rules would be entered into
once reviewed.
