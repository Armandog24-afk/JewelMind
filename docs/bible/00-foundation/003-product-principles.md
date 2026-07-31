---
id: JM-BIBLE-003
title: Product Principles
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on:
  - JM-BIBLE-002
related_documents:
  - JM-BIBLE-004
implementation_status: current
---

# Product Principles

These twelve principles explain *why* JewelMind is built the way it is.
Where a principle is enforced by a specific, non-negotiable rule, that
rule is codified as a LAW in
[`004-jewelmind-constitution.md`](004-jewelmind-constitution.md) — this
document explains the reasoning; the Constitution enforces it.

## 1. Everything important is parametric

**Meaning:** every dimension that affects the geometry or the validation
outcome is a named, typed field in the canonical `JewelryDefinition`
(`shared/types/jewelry-definition.ts`), never a hardcoded constant chosen
per-case.

**Practical consequence:** adding a new adjustable dimension means adding
a schema field, a default, and (if it has a business rule) a validation
rule — not a special case in the geometry code.

**Example:** band width, thickness, and profile are all fields; there is
no "small/medium/large band" preset baked into the geometry builder.

**Prohibited violation:** a geometry function that reads an unlisted
constant (e.g. a fixed fillet radius that should have been a parameter)
instead of a definition field, when that value should vary by design.

## 2. The same definition must produce reproducible results

**Meaning:** given the same `JewelryDefinition`, the system must produce
the same outcome, every time, on every machine.

**Practical consequence:** no part of the pipeline may depend on
wall-clock time, random seeds, or ambient global state for anything that
affects the geometry or its metadata.

**Example:** `definitionHash` (`backend/jewelmind/utils/hashing.py`) is a
SHA-256 of the canonical JSON — the same input always yields the same
hash and the same cached model.

**Prohibited violation:** introducing `random.random()`, an uncached
`datetime.now()` in geometry-affecting logic, or any network call into the
geometry pipeline (see [LAW-003](004-jewelmind-constitution.md) and
[ADR-003](../03-decisions/ADR-003-deterministic-geometry.md)).

## 3. Geometry generation is deterministic

**Meaning:** distinct from principle 2 — this is specifically about *how*
geometry is produced: through fixed, testable CadQuery code paths, not
through a model that can vary its output for the same input.

**Practical consequence:** geometry code is unit-testable with exact
volume/bounding-box assertions (`backend/tests/test_geometry.py`).

**Example:** `build_ring_band()` for a `flat` profile always constructs
the same rectangular revolve for the same width/thickness/inner-diameter.

**Prohibited violation:** any geometry function whose output cannot be
predicted from its inputs alone.

## 4. Artificial intelligence must not be the source of geometric truth

**Meaning:** an LLM may be used to *write* code (as in this project's own
development), but the *running application* must never call an LLM to
decide a dimension, a shape, or a placement at request time.

**Practical consequence:** there is no LLM API call anywhere in
`backend/jewelmind/` or `frontend/src/` at runtime, and there must never
be one for geometry decisions.

**Example:** stone crown/pavilion proportions are fixed constants in
`geometry/components/stone.py`, not model-generated.

**Prohibited violation:** calling any AI model to determine a dimension,
even "just to suggest a default," inside the request-time geometry path.
Enforced by [LAW-003](004-jewelmind-constitution.md).

## 5. Validation rules must be explicit and testable

**Meaning:** every business rule has a stable ID, a single authoritative
implementation, and a dedicated test.

**Practical consequence:** `docs/validation-rules.md` is a complete,
literal list of every rule; there is no "soft" validation logic that
exists only as a comment or a UI hint.

**Example:** `JM-BAND-001` through `JM-GEOMETRY-001` — sixteen rules, each
with a `ruleId`, a severity, and a backend test in
`backend/tests/test_validation.py`.

**Prohibited violation:** a numeric threshold embedded in a React
component with no corresponding `ruleId` (see principle 6 and
[LAW-004](004-jewelmind-constitution.md)).

## 6. The backend is authoritative for generation and export

**Meaning:** the frontend's validation mirror
(`shared/validation/engine.ts`) exists purely for instant UI feedback. The
backend always re-validates before generating or exporting anything, and
its verdict wins if the two ever disagree.

**Practical consequence:** every generate/export endpoint independently
re-checks the definition; the frontend cannot bypass this by lying about
its own validation state.

**Example:** `POST /api/models/generate` runs
`validation.engine.validate_definition()` itself and rejects with
`VALIDATION_BLOCKED` regardless of what the client believed.

**Prohibited violation:** an export endpoint that trusts a
client-supplied "this is valid" flag instead of re-validating.

## 7. The stone reference remains distinct from production metal

**Meaning:** the stone is a visual/dimensional reference solid, never
unioned into the metal body, never exported unless explicitly requested.

**Practical consequence:** `combined_metal` (band + prongs + basket) and
`stone_reference` are always separate objects in
`GeneratedModel.components`, and the stone is excluded from STEP/STL
exports by default (`includeStoneReference: false`).

**Example:** `backend/tests/test_geometry.py::test_stone_reference_is_valid_and_separate_from_metal`.

**Prohibited violation:** any boolean union that merges stone geometry
into the metal solid before export. Enforced by
[LAW-006](004-jewelmind-constitution.md).

## 8. Commercial CAD software must not be required for the MVP

**Meaning:** the whole pipeline must run headlessly with free, open
tooling — no Rhino, MatrixGold, JewelCAD, or interactive FreeCAD.

**Practical consequence:** the only CAD dependency is `pip install
cadquery`, which ships prebuilt OpenCascade wheels (verified directly —
see `docs/development.md`).

**Example:** `backend/requirements.txt` lists `cadquery`, nothing else CAD-
related.

**Prohibited violation:** adding a dependency that requires a licensed
desktop CAD application to be running. Enforced by
[LAW-... see Constitution intro](004-jewelmind-constitution.md) and
[ADR-002](../03-decisions/ADR-002-no-rhino-runtime-dependency.md).

## 9. Neutral export formats are strategic

**Meaning:** STEP and STL are chosen because they are vendor-neutral and
importable by essentially every downstream CAD/manufacturing tool,
deliberately avoiding lock-in to one CAD vendor's native format.

**Practical consequence:** no native Rhino (`.3dm`) or MatrixGold export
exists or is planned for the MVP.

**Example:** `backend/jewelmind/exporters/step_exporter.py`,
`stl_exporter.py`.

**Prohibited violation:** treating a vendor-native export as a
requirement for a professional to be able to use JewelMind's output.

## 10. Professional manufacturing review is mandatory

**Meaning:** every export and every technical specification states, in
the same wording, that the model is preliminary and requires review by a
qualified jewelry professional before production.

**Practical consequence:** the disclaimer text lives in exactly one place
per language layer (`shared/disclaimer.ts`,
`backend/jewelmind/domain/disclaimer.py`) and is never optional or
removable from the UI or the specification output.

**Example:** `ProfessionalReviewNotice.tsx` renders it permanently in the
header; `exporters/specification.py` includes it in every specification.

**Prohibited violation:** any code path that produces an export or a UI
state where this notice is absent. Enforced by
[LAW-010](004-jewelmind-constitution.md).

## 11. Current functionality must never be confused with future vision

**Meaning:** see [`000-bible-governance.md`](000-bible-governance.md)'s
CURRENT/PARTIAL/PLANNED/VISION rule — this principle is why that rule
exists.

**Practical consequence:** this Bible, the README, and all in-app text
distinguish what works today from what is aspirational.

**Example:** [`002-vision-and-mission.md`](002-vision-and-mission.md) is
marked `source_of_truth: false` precisely so it can never be mistaken for
a claim about the current product.

**Prohibited violation:** writing "JewelMind supports X" anywhere when X
is actually planned or vision. Enforced by
[LAW-012](004-jewelmind-constitution.md).

## 12. Every architectural change must be documented

**Meaning:** a decision that changes the shape of the system belongs in
an ADR, not only in a commit message.

**Practical consequence:** see "When an ADR is required" in
[`000-bible-governance.md`](000-bible-governance.md).

**Example:** the ten ADRs in [`03-decisions/`](../03-decisions/) capture
the reasoning behind CadQuery, determinism, backend authority, the
canonical definition, the metal/stone separation, the backend-generated
preview, the monorepo shape, the millimeter convention, and the STEP/STL
export strategy.

**Prohibited violation:** merging a change that meets one of the "ADR
required" conditions without the ADR. Enforced by
[LAW-011](004-jewelmind-constitution.md).
