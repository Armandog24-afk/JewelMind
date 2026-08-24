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

**Foundry** — the artifact production/export layer (STEP, STL, JSON,
technical specification), named in this Sprint's architecture but not
yet formalized as its own Bible section — see Sprint 7.

**Vision** — the preview/rendering layer, named in this Sprint's
architecture but not yet formalized as its own Bible section.
