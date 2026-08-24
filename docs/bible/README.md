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

This Bible now spans five Sprints:

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

All five Sprints are documentation milestones: no application code
behavior was changed to produce them, beyond the tiny naming corrections
noted in each document's own text where applicable, and beyond Sprints
3–5's small additive test-only dependency (`jsonschema`) and test files
(`test_jdl_schema_examples.py`, `test_forge_registry.py`,
`test_atlas_registry.py`).
