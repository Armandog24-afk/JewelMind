---
id: JM-BIBLE-A10
title: "Appendix: JDL Enumeration Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-072
related_documents:
  - JM-BIBLE-A09
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: JDL Enumeration Catalog

Every enumeration in the current schema, cross-checked against `backend/jewelmind/domain/schema.py` (`Literal[...]` definitions) and `shared/types/jewelry-definition.ts` (matching union types) during this Sprint.

| Enum | Field(s) | Current members | Future values |
|---|---|---|---|
| `JewelryCategory` | `jewelry.category` | `ring` | None reserved yet — a second category (e.g. earring, pendant) requires an RFC per [`04-jewelry-domain/056-domain-extension-strategy.md`](../04-jewelry-domain/056-domain-extension-strategy.md); must not pass current validation |
| `JewelryStyle` | `jewelry.style` | `solitaire` | Same — a second ring style is RFC-gated |
| `RingSizeSystem` | `ring.sizeSystem` | `EU` | US/UK/JP sizing systems are plausible future additions, not implemented; RESERVED extension point in `specs/jdl/v1/jdl.ebnf`'s `size-system-literal` production |
| `BandProfile` | `band.profile` | `comfort_fit`, `flat` | RESERVED extension point in `jdl.ebnf`'s `band-profile-literal`; no specific future value has been decided |
| `StoneShape` | `stone.shape` | `round` | RESERVED extension point in `jdl.ebnf`'s `stone-shape-literal`; princess/oval/emerald/etc. are plausible but not decided or implemented |
| `SettingType` | `setting.type` | `prong` | RESERVED extension point in `jdl.ebnf`'s `setting-type-literal`; bezel/pave/tension are plausible but not decided or implemented |
| `prongCount` (valid set, semantic-layer only) | `setting.prongCount` | `{4, 6}` (enforced by `JM-PRONG-001`, not a type-level enum — see [`070-type-system.md`](../05-jdl/070-type-system.md)) | No other value is planned; a value outside `{4, 6}` is not RESERVED, it is simply invalid |
| `MetalType` | `material.metal` | `yellow_gold_18k`, `white_gold_18k`, `rose_gold_18k`, `platinum`, `silver` | RESERVED extension point in `jdl.ebnf`'s `metal-literal`; no specific future alloy decided |
| `ManufacturingMethod` | `manufacturing.method` | `lost_wax_casting`, `direct_resin_printing` | RESERVED extension point in `jdl.ebnf`'s `method-literal`; no specific future method decided |
| units | `project.units` | `mm` (fixed, not a real choice) | None — LAW-007 makes this permanent, not merely current |

## VISION-tier values

None. No document in this Bible describes a specific future enum member as VISION — every "future values" cell above is a RESERVED *extension point in the grammar* (a place a value could go), not a named, half-planned value. Per [`04-jewelry-domain/040-domain-governance.md`](../04-jewelry-domain/040-domain-governance.md) rule 2, no measurement or specific future enum member is invented here.

## Cross-check method

Every "current members" cell above was read directly from the `Literal[...]` type alias in `backend/jewelmind/domain/schema.py` and confirmed identical to the corresponding union type in `shared/types/jewelry-definition.ts` during this Sprint — **total named enumerations catalogued: 8** (`JewelryCategory`, `JewelryStyle`, `RingSizeSystem`, `BandProfile`, `StoneShape`, `SettingType`, `MetalType`, `ManufacturingMethod`), plus 2 additional value sets listed above for completeness that are not named `Literal` type aliases: the fixed `units: "mm"` inline literal, and the semantic-layer-only `prongCount ∈ {4, 6}` set.
