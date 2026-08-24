---
id: JM-BIBLE-076
title: Canonicalization and Definition Hashing
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-065
related_documents:
  - JM-BIBLE-086
implementation_status: current
professional_validation: not_required
normative: true
---

# Canonicalization and Definition Hashing

The exact algorithm and byte-level rules are documented once, in [`specs/jdl/v1/canonicalization.md`](../../../specs/jdl/v1/canonicalization.md), to avoid two documents drifting apart on the same fact. This document covers what that one doesn't: risk, stability, and how the hash is actually used by the running system today.

## What the hash is used for today

`GeneratedModel.definition_hash` becomes `ModelService`'s `model_id` — the key under which a generated model (and its temp directory of preview meshes) is cached in `ModelService._records`, and the identifier a frontend client passes back to request an export or a preview file. It is an **identity** key, not a content-integrity signature and not a security token: `backend/jewelmind/services/model_service.py` uses it purely to look up an in-memory cache entry.

## Stability guarantee, and where it is not (yet) guaranteed

The hash is stable **within one running process and one `GENERATOR_VERSION`**, proven by `specs/jdl/v1/test-vectors/definition-hash-vectors.json` and re-verified against a live run on every `pytest` invocation. What has **not** been separately verified in this Sprint:

- **Cross-Python-version stability.** `json.dumps` float formatting is a CPython implementation detail; this Sprint did not test hash stability across different Python patch versions. Flagged here as a risk, not fixed — no evidence exists either way, and inventing a claim would violate JDL-GOV-009.
- **Cross-OS stability.** Not separately tested in this Sprint; the same caveat applies.

Neither gap is treated as a defect requiring an immediate change — no evidence has been produced that either actually causes instability. They are recorded as open items so a future sprint verifies before relying on hash equality across environments (e.g. for cross-machine caching).

## Is the current scheme underspecified?

**Partially.** Two aspects are underspecified relative to what a fully rigorous cross-language canonicalization spec would need:

1. **Negative zero** (`-0.0`) has no defined normalization rule (see [`065-canonical-json-serialization.md`](065-canonical-json-serialization.md)). No current field's valid range produces it, so this has never been exercised by a real document.
2. **Whether `preview.meshTolerance`/`preview.angularTolerance` should participate in the definition hash at all** is genuinely unresolved — see open question JDL-OQ-001 in [`086-open-jdl-questions.md`](086-open-jdl-questions.md). Today's code includes them (proven by the test vectors); this document does not silently change that to "fix" the ambiguity.

**Neither gap is being resolved by changing the hash in this Sprint.** Per the explicit instruction governing this milestone: if current hashing is underspecified, document it and flag the risk — do not silently change the hash. Any future resolution (e.g. excluding preview fields, or defining `-0.0` normalization) is a MAJOR-version-worthy change to the hashing contract and requires an ADR, because it would change `definitionHash` for existing documents (see [`081-schema-versioning-and-migrations.md`](081-schema-versioning-and-migrations.md)).

## Proposed future migration path (not implemented)

If preview-field exclusion is adopted in a future sprint: introduce a new hash function version (e.g. tag hashes with a `hashAlgorithmVersion` field wherever they're surfaced), keep the current algorithm as `v1` indefinitely for backward compatibility with any persisted `model_id` values, and require both old and new test vectors to exist side by side in `specs/jdl/v1/test-vectors/` rather than replacing the old ones. This is a proposal for a future sprint to accept or reject — it is not being implemented now.
