---
id: JM-BIBLE-A107
title: "Appendix: Ring Family Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-RING-README
  - JM-BIBLE-520
related_documents:
  - JM-BIBLE-524
implementation_status: current
professional_validation: not_required
normative: false
---

# Appendix: Ring Family Catalog

All 8 `RingFamilyId` values
([`backend/jewelmind/ring/models.py`](../../../backend/jewelmind/ring/models.py)),
cross-checked against
[`RING_FAMILY_GENERATORS`](../../../backend/jewelmind/ring/families.py)
and `RESERVED_PLANNED_RING_FAMILIES` in
[`backend/jewelmind/ring/families.py`](../../../backend/jewelmind/ring/families.py).

| `RingFamilyId` value | Status | Real generator in `RING_FAMILY_GENERATORS` |
|---|---|---|
| `solitaire` | CURRENT | `build_solitaire_ring` |
| `three_stone` | PLANNED | none |
| `toi_et_moi` | PLANNED | none |
| `halo` | PLANNED | none |
| `eternity` | PLANNED | none |
| `signet` | PLANNED | none |
| `plain_band` | PLANNED | none |
| `cluster` | PLANNED | none |

Only `solitaire` has a real generator. The other 7 are recognized,
reserved values in `RingFamilyId` and in `RESERVED_PLANNED_RING_FAMILIES`
— a real value the type system accepts as valid, never a fake
implementation (JEWELRY-ARCH-GOV-010). Requesting one of the 7 PLANNED
families raises `RingFamilyUnsupportedError`
(`backend/tests/test_ring_architecture.py::TestSolitaireFamilyDispatch::test_unsupported_ring_family_raises_a_clean_error`),
never a silent fallback to `solitaire`.
`test_reserved_planned_families_have_no_generator_yet` verifies all 7
PLANNED families are absent from `RING_FAMILY_GENERATORS`.
