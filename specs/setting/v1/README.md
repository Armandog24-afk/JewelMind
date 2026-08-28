# Setting v1 — Machine-Readable Specification

The machine-readable half of the Setting System. The narrative, architecture, and contract half lives in [`docs/bible/21-setting/`](../../../docs/bible/21-setting/README.md); start there for context.

## What the Setting System is

A Setting defines how metal geometry interacts with one or more stones. Setting System v1 (Sprint 19) extracts it from the solitaire vertical slice into **shared, category-neutral infrastructure**: `jewelmind.setting` never imports `jewelmind.ring`, `jewelmind.jewelry_category`, or the Shank subsystem (SETTING-GOV-001, enforced by AST inspection in [`backend/tests/test_setting_system_no_ring_dependency.py`](../../../backend/tests/test_setting_system_no_ring_dependency.py)).

The dependency arrow is one-way:

```
Ring / future category  ->  geometry/setting_adapter.py  ->  jewelmind.setting  ->  Stone contracts
```

A `RingHead` consumes a `SettingAttachmentInterface`; a future `PendantBody` or `EarringBody` consumes the same contract. The Setting never learns which one it is.

**Two families are CURRENT: `prong` and `bezel`.** `channel`, `flush`, `bar`, `tension`, `bead`, `pave`, and `custom` are reserved names carried in `setting-registry.json`'s `reservedFamilies` — they have no generator and are deliberately **not** `SettingFamily` enum members (SETTING-GOV-005).

## Files

| File | Purpose |
|---|---|
| [`setting-definition.schema.json`](setting-definition.schema.json) | The full Setting input contract, including the `StoneSettingReference` facts a Setting may consume. Sub-schemas inlined under `$defs`. |
| [`setting-capability.schema.json`](setting-capability.schema.json) | One Setting family's capability entry, with `generatable` and `professionalValidationStatus` as independent axes |
| [`prong-setting.schema.json`](prong-setting.schema.json) | Prong-family parameters |
| [`prong-placement.schema.json`](prong-placement.schema.json) | One resolved placement result: strategy + real positions |
| [`bezel-setting.schema.json`](bezel-setting.schema.json) | Bezel-family parameters |
| [`setting-attachment.schema.json`](setting-attachment.schema.json) | The generic, category-neutral attachment handoff |
| [`setting-registry.schema.json`](setting-registry.schema.json) | Structure of `setting-registry.json` |
| [`setting-registry.json`](setting-registry.json) | Every family's real capability entry, the reserved-family list, and the full Stone × Setting compatibility matrix — generated from `setting/capability.py` |

## Examples

5 in [`examples/`](examples/), each produced by actually running the Setting System: `round-4-prong.json`, `round-6-prong.json`, `oval-prong.json`, `round-bezel.json`, `oval-bezel.json`.

## Test vectors

5 in [`test-vectors/`](test-vectors/): `prong-placement-vectors.json` (real positions for all 7 shapes × 4/6 prongs, with the resolved strategy), `compatibility-vectors.json` (the full matrix), `bezel-vectors.json` (real generated bezel facts per shape, including the dimensions each row was generated from), `unsupported-combination-vectors.json` (the error contract), and `backward-compatibility-vectors.json`.

## Generation capability is NOT professional validation

Every family is `generatable: true` **and** `professionalValidationStatus: "NOT_REVIEWED"` at the same time (SETTING-GOV-007). Those are independent axes, and no Setting geometry in this repository has been reviewed by a qualified human.

Likewise `seatSupport`, `bearingSupport`, and `cutterSupport` are **`PLANNED` for every family**: no seat, bearing, or cutter geometry exists. Stone/metal overlap is *not* a seat, and must never be renamed as one (brief section 24).

## Prong placement is shape-aware, not professionally correct

| Strategy | When | Meaning |
|---|---|---|
| `RADIAL` | `round` | Evenly spaced angles on a circle inset from the girdle. Byte-identical to pre-Sprint-19. |
| `OUTLINE_CARDINAL` | every non-round shape | Positions sampled from the stone's **real girdle outline**, pulled inward by the same girdle inset. |

The strategy is resolved from the stone's real symmetry, never requested via JDL. For an 8 × 6 oval this measurably improves contact: off-axis prongs sat 0.784 mm away from the outline under radial placement and sit 0.049 mm from it now, while the on-axis prong is unchanged.

That is a **software** improvement. Every non-round combination is `EXPERIMENTAL`, because the layout is still provisional: it does not cluster prongs at a marquise's tips, protect a pear's tip, or align to an angular stone's corners. Real `V_PRONG` geometry does not exist.

## The bezel is real CAD, derived from the stone outline

The wall is built by offsetting the stone's **own girdle outline** (`cq.Wire.offset2D`), so the pipeline is outline-agnostic and a future custom outline flows through unchanged rather than needing an `if round / elif oval` branch. All 7 current stone shapes produce a valid single-solid bezel; `round` and `oval` are the two proven `SUPPORTED_SOFTWARE` cases.

Wall thickness and height are **PRELIMINARY SOFTWARE VALUES** (0.6 mm / 2.5 mm), in the same class as `band.width` — configurable software choices, never professional recommendations (SETTING-GOV-010). No minimum wall dimension is enforced, because no sourced professional minimum exists.

### One documented geometry-engine accommodation

`offset2D` of an **ellipse** produces edges whose `geomType()` is `OFFSET`, and an extruded `OFFSET`-curve surface does not survive a STEP write/read cycle — it re-imports as a `Shell` with zero solids. The repair is triggered by the real **curve type**, not by a shape name: any offset wire containing an `OFFSET` edge is resampled into a periodic B-spline. Measured deviation ~0.006% of volume, and the crisp corners of the angular shapes are left untouched. Only `oval` triggers it; recorded as an observable `fallbackEvents` entry (SETTING-GOV-013).

## No fabricated measurements

Every example, test-vector, and the registry were generated by running the real code (via a one-off `backend/gen_setting_specs.py`, run once and not shipped) — never hand-typed. `backend/tests/test_setting_schemas.py` re-validates all of it and re-derives the examples live.

## How these files are validated

`backend/tests/test_setting_schemas.py` (22 tests) validates all 7 schemas, all 5 examples, and every test-vector file, and asserts the registry matches the live `SETTING_CAPABILITIES` field-for-field. `backend/tests/test_setting.py` (102 tests) covers the geometry itself.
