---
id: JM-BIBLE-176
title: Compilation Cache Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-08
source_of_truth: true
depends_on:
  - JM-BIBLE-175
related_documents:
  - JM-BIBLE-083
implementation_status: current
professional_validation: not_required
normative: true
---

# Compilation Cache Model

## Current cache, exactly

`ModelService._records: OrderedDict[str, ModelRecord]`, keyed by `model_id` (= **`compilationHash`** since [`ADR-012`](../03-decisions/ADR-012-compilation-hash-as-cache-key.md); it was `definitionHash`), capped at `MAX_CACHED_MODELS = 20`, LRU eviction (`move_to_end()` on access, oldest evicted first when the cap is exceeded), each entry owning a temp directory of preview STL files, cleaned up on eviction (`shutil.rmtree`) and at process exit (`atexit`).

## What is cached

Normalized JDL (implicitly, as `record.definition`), the full `GeneratedModel` (geometry + metadata), and the preview manifest/mesh files. **Not cached**: STEP/STL export files (each export call always produces a fresh unique temp file, per-request, deleted after the response streams — see [`05-jdl/083-security-and-resource-limits.md`](../05-jdl/083-security-and-resource-limits.md)); JSON/specification text (regenerated on every call from `record.definition`, cheap enough not to need caching).

## Invalidation triggers, current vs. target

| Trigger | Currently invalidates the cache entry? |
|---|---|
| Definition changes | Yes, trivially — a changed definition produces a different `definitionHash`, hence a different cache key; the old entry simply ages toward LRU eviction, never actively invalidated |
| Compiler version changes | **Yes** — `compilerVersion` is part of the cache key, so a bump produces a different key and therefore a miss |
| Atlas/generator version changes | **Yes**, same mechanism (`geometryGeneratorVersion`) |
| Kernel changes | **Yes** — `kernelVersion` and `ocpVersion` are both part of the key |
| Output-affecting tolerance changes | **Yes** — `preview.meshTolerance`/`angularTolerance` are part of the definition and so participate through `definitionHash`; compiler-external kernel changes now participate directly |
| Artifact request changes | N/A — exports are never cached in the first place |

**ALCHEMIST-GOV-010 is now enforced by construction.** It was previously not enforced — no version fingerprint participated in the key at all — and that was recorded here as a structural risk rather than an observed defect, since the backend had never shipped a second compiler/generator/kernel version. It was closed before persistence rather than with it: while the cache clears on every restart the risk stays theoretical, and the moment anything durable depends on the key it becomes real.

## `compilationHash` as the cache key — implemented

`compilationHash` (see [`175-definition-hash-vs-compilation-hash.md`](175-definition-hash-vs-compilation-hash.md)) is the cache key. Every trigger above is handled automatically: a version bump produces a different key, so **no explicit invalidation logic exists and none is needed** — which is why a different key, rather than an invalidation pass, was the right mechanism.

Geometry reuse is gated on the same fingerprint. The Sprint 21 semantic-only reuse path matches on `geometryHash` and additionally requires the cached record's fingerprint to equal the current one; without that the identity would be honoured on lookup and bypassed on reuse.

## Still volatile, deliberately

The cache remains in-memory, cleared on restart, capped at 20 with LRU eviction. Nothing durable was introduced, and `tests/test_persistence_boundary.py::TestNothingIsPersisted` asserts a fresh `ModelService` starts empty and that generation writes only inside a `tempfile`-owned directory.
