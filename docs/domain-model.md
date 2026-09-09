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
| `setting.type` | enum | The setting FAMILY, and the value that selects the generator: `prong` (default), `bezel` (Sprint 19), and `channel`/`bar`/`flush`/`tension` (Sprint 27). Each has a real registered generator, asserted equal to `setting_generators()` in both directions. Reserved family names (`bead`, `pave`, `custom`) are deliberately not members. This row said "only prong settings are supported" until Sprint 27 and had been stale since Sprint 19. |
| `setting.prongCount` | integer | Business rule requires 4 or 6 (JM-PRONG-001) — the *type* allows any integer so an invalid value surfaces as a validation result, not a raw parse error. |
| `setting.prongDiameter` | number, mm | Prong cylinder diameter. |
| `setting.prongHeight` | number, mm | Prong height above the top of the band. |
| `setting.basketHeight` | number, mm | Basket support height above the top of the band. |
| `stone.gem` | `GemIdentity` \| null | What the stone is MADE OF, separate from every geometry field (Sprint 21). `null` on a legacy document, which normalizes to the `unknown` gem — never to diamond. Never inferred from the shape. See `docs/bible/23-gem-identity/README.md`. |
| `stone.gem.gemId` | string | A canonical registry ID (`gem/registry.py`), e.g. `corundum.ruby`. `custom` requires `customName`; `unknown` records that the gem was not identified. Validated for shape before any lookup. |
| `stone.gem.origin` | enum | `NATURAL`, `SYNTHETIC`, `SIMULANT`, `COMPOSITE`, `UNKNOWN`. Independent of treatment and of identity. |
| `stone.gem.treatments` | list | DECLARED treatments, each with a status and a disclosure source. An empty list means nothing was recorded, not that the stone is untreated. |
| `stone.gem.visualProfileId` | string \| null | Overrides the entry's default appearance. Presentation only — it never changes identity, and it is excluded from the geometry hash along with the rest of `stone.gem`. |
| `setting.prongStyle` | enum | `ROUND_PRONG` (the pre-Sprint-23 cylinder, and the default), `TAPERED_PRONG`, `CLAW_PRONG`, `V_PRONG`. Each is a real registered builder; notch and taper values are software construction parameters, never professional proportions. |
| `setting.headArchitecture` | enum | `BASKET` (the pre-Sprint-23 wall, and the default), `PEG_HEAD`, `MARTINI`, `TULIP`, `OPEN_GALLERY` (Sprint 27: the basket wall with windows pierced through it, deliberately NOT called azure). The generated component is named `basket_support` for every architecture — the name is a structural role, and the architecture is reported separately. `TRELLIS` is deliberately not a member. |
| `setting.seatMode` | enum | `NONE` (default) or `REFERENCE_SEAT`, which CUTS the stone volume out of the head and prongs. Never a fuse, so the stone is never production metal. Relief, not a setter's seat with a bearing shoulder. |
| `setting.prongTipRatio` | number | Tip radius as a fraction of the prong radius, for the tapered styles. Ignored by `ROUND_PRONG`. A construction parameter. |
| `setting.headBaseRatio` | number | Base radius as a fraction of the head radius, for `MARTINI`/`TULIP`. Ignored by `BASKET`. |
| `setting.pegDiameter` | number \| null | Read only by `PEG_HEAD`, and required by it. Deliberately not defaulted to a number (`JM-SETTING-005`). |
| `setting.pegHeight` | number \| null | As above; must be shorter than `setting.basketHeight`. |
| `setting.mode` | `SettingModeSpec` \| null | The extended setting MODE: the variant within the family `setting.type` names, plus its construction parameters (Sprint 27). `null` on every pre-Sprint-27 document, and it resolves to the variant `type`/`prongStyle` already meant — so an old design's geometry is unchanged. It REFINES `type` and never competes with it: a mode whose family disagrees is refused (`JM-SETTING-008`), not resolved by precedence. Participates in `geometryHash`. See `docs/bible/29-extended-setting-modes/README.md`. |
| `setting.mode.modeId` | enum | One of the twenty implemented setting-mode ids. Only a PRIMARY mode is valid here — the head is chosen by `setting.headArchitecture` and field retention by the pavé's own strategy, so declaring one of those would be a second authority over an axis that has one. Every reserved mode (`HEAD_TRELLIS`, `HEAD_AZURE`, `RETENTION_CHANNEL`, `TENSION_COMPRESSION_MODELLED`, …) is deliberately not a member. |
| `setting.mode.enabled` | boolean | `false` keeps the parameters in the document and builds the family's DEFAULT variant — a different state from declaring no mode at all, and reported as such by `JM-SETTING-009`. |
| `setting.mode.arrangementInstanceIds` | list | Which arrangement instances this mode holds, when it holds more than the design's own stone. OPAQUE ids: the Setting System carries the reference and never resolves it, so the arrangement stays the authority on where those instances are. |
| `setting.mode.parameters` | `SettingModeParameters` | One FLAT model of construction parameters, not a discriminated union — a union cannot be reached by a dotted-path patch, which is the defect that stopped Designer creating a pavé in Sprint 26. `MODE_PARAMETER_FIELDS` states which mode reads which field, and a value the mode does not read is reported by `JM-SETTING-009` rather than silently dropped. Every default is a construction parameter, never a recommendation. |
| `setting.galleryWindowCount` | integer | How many windows an `OPEN_GALLERY` head pierces. Read only by that architecture. |
| `setting.galleryWindowSweep` | number, degrees | Angular width of each window. |
| `setting.galleryWindowHeightFraction` | number | Fraction of the head's height the windows span, strictly below 1.0. A CONSTRUCTION CORRECTNESS bound rather than a proportion anyone reviewed: a full-height window severs the wall into disconnected pillars, and a head must be one connected body. |
| `family` | `FamilyDefinition` \| null | The design's multi-stone family: its SEMANTIC structure (Sprint 24). `null` on every pre-Sprint-24 document. A family COMPILES INTO an arrangement, so declaring both is refused (`JM-FAMILY-001`) rather than merged. Participates in `geometryHash`, because a family drives geometry. See `docs/bible/26-multi-stone-families/README.md`. |
| `family.familyType` | enum | `THREE_STONE`, `TOI_ET_MOI`, `CLUSTER`, `CENTER_WITH_ACCENTS`. Each has a real compiler; `pave`/`eternity`/`bypass`/`channel_row` are deliberately not members. A halo is not a member either, and since Sprint 25 that is because a halo is not a family: it is the separate, COMPOSABLE `halo` field below. |
| `family.params` | object | Per-family parameters, discriminated on `kind`, which must match `familyType`. Every spacing and radius is a POSITION parameter, never a clearance. |
| `family.members[]` | list | One participating stone each: a stable `memberId`, a `role`, a `stoneRef` (only `primary` resolves today), an optional per-member `gem`, `scale`, `orientationDeg`, `placementOverride` and `settingRef`. Empty means "derive every member from the parameters". |
| `halo` | `HaloDefinition` \| null | The design's halo (Sprint 25). `null` on every pre-Sprint-25 document. A halo COMPOSES onto whatever placement the design declares — a `family`, an `arrangement`, or neither — rather than replacing it, which is why it sits beside them. Participates in `geometryHash`, because a halo places stones. See `docs/bible/27-halo/README.md`. |
| `halo.variant` | enum | `SINGLE`, `DOUBLE`, `HIDDEN`. Each has a real compiler. `HIDDEN` is a structural claim: its ring's `zOffsetMm` must be negative. Reserved variants (`cushion_halo`, `floral_halo`, `compass_halo`, `triple_halo`, `pave_halo`) are refused rather than substituted. |
| `halo.rings[]` | list | One concentric ring each: a stable `ringId`, a `count`, `radiusMm`/`radiusYMm`, `startAngleDeg`/`sweepDeg`, `zOffsetMm`, `memberScale`, `alignToRadius`, a `stoneRef` (only `primary` resolves today), an optional per-ring `gem` and `settingRef`, and `members` for the individual stones that differ. Every radius is a POSITION parameter, never a clearance. |
| `halo.centerMemberId` | string \| null | The arrangement instance the halo surrounds. `null` anchors on the design origin, which is how a halo encircles a multi-stone centre. A named value must exist in the composed arrangement; an absent one is refused (`JM-HALO-001`), never re-anchored. |
| `pave` | `PaveDefinition` \| null | The design's pavé or microsetting field (Sprint 26). `null` on every pre-Sprint-26 document. A pavé COMPOSES onto whatever placement the design declares. ONE field, not a list. Participates in `geometryHash`, because a pavé places stones and cuts metal. See `docs/bible/28-pave/README.md`. |
| `pave.kind` | enum | `PAVE` (an area at a density) or `MICROSETTING` (a stated structure). Must match `pave.spec.kind`. |
| `pave.host` | enum | `BAND_OUTER` or `HEAD_PLANE` — the only two surfaces with a resolver. Every other target is reserved with a stated reason; a surface is resolved from design parameters, never by picking a face out of a solid. |
| `pave.spec` | object | Per-kind parameters, discriminated on `kind`. Every pitch and spacing is a POSITION parameter, never a clearance. |
| `pave.retention` | object | `strategy` (`NONE`/`BEAD`/`SHARED_BEAD`/`MICRO_PRONG`) plus its construction sizes. Real metal, fused into the host. No minimum bead size is enforced. |
| `pave.seat` | object | `REFERENCE_RECESS` cuts the field's stones out of the host — a cut, never a fuse. Deliberately not called a seat: it has no bearing shoulder. |
| `pave.containment` | enum | `CLIP` ends the field at the surface edge and reports how many cells it lost; `REJECT` refuses the whole field. |
| `arrangement` | `ArrangementDefinition` \| null | Which stone occurrences a design contains and how they relate (Sprint 22). `null` on every pre-Sprint-22 document, which is a single-stone design and behaves exactly as before. Participates in `geometryHash`, because an arrangement will drive geometry. See `docs/bible/24-arrangement/README.md`. |
| `arrangement.instances[]` | list | One occurrence each: a stable `instanceId`, a `stoneRef` (only `primary` resolves today), a `role`, a `placement`, a closed set of `overrides`, and an optional per-instance `gem`. An occurrence references what a stone IS rather than restating it. |
| `arrangement.groups[]` | list | Named sets with their own origin. Membership is declared by an instance naming its `groupId` — one direction only, because two would need to agree. |
| `arrangement.patterns[]` | list | `LINEAR`, `RADIAL` or `MIRROR`, each a closed-form generator applied to a named source instance. Members get derived ids (`halo.0`, …) so re-resolving is deterministic. |
| `arrangement.relations[]` | list | Declared relationships (mirrored pair, aligned, evenly spaced, concentric, shared transform). RECORDED and reference-checked, never solved: nothing moves an instance to satisfy one. |
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
