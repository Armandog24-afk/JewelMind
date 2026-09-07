---
id: JM-BIBLE-HALO-GOVERNANCE
title: "Halo System governance"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-07
source_of_truth: true
depends_on:
  - JM-BIBLE-HALO-README
implementation_status: current
professional_validation: not_required
normative: true
---

# Halo System governance

Twelve rules. Each is enforced by a named test where enforcement is possible,
because a governance rule nothing checks is a preference.

## HALO-GOV-001 — the halo layer is category- and kernel-neutral

Nothing under `backend/jewelmind/halo/` may import a jewelry category, any
geometry module, the Setting System, the CAD kernel, or `JewelryDefinition`
(which would smuggle the whole ring domain across in one import).

`halo/__init__.py` must import nothing: `domain/schema.py` imports
`halo.models`, so an eager init would make the graph cyclic — the trap
`jewelmind/stone/`, `jewelmind/gem/`, `jewelmind/arrangement/` and
`jewelmind/family/` each document.

*Enforced by* `test_halo.py::TestArrangementIsTheAuthority::test_the_halo_layer_never_imports_a_category_or_the_kernel`
and `::test_the_halo_package_init_imports_nothing`, both AST-parsed rather than
`import`-based, so they cannot pass by accident on an already-cached module.

## HALO-GOV-002 — the arrangement remains the placement authority

`halo/compile.py` emits `StoneInstanceDef`s and `ArrangementRelation`s and
nothing else. It never computes a placement the arrangement layer would compute
differently, and it must never become a second placement engine.

The ring's angular sequence comes from
`arrangement/radial.py::ring_angles_deg()` — the same function the resolver uses
to expand a `RADIAL` pattern. A copy of that arithmetic inside the halo layer is
forbidden: two copies drift, and the symptom is a halo whose stones sit where a
hand-written pattern's would not.

*Enforced by* `test_halo.py::TestSingleHalo::test_the_angular_sequence_matches_a_radial_pattern`,
which compares against the real resolver's own `RADIAL` expansion, and
`::test_the_ring_arithmetic_is_shared_rather_than_copied`.

## HALO-GOV-003 — a halo composes; it never replaces

A halo is added to whatever placement a design declares. It must never override,
discard or rewrite a family's or an arrangement's instances, patterns or
relations, and `compose_halo(base, None)` must return `base` itself.

A halo must never become a `FamilyType` member. See
[`halo-rfc.md`](halo-rfc.md).

*Enforced by* `test_halo.py::TestFamilyComposition` and
`::TestBackwardCompatibility::test_composing_no_halo_returns_the_base_object`.

## HALO-GOV-004 — the centre is resolved, never guessed

A named `centerMemberId` is looked up by id in the arrangement being composed
onto. An absent centre raises; it is never re-anchored on the design origin,
because a halo around the wrong stone is worse than one that fails loudly.

`centerMemberId: null` anchors on the design origin, and that is the only
sanctioned way to surround a multi-stone centre.

The authoritative check is **derived** from the real compiled instances.
`HALO_COMPOSITION` is a REPORTING table that explains an unsupported
combination; it must never become the gate, and a test re-derives every row by
actually composing.

*Enforced by* `test_halo.py::TestFamilyComposition::test_a_named_centre_a_family_does_not_have_is_refused`
and `::TestCompositionSupport::test_the_support_table_matches_the_real_compiler`.

## HALO-GOV-005 — the halo model holds no kernel object and no stone data

No field may hold a `cadquery.Shape`, `Workplane` or `OCP` object. No field may
restate a shape, dimension, material or visual profile: a ring REFERENCES a
stone specification and may carry a `GemIdentity`.

Per-stone overrides reuse `FamilyMember` and `placementOverride` reuses
`InstanceTransform`. A parallel member or transform model is forbidden — it
would be two definitions of one concept.

*Enforced by* `test_halo.py::TestHaloModel::test_a_halo_holds_no_kernel_object`,
`::test_a_halo_references_stones_rather_than_restating_them` and
`::test_per_stone_overrides_reuse_the_family_member_model`.

## HALO-GOV-006 — identity is by id, never by array position

Reordering `rings`, or a ring's `members`, must not change the composed
arrangement, its canonical JSON or its `arrangementFingerprint`. Named members
are matched to ring positions by sorted id.

*Enforced by* `test_halo.py::TestDeterminism::test_ring_order_carries_no_meaning`
and `::test_member_order_carries_no_meaning`.

## HALO-GOV-007 — composition is deterministic and repeatable

No wall-clock time, no randomness, no memory-derived value, no runtime-generated
identifier. Derived ids are `<ringId>.<index>`, reproducible from the ring's own
id and the stone's position in the angular sequence — never a counter across
rings, a UUID or a timestamp.

*Enforced by* `test_halo.py::TestDeterminism::test_composition_is_repeatable`,
`::test_derived_ids_are_reproducible_and_not_counters` and
`::test_geometry_is_deterministic_across_rebuilds`.

## HALO-GOV-008 — reject, never repair

A variant/ring-count mismatch, a duplicate id, a member with no position, a
hidden halo that is not below the centre plane, an unresolvable centre, an id
collision or an over-capacity halo raises. Nothing fills in a plausible ring,
truncates a member list, or substitutes a `SINGLE` halo for a reserved variant.

*Enforced by* `test_halo.py::TestHaloModel` and
`specs/halo/v1/test-vectors/invalid-halo-vectors.json`, which records WHICH
layer refused each case.

## HALO-GOV-009 — `HIDDEN` is a structural claim, enforced

A `HIDDEN` halo's ring must carry a negative `zOffsetMm`. No minimum offset is
prescribed and none may be without sourced professional evidence; what is
checked is only that a halo calling itself hidden is below the centre plane,
because a hidden halo at or above it is a `SINGLE` halo mislabelled and the
label is what every downstream consumer reads.

The offset must reach the SOLID, not only the metadata.

*Enforced by* `test_halo.py::TestHaloModel::test_a_hidden_halo_must_sit_below_the_centre_plane`
and `::TestHiddenHalo::test_the_vertical_offset_reaches_the_solid`, which
measures the built geometry's bounding box rather than trusting the field.

## HALO-GOV-010 — no invented jewelry threshold

No model, rule or message may state a minimum halo stone spacing, a
centre-to-halo proportion, a settable radius, a stone-count limit presented as a
design limit, or whether a hidden halo clears the centre stone's pavilion. Each
needs sourced professional evidence this project does not have.

`MAX_HALO_RINGS`, `MAX_HALO_STONES_PER_RING` and `MAX_HALO_STONES` are software
bounds and say so. `radiusMm` is a POSITION parameter, never a clearance — this
layer knows no stone's size. Whether two placed stones overlap is a GEOMETRIC
fact for Geometry Inspection.

*Enforced by* `test_halo.py::TestHaloRules::test_no_halo_rule_invents_a_professional_threshold`,
which scans the REAL emitted messages rather than the source, so a threshold
cannot hide in a string the test never sees.

## HALO-GOV-011 — capability status distinguishes four axes

`representable`, `composable`, `stoneGeometry` and `settingGeometry` are
independent. No variant may be marked `CURRENT` while `settingGeometry` is
`false`: halo stones exist and halo metal does not, and collapsing the two would
turn "the stones exist" into "the halo is complete".

Every registry entry, and every entry it mirrors into
`specs/capabilities/jewelmind-capabilities.json`, must be backed by a real
compiler in both directions.

*Enforced by* `test_halo.py::TestCapabilityRegistry` and
`test_capability_coverage.py::test_halo_capabilities_match_the_live_registry`
plus `::test_no_halo_claims_a_setting_it_does_not_build`.

## HALO-GOV-012 — an absent halo stays absent

`compose_halo(base, None)` returns `base`, nothing synthesizes a halo for a
single-stone design, and a document declaring neither a halo, a family nor an
arrangement must generate byte-identical geometry to its pre-Sprint-22 self.

A halo IS inside `geometryHash`, because it moves stones: excluding it would
serve stale geometry for a real design change.

*Enforced by* `test_halo.py::TestBackwardCompatibility` and
`::TestDeterminism::test_a_halo_change_changes_both_identities`.

## When an ADR is required

- letting the halo layer construct geometry or compute placements of its own;
- accepting both a family and an arrangement;
- merging any of the four capability axes;
- changing the derived member-id scheme;
- changing what `geometryHash` includes;
- moving the design-level placement resolution point out of
  `family/effective.py`.

## When an RFC is required

- a halo variant beyond the three implemented, including any reserved name;
- **a setting strategy for halo stones** — the identified next step, and
  deliberately not pre-empted here;
- an outline-following halo;
- per-halo-stone stone specifications (a compass halo);
- any professional halo proportion, spacing or settability rule.
