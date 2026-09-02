---
id: JM-BIBLE-605
title: "Stone Profile Model v2"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-02
source_of_truth: true
depends_on:
  - JM-BIBLE-600
related_documents:
  - JM-BIBLE-606
implementation_status: current
professional_validation: not_required
normative: true
---

# Stone Profile Model v2

## The separation

```
OUTLINE SHAPE          ×          3D REFERENCE PROFILE
stone.shape                       stone.profile
21 named cuts + custom            FACETED / CABOCHON / SPHERICAL
+ imported
```

`OVAL + FACETED_REFERENCE` is a faceted-style oval.
`OVAL + CABOCHON_REFERENCE` is an oval cabochon.
`CUSTOM + CABOCHON_REFERENCE` is a custom cabochon.

## Why this is two axes and not one enum

Brief section 36 asked for it directly, and the arithmetic is the argument:
`OVAL_CABOCHON`-style compound members multiply. 21 shapes × 3 profiles is 63
enum members, of which most would be meaningless, and each new profile would
multiply the list again.

Two axes also state something true that one enum cannot: **a cabochon is not
just another outline.** An oval cabochon and a faceted oval share their
silhouette exactly and differ entirely in their body. Modelling that as two
unrelated shapes would lose the shared half.

## The three profiles

### `FACETED_REFERENCE`

The Sprint 18 three-level body: culet → girdle → table, lofted `ruled=True`.
Unchanged in construction, which is what keeps every Stone v1 shape
byte-identical.

```
CROWN_FRACTION         0.35
PAVILION_FRACTION      0.65
TABLE_TO_GIRDLE_RATIO  0.56
CULET_SCALE_RATIO      0.05
```

Supported by every outline shape.

### `CABOCHON_REFERENCE`

A shallow base below the girdle plus an ellipsoidal dome above it, sampled at
`CABOCHON_DOME_SECTIONS` levels following `scale = sqrt(1 - t²)`.

```
CABOCHON_DOME_FRACTION  0.75
CABOCHON_BASE_FRACTION  0.25
CABOCHON_BASE_SCALE     0.55
CABOCHON_APEX_SCALE     0.04
CABOCHON_DOME_SECTIONS  16
```

**16 sections was measured, not guessed.** Round cabochon, 6.5 × 3.0mm:

| Sections | Volume (mm³) | Change |
|---|---|---|
| 8 | 64.4884 | — |
| 12 | 64.7957 | +0.48% |
| 16 | 64.9082 | +0.17% |

16 sits on the flat part of the curve. Same empirical approach as
`geometry/shank/builder.py::SECTION_COUNT` (Sprint 17).

Currently supported for `round`, `oval`, `heart`, `half_moon` and any custom
outline. Extending it to another shape is a registry edit plus a Golden case,
not new code — the builder never learns which shape it is building.

### `SPHERICAL_REFERENCE`

A sphere. The only profile that **ignores its outline entirely**: for a sphere
the silhouette is a consequence of the body, not an input to it. Used by
`pearl`; see [`cabochon-and-pearl.md`](cabochon-and-pearl.md).

## `ruled=True` is not a style preference

Both outline-consuming profiles loft with `ruled=True`, and both would be wrong
without it. Two measured reasons:

1. **A smooth loft overshoots the requested dimensions.** A `ruled=False`
   cabochon bulged between its sections, producing a 6.5088mm bounding box for a
   6.5mm request — breaking the requested-equals-measured contract
   (STONEV2-GOV-012).

2. **A smooth loft over ELLIPSE sections does not survive STEP export.** The
   oval cabochon re-imported with **zero solids** and a volume of 53.92mm³
   against the source's 68.22mm³. This is the same failure class Sprint 19 hit
   when `offset2D` on an ellipse produced `OFFSET`-type edges.

`ruled=True` fixed both: exact bounding boxes and exact STEP roundtrips for
every shape × profile combination, verified across all 25.

## The profile-resolution rule

A profile the shape does not support is an error — **unless** the caller never
set it.

```
requested profile is supported            → use it
explicitly set and unsupported            → STONE_SHAPE_PROFILE_COMBINATION_UNSUPPORTED
left at the schema default, and the shape
has exactly ONE supported profile         → resolve to it, and RECORD that
otherwise                                 → error
```

This exists because `{"shape": "pearl", "diameter": 8}` is a completely
reasonable request that failed deep inside the outline builder: `profile`
defaults to `FACETED_REFERENCE`, while a sphere supports only
`SPHERICAL_REFERENCE`.

The distinction that keeps this honest is `model_fields_set`: a default the
caller never touched is a default, and resolving it is disclosed as
`PROFILE_DEFAULTED:FACETED_REFERENCE->SPHERICAL_REFERENCE` in
`normalizationOperations`. An explicitly requested combination is never
overridden (STONEV2-GOV-010).

## What is not claimed

No profile models a real cutting style. The cabochon dome fractions and section
count are software construction parameters; `CABOCHON_REFERENCE` is not a
gemological cabochon, and `SPHERICAL_REFERENCE` is not a claim that the stone is
a pearl (STONEV2-GOV-003).

## Cross-references

- [`extended-native-shapes.md`](extended-native-shapes.md)
- [`cabochon-and-pearl.md`](cabochon-and-pearl.md)
- [`../20-stone/README.md`](../20-stone/README.md) — the Sprint 18 faceted body.
