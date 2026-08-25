---
id: JM-BIBLE-README
title: JewelMind Technical Bible — Index
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on: []
related_documents:
  - JM-BIBLE-000
  - JM-BIBLE-DOMAIN-README
  - JM-BIBLE-JDL-README
  - JM-BIBLE-FORGE-README
  - JM-BIBLE-ATLAS-README
  - JM-BIBLE-ALCHEMIST-README
implementation_status: current
---

# JewelMind Technical Bible

The Technical Bible is the structured, factual source of truth for what
JewelMind is, what it currently does, why it was built the way it was, and
what is and is not planned. It exists so that a founder, a developer, a
jewelry professional, a future AI coding agent, or a technical partner can
all read the same documents and reach the same understanding.

**Start here:** [`00-foundation/000-bible-governance.md`](00-foundation/000-bible-governance.md)
defines how this Bible works — document statuses, when an ADR is required,
and the rule that governs every other document: current, partial, planned,
and vision functionality must never be confused with one another.

This Bible now spans six Sprints:

- **Sprint 1 — Foundation and Current System**, documenting the
  solitaire-ring MVP that exists in this repository today. It does not
  describe a different, larger product — see
  [`00-foundation/002-vision-and-mission.md`](00-foundation/002-vision-and-mission.md)
  for the explicitly-labeled long-term vision, kept separate from the
  current system on purpose.
- **Sprint 2 — Jewelry Domain Model**
  ([`04-jewelry-domain/`](04-jewelry-domain/)), defining the jewelry
  concepts, entities, and relationships JewelMind currently understands
  — and, just as importantly, does not yet understand or has not had
  professionally validated. Start there at
  [`04-jewelry-domain/README.md`](04-jewelry-domain/README.md).
- **Sprint 3 — Jewelry Definition Language v1**
  ([`05-jdl/`](05-jdl/)), formalizing JDL: schema, syntax, semantics,
  canonicalization, diagnostics, versioning, and the compiler contract —
  the stable boundary between design input, jewelry-domain concepts,
  deterministic validation, geometry generation, and export. Canonical
  JSON is the only NORMATIVE representation today; a YAML serialization
  and a textual DSL are PLANNED, non-normative. Start there at
  [`05-jdl/README.md`](05-jdl/README.md).
- **Sprint 4 — Forge Rule System v1**
  ([`06-forge/`](06-forge/)), formalizing the architecture, provenance
  model, evaluation pipeline, diagnostics, lifecycle, and
  professional-validation process for every jewelry-domain rule
  JewelMind evaluates. Forge is a specification and classification
  layer over the existing validation engine, not a new runtime system —
  **0 of the 21 currently registered rules are professionally
  validated.** Start there at [`06-forge/README.md`](06-forge/README.md).
- **Sprint 5 — Atlas Geometry Core v1**
  ([`07-atlas/`](07-atlas/)), formalizing the deterministic geometry
  layer: primitives, coordinate conventions, component/assembly
  contracts, the construction pipeline, and the geometry-inspection
  framework — all over the existing CadQuery/OpenCascade code, adding
  no new ring style and replacing no kernel. Formalizes the
  Atlas/Forge boundary: Atlas reports geometric facts, only Forge
  interprets them as rule violations. Start there at
  [`07-atlas/README.md`](07-atlas/README.md).
- **Sprint 6 — Alchemist Compiler v1**
  ([`08-alchemist/`](08-alchemist/)), formalizing the compilation
  orchestration layer: the translation from validated JDL and Forge
  evaluation into a `GeometryPlan`, Atlas execution, and an artifact
  manifest. Almost entirely architecture-before-implementation — the
  current backend already performs every step correctly, inline, with
  no explicit `GeometryPlan` or `compilationHash` yet. Identifies the
  clearest concrete gap in the whole pipeline: preview generation is
  coupled to core geometry generation, while export generation is
  correctly decoupled. Start there at
  [`08-alchemist/README.md`](08-alchemist/README.md).
- **Sprint 7 — Foundry Export System v1**
  ([`09-foundry/`](09-foundry/)), formalizing the artifact-generation
  and export-integrity layer: STEP/STL/JSON/technical-specification
  contracts, component-inclusion policy, artifact integrity/validation
  models, filename and temp-file safety, export version fingerprints,
  and CAD interoperability boundaries. Unlike Sprint 6, this formalizes
  an export system that already runs in production, and performs a
  small set of targeted hardening changes (shared shape-selection
  extraction, checksums, non-empty-file validation) alongside the
  documentation. Finds that STEP and STL export have opposite
  determinism profiles: STL checksums are stable across repeated
  exports, STEP checksums are not (an embedded timestamp and translator
  counter vary while the geometry itself does not). Start there at
  [`09-foundry/README.md`](09-foundry/README.md).
- **Sprint 8 — Vision v1**
  ([`10-vision/`](10-vision/)), formalizing the visual-output layer —
  Technical inspection and Presentation display, both consuming the
  exact same Atlas-generated geometry that powers STEP/STL export. This
  Sprint is not documentation-only: it materially rebuilds the viewer,
  adding a Technical/Presentation view switch, 5 bounding-box-driven
  camera presets, a centralized 5-metal material system, a
  CDN-free procedural studio environment and contact-shadow grounding
  for Presentation mode, and real client-side PNG image capture — while
  proving, via the full test suite, that none of it altered STEP/STL
  export output. Start there at [`10-vision/README.md`](10-vision/README.md).

## How this relates to the existing `docs/` folder

`docs/*.md` (architecture, geometry conventions, domain model, validation
rules, API reference, development guide, known limitations) already existed
before this Bible and remains authoritative for the day-to-day technical
detail it covers — none of it was deleted or contradicted. The Bible does
not repeat that detail; it links to it, gives it a place in a bigger
structure (product rationale, architectural decisions, constitutional
rules, and a governance model for keeping all of it honest over time), and
is the place future changes should update first when they affect product
scope or architecture. See
[`appendices/documentation-index.md`](appendices/documentation-index.md)
for the complete map of every document, old and new.

## Structure

| Section | Contents |
|---|---|
| [`00-foundation/`](00-foundation/) | Governance, product overview, vision, principles, constitution, current status, scope, system map, glossary |
| [`01-product/`](01-product/) | User problems, target users, user journey, functional/non-functional requirements, success metrics |
| [`02-architecture/`](02-architecture/) | Architecture overview, repository map, domain boundaries, data flow, runtime/deployment, security, known technical limitations |
| [`03-decisions/`](03-decisions/) | Architecture Decision Records (ADRs) — why the system is built the way it is |
| [`04-jewelry-domain/`](04-jewelry-domain/) | Jewelry taxonomy, ring anatomy, the solitaire domain model, per-component domain documents, parametric dependencies, invariants, validation classification, domain-to-code mapping, extension strategy, open questions, and the professional-validation register |
| [`05-jdl/`](05-jdl/) | The Jewelry Definition Language (JDL) v1: governance, language overview, processing model, canonical document model, serialization/DSL contracts, type system, semantic rules, validation pipeline, canonicalization/hashing, compiler/geometry/artifact contracts, diagnostics, versioning, extension model, security, current-implementation mapping, conformance levels, and open questions |
| [`06-forge/`](06-forge/) | The Forge Rule System v1: governance, rule anatomy, classification, provenance, lifecycle, evaluation pipeline, context/result models, severity/blocking semantics, dependencies, conflicts, suggestions/auto-fix, professional-validation lifecycle, rule families (manufacturing/geometry/export), versioning, registry, current-rule inventory, gap analysis, testing strategy, API contract, future AI-assisted discovery, and open questions |
| [`07-atlas/`](07-atlas/) | The Atlas Geometry Core v1: governance, architecture overview, geometric representation/coordinate/primitive/transformation models, curve/surface/B-Rep/mesh models, component/assembly contracts, construction pipeline, operation/boolean/fillet strategies, tolerance/determinism/naming/metadata models, inspection framework, connectivity/volume/stone-separation contracts, preview/STEP/STL contracts, error/performance models, current solitaire mapping, gap analysis, and open questions |
| [`08-alchemist/`](08-alchemist/) | The Alchemist Compiler v1: governance, architecture overview, boundaries, compilation-input/normalization/Forge-integration contracts, GeometryPlan model and generation, Atlas-execution contract, build order, compilation state machine, result model, diagnostics/failure-propagation, partial-compilation policy, determinism/version-fingerprint, definition-hash-vs-compilation-hash, cache model, artifact request/manifest contracts, preview/export integration, capability/versioning models, current-backend mapping, observability/performance/security models, gap analysis, and open questions |
| [`09-foundry/`](09-foundry/) | The Foundry Export System v1: governance, architecture overview, artifact domain model, artifact request contract, generation pipeline, component-inclusion policy, production geometry selection, STEP/STL/JSON/technical-specification contracts, artifact manifest and integrity models, export validation pipeline, diagnostics, partial-success model, filename/temp-file safety, export version fingerprint, CAD interoperability philosophy and per-format boundaries, unit/scale contract, multi-solid and fusion policy, roundtrip validation, performance/security models, current exporter code mapping, gap analysis, and open questions |
| [`10-vision/`](10-vision/) | Vision v1: governance, architecture overview, visual representation model, Atlas-to-Vision contract, preview mesh contract, scene graph model, component visual identity, Technical/Presentation view contracts, camera/lighting/material systems, metal/stone material models, background/environment/grounding models, component visibility, model framing and fit, image capture contract, render state model, stale/last-good preview, rendering diagnostics, performance/GPU resource model, accessibility, visual consistency contract, visual regression strategy, current viewer code mapping, gap analysis, and open questions |
| [`appendices/`](appendices/) | Factual inventories generated by inspecting the actual code, tests, and API |

## Reading order

1. [`00-foundation/000-bible-governance.md`](00-foundation/000-bible-governance.md) — how to use and update this Bible
2. [`00-foundation/001-project-overview.md`](00-foundation/001-project-overview.md) — what JewelMind is today
3. [`00-foundation/004-jewelmind-constitution.md`](00-foundation/004-jewelmind-constitution.md) — the rules that cannot be broken without an ADR
4. [`00-foundation/005-current-product-status.md`](00-foundation/005-current-product-status.md) — the factual implementation matrix
5. Everything else, as needed for the work at hand

## Status of this milestone

**Technical Bible Sprint 1 — Foundation and Current System** established
the governance model, the constitution, the current-state documentation,
and the first ten ADRs.

**Technical Bible Sprint 2 — Jewelry Domain Model** defines the jewelry
concepts, entities, components, relationships, parameters, and
dependencies JewelMind currently understands, classified by
implementation status (current/partial/planned/vision) and, separately,
by professional-validation status (see
[`04-jewelry-domain/040-domain-governance.md`](04-jewelry-domain/040-domain-governance.md)).
As of Sprint 2, **zero** jewelry rules in this repository have been
professionally validated — every numeric threshold is, at most, a
preliminary software rule. See
[`04-jewelry-domain/058-professional-validation-register.md`](04-jewelry-domain/058-professional-validation-register.md).

**Technical Bible Sprint 3 — Jewelry Definition Language v1** formalizes
JDL as a language and semantic contract with three representations:
Canonical JSON (CURRENT, the only NORMATIVE one), a YAML serialization
(PLANNED, non-normative), and a textual DSL (PLANNED, non-normative, grammar
only — no parser was built). It adds the machine-readable specification
under [`../../specs/jdl/v1/`](../../specs/jdl/v1/README.md) (JSON Schema,
EBNF grammar, 12 example documents, and test vectors, all generated from
and verified against the real backend) plus a `backend/tests/`
test suite that re-checks the specification against the running
implementation on every test run.

**Technical Bible Sprint 4 — Forge Rule System v1** formalizes the
architecture, provenance model, evaluation pipeline, diagnostics,
lifecycle, and professional-validation process for every jewelry-domain
rule JewelMind evaluates. Forge is a specification and classification
layer over the existing validation engine (`backend/jewelmind/validation/`)
— it adds no new rule, no new blocking behavior, and no new runtime
system. It gives the 16 pre-existing rules, plus 5 newly-named
cross-cutting rules (schema/safety/geometry-inspection/export-precondition
checks that already existed as code behavior but had no stable ID), a
formal classification (11 categories), provenance (11 types), and an
8-state lifecycle. As of Sprint 4, **0 of the 21 registered rules are
professionally validated** — see
[`06-forge/103-professional-validation-lifecycle.md`](06-forge/103-professional-validation-lifecycle.md).
It adds the machine-readable specification under
[`../../specs/forge/v1/`](../../specs/forge/v1/README.md) (4 JSON Schemas,
the real 21-rule registry, 6 example rule definitions, and 4 test-vector
files) plus a `backend/tests/test_forge_registry.py` suite.

**Technical Bible Sprint 5 — Atlas Geometry Core v1** formalizes the
deterministic geometry layer: geometric primitives, coordinate
conventions, component/assembly contracts, the construction pipeline,
and the geometry-inspection framework, all as a specification and
classification layer over the CadQuery/OpenCascade code that already
exists in `backend/jewelmind/geometry/`. It confirms the current
coordinate convention has no internal inconsistency, catalogues all 4
geometry components and 14 geometry operations actually used, documents
7 previously-undocumented magic numbers (fixed millimeter constants like
the comfort-fit flare and fillet caps) and one previously-undocumented
CAD-kernel-tolerance fact, and finds that **only one geometric fact is
inspected at runtime** (the fuse-solid-count check) — everything else
this Bible calls "current" geometry correctness is verified only by
`backend/tests/test_geometry.py`, not re-checked for a real user's
specific input. It adds the machine-readable specification under
[`../../specs/atlas/v1/`](../../specs/atlas/v1/README.md) (6 JSON
Schemas, 5 real example records generated by running the actual
geometry builders, and 5 test-vector files) plus a
`backend/tests/test_atlas_registry.py` suite.

**Technical Bible Sprint 6 — Alchemist Compiler v1** formalizes the
compilation orchestration layer sitting between Forge and Atlas:
`CompilationInput`, normalization, `GeometryPlan` (PLANNED — no such
object exists in current code), the Atlas execution contract, component
build order (confirmed: the four solitaire components have no true data
dependency on each other — only the final fuse step depends on three of
them), a compilation state machine, `CompilationResult`,
failure-propagation and partial-compilation policy, the proposed
`compilationHash` (additive to, never replacing, the existing
`definitionHash`), the cache model, artifact request/manifest contracts,
compiler capabilities/versioning, and a full current-backend-to-compiler
mapping. It identifies the clearest concrete architectural gap in the
whole pipeline to date: **preview generation is coupled to core geometry
generation inside `ModelService.generate()`, while export generation is
correctly decoupled** — a hypothetical preview failure would today fail
an entire compilation even though the underlying geometry was valid. It
adds the machine-readable specification under
[`../../specs/alchemist/v1/`](../../specs/alchemist/v1/README.md) (8
JSON Schemas, 6 example records, and 7 test-vector files) plus a
`backend/tests/test_alchemist_registry.py` suite.

**Technical Bible Sprint 7 — Foundry Export System v1** formalizes the
artifact-generation and export-integrity layer sitting after Atlas:
component-inclusion policy (confirmed identical for STEP and STL, by
construction, since both now call the same shared shape-selection
function), per-format contracts for STEP/STL/JSON/technical
specification, the 8-level artifact integrity model (only 3 levels run
for every real request today), the export-diagnostic vocabulary
(discovering that `ExportFailedError` is defined but never actually
raised by the JSON/specification export routes), filename and temp-file
safety, and CAD interoperability boundaries (zero external CAD
applications have ever actually opened a JewelMind file — every claim
beyond CadQuery's own self-consistency stays at `EXPORT_SUPPORTED`
only). Unlike Sprints 1–6, this Sprint also performs targeted, explicitly
scoped hardening: extracting a shared `select_export_shapes()` function
(closing Sprint 6's `ALCHEMIST-GAP-010`), adding SHA-256 checksums and
non-empty-file validation to every STEP/STL export, and discovering that
STEP export is not byte-for-byte deterministic (an embedded timestamp
and OpenCascade translator-instance counter vary between exports) while
STL export is. It adds the machine-readable specification under
[`../../specs/foundry/v1/`](../../specs/foundry/v1/README.md) (6 JSON
Schemas, 7 example records, and 7 test-vector files) plus a
`backend/tests/test_foundry_registry.py` suite.

**Technical Bible Sprint 8 — Vision v1** formalizes the visual-output
layer sitting after Atlas and alongside Foundry: the same
Atlas-generated preview geometry now feeds two distinct, geometrically
consistent views — a Technical inspection view (orbit, 5
bounding-box-driven camera presets, component visibility, status) and a
Presentation view (centralized 5-metal PBR material system, a
transmissive StoneReference presentation material, studio lighting, a
CDN-free procedural environment via `three-stdlib`'s `RoomEnvironment`,
and contact-shadow grounding). Unlike every prior Sprint, this one is
explicitly a **product milestone**, not documentation over pre-existing
behavior: it ships a working view-mode switch, a client-side PNG
"Save render" capture feature, and a small, additive backend
metadata extension (`geometryRole`/`productionRole`/`meshSource`/
`generationStatus` per preview component) — while proving the full
backend and frontend test suites pass unchanged in outcome for every
pre-existing test, confirming no STEP/STL export or stale/last-good-
preview behavior was altered. It also resolves Sprint 7's
`ExportFailedError` dead-code finding by removing the unused class,
confirmed safe by the unchanged test suite. It adds the machine-readable
specification under [`../../specs/vision/v1/`](../../specs/vision/v1/README.md)
(6 JSON Schemas, 6 example scene states, and 5 test-vector files) plus a
`backend/tests/test_vision_schemas.py` suite.

All eight Sprints are grounded in the real, running application, but
differ in kind: Sprints 1–6 changed no application code behavior beyond
tiny naming corrections noted in each document's own text where
applicable. Sprint 7 was the first to additionally perform small,
explicitly pre-authorized, behavior-preserving hardening changes (see
[`09-foundry/README.md`](09-foundry/README.md)). **Sprint 8 is the first
to ship new, user-visible product functionality** (see
[`10-vision/README.md`](10-vision/README.md)), verified by the full
backend test suite passing unchanged in shape (199 tests, up from 194
after Sprint 7) and the full frontend test suite growing from 41 to 72
tests, both green before and after. All eight add their own additive
test-only dependency usage (`jsonschema`) and test files
(`test_jdl_schema_examples.py`, `test_forge_registry.py`,
`test_atlas_registry.py`, `test_alchemist_registry.py`,
`test_export_integrity.py`, `test_filenames.py`,
`test_foundry_registry.py`, `test_vision_schemas.py`).
