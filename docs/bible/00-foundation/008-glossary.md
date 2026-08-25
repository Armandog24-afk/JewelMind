---
id: JM-BIBLE-008
title: Glossary
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on: []
related_documents:
  - JM-BIBLE-001
  - JM-BIBLE-DOMAIN-README
  - JM-BIBLE-JDL-README
  - JM-BIBLE-FORGE-README
  - JM-BIBLE-ATLAS-README
  - JM-BIBLE-ALCHEMIST-README
implementation_status: current
---

# Glossary

Technical and jewelry terms as used **specifically by this project**. For
jewelry terms, this glossary deliberately does not claim the current
simplified geometry represents full professional jewelry practice — see
each entry's note where relevant.

## Technical terms

**JewelryDefinition** — the canonical, structured description of a ring's
parameters (project, ring, band, stone, setting, material, manufacturing,
preview). Defined in `backend/jewelmind/domain/schema.py` (authoritative)
and mirrored in `shared/types/jewelry-definition.ts`.

**Canonical definition** — a `JewelryDefinition` serialized in a fixed,
deterministic form (sorted keys, no incidental whitespace) so it can be
hashed reproducibly. See `backend/jewelmind/utils/hashing.py`.

**Schema version** — the `schemaVersion` field, currently locked to
`"0.1.0"`. An unsupported value is rejected rather than guessed at.

**Parametric** — describing geometry entirely through a set of named,
adjustable values rather than fixed, hardcoded shapes. See Product
Principle 1.

**Deterministic** — producing the same output every time for the same
input, with no dependency on randomness, wall-clock time, or external
state. See Product Principle 2 and 3, and
[ADR-003](../03-decisions/ADR-003-deterministic-geometry.md).

**B-Rep (Boundary Representation)** — a way of representing a solid by
describing its bounding surfaces (faces, edges, vertices) precisely,
rather than as a mesh approximation. This is the representation
OpenCascade (and therefore CadQuery) uses internally.

**OpenCascade** — the open-source B-Rep geometry kernel that CadQuery is
built on. The same category of kernel used inside professional CAD
systems.

**CadQuery** — the Python library JewelMind uses to build geometry
through OpenCascade, using a fluent, code-first API (`cq.Workplane(...)`).

**STEP** — a vendor-neutral CAD interchange file format (ISO 10303) for
exact B-Rep solids, importable by virtually all professional CAD
software.

**STL** — a vendor-neutral file format storing a triangulated mesh
approximation of a solid's surface, widely used for 3D printing and
preview.

**Mesh** — a triangulated (faceted) approximation of a solid's surface,
used for STL export and for the browser preview. Distinct from the exact
B-Rep solid it approximates.

**Solid** — an exact, watertight B-Rep volume, as produced by CadQuery/
OpenCascade — the "real" geometry, before it is tessellated into a mesh
for preview or STL export.

**Assembly** — the combination of multiple named solids (band, stone
reference, prongs, basket support) into one structured
`GeneratedModel`. See `backend/jewelmind/geometry/model.py`.

**Bounding box** — the smallest axis-aligned box containing a solid or
assembly, expressed as min/max X/Y/Z in millimeters.

**Volume** — the enclosed volume of a solid, in cubic millimeters,
reported per component and for the combined metal body.

**Tolerance** — in this project, specifically the tessellation tolerance
(`preview.meshTolerance`, `preview.angularTolerance`) controlling how
closely a mesh approximates the exact solid — not a manufacturing
tolerance.

## Jewelry terms (as used by this project's simplified model)

> Authoritative source for every term in this section:
> [`04-jewelry-domain/`](../04-jewelry-domain/README.md) (Sprint 2). This
> glossary gives the short definition; the linked domain document gives
> full detail, current limitations, and professional-validation status.

**JewelryProduct** — the top-level taxonomy concept covering every
category of jewelry (ring, earring, pendant, ...). Only `Ring` is
implemented today. See
[`04-jewelry-domain/041-jewelry-product-taxonomy.md`](../04-jewelry-domain/041-jewelry-product-taxonomy.md).

**Ring style** — the overall structural category of a ring (e.g.
solitaire, halo). A separate axis from setting type, band style, and
decorative treatment — see
[`04-jewelry-domain/042-ring-taxonomy.md`](../04-jewelry-domain/042-ring-taxonomy.md).
Only `Solitaire` is implemented today.

**Band** — the ring's circular metal body, defined by width, thickness,
and profile (flat or comfort-fit). See
`docs/geometry-conventions.md` and
[`04-jewelry-domain/045-band-domain.md`](../04-jewelry-domain/045-band-domain.md).

**Flat profile** — a band cross-section that is a plain rectangle
(optionally with a small outer-rim fillet).

**Comfort fit** — a band profile whose inner surface is a shallow curve
rather than flat, intended to feel rounder against the finger. *Note:*
this project's implementation is a simplified geometric approximation of
the concept, not a manufacturing-validated ergonomic profile.

**Shoulders** — the transitional band sections leading up to the setting
(relevant to styles like cathedral). **Not implemented** — see
[`04-jewelry-domain/043-ring-anatomy.md`](../04-jewelry-domain/043-ring-anatomy.md).

**Head** — informal umbrella term for the setting + basket support
combined. Not a named concept in current code — see
[`04-jewelry-domain/043-ring-anatomy.md`](../04-jewelry-domain/043-ring-anatomy.md).

**Gallery** — decorative open or filigreed structure between the stone
and the band, often part of or visible through the basket. **Not
implemented** — see
[`04-jewelry-domain/049-basket-and-support-domain.md`](../04-jewelry-domain/049-basket-and-support-domain.md).

**Bridge** — a structural connector distinct from the gallery, sometimes
linking a basket to shoulders. **Not implemented** — see
[`04-jewelry-domain/049-basket-and-support-domain.md`](../04-jewelry-domain/049-basket-and-support-domain.md).

**Stone reference** — a simplified geometric solid representing the
approximate size and position of the center stone, used for visualization
and clearance checking. *Note:* explicitly not a gemological reproduction
of a real cut stone — see [LAW-006](004-jewelmind-constitution.md),
`docs/known-limitations.md`, and
[`04-jewelry-domain/046-stone-domain.md`](../04-jewelry-domain/046-stone-domain.md).
Deliberately not named "certified gemstone," "manufacturing stone seat,"
or "gemological model" — see the linked document for why.

**Girdle** — in real gemology, the widest edge of a cut stone, separating
crown from pavilion. In this project's simplified stone reference, the
girdle is the widest ring of the lofted approximation, sized from
`stone.diameter`.

**Crown** — in real gemology, the upper, table-facing part of a cut
stone above the girdle. In this project's stone reference, a fixed
fraction of `stone.depth` above the girdle.

**Pavilion** — in real gemology, the lower, pointed part of a cut stone
below the girdle. In this project's stone reference, a fixed fraction of
`stone.depth` below the girdle.

**Stone shape** — the geometric cut category of a stone (round, oval,
princess, ...). Only `round` is implemented today — see
[`04-jewelry-domain/046-stone-domain.md`](../04-jewelry-domain/046-stone-domain.md).

**Setting** — the general concept of how a stone is physically held
(prong, bezel, channel, pavé, ...); this project currently supports only
prong settings. See
[`04-jewelry-domain/047-setting-domain.md`](../04-jewelry-domain/047-setting-domain.md).

**Pavé** — a setting/decorative technique where many small stones are set
closely together — **not a ring style**, despite sometimes being used
loosely that way. **Not implemented.** See
[`04-jewelry-domain/047-setting-domain.md`](../04-jewelry-domain/047-setting-domain.md)
and
[`04-jewelry-domain/042-ring-taxonomy.md`](../04-jewelry-domain/042-ring-taxonomy.md)'s
explicit warning against conflating it with a structural category.

**Halo** — a ring style where a center stone is surrounded by a ring of
smaller accent stones. **Not implemented** (requires multi-stone
arrangement support the current schema does not have) — see
[`04-jewelry-domain/042-ring-taxonomy.md`](../04-jewelry-domain/042-ring-taxonomy.md).

**Bezel** — a setting type where the stone is fully or partially
encircled by a continuous metal rim, with no discrete prongs. **Not
implemented.** See
[`04-jewelry-domain/047-setting-domain.md`](../04-jewelry-domain/047-setting-domain.md).

**Channel setting** — a setting type where stones are held between two
parallel metal walls, typically in a row. **Not implemented.** See
[`04-jewelry-domain/047-setting-domain.md`](../04-jewelry-domain/047-setting-domain.md).

**Prong** — one of the metal claws (four or six, in this project) that
grip the stone reference. Modeled here as plain cylinders — see
`docs/known-limitations.md` and
[`04-jewelry-domain/048-prong-domain.md`](../04-jewelry-domain/048-prong-domain.md)
for what this does not represent (tapered or hand-finished prong
shaping, a real bearing/seat cut).

**Basket** — the structural metal support connecting the prongs to the
band. Modeled here as a plain cylindrical shell, deliberately simple
rather than decorative — see
[`02-architecture/026-known-technical-limitations.md`](../02-architecture/026-known-technical-limitations.md)
and
[`04-jewelry-domain/049-basket-and-support-domain.md`](../04-jewelry-domain/049-basket-and-support-domain.md).

**Lost-wax casting** — a traditional jewelry manufacturing method (a wax
model is cast, then used to form a mold for metal casting). Used in this
project as a `manufacturing.method` value affecting validation context,
not as a simulated physical process. See
[`04-jewelry-domain/051-manufacturing-context.md`](../04-jewelry-domain/051-manufacturing-context.md).

**(Direct) resin printing** — a manufacturing method using 3D-printed
resin patterns instead of hand-carved wax. Selecting this method in
JewelMind triggers `JM-MANUFACTURING-001`, an extra minimum-feature-size
warning, because printed features below a certain size may not resolve
reliably. See
[`04-jewelry-domain/051-manufacturing-context.md`](../04-jewelry-domain/051-manufacturing-context.md).

**Manufacturing review** — the mandatory human step, by a qualified
jewelry professional, required before any JewelMind output is used for
actual production. See [LAW-010](004-jewelmind-constitution.md) and
[`04-jewelry-domain/058-professional-validation-register.md`](../04-jewelry-domain/058-professional-validation-register.md).

**Preliminary software rule** — a validation rule or geometric constant
that is currently implemented for prototype safety or consistency, but
has not been reviewed and accepted by a qualified jewelry professional.
See
[`04-jewelry-domain/040-domain-governance.md`](../04-jewelry-domain/040-domain-governance.md).
As of Sprint 2, every numeric jewelry rule in this repository is, at
most, a preliminary software rule.

**Professionally validated rule** — a rule reviewed and accepted by an
identified, named jewelry professional through the process in
[`04-jewelry-domain/058-professional-validation-register.md`](../04-jewelry-domain/058-professional-validation-register.md).
None exist yet.

## Application-specific terms

**Validation error** — a `ValidationResult` with `severity: "error"`;
blocks generation and export until fixed.

**Validation warning** — a `ValidationResult` with `severity: "warning"`
(or `"information"`); shown to the user but never blocks anything.

**Stale model** — a generated model whose underlying `JewelryDefinition`
has since been edited; the frontend marks it stale and disables export
until the model is regenerated.

**Model ID** — the identifier returned by `/api/models/generate`, equal
to the definition hash (see below) — the same input always produces the
same model ID.

**Definition hash** — a SHA-256 hash (truncated to 16 hex characters) of
the canonical definition JSON, used as the model's cache key and identity.

## JDL terms (Sprint 3)

> Authoritative source for every term in this section:
> [`05-jdl/`](../05-jdl/README.md) (Sprint 3).

**JDL (Jewelry Definition Language)** — the language and semantic contract
governing how a piece of jewelry is expressed as data, independent of
which representation carries it. See [`05-jdl/061-language-overview.md`](../05-jdl/061-language-overview.md).

**JDL Canonical Document** — the normative, normalized in-memory result of
parsing and default-filling a Canonical JSON document — today, exactly a
`JewelryDefinition` instance. See
[`05-jdl/064-canonical-document-model.md`](../05-jdl/064-canonical-document-model.md).

**Canonical JSON** — the only NORMATIVE JDL representation today; the JSON
shape the running API actually accepts and produces. See
[`05-jdl/065-canonical-json-serialization.md`](../05-jdl/065-canonical-json-serialization.md).

**Textual JDL DSL** — a PLANNED, non-normative human-authored syntax for
JDL documents. No parser exists. See
[`05-jdl/067-textual-dsl-overview.md`](../05-jdl/067-textual-dsl-overview.md)
and [`specs/jdl/v1/jdl.ebnf`](../../../specs/jdl/v1/jdl.ebnf).

**Structural validation** — the JSON-Schema-equivalent layer that checks
types, literal/enum membership, and unknown-field rejection, deliberately
kept separate from semantic/business-rule validation. See
[`05-jdl/075-validation-pipeline.md`](../05-jdl/075-validation-pipeline.md).

**Conformance level** — one of `JDL-READER`, `JDL-VALIDATOR`,
`JDL-COMPILER`, `JDL-EXPORTER`, `JDL-FULL-V1`, describing how much of the
JDL pipeline an implementation supports. See
[`05-jdl/085-conformance-and-test-vectors.md`](../05-jdl/085-conformance-and-test-vectors.md).

## Forge terms (Sprint 4)

> Authoritative source for every term in this section:
> [`06-forge/`](../06-forge/README.md) (Sprint 4).

**Forge** — the authoritative rule system for jewelry-domain rules: a
specification and classification layer over the existing validation
engine (`backend/jewelmind/validation/`), covering schema integrity,
semantic compatibility, domain invariants, geometry preconditions,
geometry inspection, prototype heuristics, manufacturing context, export
preconditions, and (in the future) professionally validated rules. See
[`06-forge/091-rule-system-overview.md`](../06-forge/091-rule-system-overview.md).

**ForgeRule** — the normative model of one rule: ID, category, stage,
severity, blocking scope, condition, target fields, provenance,
professional-validation status, applicability, and version. See
[`06-forge/092-rule-anatomy.md`](../06-forge/092-rule-anatomy.md).

**Rule provenance** — where a rule's justification comes from: an
implementation necessity, a mathematical/geometric constraint, a
prototype heuristic, or (not yet used by any current rule) a professional
review or published reference. See
[`06-forge/094-rule-provenance-model.md`](../06-forge/094-rule-provenance-model.md).

**Rule lifecycle** — the 8-state progression a rule moves through:
`PROPOSED`, `EXPERIMENTAL`, `PRELIMINARY`, `UNDER_REVIEW`, `VALIDATED`,
`ACCEPTED`, `DEPRECATED`, `REJECTED`. See
[`06-forge/095-rule-lifecycle.md`](../06-forge/095-rule-lifecycle.md).

**Blocking scope** — which workflow(s) a rule can block if it fires:
`NONE`, `GENERATION`, `PREVIEW`, `STEP_EXPORT`, `STL_EXPORT`,
`ALL_EXPORTS`, or `WORKFLOW` — a separate axis from severity. See
[`06-forge/099-severity-and-blocking-semantics.md`](../06-forge/099-severity-and-blocking-semantics.md).

## Atlas terms (Sprint 5)

> Authoritative source for every term in this section:
> [`07-atlas/`](../07-atlas/README.md) (Sprint 5).

**Atlas** — the deterministic geometry layer: a specification and
classification layer over the CadQuery/OpenCascade code in
`backend/jewelmind/geometry/`. Atlas owns primitives, transformations,
coordinate systems, topology, construction operations, component
geometry, geometric metadata, and geometric inspection — never
jewelry-domain thresholds. See
[`07-atlas/121-atlas-architecture-overview.md`](../07-atlas/121-atlas-architecture-overview.md).

**Geometric fact** — a measurable property Atlas can report (a volume, a
solid count, a bounding box) — never a jewelry-domain or manufacturing
verdict. Only Forge may interpret a geometric fact as a rule violation.
See
[`07-atlas/140-geometry-inspection-framework.md`](../07-atlas/140-geometry-inspection-framework.md).

**AtlasGeometryComponent** — the normative model of one named
solid/compound: role, source JDL paths, derived parameters, bounding
box, volume, generation status, warnings, fallback usage. See
[`07-atlas/130-component-contract.md`](../07-atlas/130-component-contract.md).

**Assembly anchor axis** — the vertical line `x=0, y=0`, parallel to
global Z, starting at `z=band_top_z`, around which the stone reference,
prongs, and basket support are all positioned. See
[`07-atlas/123-coordinate-system-and-orientation.md`](../07-atlas/123-coordinate-system-and-orientation.md).

**B-Rep vs. mesh** — B-Rep (Boundary Representation) is the exact,
parametric source geometry every component builder constructs; a mesh
(used only for preview and STL export) is a derived, lossy
approximation that must never become the source of B-Rep truth. See
[`07-atlas/129-mesh-model.md`](../07-atlas/129-mesh-model.md).

## Alchemist terms (Sprint 6)

> Authoritative source for every term in this section:
> [`08-alchemist/`](../08-alchemist/README.md) (Sprint 6).

**Alchemist** — the compilation orchestration layer: the translation
from validated JDL and Forge evaluation into a deterministic
`GeometryPlan`, Atlas execution, and an artifact manifest. Alchemist
coordinates the pipeline and preserves traceability; it owns no
jewelry-domain thresholds, no CAD-kernel algorithms, and no artifact
serialization details. See
[`08-alchemist/161-compiler-architecture-overview.md`](../08-alchemist/161-compiler-architecture-overview.md).

**GeometryPlan** — a deterministic intermediate representation between
a valid JDL Canonical Document and Atlas execution: derived, not
user-authored, not a CAD file, not JDL itself. **PLANNED — no such
object exists in the current backend**; `build_solitaire_ring()` still
computes and consumes derived values inline. See
[`08-alchemist/166-geometry-plan-model.md`](../08-alchemist/166-geometry-plan-model.md).

**CompilationResult** — the conceptual full output of a compilation:
status, version fingerprints, the normalized definition, Forge
evaluation, geometry metadata, diagnostics, artifacts, and timings.
Partially mapped to the real `GenerateResponse`/`ModelMetadataResponse`
today, with several fields (`compilationId`, `compilationHash`,
`kernelVersion`) still PLANNED. See
[`08-alchemist/171-compilation-result-model.md`](../08-alchemist/171-compilation-result-model.md).

**Compilation hash** — a PROPOSED (not implemented) identifier
combining `definitionHash` with compiler/generator/rule-set version, so
a version change can be detected even when design intent is unchanged.
Additive to, never replacing, the existing `definitionHash`. See
[`08-alchemist/175-definition-hash-vs-compilation-hash.md`](../08-alchemist/175-definition-hash-vs-compilation-hash.md).

**Vision** — the visual-output layer, named since Sprint 6's
architecture and formalized as its own Bible section in Sprint 8 — see
the "Vision terms (Sprint 8)" section below.

## Foundry terms (Sprint 7)

> Authoritative source for every term in this section:
> [`09-foundry/`](../09-foundry/README.md) (Sprint 7).

**Foundry** — the artifact-generation and export-integrity layer: the
boundary between a validated, compiled model and a file the outside
world can open (STEP, STL, canonical JDL JSON, or a technical
specification). Unlike Alchemist, Foundry formalizes an export system
that already runs in production. See
[`09-foundry/191-foundry-architecture-overview.md`](../09-foundry/191-foundry-architecture-overview.md).

**Artifact record** — a per-artifact result (filename, MIME type, byte
size, checksum, integrity status, and more). **PARTIAL** — checksum and
byte size are real for STEP/STL as of Sprint 7; most other fields are
PLANNED, with no single object assembling them together yet. See
[`09-foundry/201-artifact-manifest-model.md`](../09-foundry/201-artifact-manifest-model.md).

**Artifact integrity level** — one of 8 conceptual validation depths,
from file existence through geometric roundtrip validation. Only 3
(file existence, non-zero size, checksum) run for every real export
request today. See
[`09-foundry/202-artifact-integrity-model.md`](../09-foundry/202-artifact-integrity-model.md).

**Export version fingerprint** — a conceptual record of every
tool/library version that influenced a given export (CadQuery,
OpenCascade, tessellation tolerances). **PLANNED** — every individual
field is independently queryable today, but none is assembled together.
See
[`09-foundry/208-export-version-fingerprint.md`](../09-foundry/208-export-version-fingerprint.md).

## Vision terms (Sprint 8)

> Authoritative source for every term in this section:
> [`10-vision/`](../10-vision/README.md) (Sprint 8).

**Vision** — the visual-output layer: the boundary between an
already-generated Atlas geometry and what a person actually sees,
across two views (Technical and Presentation) that consume the same
mesh data. Unlike Foundry, Vision v1 both formalizes architecture and
ships new, user-visible functionality in the same Sprint. See
[`10-vision/221-vision-architecture-overview.md`](../10-vision/221-vision-architecture-overview.md).

**Technical View** — the inspection-oriented Vision mode: orbit/zoom,
bounding-box-driven camera presets, component visibility, and a
flatter, non-reflective material rendering that still follows the
JDL-selected metal color. See
[`10-vision/227-technical-view-contract.md`](../10-vision/227-technical-view-contract.md).

**Presentation View** (also "Presentation Rendering") — the
display-oriented Vision mode: full PBR metal materials, a transmissive
StoneReference material, studio lighting, a procedural environment, and
contact-shadow grounding. Never described as photorealistic,
cinematic, or path-traced — it is real-time WebGL rasterization. See
[`10-vision/228-presentation-view-contract.md`](../10-vision/228-presentation-view-contract.md).

**Geometry role** (Vision-facing) — an explicit per-component field
(`production_metal` or `stone_reference`) added to the preview manifest
in Sprint 8, so Vision never has to infer a component's material
category by string-matching its name. See
[`10-vision/223-atlas-to-vision-contract.md`](../10-vision/223-atlas-to-vision-contract.md).

**Visual consistency contract** — the guarantee that the object shown
in Vision is derived from the same generated geometry used for
exports, decomposed into 5 levels (`GEOMETRY_SOURCE_CONSISTENT`,
`COMPONENT_SET_CONSISTENT`, `SCALE_CONSISTENT`,
`MATERIAL_METADATA_CONSISTENT`, `CAMERA_ONLY_TRANSFORMATION`). See
[`10-vision/244-visual-consistency-contract.md`](../10-vision/244-visual-consistency-contract.md).

## Studio terms (Sprint 9)

> Authoritative source for every term in this section:
> [`11-studio/`](../11-studio/README.md) (Sprint 9).

**Studio** — the product-workspace layer: it owns end-to-end user
workflow (input → validation → generation → review → output) around
JDL/Forge/Alchemist/Atlas/Foundry/Vision, but owns none of their
underlying rules, geometry, or rendering. See
[`11-studio/251-product-workspace-overview.md`](../11-studio/251-product-workspace-overview.md).

**Model state** — the 7-value lifecycle status of the currently
generated model (`NO_MODEL`, `GENERATING_FIRST_MODEL`, `CURRENT`,
`STALE`, `REGENERATING`, `FAILED_NO_MODEL`, `FAILED_WITH_LAST_GOOD`),
computed by `computeModelState()` and shown identically by the header's
`ModelStatusBadge` and the in-viewport banner. See
[`11-studio/259-model-state-experience.md`](../11-studio/259-model-state-experience.md).

**Output eligibility** — the 5-value availability state
(`AVAILABLE`, `UNAVAILABLE`, `EXPORTING`, `FAILED`, `STALE_BLOCKED`) of
one artifact in the consolidated Outputs area, computed by
`computeOutputEligibility()` and shared identically across STEP, STL,
JDL JSON, the technical specification, and the Presentation PNG. See
[`11-studio/261-export-experience.md`](../11-studio/261-export-experience.md).

**Advanced / technical parameters** — the collapsed-by-default group of
design-editor fields (exact inner diameter, stone depth, prong/basket
dimensions, preview tessellation tolerances) that refine an
already-made design decision rather than represent a first choice. See
[`11-studio/256-parameter-editor-model.md`](../11-studio/256-parameter-editor-model.md).

## Designer terms (Sprint 10)

> Authoritative source for every term in this section:
> [`12-designer/`](../12-designer/README.md) (Sprint 10).

**Designer** — the first controlled natural-language design layer: a
user describes a design or a change to one, in Italian or English, and
receives a structured, reviewable `DesignerProposal`. Designer sits
upstream of every existing layer and is authoritative over none of
them — it never bypasses JDL schema validation or Forge evaluation and
never writes to the authoritative design state itself. See
[`12-designer/README.md`](../12-designer/README.md).

**Design Proposal** — the structured, reviewable result of one
Designer interpretation (`DesignerProposal` in
`backend/jewelmind/designer/schemas.py`): proposed fields, unsupported
features, clarification questions, diagnostics, a candidate JDL, a
Forge evaluation, a diff, and an overall proposal status. Never applied
to `currentDefinition` automatically — only an explicit user action
does that. See
[`12-designer/294-design-proposal-model.md`](../12-designer/294-design-proposal-model.md).

**Field Provenance** — the required, non-optional tag on every
`ProposedField` recording where its value came from (e.g.
`AI_INTERPRETATION`); part of the 8-value `FieldProvenance` enum. See
[`12-designer/303-field-provenance-model.md`](../12-designer/303-field-provenance-model.md).

**Confidence Category** — a `ProposedField`'s confidence in its own
proposed value (`EXACT`, `NORMALIZED`, `INFERRED`, `DEFAULTED`,
`AMBIGUOUS`, `UNSUPPORTED`), derived entirely by JewelMind's own
deterministic code from provenance/normalization facts — never a raw
score read from an AI provider. See
[`12-designer/302-confidence-model.md`](../12-designer/302-confidence-model.md).

**Ambiguity Level** — how much a `ClarificationQuestion` matters to
design intent (`LOW_IMPACT_AMBIGUITY`, `HIGH_IMPACT_AMBIGUITY`,
`UNSUPPORTED_AMBIGUITY`) — a bare, recognized-but-incomplete reference
like "gold"/"oro" always triggers clarification rather than a guessed
value. See
[`12-designer/299-ambiguity-model.md`](../12-designer/299-ambiguity-model.md).

**Unsupported Feature** — a requested concept that has no mapping in
the current JDL schema or geometry (e.g. a halo setting, an oval
stone), surfaced explicitly on the proposal rather than approximated as
supported or silently dropped. See
[`12-designer/301-unsupported-request-handling.md`](../12-designer/301-unsupported-request-handling.md).

**Clarification Question** — a question Designer must ask the user
before a request can be resolved into a proposed field, because the
request is ambiguous or under-specified in a way that materially
affects design intent. See
[`12-designer/300-clarification-policy.md`](../12-designer/300-clarification-policy.md).

## Design Intent terms (Sprint 11)

> Authoritative source for every term in this section:
> [`13-design-intent/`](../13-design-intent/README.md) (Sprint 11).

**Design Intent** — the formal semantic layer between subjective
aesthetic language ("delicate", "minimal", "classic", "bold") and
JewelMind's deterministic `JewelryDefinition` (`DesignIntent` in
`backend/jewelmind/design_intent/schemas.py`). Subjective language may
be structured, stored, and reviewed without ever being numerically
resolved — Design Intent sits between Designer and JDL and has zero
authority to bypass either. See
[`13-design-intent/README.md`](../13-design-intent/README.md).

**Intent Statement** — one recognized aesthetic descriptor
(`IntentStatement`): a target, a concept category, a value on that
concept's continuum, a strength, a provenance, a confidence class, and
a resolution status. Never carries a numeric geometry value —
`relatedJDLPaths` is always empty in v1. See
[`13-design-intent/332-intent-domain-model.md`](../13-design-intent/332-intent-domain-model.md).

**Intent Relation** — a relative (not absolute-numeric) statement
between two `IntentTarget`s (`IntentRelation`), e.g. "the band should
look narrower than the stone" (`BAND NARROWER_THAN STONE`). See
[`13-design-intent/332-intent-domain-model.md`](../13-design-intent/332-intent-domain-model.md).

**Concept Category** — one of the 6 controlled semantic axes an intent
statement can target (`VISUAL_WEIGHT`, `SIMPLICITY`,
`STYLE_TEMPORALITY`, `VISUAL_EMPHASIS`, `PROPORTIONAL_CHARACTER`,
`STRUCTURAL_CHARACTER`), each an ordered continuum of canonical values,
never a numeric score. See
[`13-design-intent/333-intent-vocabulary.md`](../13-design-intent/333-intent-vocabulary.md).

**Style Continuum** — the ordered sequence of canonical values within
one concept category (e.g. `DELICATE` -> `LIGHT` -> `BALANCED` ->
`SUBSTANTIAL` -> `BOLD` for `VISUAL_WEIGHT`), used to measure relative
distance between two statements on the same axis without ever assigning
a millimeter or numeric value to either end. See
[`13-design-intent/338-style-continuum-model.md`](../13-design-intent/338-style-continuum-model.md).

**Intent Conflict** — a detected tension or contradiction between two
intent statements or relations (`IntentConflict`), always recorded and
surfaced, never silently rejected, and never blocking a proposal from
being returned. See
[`13-design-intent/346-intent-conflict-model.md`](../13-design-intent/346-intent-conflict-model.md).

**Deterministic Resolution Policy** — the rule that only an explicit,
deterministic, versioned, and reviewed intent-to-JDL mapping may ever
automatically influence a JDL field; v1 registers zero such mappings,
which is the deliberately correct, safe state, not an unfinished
feature. See
[`13-design-intent/349-deterministic-resolution-policy.md`](../13-design-intent/349-deterministic-resolution-policy.md).
