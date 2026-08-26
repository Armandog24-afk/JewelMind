---
id: JM-BIBLE-502
title: Golden Suite Selection
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-QUALITY-README
  - JM-BIBLE-500
related_documents:
  - JM-BIBLE-501
  - JM-BIBLE-DOMAIN-README
implementation_status: current
professional_validation: not_required
normative: false
---

# Golden Suite Selection

## Selection rationale

Every case in the Golden Suite is a real, schema-valid `JewelryDefinition` — either the exact default (`jewelmind.domain.defaults.default_definition()`) or that default with one or more fields changed to another already-valid value already accepted elsewhere in the domain schema. No case introduces an invented "professional" value, a new enum member, or a value outside the schema's existing bounds (QUALITY-GOV-002). The generating script, `backend/generate_golden_fixtures.py`, is a one-off fixture-authoring tool — run once against the real pipeline, then deleted before this Sprint's final commit, the same discipline Sprint 14 applied to `generate_inspection_specs.py`. It is not a permanently-present part of the shipped package.

## The 9 real cases

| Golden ID | What it varies |
|---|---|
| `SOL-001-default-solitaire` | The canonical default solitaire (6-prong, comfort-fit band) — no fields changed from `default_definition()`. |
| `SOL-002-four-prong-comfort-fit` | `setting.prongCount = 4`; all other fields default. |
| `SOL-003-six-prong-flat` | `band.profile = "flat"`; prong count stays at the default 6. |
| `SOL-004-four-prong-flat` | `setting.prongCount = 4` and `band.profile = "flat"` together. |
| `SOL-005-ring-size-variation` | `ring.size = 18` with `ring.innerDiameter` recomputed via `eu_size_to_inner_diameter(18)`, exercising ring-size-to-diameter scaling. |
| `SOL-006-band-dimension-variation` | `band.width = 3.2`, `band.thickness = 2.2` (wider, thicker band). |
| `SOL-007-stone-dimension-variation` | `stone.diameter = 7.5`, `stone.depth = 4.6` (larger stone, still within the 6-prong default's comfortable range). |
| `SOL-008-prong-basket-dimension-variation` | `setting.prongDiameter = 1.3`, `setting.prongHeight = 5.5`, `setting.basketHeight = 4.0`. |
| `SOL-009-warning-only-large-stone-four-prong` | `setting.prongCount = 4` and `stone.diameter = 9.0` — a valid, generatable definition that also triggers Forge warning `JM-PRONG-003` (`PRONG_COUNT_VS_STONE_SIZE`: stones over 8mm are typically more secure with six prongs). This is expected and recorded in the golden's `knownLimitations`, not treated as a defect. |

`goldens/solitaire-v1/manifest.json` lists all 9 under `fullSuite` and a 3-case subset (`SOL-001`, `SOL-002`, `SOL-003`) under `fastSuite` for quick local iteration.

## Why there is no separate "6-prong comfort-fit" case

The brief's minimum-coverage list names both "default solitaire" and "6-prong comfort-fit" as categories to cover. `SOL-001-default-solitaire`'s own description states plainly that it "also represents the '6-prong comfort-fit' case from the brief's selection list — deliberately not duplicated as a separate golden since its geometry is identical." The default solitaire already **is** the 6-prong, comfort-fit-band configuration (`default_definition()`'s prong count is 6 and its band profile default is `comfort-fit`); a tenth golden case built from the identical `JewelryDefinition` would produce a byte-for-byte identical `GeometrySnapshot` to `SOL-001`, adding suite runtime with zero additional regression coverage. This is a deliberate, documented decision — not a shortfall against the brief's minimum-10-categories language, since two of the ten named categories collapse onto one real geometry.

## What each case actually exercises

- **Prong count**: `SOL-001`/`SOL-003` (6), `SOL-002`/`SOL-004`/`SOL-009` (4).
- **Band profile**: `SOL-001`/`SOL-002`/`SOL-005` through `SOL-009` (comfort-fit, the default), `SOL-003`/`SOL-004` (flat).
- **Ring size / inner diameter scaling**: `SOL-005` only.
- **Band dimensions**: `SOL-006` only.
- **Stone dimensions**: `SOL-007`, and `SOL-009` at a larger, warning-triggering size.
- **Prong/basket dimensions**: `SOL-008` only.
- **A warning-only-but-valid range**: `SOL-009` only — the one case whose `knownLimitations` is non-empty.

## Independent reverification at authoring time

`generate_golden_fixtures.py::main()` does not merely write each `snapshot.json` and stop — after writing all 9 cases and the manifest, it calls `verify_golden()` against every case's own just-written baseline and raises `SystemExit` if any case fails to reverify as `PASS`/`PASS_WITH_KNOWN_LIMITATIONS`. Every accepted golden in the suite was independently reverified against its own saved baseline before being treated as accepted, not merely generated and trusted.
