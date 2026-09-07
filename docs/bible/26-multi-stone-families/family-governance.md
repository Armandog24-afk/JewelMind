---
id: JM-BIBLE-FAMILY-GOVERNANCE
title: "Multi-Stone Families governance"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-04
source_of_truth: true
depends_on:
  - JM-BIBLE-FAMILY-README
implementation_status: current
professional_validation: not_required
normative: true
---

# Multi-Stone Families governance

Thirteen rules. Each is enforced by a named test where enforcement is possible,
because a governance rule nothing checks is a preference.

## FAMILY-GOV-001 — the family layer is category- and kernel-neutral

Nothing under `backend/jewelmind/family/` may import a jewelry category, any
geometry module, the Setting System, or the CAD kernel. Only
`family/effective.py` may reach `JewelryDefinition`, and it is the sanctioned
meeting point — the role `geometry/setting_adapter.py` plays for settings.

`family/__init__.py` must import nothing: `domain/schema.py` imports
`family.models`, so an eager init would make the graph cyclic.

*Enforced by* `test_multi_stone_families.py::TestArrangementIsTheAuthority`
(AST inspection, not `import`).

## FAMILY-GOV-002 — the arrangement remains the placement authority

A family compiles into arrangement primitives and computes no final position of
its own. Creating a second placement engine — or having a family write a
position that bypasses the resolver — is forbidden.

*Enforced by* `::test_a_family_compiles_into_arrangement_primitives_only`.

## FAMILY-GOV-003 — one placement authority per document

A family and an explicit arrangement may not both be present.
`family/effective.py` refuses it and `JM-FAMILY-001` reports it before
generation. Merging them is never an option: there is no determinate rule for
which wins.

## FAMILY-GOV-004 — a family never duplicates stone or gem data

A member references a stone specification and may carry a `GemIdentity`. It
must never hold a shape, a dimension, a source, a material or a visual profile.

*Enforced by* `::test_a_family_references_stones_rather_than_restating_them`.

## FAMILY-GOV-005 — the family model holds no kernel object

No field may hold a `cadquery.Shape`, `Workplane` or OCP object.

## FAMILY-GOV-006 — identity is by id, never by array position

Reordering `members` must not change the compiled arrangement or its
fingerprint. Derived member ids come from the family's own structure, never from
a counter, a UUID, a timestamp or a memory address.

*Enforced by* `::TestDeterminism`.

## FAMILY-GOV-007 — compilation is deterministic and repeatable

The same family compiles to byte-identical canonical JSON on every run.

*Enforced by* `::test_compilation_is_byte_identical_across_repeats`.

## FAMILY-GOV-008 — reject, never repair

A missing role, a wrong cardinality, a role the family does not accept, or
parameters that cannot produce a determinate arrangement all raise. Filling in a
plausible member would produce a design nobody authored.

*Enforced by* `::TestThreeStone` / `::TestToiEtMoi` rejection cases.

## FAMILY-GOV-009 — roles are declared as data, not as scattered checks

`FAMILY_ROLE_RULES` is the single source of accepted roles and required counts;
Forge and the compiler read the same table, and `capability.py` mirrors it.

*Enforced by* `::test_every_family_has_role_rules`.

## FAMILY-GOV-010 — no invented jewelry threshold

No rule, model or message may judge centre-to-accent proportion, minimum
spacing, stone count, or whether a configuration is settable. Whether two placed
stones overlap is a geometric fact for Inspection, which reports it and
interprets nothing.

*Enforced by* `::test_no_family_rule_invents_a_jewelry_threshold`, which scans
the real emitted messages rather than the source.

## FAMILY-GOV-011 — capability status distinguishes four axes

`representable`, `compilable`, `stoneGeometry` and `settingGeometry` are
independent. A family that compiles and builds stones but no accent setting is
`PARTIAL`, never `CURRENT`. No family may be marked `settingGeometry: true`
without a real setting strategy behind it.

*Enforced by* `::TestCapabilityRegistry` and
`test_capability_coverage.py::test_no_family_claims_a_setting_it_does_not_build`.

## FAMILY-GOV-012 — an absent family stays absent

`compile_family(None)` returns `None`, nothing synthesizes a solitaire family,
and a design declaring no family must generate byte-identical geometry to its
pre-Sprint-24 self. The single-stone component must be the builder's own shape
object, not a re-placed copy.

*Enforced by* `::TestBackwardCompatibility` and the 39-case Golden suite.

## FAMILY-GOV-013 — every spec artifact is derived, never hand-maintained

`specs/family/v1/` is a mirror of live code: schemas, registry, examples and
vectors are produced by running the real compiler.

*Enforced by* `::TestSpecArtifacts`, which re-derives them on every run.

## When an ADR is required

- Letting a family compute a final placement without the arrangement resolver.
- Merging a family and an explicit arrangement instead of refusing both.
- Changing family compilation output (which also bumps
  `FAMILY_COMPILER_VERSION`).
- Changing the stone component naming contract, or how a per-instance transform
  is composed.
- Moving family compilation out of the family package.
- Changing what `geometryHash` includes.

## When an RFC is required

- A new family type beyond the four implemented, including any reserved name.
- An accent setting strategy — required before any family may become `CURRENT`
  (`SETTING-GOV` also requires it).
- A family-aware head spanning several stones.
- Multiple named stone specifications in one document.
- Any professional family rule, which additionally requires real professional
  validation before it may block anything.
