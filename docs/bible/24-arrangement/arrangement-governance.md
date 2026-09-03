---
id: JM-BIBLE-ARRANGE-GOVERNANCE
title: "Stone Arrangement governance"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-03
source_of_truth: true
depends_on:
  - JM-BIBLE-ARRANGE-README
implementation_status: current
professional_validation: not_required
normative: true
---

# Stone Arrangement governance

Fourteen rules. Each is enforced by a named test where enforcement is possible,
because a governance rule nothing checks is a preference.

## ARRANGE-GOV-001 — the layer is category- and kernel-neutral

Nothing under `backend/jewelmind/arrangement/` may import a jewelry category
(`jewelmind.ring`, `jewelmind.jewelry_category`), any geometry module, the CAD
kernel, or `JewelryDefinition` — the last would smuggle the whole ring domain
across in one import.

`jewelmind/arrangement/__init__.py` must import nothing: `domain/schema.py`
imports `arrangement.models`, so an eager package init would make the graph
cyclic.

*Enforced by* `backend/tests/test_arrangement_no_category_dependency.py` (AST
inspection, not `import` — a cached module imports fine regardless of what it
depends on).

## ARRANGE-GOV-002 — an arrangement never constructs geometry

This layer produces NUMBERS. No field may hold a kernel object, and no module
may call a construction operation. Atlas turns placements into solids.

*Enforced by* `test_arrangement_no_category_dependency.py::test_no_arrangement_module_constructs_geometry`,
which scans for the kernel verbs an accidental call would use.

## ARRANGE-GOV-003 — identity is by ID, never by array position

Every instance, group, pattern and relation is addressed by a stable ID.
Reordering a list must not change what an arrangement means, its canonical JSON,
or its fingerprint. Primary-instance selection uses the lowest ID, never
`instances[0]`.

*Enforced by* `test_arrangement.py::TestDeterminism` and
`::TestCompilationBoundary::test_primary_selection_does_not_depend_on_list_order`.

## ARRANGE-GOV-004 — resolution is a pure function, evaluated directly

One pass, fixed order, closed-form pattern expansion. No iteration to
convergence, no dependency search, no solver state, and no dependence on
wall-clock time, randomness, memory addresses or runtime-generated identifiers.
Generated member IDs are derived from the pattern ID and member index.

*Enforced by* `test_arrangement.py::TestDeterminism::test_resolution_is_byte_identical_across_repeats`
and `::test_no_generated_id_is_random`.

## ARRANGE-GOV-005 — reject, never repair

A missing reference, a duplicate ID, an impossible pattern or an inconsistent
relation raises. Normalization may reorder, round and wrap; it may never change
what the arrangement means by filling in a plausible value.

*Enforced by* `test_arrangement.py::TestRejections`.

## ARRANGE-GOV-006 — a resolved arrangement is the only downstream contract

Atlas, Vision, Foundry and Forge read `ResolvedArrangement`, never the raw
definition. A second consumer expanding patterns itself would eventually
disagree with the resolver, and the disagreement would surface as geometry that
does not match the preview.

## ARRANGE-GOV-007 — arrangement identity is separate from geometry identity

`arrangementFingerprint` covers the arrangement's own content plus the resolver
version. It is not `definitionHash` and not `geometryHash`, and none of the
three may be repurposed as another.

The arrangement DOES participate in `geometryHash`, because it will drive
geometry. Excluding it would serve stale geometry for a real design change.

*Enforced by* `test_arrangement.py::TestJdlIntegration`.

## ARRANGE-GOV-008 — no invented jewelry threshold

No minimum spacing, clearance, stone-count limit, accent proportion or pavé
density — in a model, a rule, or a message. The bounds that exist
(`MAX_INSTANCES`, `MAX_COORDINATE_MM`, `COORDINATE_DECIMALS`) are software
limits and each says so.

Whether two placed stones overlap is a GEOMETRIC fact for Geometry Inspection,
not a structural threshold.

*Enforced by* `test_arrangement.py::TestForgeArrangementRules::test_no_arrangement_rule_invents_a_jewelry_threshold`
(which scans the real emitted messages) and
`test_arrangement_no_category_dependency.py::test_no_arrangement_module_invents_a_jewelry_threshold`.

## ARRANGE-GOV-009 — an ungenerated instance is reported, never dropped

Every resolved instance carries a generation status. `NOT_GENERATED` REQUIRES a
reason and `GENERATED` REQUIRES a component name, both enforced by a model
validator so no code path can omit either. No placeholder solid may ever stand
in for geometry that was not built.

*Enforced by* `test_arrangement.py::TestCompilationBoundary`.

## ARRANGE-GOV-010 — capability status distinguishes three axes

`representable`, `resolvable` and `generatable` are independent. A capability
that resolves but builds nothing is PARTIAL, never CURRENT-and-supported.
Nothing may be marked `generatable` without real geometry behind it.

*Enforced by* `test_arrangement.py::TestCapabilityRegistry` and
`test_arrangement_schemas.py::test_the_registry_spec_never_claims_ungenerated_support`.

## ARRANGE-GOV-011 — an unrepresentable capability has no field

A capability marked PLANNED-and-unrepresentable must have no model field at all.
Accepting a value nothing can execute — a tilt angle, a path curve — would be a
silently ignored field, which is worse than an absent one.

*Enforced by* `test_arrangement.py::TestCapabilityRegistry::test_full_3d_orientation_is_genuinely_not_representable`.

## ARRANGE-GOV-012 — component identity stays stable and non-positional

The primary instance keeps the bare `stone_reference` name. An additional
instance is `stone_reference.<instanceId>`, derived from the authoritative ID.
`geometry/roles.py` must classify that prefix as a stone reference — never
falling through to the `production_metal` default, which would fuse a stone into
metal and ship it in a production export (LAW-006).

*Enforced by* `test_arrangement.py::TestComponentIdentity`, including a test
that the duplicated prefix literal in `geometry/roles.py` agrees with the naming
authority in `arrangement/compile.py`.

## ARRANGE-GOV-013 — an absent arrangement stays absent

`compile_arrangement(None)` returns `None`, and nothing synthesizes a
one-instance arrangement for a single-stone design. A design that declares no
arrangement must generate byte-identical geometry to its pre-Sprint-22 self.

*Enforced by* `test_arrangement.py::TestBackwardCompatibility` and the full
39-case Golden suite, which required zero baseline updates.

## ARRANGE-GOV-014 — every spec artifact is derived, never hand-maintained

`specs/arrangement/v1/` is a mirror of live code: schemas, registry, examples
and vectors are produced by running the real resolver, compiler and registry.

*Enforced by* `backend/tests/test_arrangement_schemas.py`, which re-derives them
on every run.

## When an ADR is required

- Introducing a constraint solver, or any iterative resolution.
- Changing the resolution arithmetic (member ordering, centring convention,
  frame composition order) — which is also a `RESOLVER_VERSION` bump.
- Making the arrangement layer construct geometry, or giving it a kernel
  dependency.
- Changing what `geometryHash` includes, or merging any two of the three
  identities.
- Changing the stone component naming contract.
- Generalizing Geometry Inspection's required-component set for multi-stone
  models.

## When an RFC is required

- A new pattern kind beyond LINEAR/RADIAL/MIRROR, or a path-based pattern.
- Enforced (rather than declared) relations.
- A setting strategy for accent stones — pavé, channel, shared prong.
- Multiple named stone specifications in one document (so `stoneRef` can name
  something other than `primary`).
- Any professional arrangement rule, which additionally requires real
  professional validation before it may block anything.
