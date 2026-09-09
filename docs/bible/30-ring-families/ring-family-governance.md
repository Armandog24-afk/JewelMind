---
id: JM-BIBLE-RINGFAM-GOVERNANCE
title: "Ring Family governance rules"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-09
source_of_truth: true
depends_on:
  - JM-BIBLE-RINGFAM-README
related_documents:
  - JM-BIBLE-FAMILY-GOVERNANCE
  - JM-BIBLE-SHANK-GOVERNANCE
  - JM-BIBLE-ARRANGE-GOVERNANCE
  - JM-BIBLE-ADR-014
implementation_status: current
---

# Ring Family governance rules

Fourteen rules. Each is enforced by a real test in
`backend/tests/test_ring_families.py`; a rule with no test is a wish, not a
rule.

---

## RINGFAM-GOV-001 — A ring family is a parametric relation, never a preset

A variant may not be a stored set of values. Every parameter it reads must
**modulate** something the document already states, so changing
`ring.innerDiameter`, `stone.diameter` or `band.width` regenerates the design.

*Enforced by* `TestParametricPropagation`, which changes one input per test and
measures the geometric result — and by
`test_no_derivation_replaces_a_document_value_with_a_constant`, which requires
every derivation to name the source parameters it was computed from.

## RINGFAM-GOV-002 — Every variant must differ measurably from its family's baseline

A variant whose geometry is identical to the baseline's is a name. Exactly one
variant may report `differsFromFamilyBaseline: false` — the baseline itself —
and it must be the one flagged `isFamilyBaseline: true`.

*Enforced by* `test_every_variant_but_the_baseline_changes_the_metal` (measured
solids) and
`test_exactly_one_variant_is_its_family_baseline_and_it_is_the_default`.

`SOLITAIRE_LOW_PROFILE` and `SOLITAIRE_ELEVATED` shipped identical to
`CLASSIC` during this sprint — both had `headHeightFactor = 1.0` and the variant
contributed nothing of its own. `VARIANT_HEAD_HEIGHT_FACTOR` is what fixed it,
and this rule is what caught it.

## RINGFAM-GOV-003 — Orchestrate the existing systems; never duplicate one

The layer computes **no placement, no outline and no solid of its own**. Side
stones go to the Multi-Stone Family layer, which goes to the Stone Arrangement
Engine; halos to the Halo System; pavé to the Pavé Engine; the head to Setting
System v2; the taper to `shank/taper.py`.

*Enforced by* `TestOrchestrationNotDuplication`, including
`test_the_family_delegates_placement_to_the_arrangement_engine`, which requires
the trilogy variants to derive a `family` block and to derive **no**
`arrangement` of their own.

## RINGFAM-GOV-004 — Keep the layer category- and kernel-neutral

Nothing under `backend/jewelmind/ring_family/` may import `cadquery`, `OCP`,
`jewelmind.geometry`, `jewelmind.ring`, `jewelmind.jewelry_category` or
`jewelmind.validation`. `geometry/ring_family_adapter.py` is the ONE sanctioned
meeting point with `JewelryDefinition` — the role `family/effective.py` and
`geometry/setting_adapter.py` already play.

*Enforced by* AST inspection in `test_the_layer_imports_no_geometry_or_kernel`
and `test_no_ring_family_module_builds_geometry`. AST, not `import`: an
`import` test passes on an already-cached module.

This rule caught a real violation during the sprint. `capability.py` imported
three geometry registries to measure `structuralGeometry`, which is the
derived-not-declared discipline in the right spirit and the wrong place. See
RINGFAM-GOV-006.

## RINGFAM-GOV-005 — Keep `ring_family/__init__.py` importing nothing

Load-bearing: `domain/schema.py` imports `ring_family.models`, so an eager
package init would make the import graph cyclic — the trap `stone`, `gem`,
`arrangement`, `family`, `halo` and `pave` each document.

*Enforced by* `test_the_package_init_imports_nothing`.

## RINGFAM-GOV-006 — Measure the resolver; declare only what would require a forbidden import

`differsFromFamilyBaseline` and `derivedPathCount` are **measured** by running
the real resolver, so a variant that stopped deriving anything reports it on the
next import rather than at the next code review.

`structuralGeometry` is **declared**, because measuring it needs the live
builder registries and RINGFAM-GOV-004 forbids the import. That is only
acceptable with the correspondence asserted in both directions in the test file,
which may import anything — the resolution `pave/capability.py` already uses for
its own `settingGeometry` (PAVE-GOV-001 forbids the import, PAVE-GOV-012
requires the correspondence).

*Enforced by* `test_declared_structural_geometry_matches_the_builders`.

## RINGFAM-GOV-007 — Refuse a family/variant disagreement; never resolve it by precedence

`jewelry.style` is the one authority for the family. A variant belonging to
another family raises and is reported as `JM-RINGFAM-001`. Two authorities over
one design have no determinate resolution — the discipline `JM-FAMILY-001` and
`JM-SETTING-008` already carry.

*Enforced by* `test_a_variant_from_another_family_is_refused` and
`test_the_refusal_is_also_a_validation_error`.

## RINGFAM-GOV-008 — Never overwrite a block the document declares itself

A document that declares its own `halo` keeps it. The family reports what it did
**not** derive in `skippedPaths`, and `JM-RINGFAM-002` states it as
INFORMATION — the design is valid, and an author who wrote both deserves to be
told which won.

*Enforced by* `test_a_document_declaring_a_derived_block_keeps_its_own`.

## RINGFAM-GOV-009 — Declare every derived path, and self-check every write

`RING_FAMILY_DEPENDENCIES` states every path a variant derives and every
document field that influences it. The resolver checks each write against that
table **at runtime** and raises on an undeclared path: a derivation no report
could explain is worse than a missing one.

*Enforced by* the resolver itself, plus
`test_every_derived_path_is_declared_in_the_dependency_table` as the inspectable
statement of the same invariant.

## RINGFAM-GOV-010 — Report an unread parameter; never silently ignore it

A parameter a variant does not read stays in the document and is reported by
`JM-RINGFAM-003` as INFORMATION, only when the author actually set it. Studio
shows only the parameters the chosen variant reads, which addresses the same
concern without hiding the value.

*Enforced by* `test_unread_parameters_are_reported_not_silently_ignored` and
`test_a_parameter_left_at_its_default_is_not_reported`.

## RINGFAM-GOV-011 — Reject, never repair, and never clamp

An out-of-range separation, a span past the construction limit, a reserved
variant, a non-finite value: each **raises**. Reducing a value to fit would
build a design the author never described (SETTING-GOV-013's discipline,
restated for ring structure).

*Enforced by* `TestAdversarialInput` and
`test_a_shoulder_span_past_the_construction_limit_is_refused`, which also
asserts the message does not offer a clamp.

## RINGFAM-GOV-012 — Never invent a professional threshold, and never claim one

No rule, model, message or registry description may judge whether a rail is
strong enough, a shoulder castable, a signet table thick enough or a bypass
sound. Every variant is `NOT_REVIEWED`.

The two numeric limits are arithmetic and say so: `JM-RINGFAM-004` refuses a
separation that leaves *no rail*, and `MAX_ARCH_SPAN_DEG` is the measured limit
of a ruled-loft arch.

*Enforced by* `TestNoInventedProfessionalRule`, including
`test_the_only_numeric_refusal_is_arithmetic`, which asserts that a 0.15 mm rail
is **not** refused.

## RINGFAM-GOV-013 — Keep an absent ring family absent

Nothing synthesizes a `ringFamily` block. A document with none resolves to its
family's default variant, and for `solitaire` that reproduces the pre-Sprint-28
design exactly at `341.44334316909976 mm³`. The adapter returns the **original
object** when nothing changes.

*Enforced by* `TestPreSprint28Unchanged`.

## RINGFAM-GOV-014 — Generate every spec artifact by running the real implementation

`specs/ring-family/v1/` is a mirror of live code — registry, schemas, dependency
graph, examples and vectors — re-derived on every test run. The geometry vectors
are **re-measured** by rebuilding each variant, because a spec whose figures
were typed by hand could claim any difference between two variants.

*Enforced by* `TestSpecArtifacts`. It has already caught one drift: the
generator used `variants_for_family(family)[0]`, which is alphabetical, and
recorded `HALO_DOUBLE` as the halo family's default instead of `HALO_SINGLE`.

---

## When an ADR is required

- Letting the ring-family layer compute a placement, an outline or a solid.
- Adding a competing family field beside `jewelry.style`, or resolving a
  family/variant disagreement by precedence.
- Replacing the measured `differsFromFamilyBaseline` with a declaration.
- Changing the derived-path set of an existing variant, or the shank-architecture
  dispatch order (which would put the uniform fast path at risk).
- Renaming `shoulders`, `signet_body`, or the `band` component.
- Changing what `geometryHash` includes.
- Materializing `GeometryPlan` (still an Alchemist ADR condition).

## When an RFC is required

- **Any ring family or variant beyond the thirteen implemented — including every
  reserved name.** See [`coverage-review.md`](coverage-review.md) for what each
  actually needs.
- A swept solid along a 3D spline, which is the shared prerequisite for
  `SOLITAIRE_TRELLIS`, `SPLIT_SHANK_SCULPTED` and `BYPASS_TWIST`.
- A surface-decoration system (engraving, relief, texture), the prerequisite for
  `SIGNET_ENGRAVED`.
- Metal that holds halo stones, which is what would make the `halo` family
  CURRENT.
- A stone-less ring, which changes the required-component set and is therefore
  also an ADR condition.
- Any professional threshold on a rail, shoulder, table or crossing.
