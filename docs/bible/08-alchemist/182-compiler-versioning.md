---
id: JM-BIBLE-182
title: Compiler Versioning
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-181
related_documents:
  - JM-BIBLE-108
implementation_status: planned
professional_validation: not_required
normative: true
---

# Compiler Versioning

## PATCH / MINOR / MAJOR for Alchemist

| Level | Definition | Example |
|---|---|---|
| PATCH | Diagnostic wording; internal non-output-changing fixes | Rewording a `ModelGenerationFailedError` message |
| MINOR | Backward-compatible capability additions | Adding `TECHNICAL_SPECIFICATION` as a fifth artifact type (already happened, historically, before this Bible existed) without changing any existing artifact's behavior |
| MAJOR | Geometry-plan semantic change; a changed output-affecting default; an incompatible compiler contract; changed deterministic output semantics | Changing which components are required in the solitaire assembly; changing the default `includeStoneReference` value; introducing `compilationHash` as the cache key (a behavior change even though additive in spirit) |

## No distinct compiler version exists today

`jewelmind.__version__` (`"0.1.0"`, the Python package version), `GENERATOR_VERSION` (`"0.1.0"`, `geometry/constants.py`), and `SCHEMA_VERSION` (`"0.1.0"`, `domain/schema.py`) are three independently-defined constants that currently coincide numerically — confirmed by inspection during this Sprint. **None of them is "the compiler version."** If Alchemist versioning were implemented, it would need its own fourth constant, distinct from all three, per JDL-GOV/ATLAS-GOV precedent of keeping version axes independent (see [`05-jdl/081-schema-versioning-and-migrations.md`](../05-jdl/081-schema-versioning-and-migrations.md)).

## Interaction with JDL/Forge/Atlas versions

Compiler versioning is orthogonal to all three: a compiler-version bump could occur with no JDL schema change, no Forge rule change, and no Atlas generator change (e.g. purely orchestration-level fixes) — and vice versa. This is exactly the same independence-of-axes principle Sprint 3 established for `schemaVersion` vs. `GENERATOR_VERSION` vs. product version, extended here to a fourth axis.
