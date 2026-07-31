---
id: JM-BIBLE-004
title: JewelMind Constitution
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on:
  - JM-BIBLE-003
related_documents:
  - JM-BIBLE-000
  - JM-BIBLE-005
implementation_status: current
---

# JewelMind Constitution

These are **laws**, not guidelines. Future agents and developers must not
violate any law below without first writing and accepting an ADR (see
[`000-bible-governance.md`](000-bible-governance.md), "When an ADR is
required"). Each law states its enforcement mechanism — where that
mechanism is a test, the law is currently checked automatically; where it
is "code review" or "this document," it currently relies on a human or
agent reading and following it.

## LAW-001 — No fake CAD exports

**Rule:** STEP and STL exports must always be real CadQuery/OpenCascade
output written to disk and streamed back — never a placeholder file, a
stub byte string, or a hardcoded sample file.

**Rationale:** a fake export would look identical to a real one to a
non-technical user until they tried to open it in real CAD software,
destroying trust at the worst possible moment.

**Compliant example:** `backend/jewelmind/exporters/step_exporter.py`
calls `shape.exportStep(str(destination))` on a real `cq.Shape` built by
`build_solitaire_ring()`.

**Violation example:** returning a hardcoded `.step` file from disk
regardless of the requested definition, or writing an empty file when
export "succeeds."

**Enforcement:** `backend/tests/test_api.py::test_export_step_returns_nonempty_file`
and `test_export_stl_returns_nonempty_file` assert real, non-empty output.
Also stated in the root `CLAUDE.md`.

## LAW-002 — No fake preview disconnected from backend geometry

**Rule:** the browser preview must always be derived from backend-generated
geometry — never a generic Three.js primitive standing in for the real
model.

**Rationale:** a "preview" that isn't the real geometry would mislead the
user about what they are about to export.

**Compliant example:** `useComponentGeometries.ts` fetches and parses the
actual STL bytes the backend tessellated from the real solid.

**Violation example:** rendering a generic `<torusGeometry>` sized
approximately like a ring instead of loading the real mesh.

**Enforcement:** `backend/tests/test_api.py::test_preview_component_endpoint_returns_nonempty_stl`;
code review of `ModelViewport.tsx` / `useComponentGeometries.ts`.

## LAW-003 — No runtime LLM dependency for deterministic geometry generation

**Rule:** the running application must never call an LLM (or any
non-deterministic model) to decide a dimension, shape, or placement.

**Rationale:** see Product Principle 4 — determinism is the whole point
of using a CAD kernel instead of a generative model for geometry.

**Compliant example:** all dimensions in `geometry/components/*.py` come
from the `JewelryDefinition` or from fixed constants.

**Violation example:** calling any AI API from
`backend/jewelmind/geometry/` or `backend/jewelmind/services/` at request
time.

**Enforcement:** code review; absence of any AI SDK dependency in
`backend/requirements.txt`; [ADR-003](../03-decisions/ADR-003-deterministic-geometry.md).

## LAW-004 — No jewelry-domain rules hidden inside UI components

**Rule:** every numeric or business threshold must live in
`backend/jewelmind/validation/` (authoritative) and its mirror
`shared/validation/` (frontend feedback only), referenced by a `ruleId` —
never written directly into a React component.

**Rationale:** a rule duplicated ad hoc in the UI drifts from the backend
rule and cannot be tested once, centrally.

**Compliant example:** `ConfigurationPanel.tsx` has no numeric
thresholds; all sixteen rules live in `validation/engine.py` and
`shared/validation/engine.ts`, both keyed by the same `ruleId` constants.

**Violation example:** `if (width < 1.5) setError('too thin')` written
directly inside a form component instead of relying on `JM-BAND-001`.

**Enforcement:** code review; `docs/validation-rules.md` is the complete
list — any threshold not found there and found in a component is a
violation.

## LAW-005 — No geometry operation may silently discard required components

**Rule:** if a boolean operation (e.g. fusing band + prongs + basket)
fails, the system must fall back to a still-valid, still-complete
representation (e.g. a multi-solid compound) — never drop a component
because combining it was hard.

**Rationale:** a "successful" export missing a prong because a fuse
failed silently is worse than a visibly different result.

**Compliant example:** `geometry/assemblies/solitaire.py::_fuse_metal`
falls back to `cq.Compound.makeCompound([band, basket, prongs])` and
records a warning if `fuse()` raises, rather than exporting only the
pieces that fused.

**Violation example:** catching a fuse exception and returning only the
band, discarding prongs/basket.

**Enforcement:** `backend/tests/test_geometry.py::test_solitaire_assembly_has_all_required_components`;
warnings surface in `GeneratedModel.warnings` and the specification export.

## LAW-006 — The stone reference must not accidentally become production metal

**Rule:** the stone solid must never be unioned into the metal body, and
must never appear in a STEP/STL export unless `includeStoneReference:
true` was explicitly requested.

**Rationale:** see Product Principle 7 — conflating a dimensional
reference with the metal to be manufactured would produce a physically
wrong (uncastable) object.

**Compliant example:** `combined_metal` in `GeneratedModel` never includes
`stone_reference`; both exporters take `include_stone: bool = False`.

**Violation example:** any code path that fuses or includes the stone
solid in the default export.

**Enforcement:** `backend/tests/test_geometry.py::test_stone_reference_is_valid_and_separate_from_metal`;
`docs/known-limitations.md`.

## LAW-007 — All measurements use millimeters internally

**Rule:** every length field, everywhere in the system, is millimeters.
No unit field, no unit conversion, no alternate-unit code path.

**Rationale:** a mixed-unit system is a predictable source of silent,
catastrophic errors (a ring sized in the wrong unit is unwearable and
possibly unmanufacturable without anyone noticing until physical
production).

**Compliant example:** `project.units: 'mm'` is a fixed literal, not a
user choice, in both the Pydantic schema and the TypeScript type.

**Violation example:** adding an `inches` option anywhere, or a new length
field without documenting it as millimeters.

**Enforcement:** `docs/geometry-conventions.md`; schema-level
`Literal["mm"]`.

## LAW-008 — Invalid definitions cannot generate or export models

**Rule:** any definition with at least one `error`-severity validation
result must be rejected before geometry generation or export — not
merely warned about.

**Rationale:** generating geometry from parameters known to be invalid
(e.g. a negative band thickness) wastes computation at best and produces
degenerate/incorrect solids at worst.

**Compliant example:** `services/model_service.py::generate()` raises
`ValidationBlockedError` (HTTP 422) before calling `build_solitaire_ring()`
if `has_errors(results)` is true.

**Violation example:** generating geometry first and only checking
validation afterward, or allowing an export endpoint to skip
re-validation.

**Enforcement:** `backend/tests/test_api.py::test_generate_invalid_definition_returns_422`.

## LAW-009 — Warnings must be distinguishable from errors

**Rule:** the `ValidationResult.severity` field (`error | warning |
information`) must always be present and correctly categorized; only
`error` blocks generation/export.

**Rationale:** conflating "must fix" with "consider checking this" either
blocks users unnecessarily or lets real problems through unflagged.

**Compliant example:** `JM-BAND-003` (band width > 12mm) is `warning` and
does not block; `JM-BAND-001` (width < 1.5mm) is `error` and does.

**Violation example:** a rule that should be advisory implemented as an
`error`, or vice versa.

**Enforcement:** `backend/tests/test_validation.py::test_warnings_alone_do_not_block`;
`docs/validation-rules.md` table.

## LAW-010 — No claim of manufacturing readiness without professional verification

**Rule:** every export, every technical specification, and the
application's UI must state that generated models are preliminary and
require review by a qualified jewelry professional before production —
this wording must never be removed, softened, or made conditional.

**Rationale:** see Product Principle 10 and
[`002-vision-and-mission.md`](002-vision-and-mission.md)'s explicit
rejection of "production-ready" language.

**Compliant example:** `PROFESSIONAL_REVIEW_NOTICE` appears in the app
header, permanently, and in every specification export.

**Violation example:** an export mode or UI state that omits the notice.

**Enforcement:** `backend/tests/test_api.py::test_specification_export_contains_disclaimer`;
`ProfessionalReviewNotice.tsx` rendered unconditionally in `App.tsx`.

## LAW-011 — Tests and documentation must accompany architectural changes

**Rule:** a change matching any "ADR required" condition in
[`000-bible-governance.md`](000-bible-governance.md) must ship with its
ADR, its tests, and any Bible/`docs/` updates it makes necessary, in the
same change — not as a follow-up.

**Rationale:** documentation written "later" reliably does not get
written.

**Compliant example:** this Bible's own creation is documented as a Bible
milestone with governance rules defined before the ADRs that depend on
them.

**Violation example:** merging a schema-breaking change with a promise to
"document it next time."

**Enforcement:** code review; this document.

## LAW-012 — Current, planned, and visionary functionality must remain clearly separated

**Rule:** see [`000-bible-governance.md`](000-bible-governance.md)'s
CURRENT/PARTIAL/PLANNED/VISION classification — no document, UI text, or
external communication may describe planned or vision functionality using
present-tense "the system does X" language.

**Rationale:** see Product Principle 11 — this is the law most directly
protecting the founder, developers, and any partner from being misled
about what exists.

**Compliant example:** [`002-vision-and-mission.md`](002-vision-and-mission.md)
is marked `source_of_truth: false` and uses future/aspirational language
throughout.

**Violation example:** README or marketing text stating "JewelMind
supports pavé settings" when it does not.

**Enforcement:** this document; [`005-current-product-status.md`](005-current-product-status.md)
as the single implementation-matrix source of truth for status claims.
