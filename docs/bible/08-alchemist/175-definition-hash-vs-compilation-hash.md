---
id: JM-BIBLE-175
title: Definition Hash vs. Compilation Hash
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-08
source_of_truth: true
depends_on:
  - JM-BIBLE-174
related_documents:
  - JM-BIBLE-076
implementation_status: current
professional_validation: not_required
normative: true
---

# Definition Hash vs. Compilation Hash

## Two different identities

**`definitionHash`**: identity of canonical design intent. `backend/jewelmind/utils/hashing.py::definition_hash()` — SHA-256 of the canonical JSON serialization, truncated to 16 hex characters. **This is the current, real, tested identifier** used as `ModelService`'s cache key. It is unchanged by this document.

**`compilationHash`** (IMPLEMENTED — `backend/jewelmind/compilation/identity.py`): identity of canonical design intent **plus** compiler version, plus Forge rule-set version, plus geometry generator version, plus kernel version, plus OpenCascade build. It is the `ModelService` cache key and is returned as `compilationHash` on the generate and metadata responses. See [`ADR-012`](../03-decisions/ADR-012-compilation-hash-as-cache-key.md).

## Implemented formula and real computed examples

`specs/alchemist/v1/test-vectors/compilation-hash-vectors.json` documents:

```
compilationHash = sha256(
    f"{definitionHash}|{compilerVersion}|{geometryGeneratorVersion}"
    f"|{forgeRuleSetVersion}|{kernelVersion}|{ocpVersion}"
).hexdigest()[:16]
```

The last two components were added when the formula was implemented, because
this document's own prose above requires "plus kernel version" and
[`174-determinism-and-version-fingerprint.md`](174-determinism-and-version-fingerprint.md)
states explicitly that a `compilationHash` including a kernel version "would
let two different kernel builds carry two different hashes for the same design
intent — arguably more honest". Sprint 5's CI had already proved two OCCT builds
produce different volumes for one design, so the kernel is the component
empirically shown to matter. An absent OCP build hashes as the literal
`absent`, so an environment that cannot read its build is distinguishable from
one that reports a build of that name rather than silently colliding with it.

**Deliberately excluded**: `jdlSchemaVersion` (already inside `definitionHash`,
since `schemaVersion` is a field of the document) and `inspectionVersion`
(Geometry Inspection is read-only by contract, INSPECT-GOV-013 — including it
would discard correct cached geometry for a change that cannot affect
geometry).

deliberately modeled on `definition_hash()`'s own truncation scheme, not inventing a new hashing convention. Three real, deterministically-computed example values are checked in (e.g. `definitionHash: "355ddca57e7e49ad"`, `compilerVersion: "0.1.0"` → `proposedCompilationHash: "49092ec7ab9154a8"`), verified by `backend/tests/test_alchemist_registry.py::test_proposed_compilation_hash_vectors_are_reproducible`.

## Why two identities matter

`definitionHash` answers "is this the same design?" `compilationHash` would answer "would compiling this design today produce the same output as compiling it before?" — a compiler-version bump, a Forge rule-set update, or a kernel upgrade could all change the actual generated geometry for an *unchanged* `definitionHash`, and today's system has no identifier that would reveal this. Two of `compilation-hash-vectors.json`'s three examples demonstrate exactly this: identical `definitionHash`, different `compilerVersion`, different `proposedCompilationHash`.

## Additive; not replacing anything

`definitionHash` is not silently replaced or altered — it remains exactly `backend/jewelmind/utils/hashing.py::definition_hash()`, unchanged, and `tests/test_persistence_boundary.py::TestDefinitionHashUnchanged` re-checks it against the shipped vectors on every run. `compilationHash` was added **beside** it, never as a migration: `ModelRecord` carries both as separate fields so neither can stand in for the other.

## Why it was implemented when it was

This document originally deferred implementation until "a second compiler
version ships, a second Atlas generator version ships, or Forge rules gain an
aggregate rule-set version". The third of those **has since happened** —
`specs/forge/v1/current-rule-registry.json` carries a real `registryVersion`,
which the fingerprint now reads.

The decisive reason, though, was ordering rather than distinguishing power:
while the cache is volatile and clears on every restart, keying it on
`definitionHash` alone is a theoretical risk. The moment anything durable
depends on that key it becomes a real defect — serving geometry no current code
would produce. Closing it before persistence exists means the future layer
never inherits the ambiguity. See
[`ADR-012`](../03-decisions/ADR-012-compilation-hash-as-cache-key.md).
