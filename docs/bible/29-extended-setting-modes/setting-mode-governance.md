---
id: JM-BIBLE-ESM-GOVERNANCE
title: "Extended Setting Modes governance"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-09
source_of_truth: true
depends_on:
  - JM-BIBLE-ESM-README
implementation_status: current
professional_validation: not_required
normative: true
---

# Extended Setting Modes governance

Fourteen rules. Each is enforced by a named test where enforcement is possible,
because a governance rule nothing checks is a preference.

All 18 SETTING-GOV rules (Sprint 19) and all 12 SETTINGV2-GOV rules (Sprint 23)
continue to apply unchanged. These add to them; none replaces one.

## ESM-GOV-001 — Extended Setting Modes is an extension, never a second engine

Every setting family is reached through `dispatch.py::generate_setting()` and
registered in `setting_generators()`. There is exactly one dispatch, one head
step and one seat step. A family generator must not be called from anywhere
else, and the assembly calls `generate_setting()` exactly once.

*Enforced by* `test_extended_setting_modes.py::TestCompilerIntegration::test_there_is_exactly_one_compilation_path`
and `::TestArchitecturalAudit::test_no_geometry_path_bypasses_the_single_dispatch`.

## ESM-GOV-002 — the mode registry is DERIVED, never declared

`setting_modes()` measures each row's `settingGeometry` from the live builder
registries. A row may not declare that axis, and a builder may not exist without
a row. Both directions are checked.

This is the difference between a registry and a fifth parallel copy of one.
Sprint 20 removed three hand-copied registries that had already drifted and
caused Designer and Setting to misreport real capabilities; the measurement is
what makes that class of drift impossible here rather than unlikely.

*Enforced by* `::TestModeRegistry::test_geometry_is_claimed_only_where_a_builder_exists`,
`::test_every_prong_mode_names_a_real_body_builder` and
`test_capability_coverage.py::test_no_setting_mode_claims_geometry_without_a_builder`.

## ESM-GOV-003 — the three axes stay separate

`PRIMARY`, `HEAD` and `RETENTION` are independent and simultaneous. A HEAD or
RETENTION mode declared as `setting.mode` is REFUSED, because the head
architecture is chosen by `setting.headArchitecture` and field retention by the
pavé's own strategy — declaring one in `setting.mode` would be a second
authority over an axis that already has one.

*Enforced by* `::TestModeResolution::test_a_head_or_retention_mode_cannot_be_declared_as_primary`
and `::TestModeRegistry::test_every_mode_is_on_exactly_one_axis`.

## ESM-GOV-004 — `setting.mode` refines `setting.type`; it never competes with it

`setting.type` names the family and selects the generator. `setting.mode` names
the variant within that family and carries its parameters. A mode whose family
disagrees with `type` is REFUSED rather than resolved by precedence: two
authorities over one setting have no determinate resolution, the same reason
`JM-FAMILY-001` refuses a family and an arrangement together.

*Enforced by* `::TestModeResolution::test_a_family_mismatch_is_refused_rather_than_resolved`,
`JM-SETTING-008`, and the frontend mirror's own
`settingModeValidation.test.ts`.

## ESM-GOV-005 — resolution happens in exactly one place

`resolve_primary_mode()` is the single resolution point, the role
`family/effective.py::effective_arrangement()` plays for placement. A consumer
that derived the mode from `type`/`prongStyle` itself would eventually disagree,
and the disagreement would surface as geometry that does not match what Studio
displayed.

*Enforced by* `::TestCompilerIntegration::test_the_adapter_carries_the_resolved_mode_and_its_identity`.

## ESM-GOV-006 — a document with no mode keeps its existing meaning

`setting.mode = null` resolves to the variant the document's existing
`type`/`prongStyle` fields already meant. Every pre-Sprint-27 design must
generate byte-identical geometry, and a default prong solitaire's metal volume
must stay `341.44334316909976 mm³`.

*Enforced by* `::TestModeResolution::test_a_document_with_no_mode_resolves_to_its_existing_meaning`,
`::TestGeometry::test_the_default_prong_solitaire_is_byte_identical`, and zero
changed Golden baselines.

## ESM-GOV-007 — a new family carries stone references and never resolves them

Nothing under `jewelmind/setting/` may import `jewelmind.arrangement`. A channel
spanning a row records the arrangement instance ids it holds as **opaque
strings**; the arrangement remains the authority on where those instances are.
A setting states its own extent and never computes a stone position.

*Enforced by* `::TestArchitecturalAudit::test_no_new_module_imports_the_arrangement_layer`
and `::test_there_is_no_second_placement_engine`, both AST-parsed.

## ESM-GOV-008 — a new family is category-neutral

Nothing under `jewelmind/setting/` may import `jewelmind.ring`, a jewelry
category, the Shank subsystem, the connection interface, the setting adapter, or
`JewelryDefinition`. A family receives an `attachmentPlaneZMm`/`embedMm`/
`supportHeightMm` triple and works from that.

`modes.py` is additionally KERNEL-FREE, because it is carried in JDL and read by
Forge — the same split `geometry/pave_surface.py` documents for host resolution.

*Enforced by* `::TestArchitecturalAudit::test_no_new_module_imports_ring_or_a_jewelry_category`,
`::test_no_new_module_imports_the_jewelry_definition` and
`::test_the_domain_layers_are_kernel_free`.

## ESM-GOV-009 — a recess is a CUT, and relief is never called a seat

The flush collar's recess and the tension supports' grooves are the existing
`REFERENCE_SEAT` relief, routed through `setting/seat.py` — the module whose own
source is asserted never to call `.fuse()` on a stone shape. The stone is a
cutting TOOL and never becomes production metal.

`REFERENCE_SEAT` has no bearing shoulder and no claim that a stone would sit
correctly in it. `bearingSupport` and `cutterSupport` stay PLANNED for all six
families.

*Enforced by* `::TestArchitecturalAudit::test_the_recess_is_a_cut_and_never_a_fuse`,
`::TestGeometry::test_the_stone_is_never_fused_into_the_metal` for every family,
and `test_setting_v2.py::test_seat_support_is_partial_not_current`.

## ESM-GOV-010 — a family whose recess IS its geometry refuses to build without it

A flush setting without relief is a solid mass with the stone buried inside it —
not a flush setting and not anything. The generator RAISES and
`JM-SETTING-010` reports it before generation is attempted.

This is a GEOMETRIC precondition, not a professional requirement.

*Enforced by* `::TestGeometry::test_a_flush_setting_without_relief_refuses_rather_than_burying_the_stone`
and `::TestForgeRules::test_a_flush_setting_without_relief_is_an_error`.

## ESM-GOV-011 — reject, never repair, and never clamp

An impossible request is refused rather than adjusted: openings that would remove
the whole bezel wall, a rim taller than the stone's crown, supports that would
meet through the middle of the stone, a degenerate prism, a window set that
would sever the head wall. Reducing a value to fit would build something the
author never described, which is the silent substitution SETTING-GOV-013 forbids.

*Enforced by* `::TestSchema::test_openings_that_would_remove_the_whole_wall_are_refused`,
`::TestGeometry::test_a_flush_rim_above_the_crown_is_refused`,
`::test_tension_supports_that_would_meet_through_the_stone_are_refused` and
`::TestFrameArithmetic::test_a_degenerate_prism_raises`.

## ESM-GOV-012 — no invented professional threshold, and no claim of one

No minimum wall thickness, minimum bar, collar thickness, clearance, spacing or
settability judgment exists anywhere in this sprint. Every dimension is a
CONSTRUCTION PARAMETER from the document, and every constant in the new modules
is either a geometric robustness value or a construction resolution, documented
as such.

`JM-SETTING-011` is the only numeric rule and it is a MATHEMATICAL CONSTRAINT: a
rim taller than the whole stone buries it, and two supports reaching past the
half-extent meet through its middle. Both are arithmetic.

`JM-SETTING-012` carries the PROFESSIONAL REVIEW category as a `warning` — the
three severities are a published contract — with
`professionalValidationStatus: required` on its registry entry, which is where
that distinction already lives. **A review requirement is not a verdict**: it
says a qualified human must look, not that anyone has.

*Enforced by* `::TestNoInventedThresholds`, which reads this sprint's own source
files, the capability registry's descriptions, and every Forge message.

## ESM-GOV-013 — no component is anonymous

Every generated setting component carries a `SettingComponentProvenance` record
naming the mode, the source stone, the arrangement instances it holds, and
whether it is production metal or reference geometry. A requested count that
could not be honoured is reported as requested-versus-generated rather than
being quietly smaller.

`GeometryPlan` is NOT materialized to hold this. A fact about a component lives
where the component's other facts live; materializing `GeometryPlan` is an
explicit ADR condition and would have been a speculative abstraction here.

*Enforced by* `::TestInspection::test_every_generated_component_carries_provenance`
for every family, and `::test_the_mode_facts_are_reported_for_every_family`.

## ESM-GOV-014 — a new mode needs a NEW Golden case, never a retrofit

`ESM-001`–`ESM-007` cover the current scope, one per real capability rather than
one per number. Every accepted baseline needs an entry in
[`golden-update-register.md`](../appendices/golden-update-register.md) and an
honest `knownLimitations`; today those are
`EXTENDED_SETTING_MODES_AWAITING_PROFESSIONAL_REVIEW`,
`TENSION_STRUCTURAL_BEHAVIOUR_NOT_MODELLED`,
`REFERENCE_RELIEF_IS_NOT_A_CUT_SEAT` and `SETTING_COVERAGE_PRIMARY_ONLY`.

No existing baseline may be modified: `BEZEL_FULL`, `BASKET` and `ROUND_PRONG`
reproduce their previous constructions exactly, so all 54 pre-existing baselines
must stay untouched.

*Enforced by* `python -m jewelmind.geometry_quality.cli verify-all` plus
`git status --porcelain goldens/`, and by QUALITY-GOV-003/004's requirement that
no code path other than `accept --reason` writes a baseline.

## When an ADR is required

- Letting a setting family compute a stone's position, or accepting a second
  placement authority.
- Merging any of the four capability axes (`representable`, `compilable`,
  `stoneGeometry`, `settingGeometry`), or replacing the derived
  `settingGeometry` measurement with a declaration.
- Resolving a `setting.mode`/`setting.type` disagreement by precedence rather
  than refusing it.
- Materializing `GeometryPlan`, or moving component provenance onto it.
- Adding a fourth mode axis, or letting one axis select another.
- Changing the derived component names (`channel_walls`, `bars`,
  `flush_collar`, `tension_supports`), or emitting more than one component per
  family.
- Letting the stone shape reach a `.fuse()` call anywhere.

## When an RFC is required

- Any setting mode beyond the twenty implemented, **including every reserved
  name** — a trellis head, azure piercing, a shared-wall or tapered channel, a
  tapered bar, millgrain, an open-back bezel, an under-gallery support, or
  retention for a halo's own stones.
- A real cut seat with a bearing shoulder, or cutter geometry.
- Anchor-driven or instance-aware prong placement (the identified next step for
  `PRONG_SHARED` — do not bypass it).
- Any professional threshold on a wall, bar, collar, clearance or grip.
- A structural model of a tension setting, which additionally requires real
  engineering evidence and a professional-validation record.
