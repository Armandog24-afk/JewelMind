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
