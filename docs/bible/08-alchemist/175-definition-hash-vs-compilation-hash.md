---
id: JM-BIBLE-175
title: Definition Hash vs. Compilation Hash
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-174
related_documents:
  - JM-BIBLE-076
implementation_status: planned
professional_validation: not_required
normative: true
---

# Definition Hash vs. Compilation Hash

## Two different identities

**`definitionHash`**: identity of canonical design intent. `backend/jewelmind/utils/hashing.py::definition_hash()` — SHA-256 of the canonical JSON serialization, truncated to 16 hex characters. **This is the current, real, tested identifier** used as `ModelService`'s cache key. It is unchanged by this document.

**`compilationHash`** (PROPOSED, not implemented): identity of canonical design intent **plus** compiler version, plus relevant rule-set version, plus geometry generator version, plus kernel version, plus any compilation option that affects output.

## Proposed formula and real computed examples

`specs/alchemist/v1/test-vectors/compilation-hash-vectors.json` documents:

```
compilationHash = sha256(f"{definitionHash}|{compilerVersion}|{geometryGeneratorVersion}|{forgeRuleSetVersion}").hexdigest()[:16]
```

deliberately modeled on `definition_hash()`'s own truncation scheme, not inventing a new hashing convention. Three real, deterministically-computed example values are checked in (e.g. `definitionHash: "355ddca57e7e49ad"`, `compilerVersion: "0.1.0"` → `proposedCompilationHash: "49092ec7ab9154a8"`), verified by `backend/tests/test_alchemist_registry.py::test_proposed_compilation_hash_vectors_are_reproducible`.

## Why two identities matter

`definitionHash` answers "is this the same design?" `compilationHash` would answer "would compiling this design today produce the same output as compiling it before?" — a compiler-version bump, a Forge rule-set update, or a kernel upgrade could all change the actual generated geometry for an *unchanged* `definitionHash`, and today's system has no identifier that would reveal this. Two of `compilation-hash-vectors.json`'s three examples demonstrate exactly this: identical `definitionHash`, different `compilerVersion`, different `proposedCompilationHash`.

## Not implemented; not replacing anything

Per this Sprint's explicit instruction, `definitionHash` is not silently replaced or altered — it remains exactly `backend/jewelmind/utils/hashing.py::definition_hash()`, unchanged. `compilationHash` is proposed as an **additive** future identifier, not a migration.

## When this would become worth implementing

Once any of the following becomes real: a second compiler version ships, a second Atlas generator version ships, or Forge rules gain an aggregate rule-set version — before any of these exist, `compilationHash` would always equal `definitionHash` combined with constants, adding no real distinguishing power yet.
