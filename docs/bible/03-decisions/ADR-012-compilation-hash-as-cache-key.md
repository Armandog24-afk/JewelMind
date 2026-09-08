---
id: JM-BIBLE-ADR-012
title: "ADR-012: compilationHash as the compilation cache key"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-08
source_of_truth: true
depends_on:
  - JM-BIBLE-175
  - JM-BIBLE-176
related_documents:
  - JM-BIBLE-174
  - JM-BIBLE-160
implementation_status: current
---

# ADR-012: `compilationHash` as the compilation cache key

## Status

Accepted.

## Why this ADR exists

[`160-alchemist-governance.md`](../08-alchemist/160-alchemist-governance.md)
names **both** "introducing `compilationHash`" and "changing cache-key
strategy" as conditions requiring an ADR. This intervention does both, so the
decision is recorded here before the change stands.

This ADR decides **nothing about persistence technology**. No database, ORM,
authentication or object storage is introduced or chosen. That decision remains
open and unmade.

## Context

`ModelService`'s cache was keyed on `definitionHash` alone.
[`176-compilation-cache-model.md`](../08-alchemist/176-compilation-cache-model.md)
had already recorded the consequence in full: a compiler upgrade, an Atlas
generator upgrade or a kernel upgrade **does not** invalidate a cache entry,
because none of them participates in the key. ALCHEMIST-GOV-010 — "cached
results must never be reused across incompatible compiler/kernel versions" —
was therefore documented as **not enforced**.

Two facts made this worth closing now rather than later:

1. **The risk is real, not hypothetical.** Sprint 5's CI run demonstrated two
   OCCT builds producing different `combined_metal_volume_mm3` for one design.
   The kernel genuinely changes output for an unchanged document.
2. **The risk is currently masked by a property that is about to disappear.**
   The cache is in-memory and clears on every restart, and the project has
   shipped one compiler version. Persistence removes the mask: a durable cache
   would inherit the ambiguity and serve geometry no current code would
   produce. Closing it *before* persistence means the future layer never
   carries the defect.

The material for the fix already existed —
[`175-definition-hash-vs-compilation-hash.md`](../08-alchemist/175-definition-hash-vs-compilation-hash.md)
specified the formula, `specs/alchemist/v1/test-vectors/compilation-hash-vectors.json`
held computed examples, and `geometry_quality/fingerprint.py` already read every
version from a real source. It was specified, tested and unused.

## Decision

**1. `compilationHash` is implemented**, in a new `jewelmind/compilation/`
package split in two: `identity.py` is pure and kernel-free (strings in, string
out); `environment.py` reads the real installed versions.

**2. It becomes the cache key.** `ModelRecord.model_id` — the id every API route
addresses a model by — is now the `compilationHash`. `ModelRecord` carries
`definition_hash` as its own separate field, so neither identity can stand in
for the other.

**3. `definitionHash` is unchanged.** Same function, same value, same meaning.
Every Golden baseline, spec vector and stored hash still means what it meant.
This is additive, exactly as 175 required.

**4. Geometry reuse is gated on the same fingerprint.** The Sprint 21
semantic-only reuse path matches on `geometryHash`; it now also requires the
cached record's fingerprint to equal the current one. Without this the identity
would be honoured on lookup and bypassed on reuse.

**5. The fingerprint's components are prescribed, not chosen:**

| Component | Source |
| --- | --- |
| `definitionHash` | 175's formula |
| `compilerVersion` | 175's formula |
| `geometryGeneratorVersion` | 175's formula |
| `forgeRuleSetVersion` | 175's formula |
| `kernelVersion` | 175's prose ("plus kernel version") and 174's explicit endorsement |
| `ocpVersion` | 174's fingerprint table lists OpenCascade as a field distinct from CadQuery |

**Two components are deliberately excluded**, and this is the substantive
judgment in this ADR:

- **`jdlSchemaVersion`** — already inside `definitionHash`, because
  `schemaVersion` is a field of the document. Including it again adds no
  distinguishing power.
- **`inspectionVersion`** — Geometry Inspection is read-only by contract
  (INSPECT-GOV-013): it measures geometry and never produces it. Including it
  would discard correct cached geometry whenever a measurement changed.

**6. The cache remains volatile.** Still an in-memory `OrderedDict`, still
cleared on restart, still capped at 20 with LRU eviction. Nothing durable was
introduced.

## Consequences

- **ALCHEMIST-GOV-010 is now enforced** by construction: a version bump
  produces a different key and therefore a cache miss. No invalidation routine
  exists, and none is needed — which is why 176 named a different key as the
  target rather than an invalidation pass.
- **`modelId`'s value changes; its contract does not.** It was always an opaque
  handle, and both `definitionHash` and the new `compilationHash` are returned
  as their own named fields on the generate and metadata responses — so a
  client never has to know that `modelId` happens to equal one of them.
- **Two stale statements in existing documents were corrected**, not worked
  around: 174's table recorded "no aggregate Forge rule-set version exists" and
  the vectors file called `forgeRuleSetVersion: "none"` a placeholder. A real
  `registryVersion` has since existed in
  `specs/forge/v1/current-rule-registry.json`, and the fingerprint reads it.
- **The vectors file's formula gained the kernel components.** Its previous
  four-component formula matched 175's code block but not 175's own prose. The
  file was regenerated from the real implementation and its status changed from
  `PROPOSED, NOT IMPLEMENTED` to implemented.
- **`geometry_quality/fingerprint.py` no longer reads versions itself.** It
  derives from `compilation/environment.py`, so the Golden suite's report and
  the cache key can never disagree about which kernel built a model.
- **A second compiler or kernel version now produces different ids for one
  design.** That is the intent. It also means a cached model cannot be
  addressed by an id computed under a different environment — correct, and the
  reason a stored id will need its fingerprint stored beside it when
  persistence arrives.

## Alternatives considered

**Leave the key as `definitionHash` and add explicit invalidation on version
change.** Rejected: it requires code that notices every output-affecting
version, and 176 already identified the key itself as the correct mechanism —
a different key needs no invalidation logic at all.

**Include every fingerprint field, `inspectionVersion` included.** Rejected: it
would throw away correct geometry for a change that provably cannot affect
geometry, trading a real cost for no correctness gain.

**Defer until persistence is implemented.** Rejected. The ambiguity is cheap to
fix while the cache is volatile and expensive once anything durable depends on
it — and deferring would mean the persistence sprint had to both introduce a
store and correct an identity defect, with no way to tell which had caused a
regression.

**Introduce a repository/DAO abstraction now, in anticipation.** Rejected as
speculative. The audit that preceded this work found the domain layer already
free of storage concerns; the boundary needed *proving*, not building.
`tests/test_persistence_boundary.py` asserts it over the real package tree
instead, so the next sprint inherits a checked invariant rather than an unused
interface.
