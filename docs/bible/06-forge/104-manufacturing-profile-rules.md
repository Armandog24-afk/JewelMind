---
id: JM-BIBLE-104
title: Manufacturing Profile Rules
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-093
related_documents:
  - JM-BIBLE-051
implementation_status: partial
professional_validation: preliminary
normative: true
---

# Manufacturing Profile Rules

## `ManufacturingRuleProfile` (conceptual)

A named bundle of rules whose applicability or verdict is conditioned on a manufacturing method: `profileId`, `process`, `materialCompatibility`, `activeRules`, `ruleVersions`, `professionalValidation`, `geographicOrSupplierScope`, `validityDates`.

**No such object exists in the current codebase.** `manufacturing.method` is a plain enum field; there is no separate "profile" abstraction — rule applicability is expressed inline as an `if` condition inside `_manufacturing_rules()`.

## Current manufacturing contexts

| Method | Status | Active rules referencing it |
|---|---|---|
| `lost_wax_casting` | PRELIMINARY (the default; no rule currently fires specifically because of this choice) | none directly conditioned on it |
| `direct_resin_printing` | PRELIMINARY | `JM-MANUFACTURING-001` |

If this were expressed as two `ManufacturingRuleProfile` objects today, they would look like:

| Field | `lost_wax_casting` profile | `direct_resin_printing` profile |
|---|---|---|
| `profileId` | (not implemented) | (not implemented) |
| `process` | Traditional lost-wax casting | Direct resin printing |
| `materialCompatibility` | All 5 current `MetalType` values | All 5 current `MetalType` values (no material/method incompatibility is currently enforced) |
| `activeRules` | none | `JM-MANUFACTURING-001` |
| `professionalValidation` | not_required (no rule to validate) | preliminary |
| `geographicOrSupplierScope` | Not scoped — applies globally | Not scoped — applies globally |
| `validityDates` | Not tracked | Not tracked |

## Future profiles

Additional manufacturing processes (e.g. CNC milling, electroforming) are plausible future profiles but are not decided, named, or implemented — adding one requires an RFC per [`060-jdl-governance.md`](../05-jdl/060-jdl-governance.md) since it would also require a new `ManufacturingMethod` enum member (a JDL-level change).

## No invented thresholds

This document does not add a shrinkage percentage, a tolerance value, or any manufacturing threshold beyond the single existing `0.8mm` minimum-feature-size floor already documented as `JM-MANUFACTURING-001` in [`04-jewelry-domain/051-manufacturing-context.md`](../04-jewelry-domain/051-manufacturing-context.md) and [`appendices/jdl-error-code-catalog.md`](../appendices/jdl-error-code-catalog.md).
