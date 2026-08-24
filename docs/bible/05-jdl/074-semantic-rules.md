---
id: JM-BIBLE-074
title: Semantic Rules
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-063
related_documents:
  - JM-BIBLE-054
  - JM-BIBLE-075
implementation_status: current
professional_validation: preliminary
normative: true
---

# Semantic Rules

This document is the JDL-level index of every current semantic rule, distinct from the numeric-threshold detail already owned by [`04-jewelry-domain/054-domain-validation-classification.md`](../04-jewelry-domain/054-domain-validation-classification.md). It does not restate thresholds; it states which JDL processing stage (JDL-5/JDL-6, see [`063-jdl-processing-model.md`](063-jdl-processing-model.md)) each rule belongs to and what kind of semantic concern it addresses.

| Rule ID | Condition family | Outcome | Severity range | Status | Related Sprint 2 doc | Code | Tests |
|---|---|---|---|---|---|---|---|
| JM-RING-001 | `ring.innerDiameter` range | reject | error | PRELIMINARY SOFTWARE RULE | [`04-jewelry-domain/054`](../04-jewelry-domain/054-domain-validation-classification.md) | `validation/engine.py::_ring_rules` | `test_validation.py` |
| JM-RING-002 | `ring.size` range | reject | error | PRELIMINARY SOFTWARE RULE | same | same | same |
| JM-RING-003 | `size` vs `innerDiameter` consistency | advise, never overwrite | information/warning | PRELIMINARY SOFTWARE RULE | same | `validation/sizing.py` | same |
| JM-BAND-001 | `band.width` minimum | reject | error | PRELIMINARY SOFTWARE RULE | same | `validation/engine.py::_band_rules` | same |
| JM-BAND-002 | `band.thickness` minimum, two thresholds | reject or warn depending on threshold | error or warning (same rule ID, value-dependent) | PRELIMINARY SOFTWARE RULE | same | same | same |
| JM-BAND-003 | `band.width` maximum | advise | warning | PRELIMINARY SOFTWARE RULE | same | same | same |
| JM-STONE-001 | `stone.diameter` range | reject | error | PRELIMINARY SOFTWARE RULE | same | `_stone_rules` | same |
| JM-STONE-002 | `stone.depth` vs `stone.diameter` | reject | error | PRELIMINARY SOFTWARE RULE | same | same | same |
| JM-PRONG-001 | `setting.prongCount` set membership `{4, 6}` | reject | error | PRELIMINARY SOFTWARE RULE | same | `_prong_rules` | same |
| JM-PRONG-002 | `setting.prongDiameter` minimum, two thresholds | reject or warn | error or warning (value-dependent) | PRELIMINARY SOFTWARE RULE | same | same | same |
| JM-PRONG-003 | large stone + 4 prongs | advise | warning | PRELIMINARY SOFTWARE RULE | same | same | same |
| JM-PRONG-004 | `prongHeight` vs `basketHeight` ordering | reject | error | PRELIMINARY SOFTWARE RULE | same | same | same |
| JM-SETTING-001 | `basketHeight` positivity | reject | error | PRELIMINARY SOFTWARE RULE | same | `_setting_rules` | same |
| JM-SETTING-002 | `basketHeight` maximum | advise | warning | PRELIMINARY SOFTWARE RULE | same | same | same |
| JM-MANUFACTURING-001 | thin features under `direct_resin_printing` | advise | warning | PRELIMINARY SOFTWARE RULE | same | `_manufacturing_rules` | same |
| JM-GEOMETRY-001 | band thickness/width produce a valid outer dimension | reject | error | PRELIMINARY SOFTWARE RULE | same | `_geometry_rules` | same |

**All sixteen rules are, at most, PRELIMINARY SOFTWARE RULEs** — zero have been professionally validated (see [`04-jewelry-domain/058-professional-validation-register.md`](../04-jewelry-domain/058-professional-validation-register.md)). This document does not change that status; it locates each rule within the JDL processing model.

## Semantic rules vs. numeric validation thresholds — the distinction this document exists to preserve

A "semantic rule" here means: a check whose *outcome* (reject/advise, and which field it points at) matters at the language level, independent of the exact numeric threshold chosen. The exact threshold (`1.5mm`, `0.8mm`, `{4, 6}`) is domain content, owned by Sprint 2's classification system, and can change without changing this document. This document would only need updating if a rule moved between JDL-5 and JDL-6, changed which field it targets, or changed its severity *class* (error vs. warning) — not if a number inside it were revised after professional review.

## Same rule ID, different severity

`JM-BAND-002` and `JM-PRONG-002` each fire at two different thresholds with two different severities (a harder error floor and a softer warning floor above it). This is intentional existing behavior — see [`080-errors-warnings-and-diagnostics.md`](080-errors-warnings-and-diagnostics.md) for how the diagnostics model represents a single rule ID with value-dependent severity, and [`jdl-error-code-catalog.md`](../appendices/jdl-error-code-catalog.md) for both thresholds recorded together under one code.
