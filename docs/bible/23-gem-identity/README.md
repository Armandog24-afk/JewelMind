---
id: JM-BIBLE-GEM-README
title: "Gem Identity & Material System v1"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-03
source_of_truth: true
depends_on:
  - JM-BIBLE-STONEV2-README
  - JM-BIBLE-SETTING-README
  - JM-BIBLE-VISION-README
  - JM-BIBLE-FORGE-README
related_documents:
  - JM-BIBLE-600
implementation_status: current
professional_validation: not_required
normative: true
---

# Gem Identity & Material System v1

Sprint 21. The machine-readable half lives at
[`specs/gem/v1/`](../../../specs/gem/v1/README.md).

## The problem this sprint solves

Before Sprint 21 a stone's complete semantic identity was **implicit in its
geometry**. There was one `StoneSpec` with a shape, some dimensions and a
transparent gemstone-like appearance, and everything else about the stone — what
it was made of, whether it was natural, whether it had been treated — simply had
nowhere to live. In practice that meant every stone was an unnamed
diamond-looking thing.

This sprint separates five concerns that had been running together:

| Concern | Where it now lives |
| --- | --- |
| Physical stone geometry | `StoneSpec` + `jewelmind/stone/`, `geometry/stone/` (Sprints 18/20) |
| Gem / mineral identity | `stone.gem` + `jewelmind/gem/` (**this sprint**) |
| Visual / material representation | `gem/visual.py` + `frontend/src/vision/gemMaterials.ts` (**this sprint**) |
| Jewelry setting | `jewelmind/setting/` (Sprint 19) |
| Arrangement / instance information | `gem/models.py::StoneInstance` (model only; see below) |

## The type / instance split

The central design decision. `GemDefinition` is **type level** — it says what a
ruby *is*: its family, its canonical and localized names, which origins are
applicable to it, and how it should be drawn by default. `GemIdentity` is
**instance level** — it says what *this* ruby is: its declared origin, its
declared treatments, an optional appearance override, an optional note.

The split is forced by the domain. A registry entry for "ruby" cannot know
whether a particular ruby was heated, who said so, or which appearance the
designer wants. Collapsing the two would mean either inventing per-stone facts
in shipped data or refusing to record them at all.

## Identity is not geometry

`stone.gem` sits beside the geometry fields and never touches them. A round
stone is not a diamond. A red stone is not a ruby. An 8×6 oval is not a
sapphire. Nothing in `jewelmind/gem/` reads a shape, a dimension, an outline or
a girdle plane, and `test_gem_no_category_dependency.py` enforces that
structurally by parsing the source for those attribute names rather than
trusting review.

The converse also holds: choosing a gem never changes what Atlas builds.

## Geometry hash vs definition hash

The practical consequence of the separation, and the sprint's most
load-bearing new mechanism.

- `definition_hash(definition)` — the whole document. Changing the gem changes
  it, because the design genuinely changed.
- `geometry_hash(definition)` — the document **minus** the parts that do not
  affect geometry (`stone.gem`, `material`, `manufacturing`, `project`,
  `preview`).

Two definitions with the same `geometryHash` build the same shape, so
`ModelService.generate()` reuses an already-built model instead of
re-running the kernel. That is why changing a gem is instant.

**Every exclusion in that list is an EMPIRICAL claim, verified by generating
geometry with each field varied and comparing the result — not an assumption
from reading the code.** A field may only be added to the exclusion list the
same way. `specs/gem/v1/test-vectors/geometry-identity-hash-vectors.json`
records the measured behaviour, and
`test_gem_identity.py::TestGeometryIdentitySeparation` re-measures it on every
run, including the complement (a real geometry change *does* move the hash) so
the test cannot pass by measuring nothing.

`definitionHash` keeps its existing meaning. `geometryHash` is a **separate**
value, not a repurposing of it — the same discipline
`docs/bible/08-alchemist/175-definition-hash-vs-compilation-hash.md` states for
a future `compilationHash`.

## Origin and treatment are independent axes

A stone may be natural **and** treated, or synthetic **and** untreated. So
`origin` is not a boolean and treatment is not a flag:

- `origin` — `NATURAL | SYNTHETIC | SIMULANT | COMPOSITE | UNKNOWN`, checked
  against the entry's own `applicableOrigins` by `JM-GEM-002`. A cubic zirconia
  declared `NATURAL` is refused rather than corrected, because resolving it
  would mean deciding whether the user meant the material or the origin.
- `treatments` — a list of declarations, each with a type, a `status`, a
  `disclosure` source and a confidence.

### Three states that must never be conflated

| State | Representation | Meaning |
| --- | --- | --- |
| Nothing recorded | `treatments: []` | Nobody said anything about treatment. |
| Declared untreated | one entry, `status: NOT_PRESENT` | Someone asserted the stone is untreated. |
| Treated, kind unstated | one entry, `treatment: UNKNOWN`, `status: PRESENT` | Someone asserted a treatment exists but did not name it. |

An empty list is **not** a claim of being untreated. Rendering the first state
as the second would put a claim in the technical specification that the user
never made, so `treatment_summary()` keeps them apart and the Studio control
keeps them as distinct options.

`"trattato"` / `"treated"` therefore resolves to the `UNKNOWN` treatment type.
Mapping it to `FRACTURE_FILLING` because emeralds are commonly oiled would be
inventing a gemological claim.

## What the system deliberately does not do

Every one of these is absent because it would require professional evidence
JewelMind does not have. Each is recorded as `PLANNED` or `OUT_OF_SCOPE` in
`specs/capabilities/jewelmind-capabilities.json`, and
`test_capability_coverage.py` asserts that no seventh `JM-GEM-*` rule has
appeared.

- **No hardness or durability data.** No Mohs value, no toughness class.
- **No heat-sensitivity or treatment-safety rule.** Nothing warns that a stone
  should not be heated, cast in place, or steam-cleaned.
- **No setting recommendation derived from the gem.** A bezel is not suggested
  for a soft stone, and a prong setting is not refused for one.
- **No gemological certification.** `origin` and `treatments` record what
  someone **declared**, with the declaration's source. Nothing verifies a claim
  and no lab report is stored as evidence.
- **No measured optics.** A visual profile's `ior` and `dispersion` are
  rendering parameters chosen to look plausible on screen.

The registry is an **internal taxonomy** (`provenance: INTERNAL_TAXONOMY`),
sufficient to identify, name and draw a gem. `SOURCED` and
`PROFESSIONALLY_VALIDATED` exist in the vocabulary and are used by zero entries,
which is honest rather than a gap to fill casually.

## Never guessed, never substituted

`resolve_gem()` never raises and never picks a different real gem. A design
referencing an entry that has since been removed still loads: resolution
degrades to `unknown`, sets `wasUnresolved`, and preserves the original
reference so a reader can see what was asked for. An unrecognized term resolves
to *nothing* rather than to the nearest-looking entry.

The visual fallback is deliberately **neutral**, not diamond-like. Falling back
to a brilliant colourless stone would render an unidentified gem as the most
valuable possible reading of itself — the one appearance a fallback must never
have.

## Cut names and species names are different vocabularies

Sprint 20 established that `stone.shape = "emerald"` is the clipped-corner
**outline**, and that a shape synonym must never resolve a species name to a cut
(`STONEV2-GOV-008`). The mirror obligation lands here: Designer must not
silently resolve a **cut** name to a **species** either.

So `"emerald"`/`"smeraldo"` and `"pearl"`/`"perla"` are reported as **ambiguous**
and produce a clarification asking whether the user meant the cut or the
material — the same treatment bare `"gold"` already gets. They are excluded from
the gem alias index precisely so a lookup cannot resolve one by accident.

## Boundaries

- `jewelmind/gem/` imports no jewelry category, no geometry, no kernel, and not
  `JewelryDefinition` (which would smuggle the whole ring domain across in one
  import). Enforced by AST inspection.
- `jewelmind/gem/__init__.py` **imports nothing**, and that is load-bearing:
  `domain/schema.py` imports `jewelmind.gem.models` for its vocabularies while
  `gem` submodules must not import `domain.schema`. The graph is acyclic only
  because the package init pulls in no submodule — the same trap
  `jewelmind/stone/__init__.py` documents.
- Designer proposes `gemId`, `origin`, `customName` and `note` only.
  `visualProfileId` is a presentation choice rather than design intent, and
  `treatments` is a list a dotted-path patch cannot express; both are set
  through the Studio UI and the API.
- Conversation gained **no new action type**. A gem request is a
  `MODIFY_DESIGN_PROPOSAL` routed through the real `DesignerService`, so no RFC
  was required and no code in `conversation/` writes a JDL path directly.

## Arrangement is a model, not a capability

`StoneInstance` carries an `instanceId`, a `StoneRole` and its own
`GemIdentity`, so a future halo or three-stone design can give each stone a
different gem. **No generator builds more than one stone**, `JewelryDefinition`
has no `stones` field, and the capability registry records the arrangement half
as `PLANNED`. The model's existence must not be read as a working feature —
`test_gem_identity.py::TestStoneInstance` asserts that boundary explicitly.

## Governance

See [`gem-governance.md`](gem-governance.md) for the full `GEM-GOV` rules.
