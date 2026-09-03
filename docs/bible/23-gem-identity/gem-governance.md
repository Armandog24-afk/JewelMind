---
id: JM-BIBLE-GEM-GOVERNANCE
title: "Gem System governance"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-03
source_of_truth: true
depends_on:
  - JM-BIBLE-GEM-README
implementation_status: current
professional_validation: not_required
normative: true
---

# Gem System governance

Sixteen rules. Each one is enforced by a named test where enforcement is
possible, because a governance rule nothing checks is a preference.

## GEM-GOV-001 — the Gem System is category-neutral

Nothing under `backend/jewelmind/gem/` may import a jewelry category
(`jewelmind.ring`, `jewelmind.jewelry_category`), any geometry module, the CAD
kernel, or `JewelryDefinition`. A gem material is not a ring concept.

`jewelmind/gem/__init__.py` must import nothing: `domain/schema.py` imports
`jewelmind.gem.models` for its vocabularies, and an eager package init would
make the import graph cyclic.

*Enforced by* `backend/tests/test_gem_no_category_dependency.py` (AST
inspection, not `import` — a cached module imports fine regardless of what it
depends on).

## GEM-GOV-002 — gem identity never derives from geometry

No code may infer a gem from a shape, a dimension, an outline, a colour or a
setting. A round stone is not a diamond; a red stone is not a ruby.

*Enforced by* `test_gem_no_category_dependency.py::test_no_gem_module_reads_a_geometry_field`.

## GEM-GOV-003 — no invented gemological data

No hardness, toughness, Mohs value, heat sensitivity, treatment-safety rule,
durability class, cleaning instruction, or setting recommendation may be added
to the registry, to a Forge rule, or to any user-facing message. Each needs
professional evidence this project does not have; `unknown` is honest, a
plausible number is not.

*Enforced by* `test_gem_identity.py::test_no_gem_rule_makes_a_gemological_claim`
and `test_gem_api.py::test_validation_never_returns_a_gemological_claim`, which
scan the real messages the engine emits rather than the source.

## GEM-GOV-004 — the registry is a taxonomy, never a certification source

`origin` and `treatments` record what someone **declared**, with the
declaration's source in `disclosure`. Nothing in JewelMind verifies a claim, and
no lab report is stored as evidence. `GET /api/gems` must keep saying so.

## GEM-GOV-005 — no entry is professionally validated

Every entry is `NOT_REVIEWED`. `provenance: PROFESSIONALLY_VALIDATED` requires a
real record, naming a real reviewer, in the professional-validation registry —
which holds zero. A passing test suite is not professional validation
(`PROVAL-GOV-006`).

*Enforced by* `test_gem_identity.py::test_no_entry_is_professionally_validated`.

## GEM-GOV-006 — visual profiles are rendering parameters, never measurements

`ior`, `dispersion`, `transmission` and the rest exist to make a stone look
plausible on screen. None may be described as a refractive index, a dispersion
coefficient, or any other optical measurement.

## GEM-GOV-007 — the fallback appearance stays neutral

An unidentified gem must never render as a brilliant colourless stone. The
fallback is deliberately dull, and it is flagged `isFallback` so an interface
can present it *as* a fallback.

*Enforced by* `test_gem_identity.py::test_an_unresolved_gem_uses_the_neutral_fallback_appearance`
and `frontend/src/vision/gemMaterials.test.ts`.

## GEM-GOV-008 — resolution never raises and never substitutes

`resolve_gem()` degrades an unresolvable reference to `unknown`, sets
`wasUnresolved`, and preserves the original reference. It must never pick a
different real gem, and must never infer one from the stone's geometry. A
missing gem resolves to `unknown`, never to diamond.

*Enforced by* `test_gem_identity.py::TestResolution`.

## GEM-GOV-009 — a gem ID is untrusted input

Every ID is validated for shape before any lookup, so a user-authored value can
never become a filesystem path, a shell argument, or an arbitrary dictionary
key. Same for `StoneInstance.instanceId`. Every float field sets
`allow_inf_nan=False`.

*Enforced by* `test_gem_identity.py::TestGemIdSafety` and
`test_gem_api.py::TestDetailEndpoint`.

## GEM-GOV-010 — the three treatment states stay distinct

An empty `treatments` list means nothing was recorded. It is **not** a claim of
being untreated — that requires an explicit `NOT_PRESENT` record. A treatment
declared without a named type stays `UNKNOWN` and must never be resolved to a
specific treatment on the user's behalf.

*Enforced by* `test_gem_identity.py::TestTreatments`.

## GEM-GOV-011 — a cut name is not a species name

`stone.shape` is a cut; `stone.gem.gemId` is a material. A term naming both
(`emerald`, `pearl`, and their Italian forms) must be reported as ambiguous, in
both directions — Sprint 20's `STONEV2-GOV-008` forbids resolving a species to
a cut, and this forbids resolving a cut to a species.

*Enforced by* `test_gem_designer_language.py::TestTablesPointAtRealThings` and
`::TestDesignerProposals::test_an_ambiguous_term_asks_instead_of_choosing`.

## GEM-GOV-012 — an unrecognized gem is a question, not a capability gap

Every gem is expressible via `custom` or `unknown`, so an unknown term produces
a clarification, never an `UnsupportedFeature`. Nothing may be approximated to
the nearest-looking entry.

*Enforced by* `test_gem_designer_language.py::test_an_unknown_gem_offers_the_two_escape_hatches`.

## GEM-GOV-013 — the geometry hash's exclusions are empirical

A field may only be excluded from `geometry_hash()` after geometry has actually
been generated with that field varied and the output compared. Adding an
exclusion on the basis of reading the code is forbidden: a wrong exclusion
serves stale geometry for a real design change, which is worse than a slow
rebuild.

`definitionHash` keeps its existing meaning and must never be repurposed to
also encode geometry scope.

*Enforced by* `test_gem_identity.py::TestGeometryIdentitySeparation`, which
includes the complement case so it cannot pass by measuring nothing.

## GEM-GOV-014 — every spec artifact is derived, never hand-maintained

`specs/gem/v1/` is a mirror of live code: the registry, the profile set, the
alias index, every example and every test vector are produced by running the
real implementation. Sprint 20 removed three hand-copied capability lists that
had already drifted and made Designer and Setting misreport real capabilities.

*Enforced by* `test_gem_identity.py::TestSpecArtifactsMatchLiveCode`, which
re-derives them on every run.

## GEM-GOV-015 — the frontend mirrors, and never owns, gem data

`frontend/src/vision/gemMaterials.ts` may render a profile ID the backend
defines; it must never define a gem, an origin, a treatment, or a profile the
backend does not have. A local presentation table exists only so the viewer can
draw before a network round trip, and an unmirrored profile must degrade to the
fallback visibly rather than render as some other gem.

## GEM-GOV-016 — arrangement stays PLANNED until a generator exists

`StoneInstance` is the forward-looking half of the type/instance split. No
multi-stone geometry exists, and the capability registry must keep saying so. A
model is not a feature.

*Enforced by* `test_gem_identity.py::TestStoneInstance::test_multi_stone_arrangement_is_not_advertised_as_current`
and `test_capability_coverage.py::test_gem_arrangement_is_not_advertised_as_current`.

## When an ADR is required

- Letting gem identity affect geometry in any way, or merging `stone.gem` into
  the geometry fields.
- Changing what `geometry_hash()` excludes, or replacing the two-hash model.
- Moving the registry out of code into a runtime-writable store (which would
  make `registryVersion` meaningless and make a saved design's gem reference
  resolvable or not depending on when it was opened).
- Letting `conversation/` or `designer/` write a gem field without routing
  through `DesignerService`.
- Introducing a gem-property layer (hardness, durability, setting suitability),
  which additionally requires real professional validation before any rule
  derived from it may block anything.

## When an RFC is required

- A new gem entry beyond the current registry, or a new `materialClass`,
  `GemOrigin`, or `GemTreatmentType` member.
- Multi-stone arrangement (halo, pavé, three-stone) — the arrangement half of
  `StoneInstance`.
- Integrating an external gem or gemological data source.
- Per-stone material variation within a single component.
