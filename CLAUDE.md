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
  stone, prongs, basket) + `geometry/assemblies/solitaire.py` (combines
  them).
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
