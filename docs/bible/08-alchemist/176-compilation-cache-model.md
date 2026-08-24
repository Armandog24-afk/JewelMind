---
id: JM-BIBLE-176
title: Compilation Cache Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
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

`ModelService._records: OrderedDict[str, ModelRecord]`, keyed by `model_id` (= `definitionHash`), capped at `MAX_CACHED_MODELS = 20`, LRU eviction (`move_to_end()` on access, oldest evicted first when the cap is exceeded), each entry owning a temp directory of preview STL files, cleaned up on eviction (`shutil.rmtree`) and at process exit (`atexit`).

## What is cached

Normalized JDL (implicitly, as `record.definition`), the full `GeneratedModel` (geometry + metadata), and the preview manifest/mesh files. **Not cached**: STEP/STL export files (each export call always produces a fresh unique temp file, per-request, deleted after the response streams — see [`05-jdl/083-security-and-resource-limits.md`](../05-jdl/083-security-and-resource-limits.md)); JSON/specification text (regenerated on every call from `record.definition`, cheap enough not to need caching).

## Invalidation triggers, current vs. target

| Trigger | Currently invalidates the cache entry? |
|---|---|
| Definition changes | Yes, trivially — a changed definition produces a different `definitionHash`, hence a different cache key; the old entry simply ages toward LRU eviction, never actively invalidated |
| Compiler version changes | **No** — the cache key is `definitionHash` alone; a hypothetical compiler upgrade would happily keep serving an old cached `GeneratedModel` for the same `definitionHash`, even if a fresh compile would now produce different geometry |
| Atlas/generator version changes | **No**, same reasoning |
| Kernel changes | **No**, same reasoning |
| Output-affecting tolerance changes | **No** — `preview.meshTolerance`/`angularTolerance` are part of the definition, so they *do* participate in `definitionHash`; a change to them does invalidate correctly. Only *compiler-external* tolerance/kernel changes are the gap |
| Artifact request changes | N/A — exports are never cached in the first place |

**This is a real, concrete instance of ALCHEMIST-GOV-010 not being enforced today** — cached results can, in principle, be served across incompatible compiler/kernel versions, because no version fingerprint participates in the cache key at all. Since the backend has never shipped a second compiler/generator/kernel version in production, this gap has never actually manifested as a real bug — it is a structural risk, not an observed defect.

## Proposed target: `compilationHash` as the cache key

If `compilationHash` (see [`175-definition-hash-vs-compilation-hash.md`](175-definition-hash-vs-compilation-hash.md)) were implemented and used as the cache key instead of `definitionHash` alone, every trigger above would be correctly handled automatically — a version bump would simply produce a different cache key, no explicit invalidation logic required. This is recorded as the target architecture, not implemented in this Sprint.
