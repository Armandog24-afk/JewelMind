# Gem Identity & Material System v1 — machine-readable specification

The Gem System answers *what a stone is made of*, which is a different question
from *what shape the stone is* (Stone System, [`specs/stone/v2/`](../../stone/v2/README.md))
and from *how metal holds it* (Setting System, [`specs/setting/v1/`](../../setting/v1/README.md)).

Narrative half: [`docs/bible/23-gem-identity/`](../../../docs/bible/23-gem-identity/README.md).

## What this is not

- **Not a gemological database.** 40 registry entries are an internal taxonomy
  sufficient to identify, name and render common gems. They carry no hardness,
  durability, heat-sensitivity, treatment-safety or setting-suitability data,
  because JewelMind has no professional evidence for any of it.
- **Not a certification source.** `origin` and `treatments` record what someone
  **declared**, with the declaration's source (`disclosure`). Nothing here
  verifies a claim, and no lab report is stored as evidence.
- **Not professionally validated.** Every entry is `NOT_REVIEWED`; the active
  professional-validation registry holds zero records.
- **Not optical measurement.** Every value in a visual profile is a rendering
  parameter. `ior` is what the renderer is given to make a stone look plausible
  on screen, not a laboratory refractive index, and `dispersion` drives a
  sparkle effect rather than describing spectral separation.

## Files

| File | Contents |
| --- | --- |
| `gem-definition.schema.json` | A registry entry — one KIND of gem (type level). |
| `gem-identity.schema.json` | What gem THIS stone is (instance level). |
| `gem-treatment.schema.json` | One declared treatment, with status and disclosure. |
| `gem-visual-profile.schema.json` | Rendering parameters for one appearance. |
| `resolved-gem.schema.json` | Identity joined to its entry and profile. |
| `stone-instance.schema.json` | A stone's role in an arrangement, plus its own gem. |
| `jdl-gem-identity.schema.json` | The JDL-layer mirror carried on `stone.gem`. |
| `jdl-gem-treatment.schema.json` | The JDL-layer treatment mirror. |
| `gem-registry.json` | Every entry, generated from `gem/registry.py`. |
| `visual-profile-set.json` | Every profile, generated from `gem/visual.py`. |
| `alias-index.json` | Term → canonical ID, generated from the registry's own aliases. |
| `examples/*.json` | Real identities, and the `ResolvedGem` each one produces. |
| `test-vectors/*.json` | Behaviour recorded by running the real implementation. |

Every one of these was produced by running the real code, never hand-authored,
and `backend/tests/test_gem_identity.py::TestSpecArtifactsMatchLiveCode`
re-derives them on every test run — so a drift between this directory and the
implementation fails the suite rather than going unnoticed.

## The type / instance split

`GemDefinition` is type level: it says what a ruby *is*. `GemIdentity` is
instance level: it says what *this* ruby is. The split exists because a registry
entry cannot know whether a particular stone was heated, who declared that, or
which appearance the designer wants — those are facts about one stone.

## The two independent axes, and the two escape hatches

Identity is separate from origin: a synthetic ruby is still `corundum.ruby`,
with `origin: SYNTHETIC`. Identity is separate from treatment: a stone may be
natural *and* treated, or synthetic *and* untreated.

Nothing forces a gem into the enum:

- **`custom`** — a material with no registry entry, named in the user's own
  words via a required `customName`.
- **`unknown`** — the gem was not identified. A legacy design with no gem at all
  normalizes here, deliberately **not** to diamond.

## Three states an interface must not conflate

| State | Representation |
| --- | --- |
| Nothing recorded | `treatments: []` |
| Declared untreated | one entry with `status: NOT_PRESENT` |
| Treated, kind unstated | one entry with `treatment: UNKNOWN`, `status: PRESENT` |

`treatment_summary()` keeps them distinct, and
`test-vectors/treatment-summary-vectors.json` records the exact wording.

## Geometry / identity separation

A gem is semantic. Changing it changes what a design **means**, not what Atlas
**builds** — so `definitionHash` moves and `geometryHash` does not, which is
what lets an already-built model be reused across a gem edit. Measured, not
assumed: see `test-vectors/geometry-identity-hash-vectors.json` and
`docs/bible/23-gem-identity/`'s hash-separation section for the empirical
verification behind every excluded field.

## Forge rules

Six rules, all `GEM_IDENTITY_ONLY` — every one checks a **reference** or a
**coherence**, never a gemological property:

| Rule | Checks | Severity |
| --- | --- | --- |
| `JM-GEM-001` | the referenced entry exists | warning (a saved design must still load) |
| `JM-GEM-002` | the declared origin is applicable to the entry | error |
| `JM-GEM-003` | `custom` has a name, and only `custom` has one | error |
| `JM-GEM-004` | the visual profile override resolves | warning |
| `JM-GEM-005` | the declared treatment set is self-consistent | warning for a duplicate, error for a present/not-present contradiction |
| `JM-GEM-006` | the entry is deprecated but still resolvable | warning |

`test-vectors/forge-gem-rule-vectors.json` records a live engine run for each,
including the cases the JDL layer rejects before Forge is reached.
