---
id: JM-BIBLE-083
title: Security and Resource Limits
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-075
related_documents:
  - JM-BIBLE-025
implementation_status: current
professional_validation: not_required
normative: true
---

# Security and Resource Limits

This document states, for each risk category from untrusted JDL input, what the current code actually does — verified by inspection during this Sprint, not assumed. Several rows below are honestly reported as **gaps**, not silently treated as covered.

| Risk | Current status | Evidence |
|---|---|---|
| Oversized payload | **NOT MITIGATED** — no custom request body size limit exists in `backend/jewelmind/api/app.py` or anywhere else in the backend; FastAPI/Starlette/uvicorn apply no size cap by default either | Inspected `api/app.py`, `main.py`; no `Content-Length` guard or body-size middleware found |
| Deep nesting | **PARTIALLY MITIGATED** — `JewelryDefinition`'s fixed, non-recursive schema has a bounded nesting depth by construction (at most 2 levels: root → section → field); an attacker cannot submit arbitrarily deep JSON that Pydantic would still accept, because `extra="forbid"` rejects any unexpected nested object | `domain/schema.py` structure |
| Excessive string length | **PARTIALLY MITIGATED** — `project.name` has `max_length=200`; no other string field exists in the schema today | `domain/schema.py::ProjectInfo.name` |
| Extreme numeric values | **PARTIALLY MITIGATED** — `allow_inf_nan=False` blocks non-finite values on every float field; finite-but-extreme values (e.g. `band.width: 1e300`) are not structurally rejected, only caught downstream by semantic range rules (`JM-BAND-*`, etc.) if they fall outside the modeled range — a value like `1e300` for a field with no semantic ceiling would pass both layers | `domain/schema.py`, `validation/engine.py` |
| DoS via pathological geometry | **NOT SEPARATELY MITIGATED** — an extreme-but-schema-valid dimension could in principle produce an expensive or slow CadQuery/OCCT operation; no generation timeout exists in `services/model_service.py::generate()` | Inspected `model_service.py` |
| Excessive mesh tolerance requests | **PARTIALLY MITIGATED** — `preview.meshTolerance`/`angularTolerance` require `gt=0`, preventing a zero/negative tolerance (which could cause a pathological or infinite tessellation), but no upper bound exists on how small (expensive) a tolerance can be requested | `domain/schema.py::PreviewSpec` |
| Path traversal via project names | **MITIGATED** — every export filename passes through `exporters/filenames.py::sanitize_filename()`, which collapses any character outside `[A-Za-z0-9._-]` to `_`, strips leading dots/dashes, and caps length at 120 | `exporters/filenames.py` |
| Malicious YAML tags | **N/A today** — no YAML loader exists in the codebase; the restriction list in [`066-yaml-serialization-contract.md`](066-yaml-serialization-contract.md) is a requirement for if/when one is built | Repository-wide search found no `yaml`/`pyyaml` import |
| Textual-parser abuse | **N/A today** — no textual DSL parser exists | `specs/jdl/v1/jdl.ebnf` is grammar only |
| Duplicate keys | **Standard JSON behavior, not a JDL-specific mitigation** — Python's `json` module resolves a duplicate object key to the last value before Pydantic ever sees the data; this is not a vulnerability specific to JDL | Standard library behavior |
| Unsupported extensions | **MITIGATED by rejection** — `extra="forbid"` on every model means an unrecognized field is a hard validation error, never silently ignored or silently influential | `domain/schema.py::StrictModel` |
| Artifact-cache exhaustion | **MITIGATED** — `ModelService` caps cached models at `MAX_CACHED_MODELS = 20`, evicting the oldest entry (and deleting its temp directory) once the cap is exceeded; export temp files use unique per-request paths cleaned up via a `BackgroundTask` after the response is sent | `services/model_service.py` |
| Executable code in a document | **MITIGATED by design** — no field in the current schema, YAML contract, or DSL grammar accepts an expression, script, or function body (see [`062-design-goals-and-non-goals.md`](062-design-goals-and-non-goals.md) non-goal 1) | Schema/grammar inspection |
| Arbitrary external network references | **MITIGATED by design** — no URI-typed field exists (see [`070-type-system.md`](070-type-system.md)); nothing in the compiler fetches a remote resource | Schema inspection; `services/model_service.py` performs no outbound network calls |
| Arbitrary filesystem paths | **MITIGATED** — every temp file is created via `tempfile.mkdtemp()`/`tempfile.mkstemp()`, never from a user-supplied path | `services/model_service.py` |
| Secrets in JDL | **N/A** — no credential, token, or secret-shaped field exists anywhere in `JewelryDefinition` | Schema inspection |

## Honest summary

The strongest current protections are structural (`extra="forbid"`, `allow_inf_nan=False`, filename sanitization, a bounded cache). The weakest are **request-size limiting and generation-time resource bounding** — a sufficiently large or numerically extreme (but schema-valid) request could consume more memory or CPU than intended, with no current backstop beyond the semantic-range rules that happen to cover some (not all) fields. This is recorded here as a real gap for a future hardening sprint to address; it is not fixed in this documentation-only milestone.
