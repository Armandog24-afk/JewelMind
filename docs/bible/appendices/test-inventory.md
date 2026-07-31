---
id: JM-BIBLE-A02
title: "Appendix: Test Inventory"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on: []
related_documents:
  - JM-BIBLE-005
implementation_status: current
---

# Appendix: Test Inventory

Test counts below were obtained directly from `pytest --collect-only -q`
and by counting `it(...)` blocks in the frontend test files — not
estimated.

## Backend — 139 tests total

Command: `cd backend && .venv/Scripts/python -m pytest -q` (`.venv/bin/python` on macOS/Linux).

| Suite | Tests | Covered behavior | Missing coverage |
|---|---|---|---|
| `test_schema.py` | 3 | Default definition matches the product spec exactly; JSON round-trip preserves equality; unknown fields rejected. | None significant — this is the smallest, most stable suite. |
| `test_schema_safety.py` | 70 | Numeric-string rejection (11 fields), non-finite (`NaN`/±`Infinity`) rejection (11 fields × 3 bad values), preview-tolerance positivity/finiteness, schema-version acceptance/rejection, integer-widening still works, clear error structure, example files still parse, strict mode + `extra=forbid` interplay. | Does not test every possible malformed-JSON shape (e.g. deeply nested wrong types) — covers the specific classes of input found risky during the hardening pass. |
| `test_validation.py` | 20 | All sixteen validation rules, both error and warning branches where applicable, and that warnings alone never block. | Does not test combinations of multiple simultaneous rule violations in one definition (each test isolates one rule). |
| `test_geometry.py` | 14 | Flat/comfort-fit band validity and distinctness, stone reference validity and separation, 4/6 prong counts and their volume difference, basket validity, full assembly component completeness and single-fused-solid behavior, deterministic hashing. | Does not assert exact numeric geometry values beyond "positive volume" / "distinct volume" — no golden-file geometry regression test. |
| `test_api.py` | 15 | Health endpoint (happy path), validate/generate/export endpoints end-to-end via `TestClient`, 404s for unknown models, sanitized filenames, disclaimer presence in the specification. | Concurrency (many simultaneous requests) is not exercised here — see `test_api_hardening.py` for the specific concurrent-export test. |
| `test_api_hardening.py` | 17 | Health endpoint degradation (503 when CAD engine not ready), CAD-engine probe success/failure reporting, error-code mapping for generation/STEP/STL failures and CAD-engine unavailability, unique per-export temp files, temp-file cleanup on success and failure, STL tolerance validation (including a raw-`Infinity` JSON body), specification timestamp stability across repeated downloads. | Does not simulate a genuinely broken CadQuery install at the process level (the CAD-unavailable test monkeypatches the import instead) — a true broken-environment integration test would require a separate CI matrix leg. |

## Frontend — 41 tests total

Command: `cd frontend && npm run test` (Vitest).

| Suite | Tests | Covered behavior | Missing coverage |
|---|---|---|---|
| `BackendStatus.test.tsx` | 3 | Renders online/offline/checking states correctly. | Does not test the actual polling interval behavior in `App.tsx`. |
| `ConfigurationPanel.test.tsx` | 3 | Default values render; a field edit updates the store and the JSON tab; every numeric field has an accessible label. | Does not exercise every single field individually (spot-checks a representative subset). |
| `JsonViewer.test.tsx` | 2 | Reflects the current definition; updates immediately on a store change. | None significant for this small, presentational component. |
| `ProjectActions.test.tsx` | 5 | Generate disabled on validation errors, not disabled on warnings-only; export buttons disabled until a valid model exists and enabled once it does; export buttons re-disable when the model goes stale. | Does not test the actual network call each button triggers (mocked). |
| `ValidationPanel.test.tsx` | 3 | Empty state when no findings; error message rendering; warning message rendering. | Does not test the display of `information`-severity results specifically. |
| `useComponentGeometries.test.ts` | 7 | Loads geometries for components with a URL; skips null-URL components; keeps previous geometries and reports an error on a failed reload; disposes the previous geometry once replaced; aborts an in-flight fetch when superseded; disposes all geometries on unmount. | Does not test simultaneous, out-of-order network responses (e.g. a slow first request resolving after a faster second one) beyond the abort-based supersede test. |
| `persistence.test.ts` | 14 | Round-trips a valid definition; corrupted JSON, non-object JSON, missing sections, obsolete schema version, string-typed numbers, non-finite numbers, invalid enums, and non-positive tolerances are all rejected; a throwing `localStorage` does not crash either load or save. | Does not test browser storage-quota-specific error types beyond a generic thrown exception. |
| `useProjectStore.test.ts` | 4 | Reset restores the default definition; a parameter change after generation marks the model stale; `generationStatus` reflects an in-flight request; a failed regeneration preserves the last successful preview. | Does not test the export flow's store-side state transitions (`exportStatus`) directly — covered indirectly via `ProjectActions.test.tsx`. |

## Execution commands

```bash
# Backend
cd backend && .venv/Scripts/python -m pytest -q   # .venv/bin/python on macOS/Linux

# Frontend
cd frontend && npm run test
```

Both suites also run automatically in CI — see
[`02-architecture/024-runtime-and-deployment.md`](../02-architecture/024-runtime-and-deployment.md).
