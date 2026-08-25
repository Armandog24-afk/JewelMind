---
id: JM-BIBLE-296
title: Capability Awareness
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-295
related_documents:
  - JM-BIBLE-297
implementation_status: current
professional_validation: not_required
normative: true
---

# Capability Awareness

## `current_capabilities()`, derived from real code

`backend/jewelmind/designer/capability.py::current_capabilities()` builds its answer by calling `typing.get_args()` on the actual `Literal` type aliases in `backend/jewelmind/domain/schema.py`:

```python
{
    "jewelryCategory": list(get_args(S.JewelryCategory)),
    "jewelryStyle": list(get_args(S.JewelryStyle)),
    "stoneShape": list(get_args(S.StoneShape)),
    "settingType": list(get_args(S.SettingType)),
    "bandProfile": list(get_args(S.BandProfile)),
    "metal": list(get_args(S.MetalType)),
    "manufacturingMethod": list(get_args(S.ManufacturingMethod)),
    "ringSizeSystem": list(get_args(S.RingSizeSystem)),
    "prongCount": list(SUPPORTED_PRONG_COUNTS),
}
```

This is the single source of truth both for what `capability.is_supported_enum_value()` accepts and for what `prompts.py::build_capabilities_block()` tells a real LLM provider is currently supported. If the schema's `Literal` gains or loses a member, this dict changes automatically the next time it's called — there is no separate list to keep in sync by hand for 8 of the 9 keys.

## The one deliberate exception: `prongCount`

`setting.prongCount` is an `int` field in `domain/schema.py`, not a `Literal`. Its actual allowed set — `(4, 6)` — is enforced only by the Forge rule `JM-PRONG-001` in `validation/rules.py`/`engine.py`. `capability.py` hardcodes `SUPPORTED_PRONG_COUNTS = (4, 6)` as a literal tuple, with an explicit code comment: *"kept as a literal tuple here too since the rule module doesn't expose it as an importable constant. If that rule's allowed set ever changes, this must change with it in the same commit."*

This is a real architectural quirk, not an oversight: prong count's validity is Forge's domain-rule concern (a manufacturing/geometric constraint), while its schema type is just `int`. Capability-awareness has to duplicate the (4, 6) fact rather than introspect it, because there is no single importable source for it today. A future refactor could expose `JM-PRONG-001`'s allowed set as an importable constant that both `validation/rules.py` and `capability.py` import — see [`321-designer-gap-analysis.md`](321-designer-gap-analysis.md).

## Why this keeps Designer honest

Because 8 of 9 capability sets are read live from the schema, Designer cannot silently drift out of sync with what the CAD engine actually supports — a new stone shape added to `StoneShape` becomes proposable the moment the schema changes, with no Designer-side code change required. The one manually-duplicated fact (`prongCount`) is flagged in the module's own docstring precisely because it's the one place this guarantee doesn't hold automatically.

## Enum-field capability keys

`_ENUM_FIELD_CAPABILITY_KEY` maps 9 of the 19 known JDL paths to a capability-set key; the other 10 (numeric fields plus `project.name`) have no enum capability set — their bounds are Forge's job, not capability-awareness's, per `is_supported_enum_value()`'s own comment: "Not an enum field... capability-awareness has nothing to say about it."

See [`297-supported-language-scope.md`](297-supported-language-scope.md) for how these capability values are reached regardless of input language.
