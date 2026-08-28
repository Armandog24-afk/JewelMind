---
id: JM-BIBLE-589
title: Setting Capability Model
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
  - JM-BIBLE-575
  - JM-BIBLE-591
implementation_status: current
professional_validation: not_required
normative: true
---

# Setting Capability Model

## The central point

> **Generatable is not validated, and a generatable stone shape is not a compatible one.**

Two independent separations, both enforced by test:

1. `generatable` vs `professionalValidationStatus` (SETTING-GOV-007) — every family is `generatable: true` **and** `NOT_REVIEWED` at the same time.
2. Stone-shape generation vs Stone × Setting compatibility (SETTING-GOV-006) — all 7 stone shapes generate; only `round` is prong-supported and only `round`/`oval` bezel-supported.

## The axes

`SettingCapability` (`setting/capability.py`):

| Axis | Meaning |
|---|---|
| `status` | `CURRENT` / `PARTIAL` / `PLANNED` / `BLOCKED` / `OUT_OF_SCOPE` |
| `generatable` | A registered generator produces real CAD geometry. |
| `inspectable` | Covered by real runtime inspection facts. |
| `categoryNeutral` | The generator is free of any jewelry-category dependency. |
| `stoneShapesSupported` | `SUPPORTED_SOFTWARE`: the geometry was designed for this shape. |
| `stoneShapesExperimental` | Generates real geometry via a provisional strategy. |
| `stoneShapesUnsupported` | Would be refused. Empty for both families today. |
| `stoneSourceModesSupported` | `PARAMETRIC_REFERENCE_STONE` only. |
| `seatSupport` / `bearingSupport` / `cutterSupport` | `PLANNED` for every family. |
| `professionalValidationStatus` | `NOT_REVIEWED` for every family. |
| `settingGeometryVersion` | `1.0.0`; bumped on a MAJOR construction change. |

## The registry

| Family | status | gen | insp | cat-neutral | supported | experimental | seat/bearing/cutter | prof. validation |
|---|---|---|---|---|---|---|---|---|
| `prong` | `CURRENT` | ✔ | ✔ | ✔ | `round` | oval, pear, emerald, cushion, princess, marquise | all `PLANNED` | `NOT_REVIEWED` |
| `bezel` | `CURRENT` | ✔ | ✔ | ✔ | `round`, `oval` | pear, emerald, cushion, princess, marquise | all `PLANNED` | `NOT_REVIEWED` |

Mirrored — never hand-maintained — at `specs/setting/v1/setting-registry.json`, together with the reserved-family list and the full 14-row compatibility matrix. `test_setting_schemas.py` re-derives all three from the live registry and asserts field-for-field equality.

## Reserved families

`channel`, `flush`, `bar`, `tension`, `bead`, `pave`, `custom` are carried in `RESERVED_SETTING_FAMILIES` and mirrored into the registry's `reservedFamilies`. They are **not** `SettingFamily` enum members and have no generator.

Listing them documents direction without implying capability. `test_setting.py::test_reserved_families_have_no_generator` asserts none of them is registered or has a capability entry, so the list cannot quietly become a set of half-implemented families.

## Compatibility statuses

| Status | Meaning |
|---|---|
| `SUPPORTED_SOFTWARE` | The setting geometry was designed for this shape. Still **not** professionally validated. |
| `EXPERIMENTAL` | Generates real geometry, via a provisional strategy that is known not to be shape-optimized. |
| `UNSUPPORTED` | Refused with an explicit error (SETTING-GOV-012). |

The name `SUPPORTED_SOFTWARE` rather than `SUPPORTED` is deliberate: it carries its own qualifier, so the strongest status the system can express still cannot be misread as professional endorsement.

`compatibility_matrix()` generates the full cross-product from the capability entries, so the matrix cannot drift from the per-family lists.

## Seats, bearings, cutters

All three are `PLANNED` for every family, because **none exists**. This is the honesty requirement of brief section 24, and it is asserted in two places — `test_setting.py::test_seats_bearings_and_cutters_are_honestly_planned` and the Capability Coverage Guard's `test_seats_bearings_and_cutters_are_planned_everywhere`.

The specific trap the brief names is worth restating: *"Do not rename arbitrary Stone overlap as a seat."* A prong overlapping a stone's girdle, or a bezel wall surrounding it, is a reference-volume intersection. A seat is a deliberately cut bearing surface the stone rests on. The first exists; the second does not, and calling the first the second would be a fabricated capability claim.

## Professional validation

Every family is `NOT_REVIEWED`, and `test_setting.py::TestNoFakeProfessionalValidation` asserts three things: no family claims validation, no matrix row claims validation, and every family is `generatable AND not VALIDATED` simultaneously — the last specifically to keep the two axes from being conflated.

The active professional-validation registry remains at **zero records**, verified independently by the Capability Coverage Guard.

## The cross-product Capability Coverage Guard

Beyond the Setting registry, this Sprint introduced `specs/capabilities/jewelmind-capabilities.json`: **101 capabilities across 26 domains**, each with a `CURRENT`/`PARTIAL`/`PLANNED`/`BLOCKED`/`OUT_OF_SCOPE` status and a substantive note.

Its value is that it cannot quietly lie. `backend/tests/test_capability_coverage.py` checks it against the real code wherever the code can answer:

- `CURRENT` setting families must equal the live `SETTING_CAPABILITIES` keys.
- `PLANNED` setting families must **not** be registered generators.
- `CURRENT` stone shapes must equal the live stone registry; `PLANNED` shapes must not be accepted by JDL.
- `CURRENT` jewelry categories must equal the categories with `generationSupported`.
- Every escape hatch must be present and `PLANNED`/`PARTIAL`.
- No entry may claim professionally validated setting geometry.
- Every entry needs a note of real length — a status with no justification is unauditable, and this test caught five genuinely thin notes on its first run.

Current distribution: 30 `CURRENT`, 1 `PARTIAL`, 66 `PLANNED`, 1 `BLOCKED`, 3 `OUT_OF_SCOPE`. The single `BLOCKED` entry is the live Designer provider credential, which genuinely cannot be exercised in this environment.

## Adding a family

1. An RFC (a new setting family is a jewelry-domain extension).
2. A generator, registered in `SETTING_GENERATORS`.
3. A `SETTING_CAPABILITIES` entry with an **honest** compatibility list and `NOT_REVIEWED` status.
4. Regenerate `setting-registry.json` from the live registry; never hand-edit.
5. Update the two hand-mirrored consumers: Studio's `SETTING_TYPE_OPTIONS` and Designer's `SETTING_TYPE_SYNONYMS`.
6. Real inspection facts and its own new Golden case (SETTING-GOV-015).
7. Update the Capability Coverage Guard.
