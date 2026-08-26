---
id: JM-BIBLE-094
title: Rule Provenance Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-092
related_documents:
  - JM-BIBLE-A15
implementation_status: current
professional_validation: not_required
normative: true
---

# Rule Provenance Model

Every rule must declare where it comes from. Provenance is a separate axis from severity, category, and professional-validation status.

## Provenance types

| Type | Meaning |
|---|---|
| `implementation_necessity` | Required for the geometry builder or system to function at all (e.g. a non-positive dimension cannot become a solid) |
| `mathematical_constraint` | A real, named formula or geometric relationship (e.g. the EU/French ring-sizing conversion) |
| `geometry_engine_constraint` | A fact about how the CAD kernel (OpenCascade/CadQuery) behaves |
| `prototype_heuristic` | Chosen by the original implementer for prototype safety or plausibility, with no external citation |
| `professional_review` | Reviewed and stated by an identified, qualified jewelry professional |
| `published_technical_reference` | Drawn from a citable published source (a book, standard, or technical article) |
| `manufacturer_specification` | Drawn from a specific manufacturer's published tolerances or process documentation |
| `regulatory_or_standards_body` | Drawn from a jurisdictional or industry standards body |
| `experimental_observation` | Derived from observed test/production outcomes, not a citation |
| `migrated_legacy_rule` | Carried over from a prior system or prior JewelMind version without independent re-derivation |
| `unknown` | Provenance genuinely could not be determined |

## Provenance fields

`provenanceType`, `sourceTitle`, `sourceAuthor`, `sourceOrganization`, `sourceReference`, `sourceVersion`, `geographicScope`, `manufacturingScope`, `reviewer`, `reviewDate`, `confidence`, `notes` — see `specs/forge/v1/rule.schema.json`'s `Provenance` definition for the exact shape.

## No invented sources

Per this Sprint's explicit governing instruction, no source was invented for any current rule. `specs/forge/v1/test-vectors/provenance-vectors.json` assigns every one of the 21 current rules exactly one of `implementation_necessity`, `mathematical_constraint`, `geometry_engine_constraint`, or `prototype_heuristic` — **never** `professional_review`, `published_technical_reference`, `manufacturer_specification`, or `regulatory_or_standards_body`, because none of those provenances currently apply to anything in this codebase. See the summary table there:

| Provenance type | Count |
|---|---|
| `prototype_heuristic` | 11 |
| `implementation_necessity` | 6 |
| `mathematical_constraint` | 2 |
| `geometry_engine_constraint` | 2 |
| all others | 0 |

## Why `JM-RING-003` and `JM-STONE-002` are `mathematical_constraint`, not `prototype_heuristic`

`JM-RING-003` rests on a real, named sizing convention (`sizing.py`'s own docstring: "size = (pi × inner_diameter_mm) − 40, the common EU/French civil ring sizing convention"). `JM-STONE-002` rests on the geometric fact that a stone's depth cannot exceed its own diameter under the lofted round-brilliant approximation this codebase uses. In both cases, the *relationship* is a real mathematical/geometric fact — only the *exact tolerance threshold* deciding when to flag a discrepancy (0.15mm/0.5mm for `JM-RING-003`) is separately a prototype choice, noted in each rule's provenance `notes` field rather than changing the rule's overall `provenanceType`.

## Marking provenance UNKNOWN

If a future rule's origin genuinely cannot be determined (e.g. inherited from an external contribution with no accompanying rationale), it must be marked `unknown` rather than assigned a plausible-sounding but unverified type. No current rule requires this marking — every one of the 21 traces cleanly to either a code necessity, a named formula, or an acknowledged prototype choice.

## Relationship to Sprint 13

A rule's `provenanceType` here and its `professionalValidationStatus` (see [`110-current-rule-inventory.md`](110-current-rule-inventory.md)) are the inputs a real professional review, when it eventually happens, actually reviews — see [`15-professional-validation/README.md`](../15-professional-validation/README.md) and [`15-professional-validation/419-rule-validation-process.md`](../15-professional-validation/419-rule-validation-process.md) for the now-implemented structured workflow a rule's provenance and classification feed into. This document's own provenance model is unchanged by Sprint 13; it only gains a real downstream consumer.
