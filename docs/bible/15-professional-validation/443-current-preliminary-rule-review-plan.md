---
id: JM-BIBLE-443
title: Current Preliminary Rule Review Plan
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-PROVAL-README
  - JM-BIBLE-410
related_documents:
  - JM-BIBLE-419
  - JM-BIBLE-445
implementation_status: current
professional_validation: not_required
normative: false
---

# Current Preliminary Rule Review Plan

Every rule below is read directly from `specs/forge/v1/current-rule-registry.json` (real `ruleId`/`classification`/`professionalValidationStatus`) and `backend/jewelmind/validation/engine.py` (real rule statements). 21 rules total: 16 need eventual professional review, 5 do not.

## Rules needing professional review (16)

| Rule ID | Statement | Classification | Reviewer role | Priority | Evidence types | Boundary case |
|---|---|---|---|---|---|---|
| JM-RING-001 | Ring inner diameter must fall within a plausible range. | PROTOTYPE_HEURISTIC | JEWELRY_CAD_DESIGNER | Medium | LIVE_SOFTWARE_OBSERVATION, MEASUREMENT | Values just inside/outside the current range. |
| JM-RING-002 | Ring size (EU) must fall within a plausible range. | PROTOTYPE_HEURISTIC | JEWELRY_CAD_DESIGNER | Medium | MEASUREMENT | Smallest/largest supported EU size. |
| JM-RING-003 | Ring size and inner diameter must be mutually consistent. | SEMANTIC_COMPATIBILITY | JEWELRY_CAD_DESIGNER | Low | LIVE_SOFTWARE_OBSERVATION | A size/diameter pair near the tolerance edge. |
| JM-BAND-001 | Band width must be at least 1.5mm. | PROTOTYPE_HEURISTIC | GOLDSMITH_BENCH_JEWELER | High | DIRECT_PHYSICAL, PROFESSIONAL_EXPERIENCE | 1.5mm and just below. |
| JM-BAND-002 | Band thickness must be at least a minimum value. | PROTOTYPE_HEURISTIC | GOLDSMITH_BENCH_JEWELER | High | DIRECT_PHYSICAL, PROFESSIONAL_EXPERIENCE | The minimum thickness and just below. |
| JM-BAND-003 | Band width must not exceed 12mm. | PROTOTYPE_HEURISTIC | JEWELRY_CAD_DESIGNER | Medium | LIVE_SOFTWARE_OBSERVATION | 12mm and just above. |
| JM-STONE-001 | Stone diameter must fall within 2–15mm. | PROTOTYPE_HEURISTIC | GEMOLOGIST | Medium | MEASUREMENT, REFERENCE_DOCUMENT | 2mm and 15mm exactly. |
| JM-STONE-002 | Stone depth must be greater than 0.5mm and less than stone diameter. | DOMAIN_INVARIANT | GEMOLOGIST | Medium | MEASUREMENT | Depth just above 0.5mm; depth near the diameter itself. |
| JM-PRONG-001 | Prong count must be 4 or 6. | PROTOTYPE_HEURISTIC | STONE_SETTER | High | PROFESSIONAL_EXPERIENCE, STONE_SETTING_TEST | Any other prong count (already schema-permitted to attempt, Forge-blocked). |
| JM-PRONG-002 | Prong diameter must meet a minimum. | PROTOTYPE_HEURISTIC | STONE_SETTER, CASTING_SPECIALIST | High | DIRECT_PHYSICAL, CAST_SAMPLE | The minimum diameter and just below. |
| JM-PRONG-003 | 4 prongs are blocked when stone diameter exceeds 8mm. | PROTOTYPE_HEURISTIC | STONE_SETTER | High (Priority 1 target, see [`444`](444-current-solitaire-review-plan.md)) | STONE_SETTING_TEST, PROFESSIONAL_EXPERIENCE | Exactly 8.0mm and 8.1mm, both prong counts. |
| JM-PRONG-004 | Prong height must be compatible with basket height. | SEMANTIC_COMPATIBILITY | JEWELRY_CAD_DESIGNER, STONE_SETTER | Medium | LIVE_SOFTWARE_OBSERVATION | A prong/basket height pair near the compatibility boundary. |
| JM-SETTING-001 | Basket height must be positive. | GEOMETRY_PRECONDITION | JEWELRY_CAD_DESIGNER | Low | LIVE_SOFTWARE_OBSERVATION | Values near zero. |
| JM-SETTING-002 | Basket height must not exceed a maximum. | PROTOTYPE_HEURISTIC | JEWELRY_CAD_DESIGNER, GOLDSMITH_BENCH_JEWELER | Medium | LIVE_SOFTWARE_OBSERVATION | The maximum and just above. |
| JM-MANUFACTURING-001 | A minimum feature-size context applies specifically under direct resin printing. | MANUFACTURING_CONTEXT | RESIN_PRINTING_SPECIALIST | Medium | PHYSICAL_PRINT, MANUFACTURER_GUIDANCE | The minimum feature size and just below, printed physically. |
| JM-GEOMETRY-001 | Outer band radius must remain positive relative to inner geometry. | GEOMETRY_PRECONDITION | JEWELRY_CAD_DESIGNER | Low | LIVE_SOFTWARE_OBSERVATION | Values near the zero-crossing. |

## Rules NOT needing professional review (5)

| Rule ID | Classification | Why no professional review is needed |
|---|---|---|
| FORGE-SCHEMA-001 | SCHEMA_INTEGRITY | Enforces the JDL schema version literal — a software compatibility check, not a jewelry judgment call. |
| FORGE-SAFETY-001 | SYSTEM_SAFETY | Rejects non-finite floats (`inf`/`NaN`) — a numerical-safety precondition for the CAD kernel, not a domain question. |
| FORGE-SAFETY-002 | SYSTEM_SAFETY | Rejects unknown/extra fields (`extra="forbid"`) — a data-integrity check, not a domain question. |
| FORGE-GEOM-001 | GEOMETRY_INSPECTION | Confirms the metal body is a single fused solid — a topological fact about the CAD output, verifiable by software alone. |
| FORGE-EXPORT-001 | EXPORT_PRECONDITION | Confirms a model exists before allowing an export — a precondition check, not a domain question. |

## Priority order, restated

Per [`444-current-solitaire-review-plan.md`](444-current-solitaire-review-plan.md)/the original brief's section 63: setting/prong/basket rules (`JM-PRONG-*`, `JM-SETTING-*`) are Priority 1–2, band geometry (`JM-BAND-*`) is Priority 3, and the remaining preliminary Forge thresholds are Priority 5 — do not send every rule to a reviewer at once; start where the current geometry is most simplified.

## Cross-references

- [`419-rule-validation-process.md`](419-rule-validation-process.md) — how one of these rules is actually reviewed once a reviewer is assigned.
- [`445-professional-validation-register.md`](445-professional-validation-register.md) — where the resulting `ValidationRecord` would eventually live.
- `docs/bible/appendices/professional-rule-review-matrix.md` — the compact table-only version of this same content.
