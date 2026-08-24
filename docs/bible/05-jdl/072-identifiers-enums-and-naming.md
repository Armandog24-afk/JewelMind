---
id: JM-BIBLE-072
title: Identifiers, Enums, and Naming
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-070
related_documents:
  - JM-BIBLE-A10
implementation_status: current
professional_validation: not_required
normative: true
---

# Identifiers, Enums, and Naming

The authoritative, exhaustive enum catalog lives in [`jdl-enumeration-catalog.md`](../appendices/jdl-enumeration-catalog.md), cross-checked field-by-field against `backend/jewelmind/domain/schema.py` and `shared/types/jewelry-definition.ts`. This document states the naming rules those enums follow.

## Naming rules

1. **Field names**: camelCase, exactly matching both the Pydantic field name and the TypeScript property name (`innerDiameter`, `prongCount`, `angularTolerance`). No JDL representation renames a field.
2. **Enum member values**: snake_case string literals (`comfort_fit`, `yellow_gold_18k`, `lost_wax_casting`). This is the JSON wire value, not a display label — display formatting is a frontend presentation concern, out of scope for JDL.
3. **Category/style/type discriminators** (`jewelry.category`, `jewelry.style`, `setting.type`, `stone.shape`, `band.profile`) are plain string enums today, not a tagged-union discriminator pattern — because only one value exists for `category` and `style`, there has been no need for polymorphic field sets yet. See [`04-jewelry-domain/056-domain-extension-strategy.md`](../04-jewelry-domain/056-domain-extension-strategy.md) for how this would change if a second ring style were added (via RFC).

## Authoritative enum catalog (minimum required set)

| Enum | Current members | Where declared |
|---|---|---|
| `category` | `ring` | `JewelryCategory` in `schema.py`; `JewelryCategory` in `jewelry-definition.ts` |
| `style` | `solitaire` | `JewelryStyle` |
| `sizeSystem` | `EU` | `RingSizeSystem` |
| `bandProfile` | `comfort_fit`, `flat` | `BandProfile` |
| `stoneShape` | `round` | `StoneShape` |
| `settingType` | `prong` | `SettingType` |
| `prongCount` | not an enum — a plain `int`, deliberately (see [`064-canonical-document-model.md`](064-canonical-document-model.md) and `schema.py`'s own comment); the *valid set* `{4, 6}` is enforced only by semantic rule `JM-PRONG-001` | `SettingSpec.prongCount` |
| `metal` | `yellow_gold_18k`, `white_gold_18k`, `rose_gold_18k`, `platinum`, `silver` | `MetalType` |
| `manufacturingMethod` | `lost_wax_casting`, `direct_resin_printing` | `ManufacturingMethod` |
| `unitSystem` | `mm` (fixed literal, not a real choice) | `ProjectInfo.units` |

## Future values: RESERVED / PLANNED / VISION

No enum member beyond the ones listed above exists in this specification. A future member must be added via the RFC process in [`04-jewelry-domain/056-domain-extension-strategy.md`](../04-jewelry-domain/056-domain-extension-strategy.md) and must not pass current validation until the corresponding code change ships — `specs/jdl/v1/jdl.schema.json` and `backend/jewelmind/domain/schema.py` reject any value not in the lists above today, by design (`extra="forbid"` / `additionalProperties: false` for objects; `Literal`/enum membership for scalar fields).

## Case sensitivity and duplicate handling

All enum comparisons are case-sensitive and exact-match (`"Round"` is not `"round"`). JSON's own duplicate-key handling (last-value-wins before Pydantic ever sees the data) is the only duplicate-handling behavior that exists today; no JDL-specific duplicate-detection code runs at the enum or field level.
