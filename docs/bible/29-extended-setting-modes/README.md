---
id: JM-BIBLE-ESM-README
title: "Extended Setting Modes v1"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-09
source_of_truth: true
depends_on:
  - JM-BIBLE-SETTING-README
  - JM-BIBLE-SETTINGV2-README
  - JM-BIBLE-PAVE-README
  - JM-BIBLE-STONEV2-README
  - JM-BIBLE-ARRANGE-README
  - JM-BIBLE-FAMILY-README
  - JM-BIBLE-HALO-README
related_documents:
  - JM-BIBLE-ADR-013
implementation_status: partial
professional_validation: not_required
normative: true
---

# Extended Setting Modes v1

Sprint 27. The machine-readable half lives at
[`specs/setting/v3/`](../../../specs/setting/v3/README.md); Sprint 19's
[`specs/setting/v1/`](../../../specs/setting/v1/README.md) and Sprint 23's
[`specs/setting/v2/`](../../../specs/setting/v2/README.md) remain accurate for
what they describe, and all 18 SETTING-GOV plus 12 SETTINGV2-GOV rules still
apply in full.

**This is an EXTENSION of the Setting System, not a second setting engine.**
Every new family joins the same `setting_generators()` registry the existing two
are in, is reached through the same `generate_setting()` entry point, and
receives the same head and seat handling. There is still exactly one dispatch,
one head step, one seat step and one placement authority.

**Implementation status is PARTIAL, precisely.** Twenty setting modes are
implemented and every one builds real geometry; two of them —
`PRONG_SHARED` and `TENSION_OPPOSED` — are honestly PARTIAL rather than CURRENT,
for two different and specific reasons given below. Fifteen further techniques
are named, reserved, and refused by the model.

## What a setting mode is

A **setting mode** is a named strategy for holding or supporting a stone. It is
not the stone, not the material, not where the stones sit, and not the resulting
solids:

| Question | Owner |
| --- | --- |
| What the stones ARE | Stone System v2 |
| What they are MADE OF | Gem Identity v1 |
| WHICH individual stones | Stone Arrangement Engine v1 |
| WHERE they sit | Stone Arrangement Engine v1 |
| WHICH FIELD populates a surface | Pavé & Microsetting Engine v1 |
| **HOW metal HOLDS them** | **this section** |
| The solids | Atlas |

## Why the taxonomy exists at all

Before this sprint the Setting System carried four independent axes —
`settingType`, `prongStyle`, `headArchitecture` and the pavé's own
`PaveRetentionStrategy` — each with its own registry, each honest about itself,
and no single place that could answer *which setting techniques does JewelMind
actually build?* A reader had to consult four registries and know that a
`SHARED_BEAD` and a `V_PRONG` are the same KIND of thing expressed at different
points in the pipeline.

`setting/modes.py` adds the missing noun. `capability.py::setting_modes()` is
the registry, and it is **not a fifth parallel one**: each row's
`settingGeometry` axis is **measured** from the live builder registries —
`setting_generators()`, `prong_solid_builders()`, `head_builders()`,
`retention_builders()` — rather than declared. A mode cannot claim a solid no
builder produces, and a builder cannot exist without a row, because
`test_extended_setting_modes.py` asserts both directions.

## The three axes are preserved, not collapsed

| Axis | What it chooses | Selected by |
| --- | --- | --- |
| `PRIMARY` | How the design's own stone is held | `setting.type` (+ `setting.mode`) |
| `HEAD` | What the setting rises from | `setting.headArchitecture` |
| `RETENTION` | How a FIELD of small stones is held | the pavé's `retention.strategy` |

A primary mode and a head mode are present in one design **at the same time**;
they are not alternatives. "A bezel on a martini with relief" is one setting
with three choices, and collapsing the axes into one enum would make it
inexpressible.

## The implemented modes

### PRIMARY — how the design's own stone is held

| Mode | Status | What is built |
| --- | --- | --- |
| `PRONG_ROUND` | CURRENT | The pre-Sprint-23 cylinder, unchanged and still the default |
| `PRONG_TAPERED` | CURRENT | A cone frustum |
| `PRONG_CLAW` | CURRENT | A shaft fused to a tapered head |
| `PRONG_V` | CURRENT | A cylinder with a V notch cut into its tip |
| `PRONG_SHARED` | PARTIAL | Real prongs at EXPLICIT positions carrying `servesStoneInstanceIds` |
| `BEZEL_FULL` | CURRENT | The continuous offset wall, preserved byte-identically |
| `BEZEL_PARTIAL` | CURRENT | That same wall with evenly spaced angular openings cut through it |
| `CHANNEL_LINEAR` | CURRENT | Two parallel walls with the stones between them, with optional end caps |
| `BAR_TRANSVERSE` | CURRENT | Transverse bars across a run, one component carrying every bar |
| `FLUSH_GYPSY` | CURRENT | A solid collar with the stone's own solid cut out of it |
| `TENSION_OPPOSED` | PARTIAL | Two opposing supports, each relieved by the stone |

### HEAD — what the setting rises from

| Mode | Status | What is built |
| --- | --- | --- |
| `HEAD_BASKET` | CURRENT | The pre-Sprint-23 hollow cylindrical wall, preserved character-for-character |
| `HEAD_PEG` | CURRENT | A basket on a narrower peg, joined by a structural flare |
| `HEAD_MARTINI` | CURRENT | A hollow conical wall |
| `HEAD_TULIP` | CURRENT | A concave flare of stacked frusta |
| `HEAD_OPEN_GALLERY` | CURRENT | The basket wall with evenly spaced windows pierced through it |

### RETENTION — how a field of small stones is held

| Mode | Status | What is built |
| --- | --- | --- |
| `RETENTION_BEAD` | CURRENT | One bead per lattice corner of each stone |
| `RETENTION_SHARED_BEAD` | CURRENT | One bead per corner, shared by every stone touching it |
| `RETENTION_MICRO_PRONG` | CURRENT | A cylinder normal to the surface at each corner |
| `RETENTION_SHARED_PRONG` | CURRENT | A micro prong at each SHARED corner |

## The two PARTIAL modes, and why each is PARTIAL

### `TENSION_OPPOSED` — complete geometry, absent engineering

The solids are real and the grooves the relief leaves are real. What is **not
modelled** is the thing a tension setting exists to do: nothing here computes the
elastic response of the metal, the force the supports apply, whether the stone
would be retained under load, wear or impact, or whether the configuration is
manufacturable as a tension setting at all.

Those require material properties and a validated engineering model this project
does not have, so **no threshold is invented** — there is no minimum shoulder
section, no maximum span, no spring constant and no safety factor. The mode
carries `professionalReviewRequirement: REQUIRED`, the component metadata
carries `structuralBehaviourModelled: false`, Geometry Inspection reports that as
a fact, and `JM-SETTING-012` says a qualified professional must look.

Marking it CURRENT would read as a claim that the function is modelled. It is
not.

### `PRONG_SHARED` — real metal, stated position

A prong serving two or more stones is expressed through EXPLICIT positions
carrying `servesStoneInstanceIds`; the prongs are real solids and the assignment
is reported per component. What is not provided is DERIVATION of the shared
position from the two stones' own geometry, so whether a shared prong actually
reaches both stones it names is a **geometric fact for inspection** rather than
a guarantee. No interface authors explicit positions yet, which is why Studio,
Designer and Conversation are PLANNED for this one mode.

This supersedes Sprint 23's record, which said shared prongs were not generatable
at all because one stone component was built per model. Sprints 24–26 made
multiple stone components real; what remains missing is narrower and is stated
narrowly.

## What is reserved, and why

Fifteen techniques are named in `RESERVED_SETTING_MODES` with the **real
technical reason** each is absent, never the word "planned". A reader should be
able to tell what would have to exist first. The four that matter most:

- **`HEAD_TRELLIS`** — interwoven curved rails need a swept solid along a 3D
  spline. The pipeline builds solids of revolution and lofts reliably; a swept
  trellis is not yet verifiable, and a "simplified trellis" that was really four
  bent prongs would be a different structure wearing the name.
- **`HEAD_AZURE`** — azure/ajouré work is arbitrary decorative piercing, whose
  pattern is not expressible as parameters. `HEAD_OPEN_GALLERY` is the
  parametric subset that is, and it is deliberately not called azure.
- **`RETENTION_CHANNEL`** / **`RETENTION_BAR`** — the pavé's retention anchors
  are lattice CORNERS. That is the right topology for a bead or a prong and the
  wrong one for a rail running a whole row or a bar sitting at a cell midpoint.
  Channel and bar setting exist as their own PRIMARY families instead, which is
  where a rail's extent is actually stated.
- **`HALO_HIDDEN_SETTING`** — halo retention metal is still PLANNED (Sprint 25
  recorded halo `settingGeometry` as false, and it still is). A mode here would
  have nothing to build.

## What this sprint did NOT do

- **`GeometryPlan` is still not materialized.** The provenance requirement — every
  setting component traceable to the mode, the stone and the placements it came
  from — is met by `SettingComponentProvenance` on the existing setting result,
  where the component's other facts already live. Materializing `GeometryPlan`
  is an explicit ADR condition, and inventing an unrequested compiler stage to
  hold a fact about a component would have been a speculative abstraction.
- **No professional threshold was added anywhere.** No minimum wall thickness,
  no minimum bar, no collar thickness, no clearance between a wall and a stone,
  no settability judgment. Every dimension is a construction parameter supplied
  by the document.
- **No second engine of any kind.** Not a placement engine (a channel states its
  own extent and never computes a stone position), not a retention
  implementation (every retention solid comes from `setting/retention.py`), and
  not a second offset pipeline (the flush collar reuses the bezel's verified
  one).

## Where the code lives

| Concern | Module |
| --- | --- |
| The taxonomy, the spec model, resolution, identity | `setting/modes.py` |
| The registry and the capability axes | `setting/capability.py` |
| Per-family parameters | `setting/models.py` |
| The shared construction frame | `setting/frame.py` |
| The shared result and provenance record | `setting/result.py` |
| Channel / bar / flush / tension generators | `setting/{channel,bar,flush,tension}.py` |
| The partial bezel | `setting/bezel.py` |
| The open gallery | `setting/head.py` |
| Shared micro-prong retention | `setting/retention.py` |
| JDL → Setting translation | `geometry/setting_adapter.py` |
| Forge rules | `validation/engine.py::_setting_mode_rules` |
| Studio controls | `frontend/src/components/SettingModeSection.tsx` |

## Read next

- [`setting-mode-governance.md`](setting-mode-governance.md) — the 14 ESM-GOV
  rules, each with the test that enforces it.
- [`execution-boundary.md`](execution-boundary.md) — exactly what does and does
  not execute, and in which order the gaps have to close.
- [`taxonomy-coverage-review.md`](taxonomy-coverage-review.md) — the coverage
  audit against the setting families used in contemporary jewelry CAD, with each
  deferral classified and justified.
- [`ADR-013`](../03-decisions/ADR-013-extended-setting-modes.md) — why the
  taxonomy is a derived registry rather than a fifth parallel one, and why
  `setting.mode` refines `setting.type` rather than competing with it.
- [`SPRINT-27-VALIDATION-REPORT.md`](SPRINT-27-VALIDATION-REPORT.md) — what was
  built, what was measured, and every defect found and fixed.
