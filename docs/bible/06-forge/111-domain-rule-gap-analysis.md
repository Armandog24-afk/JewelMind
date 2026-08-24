---
id: JM-BIBLE-111
title: Domain Rule Gap Analysis
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-110
related_documents:
  - JM-BIBLE-057
implementation_status: current
professional_validation: not_required
normative: false
---

# Domain Rule Gap Analysis

Comparing the 21 rules in [`110-current-rule-inventory.md`](110-current-rule-inventory.md) against the jewelry-domain model established in Sprint 2 ([`04-jewelry-domain/`](../04-jewelry-domain/README.md)). **No thresholds are proposed for any gap below** — only the gap itself, why it matters, and what it would take to close responsibly.

| Gap ID | Domain area | Why it matters | Risk if unaddressed | Required expert | Priority | Implementation dependency | Professional-validation requirement |
|---|---|---|---|---|---|---|---|
| `FORGE-GAP-001` | Prong-to-stone contact | Current prongs are plain cylinders (per [`04-jewelry-domain/048-prong-domain.md`](../04-jewelry-domain/048-prong-domain.md)) with no modeled bearing/seat; there is no rule checking whether a prong actually contacts the stone reference at a plausible point | A generated model could look plausible in preview while being unmanufacturable as drawn | Bench jeweler / setter | Medium | Requires prong geometry to model a seat cut first (Sprint 5, Atlas) | required |
| `FORGE-GAP-002` | Stone seat | No concept of a "seat" (the cut surface a stone rests in) exists in geometry or validation | Same as above — a seatless prong cannot actually hold a stone in reality | Bench jeweler / setter | Medium | Geometry precondition first | required |
| `FORGE-GAP-003` | Shoulder transition | Ring anatomy documents "shoulders" as NOT IMPLEMENTED (see [`04-jewelry-domain/043-ring-anatomy.md`](../04-jewelry-domain/043-ring-anatomy.md)); no rule can exist for a component that doesn't exist | N/A until shoulders are implemented | Jewelry designer | Low (blocked on geometry) | Requires shoulder geometry first | not_required (until implemented) |
| `FORGE-GAP-004` | Basket connection quality | `FORGE-GEOM-001` checks only that *a* fuse succeeded or fell back to a compound — it does not check whether the basket-to-band connection is structurally sound (e.g. minimum contact area) | A "successful" fuse could still be structurally marginal | Bench jeweler / CAD engineer | Medium | Requires a defined minimum-contact-area concept, currently undefined | required |
| `FORGE-GAP-005` | Local wall thickness | No rule checks minimum wall thickness anywhere except at the parameter level (`band.thickness`, `prongDiameter`) — no check on the *resulting geometry's* thinnest point after fusion | A geometrically valid parameter combination could still fuse into a locally thin, fragile region | Manufacturing engineer | High | Requires a mesh/solid thickness-analysis capability not present in `geometry/` today | required |
| `FORGE-GAP-006` | Material-specific rules | `material.metal` has zero validation rules; different alloys have different real-world strength/ductility, unmodeled | A thin feature acceptable in platinum might not be in a softer alloy, or vice versa — currently unmodeled entirely | Metallurgist / bench jeweler | Medium | Requires per-metal parameter data, not currently in the schema | required |
| `FORGE-GAP-007` | Manufacturing-specific rules beyond the one current threshold | Only one manufacturing-context rule exists (`JM-MANUFACTURING-001`); casting has no dedicated rules at all today (see [`104-manufacturing-profile-rules.md`](104-manufacturing-profile-rules.md)) | Casting-specific failure modes (e.g. wax-pattern fragility, vent placement) are entirely unaddressed | Casting specialist | Medium | Requires casting-domain knowledge not currently in this codebase | required |
| `FORGE-GAP-008` | Setting accessibility | No rule checks whether the modeled prong/basket geometry would actually be reachable by a setter's tools | Same underlying risk as GAP-001/002 | Bench jeweler / setter | Low | Requires a defined accessibility/clearance concept | required |
| `FORGE-GAP-009` | Polishing accessibility | No rule checks whether generated geometry has unreachable internal surfaces that couldn't be polished | Same category of risk as GAP-008 | Bench jeweler / polisher | Low | Same | required |
| `FORGE-GAP-010` | Stone clearance | No rule checks clearance between the stone reference and surrounding metal beyond the girdle-radius approximation already in `geometry/constants.py::prong_center_radius()` | A tight-but-schema-valid combination could produce visually or physically implausible stone/metal proximity | Bench jeweler / gemologist | Medium | Requires a defined clearance concept | required |
| `FORGE-GAP-011` | Multiple-component connectivity | No rule verifies the full assembly forms one connected structure beyond the single fuse-or-compound check in `FORGE-GEOM-001` | An edge-case parameter combination could in principle produce a disconnected basket or prong that only the compound fallback would silently mask | CAD engineer | Medium | Requires connectivity analysis, not present today | not_required (a software-correctness question, not a jewelry-domain one) |
| `FORGE-GAP-012` | Printability (beyond the one existing threshold) | `JM-MANUFACTURING-001` only checks a flat 0.8mm floor on two fields; real resin-printing printability also depends on overhang angles, support requirements, and orientation, none of which are modeled | A definition could pass the current rule and still be difficult or impossible to print reliably | 3D-printing/resin specialist | Medium | Requires geometry-orientation-aware analysis not present today | required |
| `FORGE-GAP-013` | Casting considerations (sprue/vent placement, shrinkage) | No shrinkage or casting-process rule exists at all, and LAW-forbidding invented values means none can be added without a real source | Real cast pieces will differ dimensionally from the CAD model in ways this system does not currently predict or warn about | Casting specialist | Medium | Requires a professionally-sourced shrinkage figure — explicitly not to be invented (see [`04-jewelry-domain/040-domain-governance.md`](../04-jewelry-domain/040-domain-governance.md)) | required |
| `FORGE-GAP-014` | Ring sizing standards beyond EU | Only the EU/French sizing convention is implemented (`RingSizeSystem = Literal["EU"]`); no US/UK/JP/other system exists, so no rule can validate cross-system consistency | International customers are entirely unserved by any sizing cross-check | Jewelry sizing specialist | Low (blocked on JDL schema extension) | Requires a new `RingSizeSystem` enum member first, a JDL schema change | not_required (until implemented) |

## Summary

14 gaps identified, spanning geometry-precondition territory not yet modeled (GAP-001, 002, 004, 005, 008–011), manufacturing/material territory (GAP-006, 007, 012, 013), and JDL-schema-blocked territory (GAP-003, 014). **Every gap requiring a numeric threshold to close is marked `professional-validation requirement: required`** — none may be filled by an invented number, consistent with this Sprint's explicit governing instruction.
