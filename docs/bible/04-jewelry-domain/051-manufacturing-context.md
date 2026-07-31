---
id: JM-BIBLE-051
title: Manufacturing Context
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on:
  - JM-BIBLE-044
related_documents:
  - JM-BIBLE-050
  - JM-BIBLE-054
implementation_status: current
professional_validation: preliminary
---

# Manufacturing Context

## Current methods

`domain/schema.py::ManufacturingSpec.method` accepts exactly two values:
`lost_wax_casting`, `direct_resin_printing`.

## Manufacturing selection is context, not certification

Selecting a manufacturing method in JewelMind:

- Records the intended method as metadata (exported in JSON and the
  technical specification).
- Activates one additional validation rule
  (`JM-MANUFACTURING-001`, see below) that adds *extra scrutiny* for
  `direct_resin_printing` specifically.
- Does **not** run any process simulation (no shrinkage compensation, no
  support generation, no orientation optimization).
- Does **not** certify that the resulting geometry will actually succeed
  in that process at any specific manufacturer.

**JewelMind currently performs only preliminary software checks** — see
[`040-domain-governance.md`](040-domain-governance.md)'s classification
rule: existence of `JM-MANUFACTURING-001` in code does not mean it is a
professionally validated manufacturability threshold.

## `JM-MANUFACTURING-001` — the one existing rule

For `manufacturing.method == "direct_resin_printing"`, `band.thickness`
and `band.width` below 0.8mm each produce a `warning` (not an error).
`setting.prongDiameter` is deliberately excluded from this specific check
because `JM-PRONG-002` already errors below 0.8mm for prongs regardless
of manufacturing method — see
`backend/jewelmind/validation/engine.py::_manufacturing_rules` and its
own code comment. The `0.8mm` threshold itself is a PRELIMINARY SOFTWARE
RULE, not a professionally validated minimum-feature-size figure for any
specific resin printer or resin material.

## Four separate concerns that must not be conflated

This document's central point: manufacturing is not one monolithic
concept. JewelMind today touches only the first of these four, and only
partially:

| Concern | What it means | JewelMind today |
|---|---|---|
| **Geometry generation** | Producing the solid/mesh itself. | Fully implemented (`geometry/`). |
| **Manufacturability validation** | Checking whether the geometry can plausibly be produced by a given process. | One preliminary rule (`JM-MANUFACTURING-001`); no general manufacturability engine. |
| **Process planning** | Deciding orientation, supports, sprues, tolerancing, sequencing for an actual production run. | Not implemented at all. |
| **Professional manufacturing approval** | A qualified professional reviewing and signing off before production. | Always required, never automatable — see [LAW-010](../00-foundation/004-jewelmind-constitution.md#LAW-010). |

## Future concepts (PLANNED / VISION — no values invented)

None of the following are implemented; no numeric value is assigned to
any of them here:

| Concept | Relevant to | Status |
|---|---|---|
| Print orientation | Direct resin printing | PLANNED |
| Support placement | Direct resin printing | PLANNED |
| Casting shrinkage | Lost-wax casting | PLANNED |
| Sprue strategy | Lost-wax casting | PLANNED |
| Polishing allowance | Both | PLANNED |
| Stone-setting sequence | Both (post-casting/printing step) | VISION |
| Tolerances (manufacturing, not tessellation) | Both | PLANNED |
| Cleanup access (room to reach and finish interior surfaces) | Both | PLANNED |
| Minimum feature behavior (beyond the current single 0.8mm heuristic) | Direct resin printing primarily | PLANNED |
| Hollowing (for weight/cost reduction) | Both | VISION |
| Drainage (for hollowed forms, casting/printing residue removal) | Both | VISION |
| Assembly strategy (multi-piece construction, soldering points) | Both | VISION |

## Explicit statement

No shrinkage percentage, minimum wall thickness beyond the existing
0.8mm heuristic, print orientation rule, or process timing figure is
stated anywhere in this document as fact. Where such a number becomes
necessary for a future feature, it must go through
[`057-open-domain-questions.md`](057-open-domain-questions.md) and
[`058-professional-validation-register.md`](058-professional-validation-register.md)
before being treated as anything more than a preliminary placeholder.
