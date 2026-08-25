# Studio v1 — Machine-Readable Specification

The machine-readable half of Studio. The narrative, architecture, and contract half lives in [`docs/bible/11-studio/`](../../../docs/bible/11-studio/README.md); start there for context.

## What Studio is

Studio is the product-workspace layer — the boundary between the JDL/Forge/Alchemist/Atlas/Foundry/Vision systems and the human workflow around them. **Like Vision v1 (Sprint 8), Studio v1's schemas describe a real, newly-shipped feature set** (a unified model-status indicator, a consolidated Outputs area, a reorganized parameter editor), not a target architecture layered over pre-existing behavior.

## Files

| File | Purpose | Status |
|---|---|---|
| [`studio-state.schema.json`](studio-state.schema.json) | A composed workspace-state snapshot (session + generation + outputs + validation summary) | PARTIAL as a runtime object — every piece is independently real |
| [`project-session.schema.json`](project-session.schema.json) | The current single-project session shape | PARTIAL — each field is real; no object of this exact shape is assembled at runtime |
| [`generation-state.schema.json`](generation-state.schema.json) | The 7-value model-lifecycle state | CURRENT — matches `frontend/src/studio/modelState.ts` exactly |
| [`output-state.schema.json`](output-state.schema.json) | One artifact's eligibility state | CURRENT — matches `frontend/src/studio/outputEligibility.ts` exactly |
| [`notification.schema.json`](notification.schema.json) | A conceptual transient-notification shape | PLANNED — no toast/snackbar component exists in the running application |
| [`examples/`](examples/) | 6 example workspace states, grounded in a real live-verified session against the default solitaire (`definitionHash 355ddca57e7e49ad`) | — |
| [`test-vectors/`](test-vectors/) | 6 test-vector files covering state transitions, stale-state behavior, generation button states, export eligibility, persistence, and session recovery | — |

## No fabricated measurements

Every real value in `examples/` and `test-vectors/` — the default solitaire's `definitionHash`, network request outcomes, computed state transitions — was obtained by running the real frontend code (`modelState.test.ts`, `outputEligibility.test.ts`) or by a live browser session against the running backend during this Sprint, not estimated or hand-typed.

## How these files are validated

`backend/tests/test_studio_schemas.py` (added in Sprint 9) validates all 5 schemas and all 6 examples against their respective schemas, using the same `jsonschema` library already used for every prior sprint's specs.
