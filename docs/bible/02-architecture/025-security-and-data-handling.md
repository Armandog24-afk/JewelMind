---
id: JM-BIBLE-025
title: Security and Data Handling
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on: []
related_documents:
  - JM-BIBLE-014
  - JM-BIBLE-026
implementation_status: current
---

# Security and Data Handling

## No authentication currently

JewelMind has no login, no user accounts, and no concept of a signed-in
user. Every request to the backend is treated identically. This is a
deliberate scope boundary (see
[`006-scope-and-boundaries.md`](../00-foundation/006-scope-and-boundaries.md)),
not an oversight — there is nothing yet that requires per-user isolation.

## No sensitive user data should be stored

The `JewelryDefinition` schema contains no field intended to hold personal
data (name, address, payment information, etc.) — `project.name` is a
free-text label for the design itself (e.g. "Solitaire Ring"), not a
person's name. No part of the system is designed to accept or store
personal data, and none should be added without a corresponding update to
this document and, if it changes the trust model, an ADR.

## `localStorage` limitations

- Persists exactly one project, client-side only, in the browser that
  saved it.
- Validated on load (`isValidJewelryDefinition()` in
  `shared/types/jewelry-definition.ts`) — corrupted or structurally
  invalid data is rejected and the app falls back to defaults, never
  crashes (`frontend/src/store/persistence.ts`,
  `persistence.test.ts`).
- Not encrypted, not synced across devices or browsers, cleared by normal
  browser data-clearing actions. This is acceptable because the data it
  holds (ring design parameters) is not sensitive per the point above.

## Temporary server files

- Preview meshes live in a per-model temp directory for the life of that
  model's cache entry (up to 20 cached models, LRU-evicted).
- Export files (STEP/STL) each get a uniquely-named temp file
  (`tempfile.mkstemp`) created fresh per export request, and are deleted
  via a background task once the HTTP response finishes streaming, or
  immediately if the export itself fails
  (`backend/jewelmind/services/model_service.py`).
- All temp directories are cleaned up on process exit (`atexit` handler
  in `model_service.py`).

## Sanitized filenames

User-supplied `project.name` is passed through
`backend/jewelmind/exporters/filenames.py::sanitize_filename()` before
being used in any `Content-Disposition` header, preventing path traversal
or header-injection via a crafted project name.

## Safe error responses

- Every error response uses one documented envelope shape:
  `{ "error": { "code", "message", "requestId", "details" } }`.
- Unexpected exceptions are caught by a generic handler
  (`backend/jewelmind/api/app.py::handle_unexpected_error`) that never
  includes a Python traceback in the response body.
- A hardening pass specifically found and fixed a case where a rejected
  `Infinity`/`NaN` value, echoed back by Pydantic's own error details,
  could crash the error handler itself — see `AUDIT_FIXES.md` §1 and
  `api/app.py::_json_safe`.

## Absence of runtime API keys

No part of the running application calls any external paid API or LLM
service (see [LAW-003](../00-foundation/004-jewelmind-constitution.md)),
so there is no API key to manage, rotate, or leak. `.env.example`
documents only two plain URL configuration variables — no secrets.

## What this document does not cover (not yet applicable)

Authentication/authorization design, encryption at rest, and data
retention policy are not applicable to the current system and are not
speculated about here — they would need their own ADR if and when
JewelMind grows a feature that requires them.
