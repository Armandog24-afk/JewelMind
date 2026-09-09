---
id: JM-BIBLE-ESM-SPRINT-27-REPORT
title: "Sprint 27 Validation Report — Extended Setting Modes v1"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-09
source_of_truth: true
depends_on:
  - JM-BIBLE-ESM-README
implementation_status: current
professional_validation: not_required
normative: false
---

# Sprint 27 validation report — Extended Setting Modes v1

What was built, what was measured, and every defect found and fixed. Numbers
here were read out of the real artefacts rather than recalled.

## What was built

| Capability | Where | Status |
| --- | --- | --- |
| A setting-mode taxonomy: 20 modes, 3 axes, 15 reserved | `setting/modes.py` | CURRENT |
| A registry whose geometry axis is MEASURED from the live builders | `setting/capability.py::setting_modes()` | CURRENT |
| Channel setting: two walls, optional end caps | `setting/channel.py` | CURRENT |
| Bar setting: transverse bars, symmetric or asymmetric | `setting/bar.py` | CURRENT |
| Flush / gypsy setting: a collar with the stone cut out | `setting/flush.py` | CURRENT |
| Tension setting: two opposing supports | `setting/tension.py` | PARTIAL |
| Partial bezel: openings cut through the full wall | `setting/bezel.py` | CURRENT |
| Open gallery head: windows pierced through the basket | `setting/head.py` | CURRENT |
| Shared micro-prong retention | `setting/retention.py` | CURRENT |
| Per-component provenance | `setting/{models,result}.py` | CURRENT |
| Six Forge rules (`JM-SETTING-008`…`013`) | `validation/engine.py::_setting_mode_rules` | CURRENT |
| Nineteen new Geometry Inspection facts | `geometry/inspection/` | CURRENT |
| Studio controls for every mode axis | `frontend/src/components/SettingModeSection.tsx` | CURRENT |
| Designer/Conversation vocabulary for every implemented mode | `designer/{capability,normalizer}.py` | CURRENT |
| `specs/setting/v3/` — 16 generated artefacts | `specs/setting/v3/` | CURRENT |
| Seven new Golden cases | `goldens/solitaire-v1/ESM-00*` | CURRENT |

## What was measured

### Every family builds a real, measurable solid

| Family | Component | Volume (mm³) | Solids |
| --- | --- | --- | --- |
| channel | `channel_walls` | 109.760 | 1 |
| bar | `bars` | 66.150 | 3 |
| flush | `flush_collar` | 229.758 | 1 |
| tension | `tension_supports` | 43.158 | 2 |
| bezel (partial) | `bezel` | 20.632 | 3 |
| prong (open gallery) | `basket_support` | 54.190 | 1 |

### Three findings that only a measurement could establish

- **The recess removes real metal.** `ESM-003` and `ESM-006` record
  `basket_support` at `79.3716` where an untouched head is `83.1558`. A recess
  that removed nothing would be indistinguishable from one never applied.
- **The windows keep the head connected.** `ESM-005`'s head is `54.190` rather
  than `83.156` and is still **one** solid. The rims are what hold it together,
  and the schema's `windowHeightFraction < 1.0` bound is what preserves them.
- **Sharing genuinely shares.** `ESM-007` carries 22 pavé stones and a
  `pave_retention` component of **46 solids**. An individual field would need
  88. That number is the only evidence the shared-corner topology is real rather
  than a label.

### Backward compatibility

- A default prong solitaire's combined metal volume is still
  `341.44334316909976 mm³`.
- **All 54 pre-existing Golden baselines verified unchanged**;
  `git status --porcelain goldens/` reports only the manifest and the seven new
  directories.
- Every new family and every new variant is reached only by a document that asks
  for it.

### Repeatability

Every family was generated twice and compared: combined metal volume, every
component volume, and the aggregate bounding box, at `rel=1e-9`. Kernel-derived
floats are not bit-identical across OpenCascade builds — Sprint 5's CI proved it
— so the tolerance is a software comparison tool and never a manufacturing one.

## Defects found and fixed

Classified per the brief's scheme.

### A. Introduced defects (found by test, fixed at the source)

1. **`SHARED_PRONG` shared nothing.** `_lattice_anchors()` switched on
   `strategy == "SHARED_BEAD"` literally, so the new strategy fell into the
   individual-bead branch and produced four pieces per stone. Fixed by
   extracting `SHARED_RETENTION_STRATEGIES` — one membership test, stated once,
   because two copies is how a new shared strategy silently becomes an
   individual one. The 46-vs-88 count above is what proves the fix.
2. **Designer reported channel and bar setting as unsupported.** The
   reserved-mode concepts are derived from `RESERVED_SETTING_MODES`, and
   `RETENTION_CHANNEL`/`RETENTION_BAR` strip to the tokens `channel` and `bar` —
   which are real families with real generators. Designer would therefore have
   told a user that channel setting is unsupported while the product was
   building it, precisely the misreport Sprints 18, 20 and 26 each had to
   correct. Fixed by refusing any stripped token that names a live
   `SettingType`, read from the enum rather than listed.
3. **Two reserved modes collided on one concept.** `CHANNEL_TAPERED` and
   `BAR_TAPERED` both strip to `tapered`. Answering a request for "a tapered
   setting" with one of the two reasons would pick an interpretation the author
   never gave, so an ambiguous token is not emitted at all.
4. **The new enum fields could not be normalized.** `setting.mode.modeId`,
   `setting.headArchitecture` and `setting.prongStyle` had no synonym table, so
   Designer silently dropped a proposed value. Fixed by DERIVING three tables
   from the registry's own `designerTerms`, split per axis so a head term cannot
   resolve into `setting.mode.modeId`.
5. **A mode patch on a design with no mode produced an invalid proposal.**
   `SettingModeSpec.modeId` is required, so a dotted patch left a half-formed
   object — exactly the defect class Sprint 26 hit when Designer could not
   create a pavé. Fixed by seeding the domain's own default mode first, from the
   same function the Studio panel mirrors.
6. **The bezel wall controls were shown for every non-prong family.** The panel
   gated them on `type !== 'prong'`, which was correct with two families and
   wrong the moment there were six: it offered bezel wall dimensions for a
   channel. Fixed by gating on the bezel family.

### B. Pre-existing defects fixed in passing

1. **The JDL schema rejected every bezel document.**
   `specs/jdl/v1/jdl.schema.json` declared `setting.type` as
   `{"const": "prong"}` — so it had structurally refused every `bezel` document
   the backend has accepted since Sprint 19, and nothing compared the two. The
   schema's own Sprint 22 note claims the subtree was "generated from the live
   Pydantic models"; this field evidently was not. Fixed by regenerating the
   whole subtree from `SettingSpec.model_json_schema()`, which makes that class
   of drift impossible rather than unlikely.
2. **Sprint 23's advanced head and prong fields had no Studio control at all.**
   `prongStyle`, `headArchitecture` and `seatMode` had real builders and were
   unreachable from the workspace, so a capability the backend genuinely had
   could only be used through the API. `SettingModeSection.tsx` exposes all
   three — which is also why the mode registry can honestly record
   `studio: CURRENT` for those modes rather than PLANNED.
3. **The capability-coverage guard only checked CURRENT rows.** It collected the
   `*_setting` rows marked CURRENT and compared the set, which would have
   silently accepted a row whose status disagreed with the live registry.
   Tightened to compare the STATUS of every family — which is what made
   `tension`'s honest PARTIAL expressible at all.
4. **A stale limitation.** `docs/known-limitations.md` still said "only round
   stones and 4/6-prong solitaire settings", which had been wrong since
   Sprint 18. Corrected with what is actually true.

### C. Expected behaviour, recorded rather than changed

- **A partial bezel is several solids.** Cutting *n* openings from a closed ring
  leaves *n* arcs, joined through the head below rather than to each other.
  `BEZEL_WALL_CONTINUOUS` correctly reports `false`, and the variant is reported
  beside it so that reads as a fact rather than a surprise.
- **Channel and bar produce congruent volumes on their defaults.** For a round
  stone with symmetric defaults, both are two `0.7 × 6.5` prisms at `±3.6` —
  rotated 90° from each other. Real and correct; the Golden cases use
  non-default parameters so each locks in something distinguishable.
- **`definitionHash` changed for every document.** `SettingSpec` gained four
  fields and defaults participate in canonical JSON. Every spec vector and
  example was regenerated by running the real implementation, as Sprints 22, 24,
  25 and 26 each did.

### D. Current limitations

Recorded in [`execution-boundary.md`](execution-boundary.md) and
`docs/known-limitations.md`, with the dependency order for closing them.

### E. Professional validation required

The tension family's structural behaviour, and every dimension in every mode.
`JM-SETTING-012` reports the first; the goldens' `knownLimitations` record the
second. Nothing in this sprint is professionally validated, and the active
validation registry still holds zero records.

### F. Unknown

None outstanding.

## Test expectations corrected in my own new tests

Each fix went to the real interface, never to a looser assertion:

- `report.assemblyResult.stoneMetalSeparation`, not `report.assembly`.
- `build_specification(definition, model, validation_results, generated_at)` —
  the exporter takes a fixed timestamp rather than reading the clock, which is
  what keeps a rendered specification reproducible.
- `RawDesignerResponse.detectedUnsupportedFeatures`, and `DesignIntent` requires
  a `sourceText`.
- The fingerprint-purity check became an **AST** check for real imports and
  calls. A text scan was the wrong instrument: the module's own docstring
  documents the rule by naming the forbidden sources, so scanning for the words
  flagged the documentation.
- The open-gallery check now asserts the guarantee that actually holds — the
  schema's `< 1.0` bound keeps a rim, so the wall stays one solid — plus the
  schema's refusal of a fraction at or above 1.0, which is where the real
  boundary is. The original test asserted a raise that correctly did not happen.

## Architectural audit (brief §40)

| Check | Result |
| --- | --- |
| No second Setting Engine | One `setting_generators()`, one `generate_setting()`, called once by the assembly |
| No second Arrangement Engine | No `compile_arrangement`/`resolve_arrangement`/`ring_angles_deg` anywhere under `jewelmind/setting/` (AST) |
| No Stone/Gem/Halo/Pavé duplication | No new module imports `jewelmind.arrangement`, a category, or `JewelryDefinition` (AST) |
| No second retention implementation | No `makeSphere` outside `retention.py` (AST) |
| No second offset pipeline | `flush.py` calls `offset_stone_outline()` and contains no `offset2D` (AST) |
| No geometry path bypassing Alchemist | `generate_setting(` appears once in the assembly; no family generator is named there |
| No AI-generated geometry | Designer proposes JDL scalars only; `designer/` imports no geometry module |
| No duplicated registry | `settingGeometry` is measured from the live builders, both directions asserted |
| No capability CURRENT without runtime proof | Every CURRENT mode has a builder and a Golden case; `TestCapabilityHonesty` |
| schema ↔ Pydantic | `test_setting_schemas.py`, and the JDL subtree is regenerated from the model |
| Pydantic ↔ TypeScript | `SettingType`/`HeadArchitecture`/`PaveRetentionStrategy`/`SettingModeId` mirrored; `npx tsc -b` clean |
| registry ↔ Forge | `test_forge_registry.py::test_registry_lists_every_live_jm_rule`, both directions |
| registry ↔ capability matrix | `test_capability_coverage.py`, status-for-status |
| JDL ↔ compiler ↔ Atlas ↔ Inspection | `TestCompilerIntegration`, `TestGeometry`, `TestInspection` per family |
| geometry ↔ Foundry | STEP/STL/JSON/specification export asserted for every new family |
| Studio ↔ backend | `SettingModeSection.test.tsx` asserts the option lists equal the backend's literals |
| Designer ↔ JDL | `TestDesigner` drives the real `DesignerService` |
| Conversation ↔ design state | `TestConversation` asserts field preservation on a MODIFY turn |
| documentation ↔ implementation | Every number in this report read from a real artefact |

## Gates

| Gate | Result |
| --- | --- |
| `ruff check .` | All checks passed |
| `pytest -q` | see the commit's CI run |
| `verify-all` | All 61 golden(s) PASS; zero pre-existing baselines modified |
| `npx tsc -b` | exit 0 |
| `npm run test` | all frontend suites pass |
