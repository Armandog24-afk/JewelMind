---
id: JM-BIBLE-PAVE-GOVERNANCE
title: "Pavé & Microsetting governance"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-08
source_of_truth: true
depends_on:
  - JM-BIBLE-PAVE-README
implementation_status: current
professional_validation: not_required
normative: true
---

# Pavé & Microsetting governance

Fourteen rules. Each is enforced by a named test where enforcement is possible,
because a governance rule nothing checks is a preference.

## PAVE-GOV-001 — the pavé layer is category- and kernel-neutral

Nothing under `backend/jewelmind/pave/` may import a jewelry category, any
geometry module, the Setting System, the CAD kernel, or `JewelryDefinition`.
`pave/__init__.py` must import nothing: `domain/schema.py` imports
`pave.models`, so an eager init would make the graph cyclic — the trap
`stone`, `gem`, `arrangement`, `family` and `halo` each document.

*Enforced by* `test_pave.py::TestBoundaries::test_the_pave_layer_never_imports_a_category_or_the_kernel`
and `::test_the_pave_package_init_imports_nothing`, both AST-parsed rather than
`import`-based.

## PAVE-GOV-002 — the arrangement remains the placement authority

`pave/compile.py` emits `StoneInstanceDef`s and `ArrangementRelation`s and
nothing else. The angular sequence of a full planar ring comes from
`arrangement/radial.py::ring_angles_deg()` — the same function the resolver uses
— and a copy of that arithmetic inside the pavé layer is forbidden.

A lattice is placed EXPLICITLY rather than through a `RADIAL` pattern, because a
pattern's members inherit their source instance's overrides and the only
instance at a field's origin is the centre stone.

*Enforced by* `::test_the_ring_arithmetic_is_shared_rather_than_copied` and the
composition-vector round trip.

## PAVE-GOV-003 — a pavé composes; it never replaces

A pavé is added to whatever placement a design declares — a family, a halo, an
explicit arrangement, or nothing. `compose_pave(base, None)` must return `base`
itself.

A pavé-only design keeps its centre stone: composing onto `None` synthesizes one
`CENTER` instance, without which the deterministic primary selection would pick
a pavé stone and the centre stone would silently become one.

*Enforced by* `::TestComposition` and
`::TestGeometry::test_the_centre_stone_survives_a_pave`.

## PAVE-GOV-004 — a host surface is resolved from parameters, never picked

Every supported host derives from the same `constants.py` expressions the
assembly uses. No code may select a face out of a solid: a face index is not
reproducible across kernel versions or across a change to an unrelated
parameter.

A host with no resolver raises. It is never approximated onto another surface.

*Enforced by* `::TestSurfaceTargeting`, including
`::test_the_stone_anchor_matches_the_builders_own_expression`.

## PAVE-GOV-005 — the surface resolver stays kernel-free

`geometry/pave_surface.py` must not import CadQuery. Forge imports it so a
pavé rule can answer "does this field compile against this design's real
surface?" with the SAME code generation uses, and Forge must not import the
kernel.

*Enforced by* `::TestBoundaries::test_the_surface_resolver_is_kernel_free`.

## PAVE-GOV-006 — retention geometry belongs to the Setting System

The bead and micro-prong builders live in `setting/retention.py`. Setting System
v2 is authoritative for how metal holds a stone, and a bead is metal holding a
stone. A second retention implementation inside `jewelmind/pave/` is forbidden,
and so is kernel code there.

The split: the pavé owns WHERE retention goes (it owns the lattice); the Setting
System owns WHAT a piece is.

*Enforced by* `::TestBoundaries::test_retention_geometry_lives_in_the_setting_system`.

## PAVE-GOV-007 — retention anchors are derived in surface parameters

Corners are computed in (angle, axial) and mapped to 3D once, never in the
tangent plane at each stone. A tangent-plane corner lands on the chord rather
than the surface, so two adjacent stones' shared corner comes out at two
different points and a `SHARED_BEAD` field silently degrades into an
individual-bead field with four times the solids.

A `SHARED_BEAD` anchor must name every stone it touches, so "shared" is a
checkable statement about the topology rather than a label.

*Enforced by* `::TestRetention::test_shared_beads_are_genuinely_shared` and
`::test_the_two_strategies_build_different_metal`.

## PAVE-GOV-008 — a recess is a CUT, and is never called a seat

The recess routes through `setting/seat.py`, whose own source is asserted never
to call `.fuse()` on a stone shape (SETTINGV2-GOV-008, LAW-006). The pavé
inherits that guarantee rather than restating it, and `pave_adapter.py` must
contain no `.fuse` call at all.

`REFERENCE_RECESS` has no bearing shoulder and makes no claim that a stone would
sit correctly in it.

*Enforced by* `::TestGeometry::test_the_recess_is_a_cut_and_never_a_fuse`
(AST-parsed) and `::test_the_recess_removes_real_host_material`.

## PAVE-GOV-009 — identity is derived, and provenance is carried

A placement id is `<paveId>.r<row>.c<column>` — derived from the field's own id
and the cell's lattice coordinates, never a UUID, a counter or a timestamp. Row
and column are PROVENANCE, never identity, and an explicit placement records
`-1` for both rather than a fabricated cell.

Every generated solid must be traceable to the definition that produced it: the
retention component's metadata carries every anchor's id and the stones it
serves.

*Enforced by* `::TestDeterminism::test_derived_ids_carry_lattice_coordinates_and_are_not_counters`.

## PAVE-GOV-010 — reject, never repair

An unsupported host, an unresolvable host, an empty field, an over-capacity
field, an id collision, or a field that does not fit under a strict containment
policy raises. A clipped field reports how many cells it lost. Nothing invents a
plausible lattice, truncates a member list, or substitutes a reserved strategy
with one that has a builder.

*Enforced by* `::TestCompilation` and
`specs/pave/v1/test-vectors/invalid-pave-vectors.json`, which records WHICH
layer refused each case.

## PAVE-GOV-011 — no invented professional threshold

No model, rule or message may state a minimum pavé spacing, a minimum bead
diameter, a maximum stone density, a settable seat depth, or whether a field
could be cut by a setter.

`JM-PAVE-006` is the only numeric rule and it is a MATHEMATICAL CONSTRAINT: two
stones whose footprints exceed the pitch between them overlap as a matter of
arithmetic. Its Forge classification is `GEOMETRY_PRECONDITION`, not a domain
threshold.

`MAX_PAVE_STONES`, `MAX_PAVE_ROWS` and `MAX_PAVE_COLUMNS` are software safety
limits and say so. `_INDIVIDUAL_BEAD_INSET_FRACTION` is a construction parameter
and says so.

*Enforced by* `::TestPaveRules::test_no_pave_rule_invents_a_professional_threshold`,
which scans the REAL emitted messages rather than the source.

## PAVE-GOV-012 — every capability entry is backed by a real builder

`representable`, `composable`, `stoneGeometry` and `settingGeometry` are
independent. A host entry must have a resolver, a retention entry must have a
builder, and a PLANNED capability must claim neither kind of geometry — in both
directions.

`settingGeometry` is `true` here for the first time in the programme, and that
claim is asserted comparatively against the Family and Halo registries rather
than self-declared.

*Enforced by* `::TestCapabilityRegistry` and
`test_capability_coverage.py`'s pavé guards.

## PAVE-GOV-013 — an absent pavé stays absent

`compose_pave(base, None)` returns `base`, nothing synthesizes a field for a
design that declares none, and a document with no pavé must generate
byte-identical geometry to its pre-Sprint-26 self.

A pavé IS inside `geometryHash`, because it places stones and cuts metal:
excluding it would serve stale geometry for a real design change.

*Enforced by* `::TestBackwardCompatibility` and
`::TestDeterminism::test_every_geometry_affecting_field_changes_the_geometry_hash`.

## PAVE-GOV-014 — one definition of the default field

`pave/models.py::default_pave_field()` is the single answer to "turn the pavé
on". Designer materializes it before applying a `pave.*` patch, because a dotted
patch cannot construct a discriminated union from nothing; the Studio panel
offers the same field. Two copies would let a spoken instruction and a UI toggle
produce different designs from the same intent.

Every value in it is a construction default inside the schema's range, and none
is professionally validated.

## When an ADR is required

- letting the pavé layer construct geometry or compute placements of its own;
- accepting more than one field per design;
- merging any of the four capability axes;
- changing the derived placement-id scheme;
- changing what `geometryHash` includes;
- selecting a host surface by face index rather than by parameter;
- materializing `GeometryPlan`.

## When an RFC is required

- a host surface beyond the two implemented, including any reserved name;
- a retention strategy beyond the four implemented, including any reserved name;
- **a real cut seat with a bearing shoulder** for a pavé stone;
- an outline-following field;
- per-cell stone specifications (a field of mixed shapes);
- any professional pavé spacing, density or settability rule.
