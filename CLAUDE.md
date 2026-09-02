# CLAUDE.md — guidance for future coding agents working on JewelMind

JewelMind is a parametric jewelry CAD prototype. Read this before making
changes, especially anything touching `backend/jewelmind/geometry/`,
`backend/jewelmind/validation/`, or the shared domain types.

## Non-negotiable rules

- **Preserve CAD determinism.** Geometry generation must never depend on
  wall-clock time, randomness, or external network calls. The same
  `JewelryDefinition` must always produce the same geometry, volumes, and
  `definitionHash`. If you add a geometry parameter, make sure it's part of
  the definition, not read from environment/global state.
- **Never fake an export.** STEP and STL exports must always be real
  CadQuery/OpenCascade output written to disk and streamed back, never a
  placeholder file, a stub byte string, or a hardcoded sample file. If an
  export path can't be made reliable, say so in
  `docs/known-limitations.md` and implement the most robust fallback that
  is still real geometry (see how `stl_exporter.py` and
  `geometry/assemblies/solitaire.py` handle a failed boolean fuse: fall
  back to a multi-solid compound, never to nothing).
- **Never require Rhino, MatrixGold, JewelCAD, a desktop FreeCAD instance,
  or any other paid/interactive CAD software.** CadQuery + OpenCascade,
  driven headlessly through the `jewelmind` Python package, is the only CAD
  engine. Do not add a dependency that requires a GUI application to be
  running.
- **Never use an LLM to generate geometry at runtime.** Geometry comes
  exclusively from deterministic CadQuery code in
  `backend/jewelmind/geometry/`. It is fine to use an LLM (e.g. yourself)
  to *write* that code, but the running application must never call out to
  an LLM to decide dimensions, shapes, or placement.
- **Keep jewelry business rules out of UI code.** Validation logic lives in
  `backend/jewelmind/validation/` (authoritative) and its mirror
  `shared/validation/` (instant frontend feedback only). Never embed a
  numeric threshold or rule directly in a React component — add or extend a
  rule in both places and reference it by `ruleId` (see
  `docs/validation-rules.md`).
- **Keep the stone reference separate from metal geometry.** The stone
  solid must never be unioned into the band/prong/basket metal body, must
  never be included in a STEP/STL export unless the caller explicitly opts
  in (`includeStoneReference: true`), and must be visually distinct in the
  viewer (transparent gemstone-like material, not a metal material).
- **Use millimeters everywhere.** No unit field, no unit conversion. If you
  add a new length parameter, it's in mm, full stop.
- **Never claim manufacturing readiness.** Every technical specification
  export, and the frontend's permanent header notice, must keep stating
  that generated models are preliminary and require review by a qualified
  jewelry professional before production. Don't soften or remove this
  wording.
- **Run tests before declaring a change complete.** Backend: `cd backend &&
  .venv/Scripts/python -m pytest -q` (or `.venv/bin/python` on
  macOS/Linux). Frontend: `cd frontend && npm run test`. Both must pass.
  Also run `npx tsc -b` in `frontend/` — the project uses strict
  TypeScript and treats new `any`-shaped leaks as regressions.
- **Update documentation with architecture changes.** If you change the
  coordinate convention, add a geometry component, add/change a validation
  rule, or add an API endpoint, update the matching file in `docs/` in the
  same change (`geometry-conventions.md`, `validation-rules.md`,
  `domain-model.md`, `api.md`, `architecture.md` respectively).
- **Avoid broad unrelated refactors.** This codebase intentionally keeps
  domain logic, API plumbing, and UI presentation in separate layers (see
  `docs/architecture.md`). A bug fix or new parameter doesn't need a
  surrounding cleanup pass.

## Where things live (quick map)

- Canonical schema: `backend/jewelmind/domain/schema.py` (Pydantic,
  authoritative) + `shared/types/jewelry-definition.ts` (TypeScript mirror,
  kept in sync by hand).
- Validation rules: `backend/jewelmind/validation/engine.py` (authoritative)
  + `shared/validation/engine.ts` (frontend mirror).
- Geometry builders: `backend/jewelmind/geometry/components/*.py` (band,
  stone and prongs are thin re-exports of `geometry/shank/build_shank()`,
  `geometry/stone/build_stone()` and the Setting System; basket is real) +
  `geometry/shank/` (the Shank subsystem: profile, taper, builder,
  capability) + `geometry/stone/` (the Stone System: outline, builder,
  capability, errors) + `jewelmind/setting/` (the Setting System —
  category-neutral: models, capability, stone_interface, placement,
  prong, bezel, dispatch; never imports Ring) +
  `jewelmind/stone/` (the Stone System v2 core — category-neutral:
  models, capability, outline_validation, anchors, normalize,
  importing, dispatch, errors; never imports a jewelry category, and
  its `__init__.py` deliberately imports nothing) +
  `geometry/stone/profile.py` (the 3D reference profiles: faceted,
  cabochon, spherical) +
  `domain/stone_dimensions.py` (the shared LENGTH/WIDTH/DEPTH resolution
  both Atlas and Forge depend on) + `geometry/connection.py` (Shank →
  RingHead interface) + `geometry/setting_adapter.py` (JewelryDefinition
  → Setting contracts; the Ring-side translation point) +
  `geometry/assemblies/solitaire.py` (the RingHead — combines them).
- Coordinate convention: `backend/jewelmind/geometry/constants.py`,
  documented in `docs/geometry-conventions.md`.
- Exporters: `backend/jewelmind/exporters/` (STEP, STL, JSON,
  specification).
- API surface: `backend/jewelmind/api/routes.py` + `schemas.py` + docs in
  `docs/api.md`.
- Frontend state: one zustand store, `frontend/src/store/useProjectStore.ts`.
- Frontend 3D viewer: `frontend/src/components/ModelViewport.tsx` +
  `frontend/src/hooks/useComponentGeometries.ts` (fetches and parses each
  component's STL directly — no `useLoader`/Suspense, see the git history
  for why that approach was replaced).

## Explicitly out of scope (do not add without being asked)

Authentication, payments, subscriptions, a marketplace, multi-user
collaboration, image generation, prompt-to-CAD, or any other feature not
already described in `README.md`. If a task seems to call for one of
these, stop and ask rather than adding it.

## TECHNICAL BIBLE RULES

`docs/bible/` is the structured source of truth for JewelMind's product
rationale, architecture decisions, and constitutional rules — start at
[`docs/bible/README.md`](docs/bible/README.md). The rules above in this
file remain the fast, always-loaded summary; the Bible is where the full
reasoning, current-status matrix, and ADRs live. Future coding agents
must:

- **Read `docs/bible/README.md` before architectural work** — specifically
  before anything that would meet an "ADR required" condition (new CAD
  engine, non-additive schema change, moving validation authority, changing
  export defaults, changing the coordinate/unit system, or violating a
  Constitution law).
- **Identify related Constitution laws** in
  `docs/bible/00-foundation/004-jewelmind-constitution.md` before making
  the change, not after.
- **Identify affected ADRs** in `docs/bible/03-decisions/` and update or
  supersede them (never silently edit around one) if the change
  contradicts an accepted decision.
- **Update implementation-status documents when functionality changes** —
  at minimum `docs/bible/00-foundation/005-current-product-status.md` and
  `docs/bible/appendices/implementation-inventory.md`, in the same change
  as the code.
- **Never mark PLANNED functionality as CURRENT.** See the CURRENT /
  PARTIAL / PLANNED / VISION rule in
  `docs/bible/00-foundation/000-bible-governance.md`.
- **Create an ADR before violating an accepted architectural decision** —
  see "When an ADR is required" in the same governance document.
- **Update functional requirements and tests together** —
  `docs/bible/01-product/013-functional-requirements.md` should reflect
  what the test suite actually proves, not what is merely intended.
- **Report contradictions between code and the Bible explicitly** —
  per the Bible's fundamental rule: never silently change the meaning of
  the product to make a contradiction disappear.
- **Avoid rewriting the Bible merely to justify an accidental
  implementation** — if the code did something unintended, fix the code
  (or write a deliberate ADR if the accident turns out to be the better
  design), not the documentation, unless the documentation itself was
  simply wrong.

## JEWELRY DOMAIN RULES

`docs/bible/04-jewelry-domain/` is the authoritative jewelry-domain
model — start at
[`docs/bible/04-jewelry-domain/README.md`](docs/bible/04-jewelry-domain/README.md).
Future coding agents must:

- **Read `docs/bible/04-jewelry-domain/README.md` before changing jewelry
  concepts** — before adding/changing a stone shape, setting type, ring
  style, band profile, or any parameter that affects geometry or
  validation.
- **Use canonical terminology** — per
  `docs/bible/00-foundation/008-glossary.md`; do not introduce a new name
  for an existing concept, and do not reuse an existing term for
  something different.
- **Not invent jewelry measurements** — no default, tolerance, density,
  shrinkage value, or proportion may be added to code or docs without a
  traceable source; see
  `docs/bible/04-jewelry-domain/040-domain-governance.md`.
- **Distinguish metadata from geometry-driving parameters** — e.g.
  `material.metal` and `manufacturing.method` currently affect
  metadata/validation-context only, never geometry; do not silently
  change that without updating
  `docs/bible/04-jewelry-domain/052-parametric-dependency-model.md`.
- **Preserve stone-reference separation** — see LAW-006; never union the
  stone into the metal body or include it in a default export.
- **Update the parameter catalog when adding parameters** —
  `docs/bible/appendices/jewelry-domain-parameter-catalog.md`, in the
  same change as the schema change.
- **Update the dependency model when changing geometric relationships**
  — `docs/bible/04-jewelry-domain/052-parametric-dependency-model.md`.
- **Update the professional-validation register when introducing
  expert-derived rules** —
  `docs/bible/04-jewelry-domain/058-professional-validation-register.md`;
  never invent a reviewer.
- **Never label preliminary thresholds as industry standards** — a
  number in `validation/engine.py` is a PRELIMINARY SOFTWARE RULE unless
  a register entry says otherwise; see
  `docs/bible/04-jewelry-domain/054-domain-validation-classification.md`.
- **Create an RFC before adding a new ring style, setting type, or
  jewelry category** — see
  `docs/bible/04-jewelry-domain/056-domain-extension-strategy.md` for the
  full workflow (an ADR is also required if the change is architectural).
- **Update domain-to-code mapping after implementation changes** —
  `docs/bible/04-jewelry-domain/055-domain-to-code-mapping.md` and
  `docs/bible/appendices/jewelry-domain-status-matrix.md`.

## JDL RULES

`docs/bible/05-jdl/` is the authoritative Jewelry Definition Language
(JDL) specification — start at
[`docs/bible/05-jdl/README.md`](docs/bible/05-jdl/README.md). The
machine-readable half lives in
[`specs/jdl/v1/`](specs/jdl/v1/README.md) (JSON Schema, the planned
textual-DSL grammar, canonicalization/compiler-contract references,
examples, and test vectors). Future coding agents must:

- **Read `docs/bible/05-jdl/README.md` before changing schemas** — before
  adding/changing a field, enum member, default, or validation layer in
  `backend/jewelmind/domain/schema.py`, `shared/types/jewelry-definition.ts`,
  or `specs/jdl/v1/jdl.schema.json`.
- **Treat Canonical JSON as the current NORMATIVE representation.** YAML
  serialization and the textual JDL DSL are PLANNED and NON-NORMATIVE —
  never describe either as currently accepted by the API, and never
  implement a production parser for either without a dedicated milestone
  and an updated `docs/bible/05-jdl/README.md`.
- **Never add executable code to JDL** — no field, in any current or
  future representation, may carry an expression, script, macro, or
  function body. See `docs/bible/05-jdl/062-design-goals-and-non-goals.md`.
- **Keep structural (schema-layer) and semantic (business-rule) validation
  separate** — a new numeric threshold belongs in
  `backend/jewelmind/validation/engine.py`, not in
  `specs/jdl/v1/jdl.schema.json`, unless it is a genuine type/structural
  fact (see `docs/bible/05-jdl/075-validation-pipeline.md`).
- **Never rename or reuse a published diagnostic code** — see JDL-GOV-007
  in `docs/bible/05-jdl/060-jdl-governance.md` and
  `docs/bible/appendices/jdl-error-code-catalog.md`.
- **Generate test vectors by running the real implementation** — never
  hand-invent a value in `specs/jdl/v1/test-vectors/`; see JDL-GOV-009.
- **Create an RFC before adding a new ring style, stone shape, setting
  type, or jewelry category** expressed as new JDL fields or enum
  members — see `docs/bible/04-jewelry-domain/056-domain-extension-strategy.md`.
- **Create an ADR for an incompatible language decision** — changing
  which JDL representation is normative, moving validation authority
  between layers, or changing the canonicalization/hashing algorithm; see
  `docs/bible/05-jdl/060-jdl-governance.md`.
- **Never describe a PLANNED JDL feature as currently supported** — a
  YAML loader, a textual-DSL parser, or a capability-declaration endpoint
  do not exist; do not imply otherwise in code comments, API docs, or the
  frontend.
- **Update `specs/jdl/v1/` and `backend/tests/test_jdl_schema_examples.py`
  together** with any schema change, so the specification cannot silently
  drift from the running implementation.

## FORGE RULES

`docs/bible/06-forge/` is the authoritative Forge Rule System
specification — start at
[`docs/bible/06-forge/README.md`](docs/bible/06-forge/README.md). The
machine-readable half lives in
[`specs/forge/v1/`](specs/forge/v1/README.md) (rule/result/context/registry
JSON Schemas, the real 21-rule `current-rule-registry.json`, examples, and
test vectors). Future coding agents must:

- **Read `docs/bible/06-forge/README.md` before modifying validation or
  jewelry rules** — before adding, changing, or removing anything in
  `backend/jewelmind/validation/`, `shared/validation/`, or a
  jewelry-domain threshold anywhere else in the codebase.
- **Use stable rule IDs** — never rename or reuse one (FORGE-GOV-001).
- **Add provenance for new rules** — every new rule declares a
  `provenanceType` from `docs/bible/06-forge/094-rule-provenance-model.md`;
  `unknown` is honest and acceptable, an absent declaration is not
  (FORGE-GOV-002).
- **Never call an unvalidated threshold an industry standard** — a rule
  with `provenanceType` of `prototype_heuristic`, `mathematical_constraint`,
  `geometry_engine_constraint`, or `implementation_necessity` can never be
  described as `professionalValidationStatus: validated` (FORGE-GOV-003).
- **Update `specs/forge/v1/current-rule-registry.json`** and
  `docs/bible/appendices/forge-rule-catalog.md` in the same change as any
  rule addition, removal, or reclassification.
- **Update tests** — `backend/tests/test_forge_registry.py` and the
  relevant rule's own test file (FORGE-GOV-011, FORGE-GOV-014).
- **Document blocking behavior** — every rule declares its
  `blockingScope`; see `docs/bible/06-forge/099-severity-and-blocking-semantics.md`
  (FORGE-GOV-006).
- **Document evaluation stage** — `FORGE-0` through `FORGE-9`; see
  `docs/bible/06-forge/096-rule-evaluation-pipeline.md` (FORGE-GOV-013).
- **Document professional validation status explicitly** —
  `not_required | preliminary | required | validated`; there is no
  implicit default (FORGE-GOV-008).
- **Never hide jewelry rules inside geometry code** — a jewelry-domain
  threshold belongs in `backend/jewelmind/validation/` with a rule ID, not
  hardcoded inside `backend/jewelmind/geometry/components/*.py`
  (FORGE-GOV-005; see `docs/bible/06-forge/111-domain-rule-gap-analysis.md`
  for where this boundary is already imperfect and tracked).
- **Never silently change rule thresholds** — a changed threshold,
  severity, or blocking behavior is a MAJOR rule-version change; see
  `docs/bible/06-forge/108-rule-versioning.md` (FORGE-GOV-007, FORGE-GOV-015).
- **Require an RFC for a major new rule family** (a new manufacturing
  profile, a new professional-validation domain, or a new rule category)
  — see `docs/bible/06-forge/090-forge-governance.md`.
- **Require an ADR for an architecture-level Forge change** — moving
  validation authority, changing blocking semantics, or introducing an
  executable rule-condition DSL; see the same document.
- **Preserve backend authority** — `shared/validation/engine.ts` may only
  mirror a subset of `backend/jewelmind/validation/engine.py`; it must
  never enforce something the backend does not, and the backend's verdict
  always wins (FORGE-GOV-004).
- **Keep frontend validation aligned** — a rule threshold changed on the
  backend must be changed identically on the frontend mirror in the same
  change, or explicitly documented as a deliberate, temporary divergence.
- **Report code/Forge contradictions** — per the Bible's fundamental
  rule, never silently change the meaning of a rule to make a
  contradiction with `docs/bible/06-forge/` disappear.

## ATLAS RULES

`docs/bible/07-atlas/` is the authoritative Atlas Geometry Core
specification — start at
[`docs/bible/07-atlas/README.md`](docs/bible/07-atlas/README.md). The
machine-readable half lives in
[`specs/atlas/v1/`](specs/atlas/v1/README.md) (component/assembly/metadata/
inspection/error/manifest JSON Schemas, real examples, and test vectors).
Future coding agents must:

- **Read `docs/bible/07-atlas/README.md` before changing geometry** —
  before modifying anything in `backend/jewelmind/geometry/`,
  `backend/jewelmind/preview/`, or `backend/jewelmind/exporters/`.
- **Preserve the Atlas/Forge boundary** — Atlas reports geometric facts
  (a volume, a solid count, a bounding box); only Forge may interpret a
  fact as a jewelry-domain or manufacturing rule violation
  (ATLAS-GOV-001, ATLAS-GOV-002).
- **Use millimeters internally** — no unit field, no conversion
  (ATLAS-GOV-008, restating LAW-007 for geometry code specifically).
- **Document coordinate assumptions** — any new component or geometry
  feature states its placement relative to the existing convention in
  `docs/bible/07-atlas/123-coordinate-system-and-orientation.md`, or
  proposes a normalization via ADR if it must diverge (ATLAS-GOV-012).
- **Preserve deterministic construction** — no wall-clock time,
  randomness, or external state in any geometry builder (ATLAS-GOV-003,
  ATLAS-GOV-014).
- **Preserve StoneReference separation** — see LAW-006 and
  `docs/bible/07-atlas/143-stone-metal-separation-contract.md`; never
  give a fuse/union function a code path that could accept the stone
  shape (ATLAS-GOV-007, ATLAS-GOV-011).
- **Never silently discard components** — a component with zero
  geometry still appears in every manifest/result, never omitted
  (ATLAS-GOV-006).
- **Report fallback geometry** — any new fallback path (fillet-like or
  boolean-like) must append a warning and be added to
  `docs/bible/appendices/atlas-fallback-register.md`
  (ATLAS-GOV-004, ATLAS-GOV-005).
- **Update the component catalog** —
  `docs/bible/appendices/atlas-component-catalog.md`, in the same change
  as a new/changed component.
- **Update the operation catalog** —
  `docs/bible/appendices/atlas-operation-catalog.md`, in the same change
  as a new CadQuery operation.
- **Update geometry invariants** —
  `docs/bible/appendices/atlas-geometry-invariant-catalog.md`, in the
  same change as a new fixed geometric constant.
- **Update the current solitaire mapping** —
  `docs/bible/07-atlas/149-current-solitaire-geometry-mapping.md`, in
  the same change as a field that gains or changes a geometry
  dependency.
- **Add geometry regression tests for output-changing modifications** —
  `backend/tests/test_geometry.py` (ATLAS-GOV-015).
- **Never make STL the source of truth** — every export/preview always
  re-tessellates from the live B-Rep; never read geometry back from a
  previously-written mesh file (ATLAS-GOV-009).
- **Never introduce jewelry-domain thresholds into Atlas** — a numeric
  jewelry-domain constant belongs in `backend/jewelmind/validation/`
  with a Forge rule ID, not hardcoded inside
  `backend/jewelmind/geometry/components/*.py` (ATLAS-GOV-002).
- **Require an ADR for a geometry architecture change** — replacing or
  wrapping the CAD kernel, changing the coordinate convention, or
  changing required/optional component membership; see
  `docs/bible/07-atlas/120-atlas-governance.md`.
- **Require an RFC for a new geometric component family** — a new
  component type beyond band/stone_reference/prongs/basket_support, or a
  new ring style's geometry; see the same document.

## ALCHEMIST RULES

`docs/bible/08-alchemist/` is the authoritative Alchemist Compiler
specification — start at
[`docs/bible/08-alchemist/README.md`](docs/bible/08-alchemist/README.md).
The machine-readable half lives in
[`specs/alchemist/v1/`](specs/alchemist/v1/README.md). Future coding
agents must:

- **Read `docs/bible/08-alchemist/README.md` before changing
  compilation orchestration** — before modifying
  `backend/jewelmind/services/model_service.py` or how
  generation/export/preview sequencing works.
- **Preserve the JDL → Forge → Alchemist → Atlas separation** — Forge
  owns thresholds, Atlas owns geometry, Alchemist only orchestrates
  (ALCHEMIST-GOV-001, ALCHEMIST-GOV-002).
- **Never put jewelry thresholds in compiler/orchestration code** — a
  jewelry-domain constant belongs in `backend/jewelmind/validation/`
  with a Forge rule ID, never in `services/model_service.py` or
  `api/routes.py`.
- **Never construct kernel geometry directly inside compiler
  orchestration** — `services/model_service.py` and `api/routes.py`
  must never import `cadquery`; geometry construction belongs in
  `backend/jewelmind/geometry/` (see
  `docs/bible/08-alchemist/168-atlas-execution-contract.md` for the one
  currently-tolerated exception: `exporters/step_exporter.py`/
  `stl_exporter.py` combining pre-built shapes for export).
- **Keep `GeometryPlan` deterministic** if and when it is ever
  implemented — same inputs, same plan, every time (ALCHEMIST-GOV-004).
- **Keep artifact requests explicit** — never generate an artifact as a
  side effect the caller didn't ask for (ALCHEMIST-GOV-008).
- **Record required version fingerprints** when adding a new version
  axis (compiler, Forge rule-set, kernel) — see
  `docs/bible/08-alchemist/174-determinism-and-version-fingerprint.md`
  (ALCHEMIST-GOV-009).
- **Preserve `definitionHash`'s meaning** — never repurpose it to also
  encode compiler/kernel version; that is what a future
  `compilationHash` is for (ALCHEMIST-GOV-010; see
  `docs/bible/08-alchemist/175-definition-hash-vs-compilation-hash.md`).
- **Update `compilationHash` rules when output-affecting versions
  change**, once `compilationHash` is implemented.
- **Never silently ignore component failures** — restates
  ATLAS-GOV-006/LAW-005 at the compiler level (ALCHEMIST-GOV-007).
- **Never report complete success when required components/artifacts
  fail** — see
  `docs/bible/08-alchemist/173-partial-compilation-policy.md`.
- **Update compiler capabilities when adding supported features** —
  `specs/alchemist/v1/compiler-capabilities.schema.json` and
  `specs/alchemist/v1/test-vectors/capability-vectors.json`, in the
  same change as a new supported band profile, stone shape, setting
  type, prong count, or artifact type.
- **Update test vectors after compiler-semantic changes** —
  `backend/tests/test_alchemist_registry.py` and the relevant
  `specs/alchemist/v1/test-vectors/*.json` file.
- **Create an ADR for compiler architecture changes** — materializing
  `GeometryPlan`, changing which stage produces which artifact,
  introducing `compilationHash`, or changing cache-key strategy; see
  `docs/bible/08-alchemist/160-alchemist-governance.md`.
- **Create an RFC for major pipeline changes** — asynchronous
  compilation, component-level regeneration, or restructuring the
  five-layer pipeline itself; see the same document.

## FOUNDRY RULES

`docs/bible/09-foundry/` is the authoritative Foundry Export System
specification — start at
[`docs/bible/09-foundry/README.md`](docs/bible/09-foundry/README.md). The
machine-readable half lives in
[`specs/foundry/v1/`](specs/foundry/v1/README.md) (artifact request/
record/manifest, export diagnostic, export validation result, and export
version fingerprint JSON Schemas, real examples, and test vectors).
Future coding agents must:

- **Read `docs/bible/09-foundry/README.md` before changing exporters** —
  before modifying anything in `backend/jewelmind/exporters/` or how
  `ModelService.export_step_file()`/`export_stl_file()` orchestrate them.
- **Keep StoneReference excluded from production artifacts by default**
  — STEP/STL export must never default `includeStoneReference` to
  `true`; restates LAW-006 at the export layer (FOUNDRY-GOV-004).
- **Never claim native CAD preservation from STEP** — no parametric
  history, feature tree, MatrixGold-equivalent editability, or
  guaranteed import quality in every CAD application (FOUNDRY-GOV-006).
- **Never claim parametric editing from STL** — it is a derived,
  tessellated, one-way artifact; it must never become the canonical
  source geometry for anything downstream (FOUNDRY-GOV-007,
  FOUNDRY-GOV-013).
- **Preserve the millimeter scale contract** — never guess a unit; a
  claim about an artifact's unit must be grounded in actually inspecting
  that artifact's real output, not assumed (FOUNDRY-GOV-012; see
  `docs/bible/09-foundry/212-unit-and-scale-contract.md`).
- **Never fake an export** — restates CLAUDE.md's own rule explicitly at
  this layer; every exporter must write one complete, real file per
  artifact in a single operation (FOUNDRY-GOV-002, FOUNDRY-GOV-008).
- **Never silently drop a required production component** from an
  export — a missing or failed required component must be an observable
  failure, never a quietly smaller file (FOUNDRY-GOV-009).
- **Use stable, namespaced diagnostic codes** — never rename or reuse
  one once published (FOUNDRY-GOV-010); see
  `docs/bible/appendices/foundry-export-diagnostic-catalog.md`.
- **Never expose an internal server path** in a public error message or
  response header (FOUNDRY-GOV-011).
- **Never call an untested external CAD workflow "validated"** — an
  `IMPORT_TESTED`/`WORKFLOW_VALIDATED` claim requires an actual recorded
  test run, never an assumption of format compatibility
  (FOUNDRY-GOV-014); see
  `docs/bible/09-foundry/209-cad-interoperability-philosophy.md`.
- **Clean up every temporary file** an exporter or export-orchestration
  function creates, on both the success and failure path
  (FOUNDRY-GOV-015).
- **Treat a changed export default as a MAJOR change** — which
  components are included, whether the stone is included by default,
  or which artifact formats exist must never shift silently
  (FOUNDRY-GOV-016).
- **Report partial success honestly** — if some requested artifacts
  succeed and others fail, never report complete success when a
  required artifact failed (FOUNDRY-GOV-017).
- **Preserve the Atlas/Forge boundary at the export layer** — Foundry
  reports what was exported and whether it passed an integrity check;
  it never interprets a geometric fact as a jewelry-domain violation
  (Forge's job) and never constructs or mutates geometry itself (Atlas's
  job) (FOUNDRY-GOV-018).
- **Update the artifact/diagnostic/interoperability appendices** —
  `docs/bible/appendices/foundry-artifact-catalog.md`,
  `foundry-mime-type-catalog.md`, `foundry-component-inclusion-matrix.md`,
  `foundry-export-diagnostic-catalog.md`, `foundry-export-test-matrix.md`,
  `foundry-code-mapping.md`, and `foundry-interoperability-matrix.md` —
  in the same change as an exporter, diagnostic, or interoperability
  change.
- **Require an ADR for a Foundry architecture change** — replacing the
  export format set, changing which components are included in a
  production export by default, changing StoneReference's default
  export inclusion, or moving integrity validation to a different layer;
  see `docs/bible/09-foundry/190-foundry-governance.md`.
- **Require an RFC for a new artifact format** beyond STEP/STL/JSON/
  technical specification, or a structural change to how artifacts are
  requested/manifested across the whole pipeline; see the same document.

## VISION RULES

`docs/bible/10-vision/` is the authoritative Vision visual-output
specification — start at
[`docs/bible/10-vision/README.md`](docs/bible/10-vision/README.md). The
machine-readable half lives in
[`specs/vision/v1/`](specs/vision/v1/README.md) (scene state, camera
state, component visual state, material presentation, render result, and
image capture request JSON Schemas, real examples, and test vectors).
Future coding agents must:

- **Read `docs/bible/10-vision/README.md` before modifying the viewer**
  — before changing anything in `frontend/src/components/ModelViewport.tsx`,
  `frontend/src/vision/`, or `frontend/src/store/useVisionStore.ts`.
- **Never reconstruct jewelry geometry in the frontend** — every mesh
  Vision renders must come from `useComponentGeometries()` parsing a
  real backend-generated STL; no frontend code may read a JDL dimension
  to build a `THREE.BufferGeometry` (VISION-GOV-001, VISION-GOV-002).
- **Use Atlas-derived preview geometry** — the visual model and the
  exported CAD model must share the same geometric origin
  (VISION-GOV-003); see `docs/bible/10-vision/223-atlas-to-vision-contract.md`.
- **Preserve component identity** — all component visibility and
  stone/metal classification must use the explicit `geometryRole`/name
  fields from the preview manifest, never render order or array index
  (VISION-GOV-011).
- **Preserve StoneReference distinction** — the stone must remain
  semantically distinct from production metal in both Technical and
  Presentation views, and must never be fused into metal geometry
  (VISION-GOV-006, restating LAW-006).
- **Keep visual state separate from JDL design intent** — Vision-only
  state (view mode, camera, material style, component visibility) lives
  in `useVisionStore`, never in `useProjectStore`, and must never change
  `definitionHash` (VISION-GOV-014).
- **Never trigger geometry regeneration for camera/material/view-only
  changes** — switching view mode, camera preset, or component
  visibility must never call `generate()` or touch `useProjectStore`
  (VISION-GOV-014).
- **Centralize material presets** — every metal color and the stone's
  color/transmission parameters live only in
  `frontend/src/vision/materials.ts`; never hardcode a color elsewhere
  (see `docs/bible/10-vision/231-material-system.md`).
- **Dispose GPU resources** — geometry disposal in
  `useComponentGeometries.ts` and material disposal via React Three
  Fiber's own unmount guarantee must be preserved; never cache a Three.js
  object outside the R3F tree without an explicit disposal path
  (VISION-GOV-004, see `docs/bible/10-vision/242-performance-and-gpu-resource-model.md`).
- **Preserve last-good preview** — a rendering or regeneration failure
  must never destroy `lastSuccessfulPreview` or the geometry currently
  on screen (VISION-GOV-007, VISION-GOV-009).
- **Identify stale models** — the existing `isStale` flag and stale
  banner must remain accurate in both view modes, and image capture must
  stay blocked (not merely labeled) while a model is stale
  (VISION-GOV-008, VISION-GOV-012).
- **Keep screenshot output derived from current generated geometry** —
  never substitute an AI-generated image for the actual CAD-derived
  render (VISION-GOV-012, VISION-GOV-013).
- **Never call Presentation View a manufacturing proof** — restates
  LAW-010 at the Vision layer; never describe Presentation rendering as
  photorealistic, cinematic, or path-traced without measurable evidence
  (VISION-GOV-005).
- **Update Vision schemas/tests after rendering-contract changes** —
  `specs/vision/v1/` and `backend/tests/test_vision_schemas.py`, plus
  the relevant frontend unit tests under `frontend/src/vision/*.test.ts`
  and `frontend/src/store/useVisionStore.test.ts`, in the same change.
- **Never introduce a hidden external-runtime dependency** — no remote
  HDRI, no CDN asset, no paid asset pack; use procedural/bundled
  alternatives like `three-stdlib`'s `RoomEnvironment` (VISION-GOV-010).
- **Create an ADR for a major rendering architecture change** —
  replacing Three.js/React Three Fiber, moving Vision state into
  `useProjectStore`, or changing the Atlas-to-scene coordinate transform;
  see `docs/bible/10-vision/220-vision-governance.md`.
- **Create an RFC for a new visual artifact class** — e.g. turntable
  video, AR preview, or a server-side rendering pipeline; see the same
  document.

## STUDIO RULES

`docs/bible/11-studio/` is the authoritative Studio product-workspace
specification — start at
[`docs/bible/11-studio/README.md`](docs/bible/11-studio/README.md). The
machine-readable half lives in
[`specs/studio/v1/`](specs/studio/v1/README.md) (studio state, project
session, generation state, output state, and notification JSON
Schemas, real examples, and test vectors). Future coding agents must:

- **Read `docs/bible/11-studio/README.md` before changing product
  workflow** — before modifying `frontend/src/studio/`,
  `ConfigurationPanel.tsx`, `AppHeader.tsx`, `ProjectActions.tsx`,
  `OutputsPanel.tsx`, or `RightPanelTabs.tsx`.
- **Preserve separation between design state and generated-model
  state** — `useProjectStore.currentDefinition` (design) and
  `{generatedModel, lastSuccessfulPreview, generationStatus, isStale}`
  (generated-model state) must never be merged into one field or
  written from the same action (STUDIO-GOV-004/013).
- **Never mark visual-only changes as design changes** — a `useVisionStore`
  change (view mode, camera, component visibility, material
  presentation) must never set `isStale` or call `generate()`
  (STUDIO-GOV-003).
- **Mark geometry-driving edits stale** — every `useProjectStore.updateXxx()`
  action must continue to set `isStale: true` via `withUpdatedDefinition()`
  when a model already exists (STUDIO-GOV-004).
- **Preserve last-good preview** — a failed generation or export must
  never clear `lastSuccessfulPreview` or the currently rendered geometry
  (STUDIO-GOV-006).
- **Keep outputs tied to the correct generated model** — every artifact's
  eligibility (STEP, STL, JSON, technical specification, Presentation
  PNG) must be computed through `computeOutputEligibility()` (or the
  equivalent `captureBlockedReason()` for PNG), never a bespoke
  per-artifact check (STUDIO-GOV-007).
- **Keep backend validation authoritative** — a `NumericField`'s
  `min`/`max` or any other client-side check is advisory only; the
  backend's `validate_definition()` result always wins (STUDIO-GOV-001/002).
- **Use JewelMind controlled terminology** — consult
  `docs/bible/00-foundation/008-glossary.md` and
  `docs/bible/04-jewelry-domain/` before introducing a new user-facing
  term; never invent a competing vocabulary (STUDIO-GOV-011).
- **Avoid exposing architecture-internal names to normal users** — never
  put "Forge," "Atlas," "Alchemist," "Foundry," or "Vision" in
  user-facing UI copy; these are Bible/architecture names only
  (STUDIO-GOV-011; see `docs/bible/11-studio/280-product-copy-and-terminology.md`).
- **Maintain accessible primary controls** — every interactive control
  must be a real, labeled, keyboard-focusable element with a visible
  `:focus-visible` state; never an icon-only or unlabeled control
  (STUDIO-GOV-014; see `docs/bible/11-studio/272-accessibility-contract.md`).
- **Preserve responsive behaviour** — do not remove or narrow the
  `1180px`/`980px` breakpoints in `frontend/src/styles/global.css`
  without re-verifying the viewport's `min-height` floor still holds on
  a stacked mobile layout.
- **Update Studio state schemas when product-state semantics change** —
  `specs/studio/v1/` and `backend/tests/test_studio_schemas.py`, plus
  the relevant frontend unit tests under `frontend/src/studio/*.test.ts`,
  in the same change.
- **Update test vectors after workflow changes** — a changed
  `ModelStateKey`/`OutputEligibilityKey` precedence rule must update
  `specs/studio/v1/test-vectors/` in the same change (this is a MAJOR,
  documented change, never a silent one).
- **Create an ADR for major frontend state architecture changes** —
  merging `useProjectStore`/`useVisionStore`, moving model-status or
  output-eligibility computation into a different layer, or introducing
  a second design-definition schema; see
  `docs/bible/11-studio/250-studio-governance.md`.
- **Create an RFC for new major product workflows** — a project
  dashboard, multiple open designs, undo/redo, or autosave; see the same
  document.

## DESIGNER RULES

`docs/bible/12-designer/` is the authoritative Designer natural-language
design-interpretation specification — start at
[`docs/bible/12-designer/README.md`](docs/bible/12-designer/README.md).
The machine-readable half lives in
[`specs/designer/v1/`](specs/designer/v1/README.md) (request/proposal/
diagnostic JSON Schemas, real examples generated against
`FakeDesignerProvider`, and test vectors). Future coding agents must:

- **Read `docs/bible/12-designer/README.md` before changing anything in
  `backend/jewelmind/designer/` or `frontend/src/components/DesignerPanel.tsx`.**
- **Preserve Designer as proposal-only** — nothing in
  `backend/jewelmind/designer/` may write to `currentDefinition`; only
  an explicit user acceptance through
  `useProjectStore.applyDesignerProposal()` may do that.
- **Never let Designer call geometry code directly** —
  `backend/jewelmind/designer/` must never import `cadquery` or anything
  under `jewelmind.geometry`; a candidate design is data, not a
  construction instruction.
- **Never bypass JDL/Forge validation for a Designer-originated
  candidate** — every `candidateJDL` goes through the real
  `JewelryDefinition.model_validate()` and `validate_definition()`, the
  same as every other entry point, with no Designer-specific shortcut.
- **Preserve field provenance** — every `ProposedField` must carry a
  `FieldProvenance` value; never construct one that omits or fakes it.
- **Distinguish system defaults from AI inference** — a field left
  unspecified by the user and filled from the schema default must never
  be labeled as though the AI inferred it.
- **Reject unsupported fields/enum values deterministically** — gate
  every field and enum value through `capability.py`
  (`is_known_field`/`is_supported_enum_value`) rather than trusting a
  provider to only ever report supported concepts.
- **Report unsupported requested features explicitly** — an
  `UnsupportedFeature` must never be silently dropped or approximated as
  something the schema does support.
- **Preserve unspecified current values during a MODIFY interpretation**
  — an untouched field must keep its value from `currentJDL`, never
  reset to the schema default.
- **Keep provider integrations behind the `DesignerProvider` interface**
  — a vendor-specific response shape must never leak past
  `designer/provider.py`; `DesignerService` depends only on
  `RawDesignerResponse`.
- **Keep API secrets backend-only** — `ANTHROPIC_API_KEY` must never
  reach the frontend bundle, a client-visible response, or a log line.
- **Keep CI independent from external AI services** — every automated
  test must use `FakeDesignerProvider`, never a live provider call.
- **Update the Designer natural-language test corpus** —
  `backend/tests/test_designer_corpus.py` — after any semantic change to
  normalization or capability logic.
- **Create an ADR before changing Designer's provider architecture** —
  see "When an ADR is required" in
  `docs/bible/12-designer/290-designer-governance.md`.
- **Create an RFC before adding a major new natural-language
  capability** — multi-turn conversation, image/sketch input, or a new
  intent category; see the same document's "When an RFC is required."

## DESIGN INTENT RULES

`docs/bible/13-design-intent/` is the authoritative Design Intent Model
specification — start at
[`docs/bible/13-design-intent/README.md`](docs/bible/13-design-intent/README.md).
The machine-readable half lives in
[`specs/design-intent/v1/`](specs/design-intent/v1/README.md) (target/
statement/relation/diagnostic/resolution/profile JSON Schemas, a
`vocabulary.json` controlled-vocabulary source of truth, real examples,
and test vectors). Future coding agents must:

- **Read `docs/bible/13-design-intent/README.md` before changing
  semantic intent** — before adding, changing, or removing anything in
  `backend/jewelmind/design_intent/` or the design-intent parts of
  `frontend/src/components/DesignerPanel.tsx`.
- **Never convert subjective descriptors into arbitrary numeric
  parameters** — no code path in `design_intent/` may write to a JDL
  dotted path; `IntentStatement.relatedJDLPaths` stays empty in v1.
- **Keep `DesignIntent` separate from canonical JDL** — no field
  overlap between `design_intent/schemas.py` and `domain/schema.py`.
- **Preserve intent provenance** — every `IntentStatement`/
  `IntentRelation` must carry a real `IntentProvenance` value; never
  construct one that omits or fakes it.
- **Preserve unresolved intent** — never discard a descriptor
  `normalize_descriptor()` can't classify; it must end up in
  `unresolvedDescriptors`, not silently dropped.
- **Use the controlled vocabulary in `vocabulary.py`** — never invent a
  new concept category or continuum value inline in application code.
- **Preserve language-neutral canonical concepts** — a synonym table
  entry must resolve to one of the real canonical values, never a
  one-off per-language special case.
- **Distinguish intent normalization from technical mapping** —
  matching a word to the controlled vocabulary and writing a JDL field
  are structurally different code paths; they must stay that way.
- **Only allow deterministic, approved intent resolution to touch JDL
  automatically** — see `349-deterministic-resolution-policy.md`'s 7
  conditions; v1 has zero such mappings, which is correct, not a gap to
  "fix" casually.
- **Require user review for any non-trivial technical resolution
  derived from intent**, if that capability is ever added.
- **Never put manufacturing rules into `design_intent/`** — that
  boundary belongs to Forge (`validation/`).
- **Never mark an intent-only change as making the geometry stale** —
  `DesignerPanel.tsx::handleApply()`'s `proposal.diff.some(d =>
  d.changed)` gate is the mechanism; never call
  `applyDesignerProposal()` unconditionally.
- **Update the design-intent test corpus**
  (`backend/tests/test_design_intent_corpus.py`) after any vocabulary
  or normalization change.
- **Create an ADR for major intent-model changes** — see
  `330-intent-governance.md`'s "When an ADR is required."
- **Create an RFC for new major semantic intent families** — see the
  same document's "When an RFC is required."

## CONVERSATION RULES

`docs/bible/14-conversation/` is the authoritative Conversation Engine
specification — start at
[`docs/bible/14-conversation/README.md`](docs/bible/14-conversation/README.md),
then [`370-conversation-governance.md`](docs/bible/14-conversation/370-conversation-governance.md)
for the full 20 CONV-GOV rules. The machine-readable half lives in
[`specs/conversation/v1/`](specs/conversation/v1/README.md) (9 JSON
Schemas, real examples generated by running the actual
`ConversationEngine`, and test vectors). Future coding agents must:

- **Read `docs/bible/14-conversation/README.md` before changing anything**
  in `backend/jewelmind/conversation/` or
  `frontend/src/components/ConversationPanel.tsx`.
- **Treat conversation as interaction state, never design truth** — a
  `ConversationSession` carries only content hashes
  (`currentJDLHash`/`currentIntentHash`) of the caller's JDL/DesignIntent,
  never a copy of either; it must never become a second source of design
  truth.
- **Always treat the caller's latest accepted JDL and DesignIntent as
  authoritative** — never reconstruct `currentJDL`/`currentDesignIntent`
  by replaying `session.turns`; both must always come fresh from the
  caller on every request.
- **Preserve unspecified fields on every modification** — route every
  `MODIFY_DESIGN_PROPOSAL`/`CREATE_DESIGN_PROPOSAL` turn through the real
  `DesignerService.interpret()`; never construct a JDL patch directly
  inside `conversation/`.
- **Never replay prose history to rebuild design state** — conversation
  history (`ConversationSummary`, `compact_summary()`) exists only to
  give a provider bounded context, never to reconstruct authoritative
  state.
- **Use structured actions, never free-form prose as ground truth** —
  classify every turn deterministically into one of the 13 canonical
  `ConversationActionType` values (`classify_action()`); never let raw
  assistant/user text stand in for a structured outcome.
- **Version every proposal against the design state it was computed
  from** — `ConversationProposal.baseDefinitionHash`/`baseIntentHash`
  must be set from the real `currentJDL`/`currentDesignIntent` at
  proposal-creation time, never omitted or approximated.
- **Never apply a stale proposal** — `state.is_proposal_stale()` must
  gate every `ACCEPT_PROPOSAL`; if the caller's current JDL/DesignIntent
  no longer match the proposal's base hashes (e.g. a concurrent manual
  edit), reject the acceptance rather than silently applying it.
- **Keep clarification threads explicit** — a clarification answer must
  resolve only the one `ClarificationThread` it was opened for; never
  let an answer silently resolve a different, unrelated open question.
- **Never apply an unaccepted proposal** — a `ConversationProposal`
  starts `ACTIVE` and only becomes usable through an explicit
  `ACCEPT_PROPOSAL` turn; nothing in `process_turn()` may apply a
  candidate JDL as a side effect of creating or reviewing it.
- **Never let an AI directly patch an arbitrary JDL path** — every
  candidate JDL must still be built exclusively by
  `DesignerService.interpret()`'s existing pipeline
  (`JewelryDefinition.model_validate()` + `validate_definition()`); no
  code in `conversation/` may write to a JDL dotted path directly.
- **Preserve the Designer/JDL/Forge boundary** — `backend/jewelmind/conversation/`
  must never import `cadquery`, never evaluate a Forge rule directly, and
  never construct a `candidateJDL` without going through Designer first.
- **Keep conversation history bounded** — `context.py::MAX_RECENT_TURNS_IN_CONTEXT`
  (a turn-count bound, not an invented token budget) must continue to
  cap what `build_turn_context()` sends to a provider.
- **Keep CI independent from live AI providers** — every automated test
  must use `FakeDesignerProvider` (via `DesignerService`), never a live
  provider call.
- **Create an ADR before changing conversation-state architecture** —
  letting Conversation write directly to `candidateJDL` without routing
  through `DesignerService`, moving session persistence server-side, or
  changing which layer owns staleness detection; see "When an ADR is
  required" in `370-conversation-governance.md`.
- **Create an RFC before adding a major new conversational capability**
  — a new action beyond the 13 `ConversationActionType` values,
  multi-session/multi-user conversation, voice/image input, or long-term
  personal memory across sessions; see the same document's "When an RFC
  is required."

## PROFESSIONAL VALIDATION RULES

`docs/bible/15-professional-validation/` is the authoritative
Professional Validation Framework specification — start at
[`docs/bible/15-professional-validation/README.md`](docs/bible/15-professional-validation/README.md),
then [`410-validation-governance.md`](docs/bible/15-professional-validation/410-validation-governance.md)
for the full 20 PROVAL-GOV rules. The machine-readable half lives in
[`specs/professional-validation/v1/`](specs/professional-validation/v1/README.md)
(10 JSON Schemas, an active registry that must stay empty until real
review occurs, template/example records, and test vectors). Future
coding agents must:

- **Read `docs/bible/15-professional-validation/README.md` before
  changing anything that touches validation status** — before editing
  `backend/jewelmind/professional_validation/`,
  `specs/professional-validation/v1/current-validation-registry.json`,
  or any code path that reports a rule/component/workflow as validated.
- **Never fabricate a reviewer** — no placeholder name, no generic
  "industry expert," no unnamed "jeweler consulted." A real `Reviewer`/
  `ReviewerQualification` record names a real, identifiable person or it
  does not exist.
- **Never fabricate evidence** — a `ValidationEvidence` record describes
  something that actually happened (a real inspection, a real physical
  sample, a real cited reference); it is never invented to make a
  decision look better-supported than it is.
- **Never mark a rule professionally validated based on software
  tests** — a passing `pytest` run, a successful geometry generation, or
  a successful STEP/STL export is not professional validation
  (PROVAL-GOV-006). `count_validated()` only ever counts real
  `ValidationRecord` entries in the active registry.
- **Never treat AI analysis as professional validation** — an LLM's
  assessment of a rule or geometry is `AI_ASSISTED`/`SOFTWARE_ONLY`
  evidence at best, and per PROVAL-GOV-007 those quality classes can
  never alone justify `VALIDATED`/`VALIDATED_WITH_CONDITIONS`.
- **Attach validation to exact versions and scopes** — a `ValidationRecord`
  without a real `target.version` or a real `ValidationScope` is not a
  valid record (PROVAL-GOV-002/003); never claim a record covers
  "the current rule" or "all manufacturing methods" when it was reviewed
  under one specific version and one specific scope.
- **Preserve conditional-validation conditions** — `conditions` is
  required non-empty whenever `decision` is `ACCEPTED_WITH_CONDITIONS`
  (PROVAL-GOV-010); never drop or paraphrase away a stated condition.
- **Preserve disagreements** — two conflicting `ValidationRecord`s are
  never merged, averaged, or silently resolved into one consensus value
  (PROVAL-GOV-012); both remain visible, each with its own scope.
- **Downgrade validation when material implementation changes invalidate
  prior evidence** — per `classify_version_impact()`
  (`backend/jewelmind/professional_validation/versioning.py`) and
  [`432-validation-versioning.md`](docs/bible/15-professional-validation/432-validation-versioning.md),
  a MAJOR change to a validated object's rule/geometry version never
  silently carries the old validation forward.
- **Keep professional observations separate from implementation
  decisions** — a `ReviewObservation` has no `decision`/`status` field;
  turning a finding into a real Forge rule or geometry change always
  goes through the workflow in
  [`435-validation-to-forge-workflow.md`](docs/bible/15-professional-validation/435-validation-to-forge-workflow.md)/
  [`436-validation-to-atlas-workflow.md`](docs/bible/15-professional-validation/436-validation-to-atlas-workflow.md)
  — engineering analysis, a rule/geometry proposal, tests, and an
  ADR/RFC where required — never a direct write.
- **Keep templates/examples out of the active validation registry** —
  `specs/professional-validation/v1/current-validation-registry.json`
  must never contain a record with `isTemplate: true`; example/template
  records live only under `specs/professional-validation/v1/examples/`.
- **Keep the active professional-validation count zero until real
  evidence exists** — do not add, or write code that could add, a
  record to the active registry without a real reviewer, real evidence,
  and a real decision behind it.
- **Update review packages when artifact contracts change** — if
  Foundry's STEP/STL/JSON/specification exporters change, verify
  `backend/jewelmind/professional_validation/review_package.py` still
  produces a correct, current bundle; see
  [`426-review-package-contract.md`](docs/bible/15-professional-validation/426-review-package-contract.md).
- **Require an ADR for a major validation-architecture change** —
  moving the active registry to a database, letting a `ValidationRecord`
  write directly to Forge/Atlas code, or any change that violates
  PROVAL-GOV-001 through 020 without superseding
  `410-validation-governance.md` first.
- **Require professional re-review when validated semantics materially
  change** — see
  [`434-implementation-change-impact.md`](docs/bible/15-professional-validation/434-implementation-change-impact.md).

## GEOMETRY INSPECTION RULES

`docs/bible/16-geometry-inspection/` is the authoritative Geometry
Inspection specification — start at
[`docs/bible/16-geometry-inspection/README.md`](docs/bible/16-geometry-inspection/README.md),
then [`460-inspection-governance.md`](docs/bible/16-geometry-inspection/460-inspection-governance.md)
for the full 20 INSPECT-GOV rules. The machine-readable half lives in
[`specs/geometry-inspection/v2/`](specs/geometry-inspection/v2/README.md)
(9 JSON Schemas, a hand-authored `fact-registry.json` with zero
professional thresholds, real examples, and test vectors). Future
coding agents must:

- **Read `docs/bible/16-geometry-inspection/README.md` before changing
  runtime geometry inspection** — before editing
  `backend/jewelmind/geometry/inspection/` or how
  `ModelService.generate()` calls `inspect_model()`.
- **Keep inspection read-only** — no function under
  `geometry/inspection/` may call `.fuse()`, `.cut()`, `.fillet()`, or
  any other geometry-mutating method on a shape it inspects
  (INSPECT-GOV-013).
- **Report geometric facts rather than jewelry judgments** — a
  `GeometricFact`/diagnostic message states a measurement ("1 solid
  detected", "0.9mm minimum distance"), never a quality judgment ("too
  thin", "not manufacturable") (INSPECT-GOV-001).
- **Keep Forge responsible for domain interpretation** — no file under
  `geometry/inspection/` may import `jewelmind.validation` or reference
  a Forge rule ID (INSPECT-GOV-002).
- **Never invent manufacturing tolerances** — `CONTACT_TOLERANCE_MM`
  (`geometry/inspection/version.py`) is a pure kernel/geometric
  tolerance; any new tolerance must be justified the same way, never a
  guessed jewelry-domain value (INSPECT-GOV-012).
- **Return `UNKNOWN`/`ERROR` instead of a fabricated `PASS`** — a
  kernel exception in `distance.py`/`intersection.py`/`topology.py`
  must produce an honest `UNKNOWN`/`ERROR` status, never an assumed
  passing result (INSPECT-GOV-006).
- **Preserve StoneReference identity** — a stone-metal separation check
  must remain structural (whether the stone's shape was ever an
  argument to a production-metal fuse call), never merely "zero
  intersection volume" — the stone legitimately intersects production
  components by design (INSPECT-GOV-008).
- **Preserve component IDs** — every fact/result must stay traceable to
  a real `componentId`/`componentIds` field; never an anonymous or
  positional reference (INSPECT-GOV-015).
- **Update the fact registry when adding inspections** —
  `specs/geometry-inspection/v2/fact-registry.json` must gain a new
  entry, with an honest `implementationStatus` and
  `forgeConsumptionStatus`, alongside any new `FactType`.
- **Update regression baselines when geometry intentionally changes** —
  `specs/geometry-inspection/v2/test-vectors/regression-vectors.json`
  and `backend/tests/test_geometry_inspection.py::TestInspectionRegression`
  must be reviewed and updated together with any deliberate geometry
  change, never silently left stale.
- **Never weaken inspection merely to make tests pass** — if a real
  finding (a disconnected group, an unexpected intersection) appears
  for legitimate geometry, record and classify it; do not loosen the
  check to hide it.
- **Record kernel-specific assumptions** — every kernel API this
  package relies on (`cadquery.Shape.distance()`/`.intersect()`/
  `.isValid()`) must be verified against the actually-installed
  CadQuery/OCP version before being used, not assumed from
  documentation or a guessed method name.
- **Keep raw CadQuery/OCP objects out of Forge contracts** — no field
  in `geometry/inspection/models.py` may ever hold a `cadquery.Shape`,
  `cadquery.Workplane`, or `OCP` object (INSPECT-GOV-016/017).
- **Add tests for every new geometric fact** — mirroring
  `backend/tests/test_geometry_inspection.py`'s existing coverage
  pattern, including a real-solitaire case and, where relevant, a
  clearly-labeled TEST-FIXTURE-ONLY broken-geometry case.
- **Create an ADR for inspection architecture changes** — replacing the
  underlying kernel-query mechanism, changing the definition of
  "connected", or any change that violates INSPECT-GOV-001 through 020
  without superseding `460-inspection-governance.md` first.
- **Create an RFC for major new inspection families** — e.g. local
  thickness, curvature, self-intersection beyond named-pair
  intersection, mesh manifold checks; see
  [`494-current-runtime-inspection-gap-analysis.md`](docs/bible/16-geometry-inspection/494-current-runtime-inspection-gap-analysis.md)
  for the candidates already identified but explicitly deferred.

## GEOMETRY QUALITY / GOLDEN MODEL RULES

`docs/bible/17-geometry-quality/` is the authoritative Geometry Quality
& Golden Models specification — start at
[`docs/bible/17-geometry-quality/README.md`](docs/bible/17-geometry-quality/README.md),
then [`500-quality-governance.md`](docs/bible/17-geometry-quality/500-quality-governance.md)
for the full 18 QUALITY-GOV rules. The machine-readable half lives in
[`specs/geometry-quality/v1/`](specs/geometry-quality/v1/README.md) (6
JSON Schemas, 5 test-vector files, all generated from real code) and the
real Golden Suite lives at
[`goldens/solitaire-v1/`](goldens/solitaire-v1/) (9 real fixtures, no
committed STEP/STL binaries). Future coding agents must:

- **Read `docs/bible/17-geometry-quality/README.md` before changing
  output geometry** — before modifying anything in
  `backend/jewelmind/geometry/`, `backend/jewelmind/geometry_quality/`,
  or a Golden fixture under `goldens/`.
- **Run Golden regression tests after geometry changes** —
  `backend/tests/test_geometry_quality_*.py` (plain pytest files, no
  special marker; they already run in the normal `pytest -q` pass) or
  `python -m jewelmind.geometry_quality.cli verify-all`.
- **Never auto-update Golden baselines to make CI pass** — no code path
  other than the explicit `geometry-quality accept --reason "..."` CLI
  command may ever write to an accepted `snapshot.json`
  (QUALITY-GOV-003/004). If a Golden test fails after your change,
  inspect the diff first; do not regenerate the baseline as a shortcut.
- **Inspect `GeometryDiff` first** — run
  `python -m jewelmind.geometry_quality.cli diff <golden_id>` (after
  `generate-candidate`) and read the human-readable output before
  deciding whether a failure is a real regression or an intentional,
  reviewable change; see
  [`513-regression-failure-triage.md`](docs/bible/17-geometry-quality/513-regression-failure-triage.md).
- **Keep Golden status separate from Professional Validation** — a
  `GoldenModel.baselineStatus` of `STABLE` never implies
  `professional_validation: validated`, and vice versa; see
  [`514-professional-validation-boundary.md`](docs/bible/17-geometry-quality/514-professional-validation-boundary.md).
- **Never use STEP byte equality as geometry equivalence** — CadQuery's
  STEP writer embeds variable OpenCascade metadata; two exports of
  identical geometry are not byte-identical. Compare via re-import and
  geometric facts only (QUALITY-GOV-007/008).
- **Use software comparison tolerances only for regression** —
  `ABSOLUTE_COMPARISON_TOLERANCE_MM`/`RELATIVE_COMPARISON_TOLERANCE`
  (`geometry_quality/version.py`) are comparison tools, never
  manufacturing or jewelry tolerances (QUALITY-GOV-006).
- **Preserve StoneReference regression protection** — every Golden
  comparison treats `designConsistency.stoneReferenceIsProductionMetal`
  as an exact invariant (QUALITY-GOV-013).
- **Preserve component identity** — a missing or unexpected component in
  a regenerated snapshot always drives `severity: REGRESSION`
  (QUALITY-GOV-011).
- **Record intentional Golden changes** — every accepted baseline change
  needs an entry in
  [`docs/bible/appendices/golden-update-register.md`](docs/bible/appendices/golden-update-register.md)
  (QUALITY-GOV-018).
- **Update version fingerprints when output-affecting dependencies
  change** — `collect_fingerprint()` in `geometry_quality/fingerprint.py`
  must keep reflecting the real installed `cadquery`/`OCP`/Forge
  registry/generator versions; see
  [`510-version-fingerprint-policy.md`](docs/bible/17-geometry-quality/510-version-fingerprint-policy.md).
- **Create an ADR for major Golden/comparison architecture changes** —
  changing which layer owns baseline acceptance, moving Golden storage
  off the filesystem, or changing the comparison algorithm's exact-vs-
  numeric-vs-relationship split; see
  [`docs/bible/17-geometry-quality/500-quality-governance.md`](docs/bible/17-geometry-quality/500-quality-governance.md).
- **Create an RFC when redefining the accepted geometry of a major
  component family** — e.g. when Sprint 16 (Ring Architecture v2)
  generalizes beyond the solitaire, or before restructuring the Golden
  Suite's coverage strategy.

## TOKEN-EFFICIENT AGENT EXECUTION

These apply to every future coding agent working on this repository, not
only Geometry Quality changes:

- **Use targeted repository searches** (Grep/Glob for specific
  symbols/paths) instead of reading entire directories or files you do
  not need.
- **Avoid rereading the entire Bible** — start from `docs/bible/README.md`,
  the relevant section's own `README.md`, and
  `docs/bible/appendices/documentation-index.md`; only open a specific
  numbered doc when a concrete question requires it.
- **Reference rather than duplicate authoritative docs** — if Atlas,
  Forge, Foundry, or Inspection already defines a concept, link to it;
  document only what is genuinely new.
- **Avoid narrating intermediate plans** — inspect, implement, test, fix,
  report; do not output a long plan before executing a milestone that
  has already been fully specified.
- **Batch repetitive work** — parallelize independent documentation or
  search tasks rather than running them one at a time.
- **Generate catalogs from machine-readable sources where practical** —
  prefer a small script deriving a catalog/table from real JSON/frontmatter
  over hand-duplicating the same data.
- **Keep final reports concise** — match the format the task actually
  asked for; do not pad with restated context the requester already has.
- **Never trade correctness or test coverage for token savings** — do not
  skip tests, weaken validation, remove error handling, omit an
  important architectural finding, hide a failure, or reduce regression
  coverage merely to finish faster or write less.

## JEWELRY CATEGORY ARCHITECTURE RULES

`docs/bible/18-ring-architecture/` is the authoritative Jewelry Category
/ Ring Architecture specification — start at
[`docs/bible/18-ring-architecture/README.md`](docs/bible/18-ring-architecture/README.md),
then [`520-jewelry-category-architecture.md`](docs/bible/18-ring-architecture/520-jewelry-category-architecture.md)
for the full 16 JEWELRY-ARCH-GOV rules. The machine-readable half lives
in [`specs/jewelry-architecture/v1/`](specs/jewelry-architecture/v1/README.md)
(category identity/capability, platform-level) and
[`specs/ring/v2/`](specs/ring/v2/README.md) (the Ring category's internal
domain contract, underneath JDL — never a second canonical JDL schema).
Future coding agents must:

- **Treat Ring as one jewelry category, not JewelMind's architectural
  root** — before adding a "generic" service, check it does not assume
  every definition has ring fields (`ring`, `band`, `setting`, prong
  count, basket height).
- **Never introduce a supposedly generic service that requires ring
  fields** — a platform-level module (anything outside
  `jewelmind.ring`/`jewelmind.geometry`/`jewelmind.validation`) must
  reach ring-specific data only through `jewelmind.ring`'s own types,
  never by assuming `definition.ring` exists as a platform guarantee.
- **Keep category-specific fields inside the category domain** — a
  future `earring.postType` belongs to an eventual `EarringDefinition`,
  never a shared/global field, exactly as `ring.size` stays under
  `RingDefinition` today (JEWELRY-ARCH-GOV-004).
- **Prefer shared Stone/Setting/Material/Manufacturing systems where
  semantically valid** — `RingDefinition` consumes `StoneSpec`/
  `MaterialSpec`/`ManufacturingSpec` as-is; it never redefines them
  (JEWELRY-ARCH-GOV-006/007). Reusable does not mean universal — don't
  force reuse where semantics genuinely differ between categories.
- **Do not advertise planned categories as supported** — a category with
  `CategoryCapability.generationSupported: false` must never appear as
  working in Designer, Studio, or any API response
  (JEWELRY-ARCH-GOV-003).
- **Add new categories through category capability/generator
  contracts** — register a new entry in
  `jewelmind.jewelry_category.registry.CATEGORY_CAPABILITIES` and a new
  generator in the category-generator registry
  (`jewelmind/jewelry_category/dispatch.py`); never branch on category
  with an `if/elif` chain scattered across unrelated modules.
- **Test non-ring extensibility** — a category-architecture change
  should keep passing (or be accompanied by an updated)
  `backend/tests/test_jewelry_category_extension.py`'s dummy-category
  proof; that dummy category must never be added to
  `CATEGORY_CAPABILITIES`, any production generator registry, Designer's
  capabilities, or the JDL schema (JEWELRY-ARCH-GOV-011).
- **Preserve backward compatibility unless an explicit JDL major-version
  migration is approved** — `domain/schema.py` is not casually
  restructured; prefer an additive adapter
  (`jewelmind.ring.adapter.ring_definition_from_jdl()`) over a breaking
  schema change (JEWELRY-ARCH-GOV-008).
- **Run relevant Golden suites after category architecture changes** —
  a dispatch/adapter change must produce zero Golden baseline updates
  unless a geometry change was intentional and explicitly reviewed
  (JEWELRY-ARCH-GOV-009/014).
- **Keep category capability machine-readable** —
  `specs/jewelry-architecture/v1/category-registry.json` is generated
  from `CATEGORY_CAPABILITIES`, never hand-maintained as a second,
  driftable copy (JEWELRY-ARCH-GOV-015).
- **Watch for cross-package circular imports when a registry needs a
  sibling package's contents** — `jewelmind.jewelry_category` and
  `jewelmind.ring` import each other's error/model types; the
  category-generator registry is built lazily inside a cached function,
  never as a module-level constant, specifically to avoid a circular
  import at package-init time (see `jewelry_category/dispatch.py`'s own
  docstring for the real bug this fixed).

## SHANK SYSTEM RULES

`docs/bible/19-shank/` is the authoritative Band & Shank System
specification — start at
[`docs/bible/19-shank/README.md`](docs/bible/19-shank/README.md),
then [`540-shank-governance.md`](docs/bible/19-shank/540-shank-governance.md)
for the full 15 SHANK-GOV rules. The machine-readable half lives in
[`specs/shank/v1/`](specs/shank/v1/README.md) (6 JSON Schemas, a real
capability registry generated from `geometry/shank/capability.py`,
examples, and test vectors). Future coding agents must:

- **Read `docs/bible/19-shank/README.md` before changing shank
  geometry** — before modifying anything in
  `backend/jewelmind/geometry/shank/`, `backend/jewelmind/geometry/connection.py`,
  or `domain/schema.py::BandSpec`/`BandTaperSpec`.
- **Never rename the public `band` JDL field to `shank`** — "Shank" is
  an internal technical term only; it must never appear in JDL field
  names, Studio UI copy, or Designer/Conversation user-facing text
  (SHANK-GOV-002).
- **Preserve the uniform-shank fast path byte-for-byte** — any request
  with `widthTaper.mode == thicknessTaper.mode == "NONE"` must keep
  using the exact pre-Sprint-17 `revolve()` construction in
  `_build_uniform_shank()`; never route a no-taper request through the
  loft-based tapered path "for consistency" (SHANK-GOV-003).
- **Never mix longitudinal variation into a section-profile builder** —
  `geometry/shank/profile.py::build_profile()` only ever sees one
  section's already-resolved dimensions; taper interpolation belongs
  exclusively in `taper.py`/`builder.py` (SHANK-GOV-004).
- **Keep taper a pure function of angular distance from the head** —
  never add a separately-duplicated "left shoulder"/"right shoulder"
  taper parameter; `taper_ratio(u, taper)` must stay the single source
  of both shoulders' behavior (SHANK-GOV-005).
- **Never let `geometry/shank/` or `geometry/connection.py` import
  `jewelmind.ring`** — these are Atlas-layer modules; Ring depends on
  Atlas, never the reverse. A real circular import was found and fixed
  this Sprint by relocating `connection.py` out of `jewelmind/ring/`
  for exactly this reason (SHANK-GOV-006).
- **Raise `ShankConstructionError` on a real construction failure —
  never silently fall back to uniform geometry** — a failed/invalid
  loft must be an observable error, not a quiet downgrade
  (SHANK-GOV-007).
- **Treat a changed `SECTION_COUNT`, head-anchoring convention, or
  taper interpolation formula as a MAJOR change** — requires a new
  Golden case or an explicit, documented Golden baseline update, never
  a silent numeric drift (SHANK-GOV-008).
- **Add new Golden cases for new Shank capabilities — never retrofit an
  existing one** — SOL-001 through SOL-009 (Sprint 15) must never be
  modified to add taper coverage; a new capability gets a new
  `goldens/solitaire-v1/` case instead (SHANK-GOV-009).
- **Route every Shank → RingHead placement through
  `ShankConnectionInterface`** — never hardcode `topZMm`/`embedMm`/
  `headCenterRadiusMm` independently inside `prongs.py`/`basket.py`
  (SHANK-GOV-010).
- **Never anchor taper anywhere but the head (`u=0`)** — the current
  `TOWARD_BOTTOM` design guarantees the connection interface never
  moves for any taper configuration; changing the anchor point is an
  architecture-level change requiring an ADR (SHANK-GOV-011).
- **Never invent a professional threshold or map a subjective
  descriptor to an arbitrary taper value** — no code in
  `geometry/shank/` or `design_intent/` may translate a word like "more
  delicate" into a `bottomRatio` number; taper is requested explicitly
  via JDL only (SHANK-GOV-012).
- **Label constructed values honestly** — `widthSamplesMm`/
  `thicknessSamplesMm` on tapered metadata are CONSTRUCTION_PARAMETER
  (computed from the same taper function used to build the geometry),
  never presented as independently re-measured MEASURED_GEOMETRY
  (SHANK-GOV-013).
- **Report every unimplemented capability as a real, documented
  limitation** — e.g. the tapered path's missing outer-rim fillet sets
  `filletApplied: false` with an explicit `filletSkippedReason`, and
  every affected Golden case lists it under `knownLimitations`
  (SHANK-GOV-014).
- **Treat `geometry/shank/capability.py`'s `SHANK_CAPABILITIES` as the
  single source of truth for CURRENT vs PLANNED** — never let
  documentation, Designer's capability list, or Studio copy claim a
  capability this registry marks `planned` (split shank, cathedral,
  knife edge, Euro shank, twisted, multi-rail, tapered-shank fillet,
  `TOWARD_HEAD` taper) (SHANK-GOV-015).
- **Update the Ring Architecture v2 mirror when `BandSpec` changes** —
  `ring/models.py::ShankDefinition` and `ring/adapter.py` claim to map
  1:1 from `JewelryDefinition.band`; keep that claim true by updating
  both, plus `specs/ring/v2/shank-definition.schema.json` and its
  examples, in the same change (see
  [`docs/bible/18-ring-architecture/526-shank-contract.md`](docs/bible/18-ring-architecture/526-shank-contract.md)).
- **Require an ADR** for a new section-profile type, a new taper mode
  beyond `NONE`/`TOWARD_BOTTOM`, a new centerline path (Euro shank),
  multiple rails (split shank), or replacing loft with a different
  construction primitive.
- **Require an RFC** for a new ring style/setting type whose geometry
  depends on Shank changes beyond what `540-shank-governance.md`
  already reserves.

## STONE SYSTEM RULES

`docs/bible/20-stone/` is the authoritative Stone System specification —
start at [`docs/bible/20-stone/README.md`](docs/bible/20-stone/README.md),
then [`560-stone-governance.md`](docs/bible/20-stone/560-stone-governance.md)
for the full 16 STONE-GOV rules. The machine-readable half lives in
[`specs/stone/v1/`](specs/stone/v1/README.md) (5 JSON Schemas, a real
`shape-registry.json` generated from `geometry/stone/capability.py`, 7
examples, and 5 test-vector files). Future coding agents must:

- **Read `docs/bible/20-stone/README.md` before changing stone
  geometry** — before modifying anything in
  `backend/jewelmind/geometry/stone/`,
  `backend/jewelmind/domain/stone_dimensions.py`, or
  `domain/schema.py::StoneSpec`.
- **Treat Stone System as shared, category-neutral infrastructure** —
  it belongs to no jewelry category. Ring may position a stone, Setting
  may interact with one, Vision may render one, Forge may evaluate rules
  involving stone facts; none of them owns `StoneDefinition`
  (STONE-GOV-001).
- **Never put a Ring dependency inside Stone System** — nothing under
  `geometry/stone/` or in `domain/stone_dimensions.py` may import
  `jewelmind.ring`. Ring depends on Stone, never the reverse; enforced by
  `backend/tests/test_stone_system_no_ring_dependency.py`, which uses AST
  parsing rather than `import` so it cannot pass by accident on an
  already-cached module (STONE-GOV-001).
- **Never let a StoneReference become production metal** — it must never
  be unioned into the metal body and must stay excluded from STEP/STL by
  default, for every shape, not only round (STONE-GOV-003/004, restating
  LAW-006).
- **Never claim gemological accuracy** — a `StoneReference` is
  deterministic CAD reference geometry. It never guarantees an exact
  facet pattern, optical behaviour, commercial cutting proportions,
  gemological certification, or vendor dimensions
  (STONE-GOV-011). `isGemologicalReproduction` is always `false`.
- **Never label a software construction constant as an industry
  standard** — the crown/pavilion/table ratios (`0.35`/`0.65`/`0.56`),
  the emerald corner clip (`0.18`), and the cushion corner radius
  (`0.25`) are `provenance: software_reference_profile`: deliberate,
  deterministic construction choices verified only to produce robust CAD
  geometry (STONE-GOV-011).
- **Keep shape separate from dimensions** — `stone.shape` selects a
  construction strategy; `diameter`/`length`/`width`/`depth` are
  independent quantities. Resolve them only through
  `domain/stone_dimensions.py`'s `resolved_length_mm()`/
  `resolved_width_mm()`/`resolved_depth_mm()`, never by reading
  `stone.diameter` directly in new code (STONE-GOV-005/006).
- **Keep orientation explicit and deterministic** —
  `stone.orientation` is a real JDL field, applied by
  `_apply_orientation()` around the stone's own local vertical axis at
  its own bounding-box center. Never infer orientation, and never
  substitute an arbitrary 3D transform (STONE-GOV-008).
- **Never fake an equivalent diameter for a non-round stone** — an
  `oval 8 × 6` is never collapsed to `diameter = 7` for rule
  compatibility. `JM-STONE-001` and `JM-PRONG-003` are explicitly scoped
  ROUND_ONLY; `JM-STONE-002` was genuinely generalized to the stone's
  real minimum horizontal extent. Any future equivalent-size metric
  requires its own explicit domain semantics (brief-level rule; see
  [`578-current-code-mapping-and-gaps.md`](docs/bible/20-stone/578-current-code-mapping-and-gaps.md)).
- **Scope round-specific Forge rules correctly** — before applying an
  existing jewelry threshold to a non-round shape, check whether its
  semantics actually generalize. If they do not, mark it
  `REQUIRES_RULE_EVOLUTION` and leave it ROUND_ONLY rather than
  evaluating it against a substituted dimension (STONE-GOV-010).
- **Keep stone-generation capability separate from Setting
  compatibility** — `generationSupported` and
  `currentSettingCompatibility` are independent axes. A shape that
  generates real geometry is never, by that fact, a shape whose prong
  setting is valid; only `round` is `SUPPORTED`, and all 6 other shapes
  are honestly `EXPERIMENTAL` (STONE-GOV-009).
- **Add registry capability metadata for every new shape** —
  `geometry/stone/capability.py::STONE_SHAPE_CAPABILITIES` is the single
  source of truth for CURRENT vs PLANNED, mirrored (never
  hand-duplicated) at `specs/stone/v1/shape-registry.json`
  (STONE-GOV-014).
- **Add Geometry Inspection and Golden coverage for every new shape** —
  a new shape needs real inspection facts and its own new Golden case;
  never retrofit an existing case (STONE-GOV-015).
- **Raise `StoneGenerationError` on a real construction failure —
  never silently fall back to another shape** — a failed/invalid loft
  must be an observable error, not a quiet substitution
  (STONE-GOV-007/013).
- **Preserve current round compatibility** — every `round` request must
  keep using the exact pre-Sprint-18 construction in
  `_build_round_stone()`; never route it through the non-round loft path
  "for consistency" (STONE-GOV-016).
- **Update the Ring Architecture v2 and JDL mirrors when `StoneSpec`
  changes** — `shared/types/jewelry-definition.ts`,
  `shared/validation/engine.ts`, `specs/jdl/v1/jdl.schema.json`, and
  `specs/ring/v2/` examples must change in the same commit.
- **Require an ADR** for a new construction primitive replacing the
  3-level loft, a change to the LENGTH/WIDTH/DEPTH axis mapping or the
  orientation convention, moving `stone_dimensions` out of `domain/`, or
  introducing a `FACETED_GEM_MODEL`/`MEASURED_STONE` layer.
- **Require an RFC** for a new stone shape (asscher, radiant, heart,
  trillion, baguette, cabochon, custom outlines, calibrated stones) —
  see [`docs/bible/04-jewelry-domain/056-domain-extension-strategy.md`](docs/bible/04-jewelry-domain/056-domain-extension-strategy.md)
  — or for multi-stone arrangements (halo, pavé, three-stone).

## SETTING SYSTEM RULES

`docs/bible/21-setting/` is the authoritative Setting System
specification — start at
[`docs/bible/21-setting/README.md`](docs/bible/21-setting/README.md),
then [`setting-governance.md`](docs/bible/21-setting/setting-governance.md)
for the full 18 SETTING-GOV rules. The machine-readable half lives in
[`specs/setting/v1/`](specs/setting/v1/README.md). Future coding agents
must:

- **Read `docs/bible/21-setting/README.md` before changing setting
  geometry** — before modifying anything in
  `backend/jewelmind/setting/`, `backend/jewelmind/geometry/setting_adapter.py`,
  or `domain/schema.py::SettingSpec`.
- **Treat Setting System as category-neutral** — a Setting defines how
  metal interacts with stones. A RingHead defines how a setting is
  incorporated into a ring. Those are different jobs.
- **Never import Ring into Setting core** — nothing under
  `jewelmind/setting/` may import `jewelmind.ring`,
  `jewelmind.jewelry_category`, `jewelmind.geometry.shank`,
  `jewelmind.geometry.connection`, `geometry/setting_adapter.py`, or
  `JewelryDefinition` (the last would smuggle the whole ring domain
  across in one import). Enforced by AST inspection in
  `backend/tests/test_setting_system_no_ring_dependency.py`. Ring may
  import Setting; the adapter is the sanctioned translation point and
  lives deliberately outside the Setting package (SETTING-GOV-001).
- **Use Stone System geometry contracts rather than round-only
  assumptions** — consume `StoneSettingReference` and
  `girdle_outline_wire()`; never read `stone.diameter` (it is `None` for
  every non-round shape) and never rebuild a stone silhouette
  (SETTING-GOV-003/008).
- **Keep Setting generation capability separate from professional
  validation** — `generatable` and `professionalValidationStatus` are
  independent axes. Every family is currently `generatable: true` AND
  `NOT_REVIEWED`; a generatable setting is never, by that fact,
  professionally validated (SETTING-GOV-007).
- **Never invent setter or manufacturing thresholds** — bezel wall
  thickness/height defaults are PRELIMINARY SOFTWARE VALUES, and **no
  minimum wall dimension is enforced** because no sourced professional
  minimum exists. The only constants in the package are construction
  parameters (SETTING-GOV-010).
- **Preserve StoneReference non-production status** — never return the
  stone as a `productionComponent`, never fuse it into metal, and keep
  it excluded from STEP/STL by default (SETTING-GOV-004, LAW-006).
- **Keep Setting attachment explicit** — a Setting receives
  `attachmentPlaneZMm`/`embedMm`/`supportHeightMm` from the category
  integration and must never compute them from a band, shank, or
  ring-size field (SETTING-GOV-014).
- **Scope Setting-specific Forge rules correctly** — all four
  `JM-PRONG-*` rules are PRONG_ONLY and `JM-SETTING-003/004` are
  BEZEL_ONLY. A prong rule must never block a valid bezel. Mirror any
  change identically in `shared/validation/engine.ts` (SETTING-GOV, FORGE-GOV-004).
- **Add capability metadata for every Setting family** —
  `setting/capability.py::SETTING_CAPABILITIES` is the single source of
  truth, mirrored (never hand-duplicated) at
  `specs/setting/v1/setting-registry.json`. Reserved families must have
  no generator and must not be `SettingFamily` enum members
  (SETTING-GOV-005).
- **Add Geometry Inspection and Golden coverage for every real Setting
  family** — a new family needs real inspection facts and its own new
  Golden case; never retrofit an existing one (SETTING-GOV-015).
- **Never silently substitute another Setting when generation fails** —
  no `BEZEL → PRONG` path and no `OUTLINE_CARDINAL → RADIAL` downgrade.
  Any documented geometric accommodation must be recorded as an
  observable `SettingFallbackEvent` (SETTING-GOV-013).
- **Preserve custom-Setting and imported-Setting escape hatches** — the
  generator registry must stay a registry, not an `if/elif` chain, so a
  future custom setting remains reachable (SETTING-GOV-018).
- **Keep seats/bearings/cutters status explicit** — all three are
  `PLANNED` for every family because **none exists**. Stone/metal
  overlap is NOT a seat and must never be renamed as one
  (SETTING-GOV-011).
- **Run old and new Golden suites after Setting changes** — all 23
  cases. Round 4/6-prong must stay byte-identical
  (`341.44334316909976 mm³`); a non-round change must go through
  `generate-candidate → diff → accept --reason`, never an automatic
  regeneration (SETTING-GOV-017).
- **Keep the Capability Coverage Guard honest** —
  `specs/capabilities/jewelmind-capabilities.json` must be updated with
  any capability change, and `CURRENT` requires real implementation AND
  tests. `backend/tests/test_capability_coverage.py` checks it against
  the live registries.

Retain the **TOKEN-EFFICIENT AGENT EXECUTION** rules from Sprint 15
(above) and the **CAPABILITY COVERAGE GUARD** — they apply to every
future sprint, not only Geometry Quality, Ring Architecture, Shank,
Stone, or Setting changes.

## STONE SYSTEM V2 RULES

`docs/bible/22-stone-v2/` is the authoritative Stone System v2 specification —
start at
[`docs/bible/22-stone-v2/README.md`](docs/bible/22-stone-v2/README.md), then
[`stone-v2-governance.md`](docs/bible/22-stone-v2/stone-v2-governance.md) for
the full 18 STONEV2-GOV rules. The machine-readable half lives in
[`specs/stone/v2/`](specs/stone/v2/README.md) (12 JSON Schemas, three
registries generated from the live code, 19 examples, 8 test-vector files).
Sprint 18's [`specs/stone/v1/`](specs/stone/v1/README.md) and
[`docs/bible/20-stone/`](docs/bible/20-stone/README.md) remain accurate for the
seven original shapes and for the shared coordinate contract; the 16 STONE-GOV
rules still apply in full. Future coding agents must:

- **Never assume the built-in shape enum covers every real stone.** Stone v2's
  whole objective is that it does not. Before adding a shape, ask whether
  `CUSTOM_OUTLINE` already covers the case (STONEV2-GOV-002).
- **Preserve the three escape hatches** — `CUSTOM_OUTLINE`, `MEASURED`,
  `IMPORTED_CAD`. A change that makes a named-enum cut the only route to stone
  geometry is a regression against this sprint, however many cuts the enum has.
- **Keep Stone shape/cut separate from Gem identity.** `stone.shape =
  "emerald"` is the clipped-corner OUTLINE; the gem species emerald is Sprint 21
  territory. The rhombus is `lozenge`, never `diamond`. `StoneSpec` carries no
  material or species field, and no shape synonym may resolve a species name to
  a cut (STONEV2-GOV-008).
- **Keep outline and profile as two independent axes.** Never add an
  `OVAL_CABOCHON`-style compound enum member; an oval cabochon is
  `shape=oval` + `profile=CABOCHON_REFERENCE` (STONEV2-GOV-005).
- **Never invent a missing Stone measurement.** A `MEASURED` stone with an
  absent measurement raises `MEASURED_STONE_INSUFFICIENT_DATA`. A
  dimension-only reference is labelled `MEASURED_DIMENSION_REFERENCE` and must
  never be described as the physical stone's real surface (STONEV2-GOV-006).
- **Never invent commercial cut proportions.** Every ratio in
  `geometry/stone/outline.py` and `geometry/stone/profile.py` is a SOFTWARE
  REFERENCE CONSTRUCTION parameter. `radiant` is not the radiant brilliant
  facet pattern, `asscher` is not the Asscher step cut, and
  `CABOCHON_REFERENCE` is not a gemological cabochon (STONEV2-GOV-003/004).
- **Never fabricate an equivalent diameter** for a non-round stone — carried
  from Sprint 18, unchanged.
- **Never guess an imported asset's unit.** `declaredUnit` is required; the
  honest failure is `STONE_IMPORT_UNITS_UNKNOWN`, never a default
  (FOUNDRY-GOV-012).
- **Never silently convert imported geometry into a native approximation.** The
  asset IS the stone: it is placed, never rebuilt (STONEV2-GOV-010).
- **Distinguish B-Rep from mesh capabilities.** An STL import reports
  `representation: MESH`, `solidCount: 0` and a null volume — the honest
  result. `supportsBrepOperations` is computed from the real parsed geometry,
  never from the file extension. **A mesh must also be transformed node by
  node**: neither `cadquery.Shape.scale()` nor `BRepBuilderAPI_Transform` moves
  a triangulation, which shipped as a real bug this sprint (STONEV2-GOV-014).
- **Keep Stone source provenance explicit, true and stable.**
  `normalizationOperations` records every operation ACTUALLY applied — an entry
  claiming an operation the geometry did not receive is worse than a missing
  one. Provenance carries no wall-clock timestamp, because it participates in
  `definitionHash` and in Golden snapshots. `sourceAssetHash` is a content
  hash, never a filesystem path (STONEV2-GOV-015).
- **Treat imported stone files as untrusted input** — content-addressed
  storage with a validated hexadecimal hash, size and complexity bounds checked
  after parsing as well as before, sanitized error messages with no stack trace
  or server path, and never any execution of file content (STONEV2-GOV-016).
- **Never repair a malformed custom outline** — validate and reject. Only unit
  conversion, winding and origin are normalized, and each is recorded.
  Normalization changes coordinates, never shape.
- **Keep requested dimensions equal to measured dimensions.** Every native
  outline's real bounding box must equal the request; four shapes violated this
  during Sprint 20 and each was fixed at the source, never by reporting the
  nominal value (STONEV2-GOV-012).
- **Keep every outline centred on the local origin** — the frame
  `_apply_orientation()` rotates about and `StoneSettingReference` reports. A
  size-only check is not enough; `half_moon` had a correct size and a wrong
  centre (STONEV2-GOV-013).
- **Preserve Stone v1 exactly.** A plain round faceted parametric stone must
  keep using `_build_round_stone()`. That is a GEOMETRY guarantee, not a
  performance note: the shared pipeline's proportional culet makes its body
  ~1.8% larger. Target and result: zero Stone v1 Golden baseline updates
  (STONEV2-GOV-017).
- **Keep the Stone System category-neutral** — nothing under
  `jewelmind/stone/`, `geometry/stone/` or `domain/stone_dimensions.py` may
  import a jewelry category, and the core must not import `JewelryDefinition`.
  `geometry/stone/builder.py` is the sanctioned placement adapter;
  `build_stone_geometry(stone, girdle_z_mm)` must remain a category-neutral
  entry point. Enforced by AST inspection in
  `backend/tests/test_stone_v2_no_category_dependency.py` (STONEV2-GOV-001).
- **Keep `jewelmind/stone/__init__.py` importing nothing.** It is load-bearing:
  `domain/schema.py` imports `jewelmind.stone.models` while
  `jewelmind.stone.normalize` imports `domain/schema.py`, and the graph is only
  acyclic because the package init pulls in no submodule.
- **Keep anchors as geometric facts, never prong positions.** An anchor a shape
  does not have is ABSENT, never approximated: a custom outline has no
  deterministic TIP, a pearl has no anchors at all (STONEV2-GOV-009).
- **Keep Setting behaviour driven by geometric properties, not shape names.**
  `jewelmind/setting/` must contain no comparison of `.shape` against a string
  literal; strategy selection reads `isRadiallySymmetric`, and bezel paths come
  from the outline. Enforced by an AST scan in
  `test_stone_v2.py::test_setting_system_has_no_custom_shape_special_case`.
- **Scope Forge rules honestly rather than loosening them.** A rule is
  evaluated only where its premise holds — `STONE_DEPTH_RANGE` is skipped for
  spherical and imported stones. Do not close a recorded gap (`pearl` has no
  diameter range; a non-round shape's `length`/`width` have none individually)
  by inventing a threshold (STONEV2-GOV-011).
- **Generate every registry, example and test vector by running the real
  implementation** — `specs/stone/v2/` and
  `specs/capabilities/jewelmind-capabilities.json` are mirrors of live code,
  never hand-maintained copies. Sprint 20 removed three hand-copies that had
  already drifted and caused Designer and Setting to misreport real
  capabilities.
- **Require registry, inspection, test and Golden coverage for every new
  capability**, in the same change — including a requested-equals-measured
  dimension assertion and a NEW Golden case, never a retrofit of an existing
  one (STONEV2-GOV-018).
- **Never mark a shape, profile or source CURRENT without a real generator AND
  real tests.** Nothing in Stone v2 is professionally validated; every entry is
  `NOT_REVIEWED` and the active validation registry holds zero records
  (STONEV2-GOV-007).
- **Create an ADR** before changing the LENGTH/WIDTH/DEPTH axis mapping or the
  orientation convention, replacing the outline-plus-profile model, moving
  `domain/stone_dimensions.py` out of `domain/`, or introducing a
  `FACETED_GEM_MODEL`/`SCANNED_MESH` layer.
- **Create an RFC** before adding a stone shape beyond the 21 implemented (see
  `RESERVED_STONE_SHAPES`), a multi-stone arrangement, a new import format, a
  real scan-processing pipeline, or curve-segment/SVG outline input.

Retain the **TOKEN-EFFICIENT AGENT EXECUTION** rules and the **CAPABILITY
COVERAGE GUARD** — they apply to every future sprint.
