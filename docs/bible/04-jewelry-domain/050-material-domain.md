---
id: JM-BIBLE-050
title: Material Domain
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on:
  - JM-BIBLE-044
related_documents:
  - JM-BIBLE-051
  - JM-BIBLE-054
implementation_status: current
professional_validation: preliminary
---

# Material Domain

## Current materials (metadata only)

`domain/schema.py::MaterialSpec.metal` accepts exactly five values:
`yellow_gold_18k`, `white_gold_18k`, `rose_gold_18k`, `platinum`,
`silver`.

## CURRENT — what material selection actually does

- Affects `GenerateResponse`/`JewelryDefinition` **metadata** — it is
  stored and exported (JSON, specification) faithfully.
- Affects **preview appearance only** —
  `frontend/src/components/ModelViewport.tsx`'s `METAL_COLORS` map picks
  a display color per metal value; this is a rendering choice, not a
  geometric or physical simulation.
- May affect **preliminary validation context** — `JM-MANUFACTURING-001`
  keys off `manufacturing.method`, not `material.metal`, so material
  choice today does not itself trigger any validation rule (see
  [`054-domain-validation-classification.md`](054-domain-validation-classification.md)
  for the full rule list and confirm none reference `material.metal`).
- **Current geometry does not adapt to material properties at all** —
  the same `band.width`/`thickness` produces the identical solid
  regardless of whether `yellow_gold_18k` or `silver` is selected.
- **Current exports do not guarantee alloy-specific manufacturing
  compensation** — no shrinkage, density, or alloy-specific tolerance is
  applied anywhere in the STEP/STL export pipeline.

## PLANNED (no values invented)

None of the following exist in code, and no numeric value for any of
them is stated here, per
[`040-domain-governance.md`](040-domain-governance.md):

| Concept | Status |
|---|---|
| Density (per alloy) | PLANNED |
| Estimated weight (derived from volume × density) | PLANNED |
| Alloy variation (e.g. different 18k yellow gold alloy recipes) | PLANNED |
| Casting shrinkage context | PLANNED |
| Structural rule profiles (material-specific minimum feature sizes) | PLANNED |
| Cost calculation | VISION |
| Finishing allowances | PLANNED |

## Material-data provenance model (for future use)

When any of the PLANNED concepts above is eventually implemented, each
material-derived numeric value should be recorded with the following
provenance fields — not as a bare number:

| Field | Purpose |
|---|---|
| `value` | The number itself. |
| `unit` | Explicit unit (e.g. `g/cm³` for density). |
| `alloy` | Which specific alloy the value applies to (18k yellow gold is not one universal alloy). |
| `source` | Where the value came from (a named reference, standard, or professional). |
| `jurisdiction_or_standard` | Whether the value is tied to a specific regional hallmarking/purity standard. |
| `date` | When the value was recorded. |
| `professional_reviewer` | Who validated it, if anyone — see [`058-professional-validation-register.md`](058-professional-validation-register.md). |
| `confidence` | An explicit statement of how certain the value is (e.g. "manufacturer datasheet" vs. "rough estimate"). |
| `version` | So a later correction can be tracked rather than silently overwriting history. |

This structure exists precisely so that when density or shrinkage values
are eventually added, they arrive with enough context to distinguish an
IMPLEMENTED FACT (a real datasheet value) from a PRELIMINARY SOFTWARE
RULE (an engineering guess) — see
[`040-domain-governance.md`](040-domain-governance.md)'s classification
table.

## Explicit non-invention statement

This document does not state a density, a shrinkage percentage, or a
price for any metal — doing so without a verifiable source would violate
[`040-domain-governance.md`](040-domain-governance.md)'s "no invented
measurements" rule. Any such value needed for a future feature must
first be logged as an open question
([`057-open-domain-questions.md`](057-open-domain-questions.md)) and
resolved through the provenance model above, not authored directly into
a Bible document.
