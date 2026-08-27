# Domain model

JewelMind has one canonical jewelry definition shape, `JewelryDefinition`.
It exists in two places that must be kept structurally in sync by hand:

- **Backend (authoritative):** `backend/jewelmind/domain/schema.py` —
  Pydantic v2 models, `extra="forbid"`.
- **Frontend (mirror, for immediate UI feedback):**
  `shared/types/jewelry-definition.ts` — plain TypeScript interfaces plus
  `createDefaultDefinition()`.

There is no codegen step linking the two in this milestone (see
`docs/known-limitations.md`). The backend is always the final authority:
every generate/export request re-validates the definition server-side
regardless of what the frontend believes.

## Canonical JSON shape

```json
{
  "schemaVersion": "0.1.0",
  "project": { "name": "Solitaire Ring", "units": "mm" },
  "jewelry": { "category": "ring", "style": "solitaire" },
  "ring": { "sizeSystem": "EU", "size": 16, "innerDiameter": 17.8 },
  "band": { "width": 2.4, "thickness": 1.8, "profile": "comfort_fit" },
  "stone": { "shape": "round", "diameter": 6.5, "depth": 4.0 },
  "setting": {
    "type": "prong",
    "prongCount": 6,
    "prongDiameter": 1.1,
    "prongHeight": 4.8,
    "basketHeight": 3.5
  },
  "material": { "metal": "yellow_gold_18k" },
  "manufacturing": { "method": "lost_wax_casting" },
  "preview": { "meshTolerance": 0.1, "angularTolerance": 0.2 }
}
```

This is also the exact default definition (see `default_definition()` /
`createDefaultDefinition()`).

## Field reference

| Path | Type | Notes |
|---|---|---|
| `project.name` | string | Used to derive sanitized export filenames. |
| `project.units` | `"mm"` | Fixed; JewelMind only works in millimeters. |
| `jewelry.category` | `"ring"` | Only `ring` is supported in this milestone. |
| `jewelry.style` | `"solitaire"` | Only `solitaire` is supported. |
| `ring.sizeSystem` | `"EU"` | Only the EU/French convention is supported — see `docs/validation-rules.md` (JM-RING-003). |
| `ring.size` | number | EU/French ring size. |
| `ring.innerDiameter` | number, mm | Finger opening diameter. |
| `band.width` | number, mm | Band extent along the finger axis. |
| `band.thickness` | number, mm | Band extent radially (metal thickness). |
| `band.profile` | `"comfort_fit"` \| `"flat"` | See `docs/geometry-conventions.md`. |
| `band.widthTaper` | `{mode, bottomRatio}` | Optional width taper toward the bottom (Sprint 17). Default `mode: "NONE"`. See `docs/bible/19-shank/README.md`. |
| `band.thicknessTaper` | `{mode, bottomRatio}` | Optional thickness taper toward the bottom (Sprint 17). Default `mode: "NONE"`. |
| `stone.shape` | `"round" \| "oval" \| "pear" \| "emerald" \| "cushion" \| "princess" \| "marquise"` | All 7 generate real geometry (Sprint 18). Only `round` has a setting designed for it — see `docs/bible/20-stone/README.md`. |
| `stone.diameter` | number \| null, mm | Girdle diameter. Required for, and meaningful only for, `round`. |
| `stone.length` | number \| null, mm | Major horizontal dimension (local Y). Required when `shape != "round"`. |
| `stone.width` | number \| null, mm | Minor horizontal dimension (local X). Required when `shape != "round"`. |
| `stone.orientation` | number, degrees | Rotation around the stone's own local vertical axis. Default 0. |
| `stone.depth` | number, mm | Total culet-to-table height of the stone reference. |
| `setting.type` | `"prong"` | Only prong settings are supported. |
| `setting.prongCount` | integer | Business rule requires 4 or 6 (JM-PRONG-001) — the *type* allows any integer so an invalid value surfaces as a validation result, not a raw parse error. |
| `setting.prongDiameter` | number, mm | Prong cylinder diameter. |
| `setting.prongHeight` | number, mm | Prong height above the top of the band. |
| `setting.basketHeight` | number, mm | Basket support height above the top of the band. |
| `material.metal` | enum | `yellow_gold_18k`, `white_gold_18k`, `rose_gold_18k`, `platinum`, `silver`. Cosmetic only in this milestone — see known limitations. |
| `manufacturing.method` | enum | `lost_wax_casting`, `direct_resin_printing`. Affects one validation rule (JM-MANUFACTURING-001). |
| `preview.meshTolerance` | number, mm | Linear tessellation tolerance for preview meshes and STL export. |
| `preview.angularTolerance` | number, rad | Angular tessellation tolerance. |

## Why `prongCount` is a plain integer, not a closed type

Pydantic could enforce `Literal[4, 6]` and reject anything else at parse
time with a generic 422. JewelMind deliberately does *not* do this for
fields that have a corresponding `JM-*` validation rule (like
`setting.prongCount` → `JM-PRONG-001`): an out-of-range value should surface
as a structured `ValidationResult` the UI can display next to the field,
not as an opaque request-validation error. Fields with **no** corresponding
business rule (`band.profile`, `stone.shape`, `material.metal`,
`manufacturing.method`) are closed enums at the type level, because there is
no dedicated rule to report a friendlier error for them.

## Canonical JSON and hashing

`backend/jewelmind/utils/hashing.py` serializes a definition with sorted
keys and no incidental whitespace, then SHA-256 hashes it and truncates to
16 hex characters. That hash is the model's `modelId`: the same input
always produces the same id, and regenerating with the same input replaces
the cached model rather than creating a duplicate.
