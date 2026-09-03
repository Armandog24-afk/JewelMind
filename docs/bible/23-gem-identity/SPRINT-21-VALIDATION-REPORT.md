---
id: JM-BIBLE-GEM-SPRINT-21-REPORT
title: "Sprint 21 validation report — Gem Identity & Material System v1"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-03
source_of_truth: false
depends_on:
  - JM-BIBLE-GEM-README
implementation_status: current
professional_validation: not_required
normative: false
---

# Sprint 21 validation report — Gem Identity & Material System v1

What was verified by running the code, what was found and fixed, and what is
honestly incomplete.

## Test results

| Gate | Result |
| --- | --- |
| `backend/.venv/Scripts/python -m pytest -q` | **1590 passed**, 1 pre-existing unrelated warning (Starlette's `httpx` deprecation notice) |
| `python -m jewelmind.geometry_quality.cli verify-all` | **All 39 goldens PASS**, **zero baseline updates** |
| `frontend/ npx tsc -b` | clean |
| `frontend/ npm run test` | **157 passed** across 24 files (148 before `GemControls.test.tsx`) |

New tests this sprint: `test_gem_identity.py` (119), `test_gem_designer_language.py`
(45), `test_gem_api.py` (16), `test_gem_no_category_dependency.py` (9),
`gemMaterials.test.ts` (11), `GemControls.test.tsx` (9), plus 3 new guards in
`test_capability_coverage.py` and 1 in `test_forge_registry.py`.

## What was verified by execution, not by reading

- **Geometry/identity hash separation.** Geometry was generated with each
  candidate non-geometry field varied, and the output compared, before that
  field was added to `geometry_hash()`'s exclusion list. The reuse path was
  then exercised end-to-end through the HTTP API: two generate calls differing
  only in `stone.gem.gemId` produce different `definitionHash` and `modelId`
  values, an identical `combinedMetalVolumeMm3`, and a reported
  `generationDurationSeconds` of exactly `0.0` on the second call — reuse, not
  a fast rebuild. The complement is asserted too (a band-width change *does*
  move the geometry hash), so the test cannot pass by measuring nothing.
- **Designer gem interpretation.** Eight scenarios were run through the real
  `DesignerService` with `FakeDesignerProvider`: `rubino centrale`,
  `zaffiro blu` + `sintetico`, `diamante sintetico`, `smeraldo` (ambiguous),
  `perla` (ambiguous), `tanzanite` (unrecognized), a custom material with a
  name, and a MODIFY preserving every untouched field.
- **Conversation reference resolution.** Gem, origin and treatment words
  resolve the target to `STONE`; metal words keep resolving to
  `MATERIAL_APPEARANCE`; cut/species words resolve nothing; a bare comparative
  stays ambiguous.
- **Boundary enforcement.** AST inspection over every file in
  `jewelmind/gem/`, not `import` — a cached module imports fine regardless of
  what it depends on.

## Defects found and fixed during the sprint

1. **`GeneratedModel` dataclass ordering.** `geometry_hash: str = ""` placed
   before required fields raised `TypeError: non-default argument
   'generator_version' follows default argument`. Moved last.
2. **Wrong `AppError` construction.** The codebase's convention is subclasses
   with class-level `status_code`/`code`, not keyword arguments. Proper
   `GemIdInvalidError`/`GemNotFoundError` subclasses were added.
3. **Cache-shared test isolation.** `test_api_hardening`'s patched-generator
   test passed alone and failed in the suite: geometry reuse satisfied it from
   the module-level `model_service` singleton's cache. Fixed with a
   test-unique `band.width` rather than by weakening the reuse path.
4. **`_apply_patch` split only once.** `stone.gem.gemId` is three segments
   deep, so a single `split(".", 1)` wrote a literal `"gem.gemId"` key that
   the schema rejects as unknown — turning a valid gem proposal into a silent
   failure. Now walks the whole dotted path and materializes `stone.gem` when
   it is `None`.
5. **`flatten_definition` could not hold a list-valued leaf.** `FieldDiff`
   takes a scalar, and `stone.gem.treatments` was the first list-valued leaf in
   any definition, so an otherwise valid interpretation raised a validation
   error. Lists are now rendered as sorted-key canonical JSON, which keeps the
   value faithful *and* keeps `changed` detection exact. Reporting a length or
   a placeholder would have made the review diff lie about what the user is
   approving.
6. **The 422 handler crashed on any `ValueError`-raising validator.**
   `_json_safe()` handled non-finite floats but not arbitrary objects, and
   `errors()` puts the exception *object* in `ctx` for a `model_validator`. A
   custom gem with no name came back as an opaque 500 instead of a 422 naming
   the field. Generalized to stringify any non-JSON value — a **pre-existing**
   fault that also applied to Sprint 20's Stone v2 outline validators.
7. **TypeScript strict `possibly undefined`** on the profile-table lookups in
   `gemMaterials.ts`. Resolved with documented non-null assertions plus a test
   that pins the invariant they rely on.

## Pre-existing drift found and closed

- **`specs/forge/v1/current-rule-registry.json` was missing Sprint 19's
  `JM-SETTING-003`/`JM-SETTING-004`.** FORGE-GOV's "update the registry in the
  same change" rule was enforced by nothing but attention. Both entries were
  added, and
  `test_forge_registry.py::test_registry_lists_every_live_jm_rule` now compares
  the registry against `validation/rules.py` in both directions, so the whole
  class of omission fails the suite. Recording the bezel rules' bezel-only
  scope required an additive `settingFamilies` property on the registry
  schema.
- **`designer/prompts.py::build_jdl_fields_block()` was a hand-written list
  that had already drifted** — it still named only the seven Stone v1 cuts
  after Sprint 20 added fourteen more, and omitted Sprint 19's bezel fields, so
  the prompt described a smaller JewelMind than the one enforcing the
  proposals. Now derived from `capability.KNOWN_JDL_FIELD_PATHS`, with a test
  asserting every known path appears.
- **`013-functional-requirements.md` had no entries for Sprints 19 or 20.**
  Sprint 21's requirements (`JM-FR-032` through `JM-FR-038`) were added.
  Sprint 19's and Sprint 20's were **not** back-filled — writing requirements
  retroactively for work whose intent was recorded elsewhere would be
  reconstructing history rather than documenting it. The gap is recorded here
  instead.
- **`implementation-inventory.md` still said the engine ran "sixteen business
  rules"**; it runs twenty-four (16 + 2 bezel + 6 gem).

## What is deliberately absent

Every item below is recorded as `PLANNED` or `OUT_OF_SCOPE` in
`specs/capabilities/jewelmind-capabilities.json`, and
`test_capability_coverage.py::test_no_gem_property_rule_is_claimed_as_current`
asserts that no seventh `JM-GEM-*` rule has appeared.

- No hardness, Mohs value, toughness or durability data.
- No heat-sensitivity or treatment-safety rule.
- No setting recommendation derived from the gem.
- No gemological certification, and no lab report stored as evidence.
- No measured optics — a profile's `ior` and `dispersion` are rendering values.
- No multi-stone arrangement. `StoneInstance` is a model; no generator builds
  more than one stone, and `JewelryDefinition` has no `stones` field.
- No external gem data source. `provenance: SOURCED` exists in the vocabulary
  and is used by zero entries.

## Reachability notes, stated rather than hidden

- **`JM-GEM-003`'s second branch** ("a custom name on a canonical gem") is
  unreachable through the API: `JdlGemIdentity` refuses the combination before
  Forge runs. It fires only for an identity constructed in Python. The test
  asserts the JDL rejection and says why.
- **`JM-GEM-006`** (deprecated entry) never fires today because no registry
  entry is deprecated. The guarantee is proved against a `GemDefinition` built
  in the test rather than by deprecating shipped data.
- **`GemDataProvenance.SOURCED` and `PROFESSIONALLY_VALIDATED`** are unused, as
  is `GemEntryStatus.DEPRECATED`. All three are honest vocabulary for states
  that do not yet exist.

## Conversation: no new action type

Section 21 asked for structured semantics for replacing a gem, changing origin,
adding or removing a treatment, changing the visual profile, and marking a gem
custom or unknown. All of these are expressed through the existing
`MODIFY_DESIGN_PROPOSAL` action, routed through the real `DesignerService`, and
surface in `technicalChanges` as the real changed dotted paths
(`stone.gem.gemId`, `stone.gem.origin`, …).

Adding a fourteenth `ConversationActionType` would have required an RFC per
CLAUDE.md's Conversation rules, and would have bought nothing: the existing
action already carries the semantics, and nothing in `conversation/` writes a
JDL path directly. What Conversation did gain is reference resolution — a gem,
origin or treatment word now resolves the target to `STONE`, mirroring the
existing metal-word exception.

## Professional validation status

Unchanged: **zero records** in the active professional-validation registry.
Every gem entry and every visual profile is `NOT_REVIEWED`, and
`test_capability_coverage.py::test_active_professional_validation_registry_is_still_empty`
continues to assert it.
