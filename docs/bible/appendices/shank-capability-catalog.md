---
id: JM-BIBLE-A111
title: "Appendix: Shank Capability Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-SHANK-README
  - JM-BIBLE-540
related_documents:
  - JM-BIBLE-A105
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Shank Capability Catalog

The complete, current catalog of all 17 named Shank capabilities — the human-readable companion to `specs/shank/v1/capability-registry.json`, which is generated from and re-derived live against `backend/jewelmind/geometry/shank/capability.py::SHANK_CAPABILITIES`, the real source of truth (SHANK-GOV-015). No documentation, Designer capability list, or Studio copy may claim a capability this registry marks `planned`.

| Capability | Status | `jdlExposed` | `generatable` | `inspectable` | Description |
|---|---|---|---|---|---|
| `uniform_shank` | current | true | true | true | Constant width/thickness all the way around — the pre-Sprint-17 default. |
| `flat_profile` | current | true | true | true | Rectangular cross-section, optional outer-rim fillet (uniform shank only). |
| `comfort_fit_profile` | current | true | true | true | Shallow outward-bulging inner edge; optional outer-rim fillet (uniform shank only). |
| `width_taper_toward_bottom` | current | true | true | true | Full base width at the head, linearly tapering to bottomRatio*base at the bottom. |
| `thickness_taper_toward_bottom` | current | true | true | true | Full base thickness at the head, linearly tapering to bottomRatio*base at the bottom. |
| `combined_width_and_thickness_taper` | current | true | true | true | Width and thickness taper applied together, independently controlled. |
| `outer_rim_fillet_on_tapered_shank` | planned | false | false | false | No single 'circle at radius X' exists once the radius varies by angle; not yet implemented. |
| `taper_toward_head` | planned | false | false | false | Would move the connection-interface anchor away from u=0; deliberately out of v1 scope. |
| `designer_taper_proposal` | planned | false | false | false | Designer may not propose widthTaper/thicknessTaper this Sprint (not in KNOWN_JDL_FIELD_PATHS). |
| `studio_taper_editor` | planned | false | false | false | No Studio UI control for taper this Sprint — JDL/API-only. |
| `split_shank` | planned | false | false | false | Multiple rails — architecture reserves the concept, v1 builds exactly one rail. |
| `cathedral_shank` | planned | false | false | false | Belongs primarily to shoulder/head integration, not a profile type. |
| `knife_edge_profile` | planned | false | false | false | A third section-profile type; not implemented. |
| `euro_shank` | planned | false | false | false | A modified centerline path; the current path is circular only. |
| `twisted_shank` | planned | false | false | false | Not implemented. |
| `multi_rail_shank` | planned | false | false | false | See split_shank — the general case of more than one rail. |
| `sculpted_shank` | planned | false | false | false | Local, non-parametric sculpting; not implemented. |

**Total: 17 capabilities. Current: 6. Planned: 11.**

## Invariant enforced by test

`backend/tests/test_shank.py::TestShankCapabilityRegistry::test_no_planned_capability_is_marked_generatable_or_jdl_exposed` and `backend/tests/test_shank_schemas.py::test_capability_registry_never_lists_a_planned_capability_as_generatable` both assert every `status: "planned"` entry has `generatable: false` and `jdlExposed: false` — no capability can be marked reachable while still labeled planned.

## Cross-references

- `backend/jewelmind/geometry/shank/capability.py` — the real source of truth.
- `specs/shank/v1/capability-registry.json` — the machine-readable mirror, re-derived live by `test_capability_registry_matches_the_real_capability_registry_live`.
- [`557-shank-capability-model.md`](../19-shank/557-shank-capability-model.md) — full narrative contract.
- [`shank-profile-catalog.md`](shank-profile-catalog.md) — geometric detail for `flat_profile`/`comfort_fit_profile`/`knife_edge_profile`.
