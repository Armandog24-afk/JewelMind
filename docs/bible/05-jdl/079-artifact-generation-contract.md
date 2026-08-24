---
id: JM-BIBLE-079
title: Artifact Generation Contract
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-078
related_documents:
  - JM-BIBLE-083
  - JM-BIBLE-178
implementation_status: current
professional_validation: not_required
normative: true
---

# Artifact Generation Contract

**No artifact produced by this pipeline may be described as manufacturing-ready** (LAW-010). Every specification export and the frontend's permanent header notice restate this; this contract does not weaken that requirement.

**Relationship to Alchemist (Sprint 6):** [`08-alchemist/177-artifact-request-model.md`](../08-alchemist/177-artifact-request-model.md)
and [`178-artifact-manifest-contract.md`](../08-alchemist/178-artifact-manifest-contract.md)
formalize this same artifact set as `ArtifactRequest`/`ArtifactManifest`
target shapes, confirming no unified manifest aggregating all artifact
types exists today — each remains a separate, independently-issued call.

**Relationship to Foundry (Sprint 7):** [`09-foundry/README.md`](../09-foundry/README.md)
formalizes this same table as the artifact-generation and
export-integrity layer, adding: real SHA-256 checksums and non-empty-file
validation for STEP/STL (new in Sprint 7, reflected in the STEP/STL rows
below), the finding that STEP checksums are not stable across repeated
exports of identical geometry while STL checksums are (see
[`09-foundry/197-step-export-contract.md`](../09-foundry/197-step-export-contract.md)),
and the discovery that `ExportFailedError` (intended for JSON/specification
export failures) is defined in `api/errors.py` but never actually raised
by either route (see [`09-foundry/204-export-diagnostics.md`](../09-foundry/204-export-diagnostics.md)).

| Artifact | Purpose | Source data | Inclusion/exclusion rule | MIME type | Extension | Naming | Deterministic? | Stone-inclusion default | Prerequisites | Known limitations |
|---|---|---|---|---|---|---|---|---|---|---|
| STEP | CAD interchange for downstream tools | `combined_metal` (+ stone if requested) | `includeStoneReference` (request param, default `false`) | `application/step` | `.step` | Sanitized project name via `sanitize_filename()`, unique temp path per request | Geometry: yes. Bytes: **no** — an embedded timestamp and OpenCascade translator-instance counter vary between repeated exports of identical geometry, confirmed in Sprint 7; see [`09-foundry/197-step-export-contract.md`](../09-foundry/197-step-export-contract.md) | Excluded by default (LAW-006) | Zero `error`-severity validation results | Boolean-fuse failures fall back to a multi-solid compound (see [`078-geometry-generation-contract.md`](078-geometry-generation-contract.md)) — the STEP file still contains real geometry, just not a single fused solid. As of Sprint 7, checksummed (SHA-256, `X-Content-SHA256` header) and validated non-empty before being returned |
| STL | Mesh export for 3D printing/preview tooling | Same, tessellated with `preview.meshTolerance`/`angularTolerance` (or request-supplied overrides) | Same `includeStoneReference` param | `model/stl` | `.stl` | Same pattern | Yes, byte-for-byte, confirmed in Sprint 7 | Excluded by default | Same | Mesh fidelity depends on the tolerance values supplied; no automatic mesh-quality certification exists. As of Sprint 7, checksummed and validated non-empty like STEP |
| JSON | Machine-readable export of the definition itself | The `JewelryDefinition` (via `export_json()`) | Always the full definition — the stone specification is metadata here, not a metal solid, so LAW-006 does not apply to this format | `application/json` | `.json` | Same pattern | Yes | n/a (not a geometry export) | None beyond a generated model existing | This is effectively a Canonical JSON round-trip, useful for verifying [`065-canonical-json-serialization.md`](065-canonical-json-serialization.md) by hand |
| Specification | Human-readable technical summary | Definition + `GeneratedModel` + validation results + `generated_at` | n/a | `text/markdown` | `.md` (served as `text/markdown`) | Same pattern | Yes, given a fixed `generated_at` (threaded through explicitly, not re-read at export time — see the hardening-sprint fix in `services/model_service.py::export_specification_text()`) | n/a | Same | Must always restate the manufacturing-readiness disclaimer (LAW-010); this is checked by `test_api.py` |
| Preview mesh (per component) | Fast in-browser 3D preview | Each `GeneratedComponent`, tessellated at generation time | Determined by `preview_manifest`; stone reference is previewed transparently and separately from metal components (LAW-006's UI half) | `model/stl` | `.stl` | `{component_name}.stl`, served from the model's temp directory | Yes | Included in preview (transparent gemstone-like material), never fused with metal preview meshes | A `ModelRecord` must exist for the requested `model_id` | Preview temp directories are capped at `MAX_CACHED_MODELS = 20` and evicted oldest-first; a preview file for an evicted model returns `ModelNotFoundError` |
| Model metadata (API response) | Volumes, bounding box, warnings, generator version | `GeneratedModel` fields | n/a | `application/json` (part of the generation API response) | n/a | n/a | Yes | Includes the stone's own metadata but never merges it into metal volume/bounding-box figures without being asked | A `ModelRecord` must exist | See [`078-geometry-generation-contract.md`](078-geometry-generation-contract.md) for the exact field set |
| Component manifest (`preview_manifest`) | Maps component name → preview file/status | `write_component_previews()` | n/a | n/a (internal structure, exposed via the preview endpoint) | n/a | n/a | Yes | n/a | A `ModelRecord` must exist | Does not yet carry the richer `productionInclusion`/`materialRole` fields discussed in [`078-geometry-generation-contract.md`](078-geometry-generation-contract.md) |

## Filename safety

Every export path runs through `exporters/filenames.py::sanitize_filename()`, which collapses any character outside `[A-Za-z0-9._-]` to an underscore, strips leading dots/dashes, and caps length at 120 characters — this is the concrete mechanism behind the "no path traversal via project names" claim in [`083-security-and-resource-limits.md`](083-security-and-resource-limits.md).

## Never a placeholder

Per CLAUDE.md, none of the above artifacts is ever a stub, a hardcoded sample, or a placeholder byte string. Where the ideal output (a single fused solid) cannot be produced, the documented fallback (a multi-solid compound, always real OpenCascade geometry) is used instead, with a warning — never nothing, and never fake data.
