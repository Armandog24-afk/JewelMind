---
id: JM-BIBLE-582
title: Setting Domain Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-27
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-SETTING-README
  - JM-BIBLE-580
related_documents:
  - JM-BIBLE-581
  - JM-BIBLE-587
implementation_status: current
professional_validation: not_required
normative: true
---

# Setting Domain Model

## SettingDefinition

The full input to a setting generator (`setting/models.py`):

| Field | Meaning |
|---|---|
| `settingId` | Stable identity for this setting within an assembly. |
| `settingType` | `prong` or `bezel` — a closed enum whose every member is implemented. |
| `stone` | A `StoneSettingReference`: the kernel-neutral stone facts a Setting may consume. |
| `attachment` | A `SettingAttachmentInterface`, supplied by the category integration. |
| `prong` | `ProngSettingDefinition` or `None` — populated for the prong family. |
| `bezel` | `BezelSettingDefinition` or `None` — populated for the bezel family. |

Note what is absent: no ring size, no band dimension, no jewelry category, no basket. A Setting is told which stone, which attachment plane, and which family parameters — nothing else.

## The discriminated model, and why JDL stayed flat

Brief section 30 asked for a discriminated Setting model *while preserving backward compatibility*. Those pull in opposite directions at the JDL layer, so the split is:

- **Public JDL (`domain/schema.py::SettingSpec`) stays flat.** It gained the `bezel` enum member and two optional bezel fields. Every prong field keeps its default, so prong fields are never *required* for a bezel and bezel fields are never required for a prong — they are simply unread. Turning this into a JSON-level discriminated union would be a breaking change to a published schema for no capability gain.
- **The Setting System is genuinely discriminated.** `ProngSettingDefinition` and `BezelSettingDefinition` are separate models with only their own fields, and `SettingDefinition.prong`/`.bezel` is `None` for the other family. There is no giant object with twenty irrelevant optionals inside the subsystem.
- **`geometry/setting_adapter.py` is the compatibility adapter** between the two, exactly as brief section 30 permits.

## Current and reserved families

`SettingFamily = Literal["prong", "bezel"]`. Both are implemented, both have registered generators, both have capability entries and Golden coverage.

Reserved names carried in `capability.py::RESERVED_SETTING_FAMILIES` and mirrored into `setting-registry.json`: `channel`, `flush`, `bar`, `tension`, `bead`, `pave`, `custom`. These are **not** `SettingFamily` members. Listing them documents direction without implying capability (SETTING-GOV-005); a future family becomes real by gaining a generator and a capability entry, not by being un-commented.

## SettingGeometryResult

What a generator returns alongside the component shapes:

| Field | Meaning |
|---|---|
| `settingId`, `settingType` | Identity. |
| `generatedComponents` | Every component name produced. |
| `productionComponents` | Which of those are production metal — read by the assembly when fusing. |
| `referenceComponents` | Non-production components. Always empty today; a Setting never produces reference geometry. |
| `attachmentInterfaces` | The interface(s) actually used, so the caller need not re-derive them. |
| `geometryFacts` | Per-component `solidCount`/`volumeMm3`/bounding box. |
| `fallbackEvents` | Observable record of any documented geometric accommodation (SETTING-GOV-013). |
| `diagnostics` | Human-readable notes, e.g. a prong-count mismatch. |
| `compatibilityStatus` | The real recorded Stone × Setting status for this combination. |
| `requestedProngCount` / `generatedProngCount` / `placementStrategy` | Prong family only; `None` otherwise. |

The prong-only fields being `None` for a bezel is deliberate and load-bearing: it is what lets inspection emit prong facts *only* for prong settings, so a fact's presence is itself honest about what was built.

`GeneratedModel` gained an optional `setting_result` field carrying this object. It is typed `Any` specifically to keep that dataclass free of a `jewelmind.setting` import, and optional so any caller constructing a `GeneratedModel` directly (fixtures, test doubles) keeps working.

## Kernel neutrality

No field in `setting/models.py` holds a `cadquery.Shape`, `Workplane`, or OCP object. Real geometry objects exist only inside the generators and on the `GeneratedComponent`s they return. This is the same discipline INSPECT-GOV-016/017 established for inspection results, applied here so Forge, Studio, Designer and any future category can depend on Setting contracts without importing a CAD kernel.

## Errors

`setting/errors.py`, all carrying a stable `code` and no kernel stack trace:

`SETTING_TYPE_UNSUPPORTED`, `SETTING_STONE_COMBINATION_UNSUPPORTED`, `SETTING_GENERATION_FAILED`, `SETTING_PLACEMENT_FAILED`, `BEZEL_OUTLINE_FAILED`, `BEZEL_SOLID_INVALID`, `SETTING_CAPABILITY_MISMATCH`. All derive from `SettingError` so a caller can catch the family.

`test_setting.py::TestUnsupportedSettingCombination` asserts the messages contain neither `Traceback` nor `OCP`.

## Cross-references

- [`prong-setting-contract.md`](prong-setting-contract.md), [`bezel-setting-contract.md`](bezel-setting-contract.md) — per-family detail.
- [`setting-capability-model.md`](setting-capability-model.md) — the capability axes.
