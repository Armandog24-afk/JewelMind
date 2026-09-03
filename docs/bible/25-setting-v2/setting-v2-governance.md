---
id: JM-BIBLE-SETTINGV2-GOVERNANCE
title: "Setting System v2 governance"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-03
source_of_truth: true
depends_on:
  - JM-BIBLE-SETTINGV2-README
implementation_status: current
professional_validation: not_required
normative: true
---

# Setting System v2 governance

Twelve rules, on top of Sprint 19's eighteen `SETTING-GOV` rules, which all
still apply. Each is enforced by a named test where enforcement is possible.

## SETTINGV2-GOV-001 — the head is category-neutral

Head construction lives in `jewelmind/setting/head.py`, driven by
`HeadSettingDefinition` plus the generic attachment interface. It must never
read a band, a ring size or any category field; the Ring adapter resolves those
and passes numbers (SETTING-GOV-001/014 restated for the head).

*Enforced by* `test_setting_system_no_ring_dependency.py` (AST inspection over
the whole package).

## SETTINGV2-GOV-002 — the head component name is fixed

Every architecture produces a component named `basket_support`. The name is a
structural role, wired into `geometry/roles.py`, the inspection
required-component set, every preview manifest, every export list and all 39
Golden baselines. The architecture is reported in
`SettingGeometryResult.headArchitecture` and in the component metadata, never
in the name.

*Enforced by* `test_setting_v2.py::TestHeadArchitectures::test_every_architecture_keeps_the_component_name`.

## SETTINGV2-GOV-003 — legacy geometry is preserved exactly

`ROUND_PRONG` and `BASKET` reproduce their pre-Sprint-23 constructions
character-for-character, and the Ring adapter passes the **original** basket
bore expression rather than re-deriving it. A default design's fused metal
volume must not move, and no Golden baseline may be updated for this sprint.

*Enforced by* `test_setting_v2.py::TestBackwardCompatibility` and the full
39-case Golden suite.

## SETTINGV2-GOV-004 — a style or architecture registry entry has a real builder

`PRONG_STYLE_CAPABILITIES` and `HEAD_ARCHITECTURE_CAPABILITIES` must agree with
`prong_solid_builders()` and `head_builders()` in **both** directions. An entry
with no builder advertises a capability that does not exist; a builder with no
entry ships one nobody declared.

*Enforced by* `test_setting_v2.py::TestCapabilityConsistency` and
`test_capability_coverage.py::test_advanced_head_and_prong_capabilities_match_the_live_registries`.

## SETTINGV2-GOV-005 — an unimplemented architecture is not an enum member

`HeadArchitecture` and `ProngStyle` are closed enums whose every member has a
builder. A reserved name (`trellis`, `cathedral`, `compass_point`,
`double_gallery`) lives in `RESERVED_HEAD_ARCHITECTURES` with a real reason, is
refused by the model, and must never be silently substituted with a basket.

*Enforced by* `test_setting_v2.py::TestCapabilityConsistency::test_reserved_names_have_no_builder`
and `::test_an_unregistered_architecture_is_refused_before_construction`.

## SETTINGV2-GOV-006 — every head is one connected solid

A builder that produces more than one solid raises. `PEG_HEAD` originally
produced two — a floating basket above an unattached peg, because a peg
narrower than the wall's bore never touches it — and shipping that would have
been a head that is not a head.

*Enforced by* `test_setting_v2.py::TestHeadArchitectures::test_every_architecture_builds_one_connected_solid`
and a check inside `_peg_head()` itself.

## SETTINGV2-GOV-007 — the vertical extent is architecture-independent

Every head spans the same Z range for the same attachment interface, so
choosing a martini never moves the stone. An architecture that needed more room
must take it from its own base, not by growing upward.

*Enforced by* `test_setting_v2.py::TestHeadArchitectures::test_every_architecture_spans_the_same_vertical_extent`.

## SETTINGV2-GOV-008 — seat relief is a cut, never a fuse

`REFERENCE_SEAT` uses the stone solid as a cutting tool. No code in `seat.py`
may call `.fuse()` on a stone shape, and the stone must never become part of
the production body (LAW-006, ATLAS-GOV-011). The operation performed is
recorded in the component metadata as `CUT_STONE_FROM_METAL`, so no reader has
to trust it.

*Enforced by* `test_setting_v2.py::TestSeatRelief::test_relief_never_fuses_the_stone_into_metal`
(AST inspection of `seat.py`).

## SETTINGV2-GOV-009 — relief is relief, not a seat

`REFERENCE_SEAT` has no bearing shoulder and no claim that a stone would sit
correctly in it. `seatSupport` is `PARTIAL`, never `CURRENT`, and
`bearingSupport`/`cutterSupport` stay `PLANNED` until real sourced professional
geometry exists for them.

*Enforced by* `test_setting_v2.py::TestCapabilityConsistency::test_seat_support_is_partial_not_current`
and `test_capability_coverage.py::test_seats_bearings_and_cutters_are_reported_honestly`.

## SETTINGV2-GOV-010 — no invented professional threshold

No rule, model or message may judge prong thickness for a stone size, head wall
castability, seat depth, or whether a setting would hold. Every taper ratio,
notch angle, section count and clearance is a CONSTRUCTION PARAMETER and says
so (SETTING-GOV-010 restated for the new parameters).

*Enforced by* `test_setting_v2.py::TestSettingV2Rules::test_no_setting_v2_rule_invents_a_professional_threshold`,
which scans the real emitted messages rather than the source.

## SETTINGV2-GOV-011 — the setting carries stone references and never resolves them

`stoneInstanceAssignments` holds opaque instance IDs. Nothing under
`jewelmind/setting/` may import `jewelmind.arrangement`, so a setting can
reference an instance without depending on the layer that defines it.

*Enforced by* `test_setting_v2.py::TestStoneInstanceMapping::test_the_setting_system_never_resolves_a_stone_instance_id`.

## SETTINGV2-GOV-012 — explicit and derived layouts never mix

A caller states every prong position or none. `positionSource="EXPLICIT"` with
no positions raises rather than falling back to the derived strategy, and a
group naming a non-existent position index raises rather than applying a
requested style to nothing.

*Enforced by* `test_setting_v2.py::TestExplicitPositions`.

## When an ADR is required

- Renaming the head component, or emitting more than one head per setting.
- Replacing the registry dispatch for styles or architectures with anything
  else.
- Letting the stone shape reach a fuse, for any reason.
- Making relief the default, or changing what `REFERENCE_SEAT` cuts.
- Moving head construction back out of the Setting System.
- Changing `ROUND_PRONG` or `BASKET` construction (which would move every
  existing design's geometry and require a documented Golden update).

## When an RFC is required

- A new head architecture or prong style beyond those implemented, including
  any reserved name.
- Support rails, or any multi-head structure.
- A real cut seat with a bearing shoulder, or cutter geometry.
- Anchor-driven or instance-aware prong placement.
- Any professional threshold on prong, head or seat dimensions, which
  additionally requires real professional validation before it may block
  anything.
