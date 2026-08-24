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
