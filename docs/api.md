# API reference

Base URL (local/dev default): `http://localhost:8000`. Interactive OpenAPI
docs are always available at `/docs` (Swagger UI) and `/redoc` while the
backend is running.

All request/response bodies are JSON except the binary preview mesh and
export endpoints, which return the raw file with an appropriate
`Content-Type` and `Content-Disposition` header.

## Error schema

Every error response (validation failures, 404s, 500s) uses the same
envelope, regardless of endpoint:

```json
{
  "error": {
    "code": "MODEL_GENERATION_FAILED",
    "message": "Human-readable message",
    "requestId": "b6b8...-uuid",
    "details": []
  }
}
```

`requestId` matches the `X-Request-Id` response header and the structured
log line for that request, for correlation. `details` is populated for
validation-related errors with the offending `ValidationResult` list (see
`docs/validation-rules.md`) or the raw FastAPI/Pydantic request-validation
errors.

| Code | Status | Meaning |
|---|---|---|
| `VALIDATION_BLOCKED` | 422 | The definition has one or more `error`-severity validation results; generation was refused. |
| `REQUEST_VALIDATION_ERROR` | 422 | The request body itself didn't match the expected schema (malformed JSON, wrong types). |
| `MODEL_NOT_FOUND` | 404 | The `modelId` doesn't correspond to a currently cached generated model. |
| `MODEL_GENERATION_FAILED` | 500 | Geometry generation raised an unexpected error. |
| `EXPORT_FAILED` | 500 | An export operation raised an unexpected error. |
| `INTERNAL_ERROR` | 500 | Any other uncaught exception. No stack trace is ever sent to the browser. |
| `DESIGNER_PROVIDER_UNAVAILABLE` | 503 | No Designer AI provider is configured — see [`docs/bible/12-designer/`](bible/12-designer/README.md). |
| `DESIGNER_PROVIDER_TIMEOUT` | 504 | The Designer AI provider timed out. |
| `DESIGNER_PROVIDER_ERROR` | 502 | The Designer AI provider call failed. |
| `DESIGNER_INVALID_RESPONSE` | 502 | The Designer AI provider returned something that isn't parseable structured output. |
| `DESIGNER_SCHEMA_VIOLATION` | 502 | The Designer AI provider's structured output failed schema validation. |
| `DESIGNER_SECURITY_REJECTED` | 400 | The Designer request text was rejected before reaching a provider (prompt-injection screening). |

## Endpoints

### `GET /api/health`

```json
{
  "status": "ok",
  "service": "jewelmind-backend",
  "version": "0.1.0",
  "cadEngine": "cadquery",
  "cadEngineReady": true
}
```

### `POST /api/models/validate`

Body: a `JewelryDefinition` (see `docs/domain-model.md`).

```json
{ "results": [ /* ValidationResult[] */ ], "hasErrors": false }
```

### `POST /api/models/generate`

Body: a `JewelryDefinition`. Runs validation first — if any `error` results
exist, responds `422 VALIDATION_BLOCKED` with the results in `details`
instead of generating.

On success:

```json
{
  "modelId": "355ddca57e7e49ad",
  "definitionHash": "355ddca57e7e49ad",
  "validation": [ /* ValidationResult[] (warnings/information only) */ ],
  "metadata": {
    "generatorVersion": "0.1.0",
    "generationDurationSeconds": 0.41,
    "componentVolumesMm3": { "band": 251.0, "stone_reference": 58.2, "prongs": 29.6, "basket_support": 83.2 },
    "combinedMetalVolumeMm3": 341.4,
    "boundingBoxMm": { "xmin": -10.7, "xmax": 10.7, "ymin": -3.6, "ymax": 3.6, "zmin": -10.7, "zmax": 15.6 },
    "prongs": { "requestedCount": 6, "generatedCount": 6, "prongRadiusMm": 0.55, "centerRadiusMm": 3.09, "positions": [ { "x": 3.09, "y": 0 }, "..." ] }
  },
  "previewComponents": {
    "band": { "vertexCount": 3260, "triangleCount": 5670, "volumeMm3": 251.0, "boundingBox": { "...": "..." }, "warnings": [], "url": "/api/models/355ddca57e7e49ad/preview/band" },
    "stone_reference": { "...": "url pointing at the stone's own preview mesh" },
    "prongs": { "...": "" },
    "basket_support": { "...": "" }
  },
  "warnings": [],
  "generatedAt": "2026-07-29T12:00:15.611873+00:00"
}
```

`modelId` equals `definitionHash`: regenerating the exact same definition
replaces the cached entry rather than creating a new one (see
`docs/domain-model.md`).

### `GET /api/models/{modelId}/metadata`

Returns the same metadata shape as the `generate` response, without
re-running generation. `404 MODEL_NOT_FOUND` if the id is unknown or has
been evicted from the in-memory cache (see `docs/known-limitations.md` for
the cache eviction policy).

### `GET /api/models/{modelId}/preview/{componentName}`

`componentName` is one of `band`, `stone_reference`, `prongs`,
`basket_support`. Returns the component's binary STL mesh
(`Content-Type: model/stl`). `404 MODEL_NOT_FOUND` if the component has no
geometry (e.g. an edge case with zero generated prongs).

### `POST /api/models/export/step`

Body: `{ "modelId": "...", "includeStoneReference": false }`.

Returns a real CadQuery/OpenCascade STEP file
(`Content-Type: application/step`) with a sanitized filename derived from
`project.name`. The stone reference is excluded unless
`includeStoneReference` is `true`.

### `POST /api/models/export/stl`

Body: `{ "modelId": "...", "includeStoneReference": false, "meshTolerance": null, "angularTolerance": null }`.

Returns a real triangulated STL mesh (`Content-Type: model/stl`) of the
combined metal geometry. `meshTolerance`/`angularTolerance` default to the
definition's own `preview.*` values when omitted.

### `POST /api/models/export/json`

Body: `{ "modelId": "..." }`. Returns the canonical `JewelryDefinition` as
formatted, downloadable JSON.

### `POST /api/models/specification`

Body: `{ "modelId": "..." }`. Returns a human-readable Markdown technical
specification (dimensions, volumes, bounding box, validation results,
warnings, and the professional-review disclaimer).

### `POST /api/designer/interpret`

Body: a `NaturalLanguageDesignRequest` — see
[`docs/bible/12-designer/292-natural-language-input-contract.md`](bible/12-designer/292-natural-language-input-contract.md).

```json
{
  "requestId": "req-1",
  "text": "Fammi un solitario in oro rosa con sei griffe.",
  "locale": "it",
  "interactionMode": "CREATE",
  "currentJDL": null
}
```

Returns a `DesignerResult` — a structured, reviewable proposal, never
geometry and never a change to any stored design. `503
DESIGNER_PROVIDER_UNAVAILABLE` when no AI provider is configured (the
default in a fresh checkout — see `.env.example`); the rest of the API is
completely unaffected when this happens. See
[`docs/bible/12-designer/README.md`](bible/12-designer/README.md) for the
full contract, governance rules, and machine-readable schemas in
[`specs/designer/v1/`](../specs/designer/v1/README.md).

### `GET /api/gems`

Every current gem registry entry and every visual profile, plus a `note`
stating what the registry is not. Read-only: the registry is code, so adding a
gem is a repository change with tests and a version bump, never a runtime
write — a mutable registry would make `registryVersion` meaningless.

### `GET /api/gems/{gemId}`

One entry with its default visual profile. A deprecated entry stays reachable
here on purpose, because a saved design may reference one. `400
GEM_ID_INVALID` for a malformed ID (validated for shape before any lookup),
`404 GEM_NOT_FOUND` for a well-formed ID with no entry.

### `POST /api/gems/resolve`

Body: `{ "term": "rubino" }`. Resolves a name or alias to a canonical gem ID in
either supported language. Returns `gemId: null` when nothing matches — it
never guesses, and never infers a gem from a stone's shape.

### `POST /api/gems/validate`

Body: `{ "gem": <GemIdentity> }`. Runs the real Forge gem rules against a
definition carrying this identity, so the answer is exactly what generation
would say, and returns the `ResolvedGem` alongside. See
[`specs/gem/v1/`](../specs/gem/v1/README.md) and
[`docs/bible/23-gem-identity/README.md`](bible/23-gem-identity/README.md).

## CORS, limits, and cleanup

- CORS origins are configured via the `JEWELMIND_CORS_ORIGINS` environment
  variable (comma-separated), defaulting to
  `http://localhost:3000,http://localhost:5173`.
- Generated models and their preview/export temp files live in an in-memory
  cache capped at `MAX_CACHED_MODELS = 20` (`services/model_service.py`);
  the oldest entry (and its temp directory) is evicted once the cap is
  exceeded, and everything is cleaned up on process exit.
- Every request gets a UUID request id (`X-Request-Id` header) that also
  appears in the structured JSON log line for that request.
