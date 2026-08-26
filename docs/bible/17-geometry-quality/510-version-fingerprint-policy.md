---
id: JM-BIBLE-510
title: Version Fingerprint Policy
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-QUALITY-README
  - JM-BIBLE-500
related_documents:
  - JM-BIBLE-174
  - JM-BIBLE-175
implementation_status: current
professional_validation: not_required
normative: true
---

# Version Fingerprint Policy

`VersionFingerprint` (`backend/jewelmind/geometry_quality/models.py`) is collected field-by-field by `collect_fingerprint()` in [`backend/jewelmind/geometry_quality/fingerprint.py`](../../../backend/jewelmind/geometry_quality/fingerprint.py). Every field is read from a real, currently-running version constant or library — none is invented (QUALITY-GOV-009).

## Field-by-field provenance

| Field | Real source | Current real value |
|---|---|---|
| `jdlSchemaVersion` | `jewelmind.domain.schema.SCHEMA_VERSION` | `"0.1.0"` |
| `forgeRuleSetVersion` | `_forge_registry_version()` reads `registryVersion` from [`specs/forge/v1/current-rule-registry.json`](../../../specs/forge/v1/current-rule-registry.json), falling back to `"unknown"` on an `OSError` | `"1.0.0"` |
| `compilerVersion` | `jewelmind.__version__` (`backend/jewelmind/__init__.py`) | `"0.1.0"` |
| `atlasGeneratorVersion` | `model.generator_version` off the real `GeneratedModel` returned by `build_solitaire_ring()` | `"0.1.0"` |
| `inspectionVersion` | `jewelmind.geometry.inspection.version.INSPECTION_VERSION` | `"1.0.0"` |
| `kernelVersion` | `cadquery.__version__` (imported as `cq`) | `"2.8.0"` on the environment that generated the current Golden Suite (see [`511-current-solitaire-golden-suite.md`](511-current-solitaire-golden-suite.md)) |
| `ocpVersion` | `OCP.__version__`, wrapped in `_ocp_version()`'s `try/except Exception: return None` since `OCP` is an optional import | `"7.9.3.1"` when present, `None` if the import fails |

`collect_fingerprint(model: GeneratedModel) -> VersionFingerprint` is the single function that assembles all seven fields; it never reads from environment variables or wall-clock state, only from the constants and the passed-in `GeneratedModel` (ATLAS-GOV-003/014 — determinism is preserved).

## What this closes, and what it deliberately does not

[`08-alchemist/174-determinism-and-version-fingerprint.md`](../08-alchemist/174-determinism-and-version-fingerprint.md) recorded that only 2 of 8 conceptual `CompilationEnvironmentFingerprint` fields were recorded anywhere in Sprint 6/7's output: JDL schema version and Atlas generator version. `VersionFingerprint` now also records `kernelVersion` and `ocpVersion` — the two fields that document explicitly called out as **"No — never recorded on any generated model"** — plus `compilerVersion`, `forgeRuleSetVersion`, and `inspectionVersion`. `VersionFingerprint` is attached to every `GoldenModel` (via `versionFingerprint`) and to every `GeometryDiff` (via `expectedFingerprint`/`actualFingerprint`), so this information now exists wherever a golden is verified or accepted.

This is a real, additive closure of part of that gap — not a reopening of Sprint 6/7's scope. It deliberately does **not**:

- Materialize `GeometryPlan` as an object (still doesn't exist — see [`516-current-code-mapping-and-gaps.md`](516-current-code-mapping-and-gaps.md)).
- Implement `compilationHash` as proposed in [`08-alchemist/175-definition-hash-vs-compilation-hash.md`](../08-alchemist/175-definition-hash-vs-compilation-hash.md). `VersionFingerprint`'s fields overlap conceptually with that document's proposed formula inputs (`compilerVersion`, `forgeRuleSetVersion`, a generator/kernel identifier), but `VersionFingerprint` is a Geometry Quality-scoped record attached to a `GoldenModel`/`GeometryDiff`, never a new hash folded into `definitionHash` or exposed as a `compilationHash` on `GeneratedModel` itself. `definitionHash` remains exactly `jewelmind/utils/hashing.py::definition_hash()`, unchanged (ALCHEMIST-GOV-010).
- Attach fingerprint information to every generated model outside the Golden Suite — a normal `POST /api/generate` request still does not carry a `VersionFingerprint` in its response; this subsystem's fingerprint collection only runs inside `generate_snapshot()`/`generate_candidate_baseline()`/`accept_candidate_baseline()`'s call paths.

Whether `compilationHash` itself should ever be implemented, and whether it should absorb `VersionFingerprint`'s fields, remains open — see question 3 in [`517-open-geometry-quality-questions.md`](517-open-geometry-quality-questions.md).

## Why `ocpVersion` is optional

`OCP` (the OpenCascade Python binding CadQuery is built on) is imported defensively inside `_ocp_version()`: `import OCP` followed by `getattr(OCP, "__version__", None)`, the whole block wrapped in `try/except Exception: return None`. If the installed `OCP` build doesn't expose `__version__`, or the import itself fails for any reason, the fingerprint still completes with `ocpVersion: null` rather than crashing generation — consistent with FORGE/ATLAS's "never fabricate a passing result" posture applied here to "never fabricate a missing value as a fake success," i.e. `None` is the honest answer, not a guessed string.

## How this feeds `VERSION_REVIEW_REQUIRED`

`compare.py::_kernel_related_fields_differ()` compares exactly three of these seven fields — `kernelVersion`, `ocpVersion`, `atlasGeneratorVersion` — between a golden's `expectedFingerprint` and the current run's `actualFingerprint`. When a topology change is otherwise the only difference and one of those three fields differs, `compare_snapshot()` classifies the result as `VERSION_REVIEW_REQUIRED` rather than an unconditional `REGRESSION` (QUALITY-GOV-010). The other four fields (`jdlSchemaVersion`, `forgeRuleSetVersion`, `compilerVersion`, `inspectionVersion`) are recorded in every `VersionFingerprint` but are not currently read anywhere in `compare_snapshot()`'s severity logic — they exist as provenance evidence a human reviews during triage (see [`513-regression-failure-triage.md`](513-regression-failure-triage.md)), not as automated classification inputs.

## Cross-references

- [`08-alchemist/174-determinism-and-version-fingerprint.md`](../08-alchemist/174-determinism-and-version-fingerprint.md) — the gap this closes part of.
- [`08-alchemist/175-definition-hash-vs-compilation-hash.md`](../08-alchemist/175-definition-hash-vs-compilation-hash.md) — the still-unimplemented `compilationHash` proposal this does not replace.
- [`513-regression-failure-triage.md`](513-regression-failure-triage.md) — how `VERSION_REVIEW_REQUIRED` is triaged in practice.
