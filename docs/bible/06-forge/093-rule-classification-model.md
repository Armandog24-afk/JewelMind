---
id: JM-BIBLE-093
title: Rule Classification Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-092
related_documents:
  - JM-BIBLE-A14
implementation_status: current
professional_validation: not_required
normative: true
---

# Rule Classification Model

## The 11 categories

| Category | Meaning |
|---|---|
| `SCHEMA_INTEGRITY` | Enforces type/literal/structural correctness (the JDL-SCHEMA / structural validation layer) |
| `SEMANTIC_COMPATIBILITY` | Enforces internal consistency between two or more fields, independent of any single numeric threshold |
| `DOMAIN_INVARIANT` | Enforces a relationship that must always hold for the current jewelry model to make geometric/domain sense, without being an arbitrarily-chosen numeric threshold |
| `GEOMETRY_PRECONDITION` | Must pass before geometry construction can produce a valid solid |
| `GEOMETRY_INSPECTION` | Evaluated against the actual generated geometry, after construction |
| `PROTOTYPE_HEURISTIC` | A numeric threshold chosen for prototype safety or plausibility, not yet professionally validated |
| `MANUFACTURING_CONTEXT` | A rule whose applicability or verdict depends on the selected manufacturing method |
| `EXPORT_PRECONDITION` | Must pass before an artifact (STEP/STL/JSON/specification) can be exported |
| `PROFESSIONAL_CANDIDATE` | Proposed by a human or (in the future) AI, not yet evaluated |
| `PROFESSIONALLY_VALIDATED` | Reviewed and accepted by an identified, qualified jewelry professional |
| `SYSTEM_SAFETY` | Protects the system itself (no NaN/Infinity, no unknown fields) rather than encoding jewelry-domain knowledge |

## Every current rule, reclassified

| Rule ID | Category | Why |
|---|---|---|
| `JM-RING-001` | `PROTOTYPE_HEURISTIC` | The 10–30mm range was chosen for prototype plausibility, not derived from a cited standard |
| `JM-RING-002` | `PROTOTYPE_HEURISTIC` | Same reasoning for the 1–50 size range |
| `JM-RING-003` | `SEMANTIC_COMPATIBILITY` | Cross-checks `ring.size` against `ring.innerDiameter` for internal consistency |
| `JM-BAND-001` | `PROTOTYPE_HEURISTIC` | 1.5mm minimum width is a prototype safety floor |
| `JM-BAND-002` | `PROTOTYPE_HEURISTIC` | 1.4mm/1.6mm thickness floors, same reasoning |
| `JM-BAND-003` | `PROTOTYPE_HEURISTIC` | 12mm "unusually wide" ceiling, same reasoning |
| `JM-STONE-001` | `PROTOTYPE_HEURISTIC` | 2–15mm diameter range, same reasoning |
| `JM-STONE-002` | `DOMAIN_INVARIANT` | A stone's depth exceeding its own diameter is geometrically implausible for this model's lofted approximation, independent of the exact 0.5mm floor |
| `JM-PRONG-001` | `PROTOTYPE_HEURISTIC` | The `{4, 6}` set reflects what the current prong builder supports, not an industry rule |
| `JM-PRONG-002` | `PROTOTYPE_HEURISTIC` | 0.8mm/1.0mm diameter floors |
| `JM-PRONG-003` | `PROTOTYPE_HEURISTIC` | 8mm stone-size advisory threshold |
| `JM-PRONG-004` | `SEMANTIC_COMPATIBILITY` | Cross-checks `prongHeight` against `basketHeight` |
| `JM-SETTING-001` | `GEOMETRY_PRECONDITION` | A non-positive basket height cannot be constructed into a solid |
| `JM-SETTING-002` | `PROTOTYPE_HEURISTIC` | 8mm "unusually tall" ceiling |
| `JM-MANUFACTURING-001` | `MANUFACTURING_CONTEXT` | Only applies when `manufacturing.method == "direct_resin_printing"` |
| `JM-GEOMETRY-001` | `GEOMETRY_PRECONDITION` | Band construction requires a positive outer-minus-inner dimension and positive width |
| `FORGE-SCHEMA-001` | `SCHEMA_INTEGRITY` | `schemaVersion` literal match |
| `FORGE-SAFETY-001` | `SYSTEM_SAFETY` | No NaN/Infinity in any numeric field |
| `FORGE-SAFETY-002` | `SYSTEM_SAFETY` | No unknown fields accepted |
| `FORGE-GEOM-001` | `GEOMETRY_INSPECTION` | Runs after geometry generation, against the actual fused/compound result |
| `FORGE-EXPORT-001` | `EXPORT_PRECONDITION` | A cached, error-free `ModelRecord` must exist before export |

**Zero rules are currently `PROFESSIONAL_CANDIDATE` or `PROFESSIONALLY_VALIDATED`** — no candidate has been proposed and no professional review has occurred (see [`103-professional-validation-lifecycle.md`](103-professional-validation-lifecycle.md)). This is the honest current state, not a gap in this classification exercise.

## Category vs. professional-validation status

These are independent axes (per Sprint 2's precedent in [`04-jewelry-domain/040-domain-governance.md`](../04-jewelry-domain/040-domain-governance.md) rule 9): a rule's `category` describes *what kind of check it is*; `professionalValidationStatus` describes *how much confidence a qualified human has given its exact threshold*. A `PROTOTYPE_HEURISTIC` rule and a future `PROFESSIONALLY_VALIDATED` rule can check the exact same field — the category can even change over time (a `PROTOTYPE_HEURISTIC` that later gets professionally reviewed and accepted becomes a `PROFESSIONALLY_VALIDATED` rule, a MAJOR version change per [`108-rule-versioning.md`](108-rule-versioning.md)).
