---
id: JM-BIBLE-008
title: Glossary
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on: []
related_documents:
  - JM-BIBLE-001
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

**Band** — the ring's circular metal body, defined by width, thickness,
and profile (flat or comfort-fit). See
`docs/geometry-conventions.md`.

**Flat profile** — a band cross-section that is a plain rectangle
(optionally with a small outer-rim fillet).

**Comfort fit** — a band profile whose inner surface is a shallow curve
rather than flat, intended to feel rounder against the finger. *Note:*
this project's implementation is a simplified geometric approximation of
the concept, not a manufacturing-validated ergonomic profile.

**Stone reference** — a simplified geometric solid representing the
approximate size and position of the center stone, used for visualization
and clearance checking. *Note:* explicitly not a gemological reproduction
of a real cut stone — see [LAW-006](004-jewelmind-constitution.md) and
`docs/known-limitations.md`.

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

**Prong** — one of the metal claws (four or six, in this project) that
grip the stone reference. Modeled here as plain cylinders — see
`docs/known-limitations.md` for what this does not represent (tapered or
hand-finished prong shaping).

**Basket** — the structural metal support connecting the prongs to the
band. Modeled here as a plain cylindrical shell, deliberately simple
rather than decorative — see
[`02-architecture/026-known-technical-limitations.md`](../02-architecture/026-known-technical-limitations.md).

**Setting** — the mechanism holding the stone in place; this project
supports only prong settings.

**Lost-wax casting** — a traditional jewelry manufacturing method (a wax
model is cast, then used to form a mold for metal casting). Used in this
project as a `manufacturing.method` value affecting validation context,
not as a simulated physical process.

**(Direct) resin printing** — a manufacturing method using 3D-printed
resin patterns instead of hand-carved wax. Selecting this method in
JewelMind triggers `JM-MANUFACTURING-001`, an extra minimum-feature-size
warning, because printed features below a certain size may not resolve
reliably.

**Manufacturing review** — the mandatory human step, by a qualified
jewelry professional, required before any JewelMind output is used for
actual production. See [LAW-010](004-jewelmind-constitution.md).

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
