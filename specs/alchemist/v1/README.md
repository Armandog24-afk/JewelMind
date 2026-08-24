# Alchemist Compiler v1 — Machine-Readable Specification

The machine-readable half of Alchemist. The narrative, architecture, and contract half lives in [`docs/bible/08-alchemist/`](../../../docs/bible/08-alchemist/README.md); start there for context.

## What Alchemist is

Alchemist is the compilation orchestration layer: the conceptual translation from validated JDL + Forge evaluation into a deterministic `GeometryPlan`, Atlas execution, and a final artifact manifest. **Alchemist v1 is almost entirely a target architecture, not a running system.** The current backend already performs every step Alchemist describes, but does so inline across `backend/jewelmind/services/model_service.py`, `api/routes.py`, and `geometry/assemblies/solitaire.py` — with no explicit `GeometryPlan` object, no `CompilationResult` object, and no `compilationHash`. This specification names and formalizes what the current code does implicitly, and defines the target shape for what it does not yet do explicitly.

## Files

| File | Purpose | Status |
|---|---|---|
| [`compilation-input.schema.json`](compilation-input.schema.json) | Structural schema for `CompilationInput` | PARTIAL — only `canonicalJDL` is real |
| [`geometry-plan.schema.json`](geometry-plan.schema.json) | Structural schema for `GeometryPlan` | PLANNED — no such object exists |
| [`geometry-plan-component.schema.json`](geometry-plan-component.schema.json) | Structural schema for one `GeometryComponentPlan` | PLANNED |
| [`compilation-result.schema.json`](compilation-result.schema.json) | Structural schema for `CompilationResult` | PARTIAL — most fields map to real current data, several are PLANNED |
| [`compiler-diagnostic.schema.json`](compiler-diagnostic.schema.json) | Structural schema for a compiler-level diagnostic | PARTIAL |
| [`artifact-request.schema.json`](artifact-request.schema.json) | Structural schema for `ArtifactRequest` | PARTIAL — maps to 4 real, separate export/preview endpoints |
| [`artifact-manifest.schema.json`](artifact-manifest.schema.json) | Structural schema for one `ArtifactManifest` entry | PARTIAL — no unified manifest exists |
| [`compiler-capabilities.schema.json`](compiler-capabilities.schema.json) | Structural schema for a capability declaration | PLANNED — populated here with real current values only |
| [`examples/`](examples/) | 6 example records, generated from real Sprint 3/5 data where numeric | — |
| [`test-vectors/`](test-vectors/) | 7 test-vector files covering normalization, plan derivation, build order, the proposed compilation-hash formula, failure propagation, capabilities, and artifact manifests | — |

## No fabricated measurements

Every numeric value in `examples/` and `test-vectors/` that represents a real geometric quantity (volumes, bounding boxes, vertex/triangle counts, hashes) is copied from Sprint 3's or Sprint 5's already-verified real generation runs, or freshly computed by running real code during this Sprint (the proposed compilation-hash values). Nothing is estimated.

## How these files are validated

`backend/tests/test_alchemist_registry.py` (added in Sprint 6) validates all 8 schemas, validates all 6 examples against their respective schemas, and cross-checks `normalization-vectors.json` and `compilation-hash-vectors.json` against a live run of the real hashing/validation code.
