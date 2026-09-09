---
id: JM-BIBLE-ADR-014
title: "ADR-014: a ring family derives JDL and orchestrates existing subsystems; jewelry.style stays the one family authority"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-09
source_of_truth: true
depends_on:
  - JM-BIBLE-RINGFAM-README
related_documents:
  - JM-BIBLE-RINGFAM-GOVERNANCE
  - JM-BIBLE-FAMILY-GOVERNANCE
  - JM-BIBLE-ARRANGE-GOVERNANCE
  - JM-BIBLE-SHANK-GOVERNANCE
  - JM-BIBLE-ADR-013
implementation_status: current
---

# ADR-014: a ring family derives JDL and orchestrates existing subsystems; `jewelry.style` stays the one family authority

## Status

Accepted.

## Why this ADR exists

Sprint 28 adds parametric ring families, and two of the decisions inside it meet
recorded ADR conditions:

- **New shank architectures.** SHANK-GOV's ADR conditions name "a new centerline
  path (Euro shank)" and "multiple rails (split shank)" explicitly. Split and
  bypass shanks are both.
- **A new layer that writes into other subsystems' JDL blocks.** FAMILY-GOV
  requires an ADR before "letting the family layer construct geometry or compute
  placements itself", and ARRANGE-GOV-006 requires every consumer to read
  `ResolvedArrangement` rather than expand patterns itself. A layer that derives
  `family`, `halo` and `pave` blocks is close enough to both that the boundary
  must be recorded before the change stands.

This ADR decides nothing about professional validation. Every ring family is
`NOT_REVIEWED` and the active professional-validation registry still holds zero
records.

## Context

Before this sprint, `jewelry.style` was a single-member enum (`solitaire`) that
had *meant* "ring family" since Sprint 16 without ever having more than one
value. Meanwhile five subsystems each owned a real capability that a designer
would describe as part of a ring's family:

| A designer says | The system that owns it |
| --- | --- |
| "a trilogy" | Multi-Stone Families v1 → the Stone Arrangement Engine |
| "with a halo" | the Halo System |
| "pavé shoulders" | the Pavé & Microsetting Engine |
| "an elevated head" | Setting System v2 |
| "a tapered band" | the Shank subsystem |

So a ring family is not a new capability. It is a **coherent relation between
capabilities that already exist**, plus three genuinely new solids (shoulders,
split/bypass rails, a signet body).

Two questions had to be answered before writing any of it, and both had a
tempting wrong answer.

## Decision 1 — a ring family DERIVES JDL; it builds and places nothing

`resolve_ring_family()` returns a set of `RingFamilyDerivation` records, each
naming a JDL path, the value, the parameters it was computed from, and the
relation in words. `geometry/ring_family_adapter.py` applies them to produce the
**effective** document, and the existing pipeline runs unchanged.

### Rejected: a ring-family geometry builder

The tempting alternative was a `ring_family/geometry.py` that built a trilogy's
stones, a halo's ring and a pavé's beads directly, since the family "knows" what
it wants. It was rejected because it would have created a **second placement
engine** — the failure ARRANGE-GOV-006 and FAMILY-GOV both exist to prevent. A
family that computed its own side-stone positions would eventually disagree with
the arrangement resolver about where a stone goes, and the disagreement would
surface as geometry that does not match the preview.

Deriving JDL instead means a family can only ever *request* what the subsystems
already do. `family/compile.py` chooses primitives and never positions; the ring
family chooses **family blocks** and never primitives. One level up, same rule.

### Consequences

- The layer imports no geometry and no kernel (RINGFAM-GOV-004), enforced by AST
  inspection. This caught a real violation during the sprint:
  `capability.py` imported three geometry registries to measure
  `structuralGeometry`. That axis is now declared, with the correspondence
  asserted in the test file — the resolution `pave/capability.py` already uses.
- Every derived path must be declared in `RING_FAMILY_DEPENDENCIES`, and the
  resolver **self-checks each write at runtime**. A derivation no report could
  explain is worse than a missing one.
- A block the document declares itself is never overwritten. The family reports
  it in `skippedPaths` and `JM-RINGFAM-002` states it as INFORMATION.
- An explicit `arrangement` beside a family that would derive one is **refused**,
  because that is the two-authorities problem one layer down.

## Decision 2 — `jewelry.style` stays the one family authority

The family is `jewelry.style`. `ringFamily` carries the **variant** and its
parameters, and has no `family` field at all.

### Rejected: a `ringFamily.family` field

A self-contained `ringFamily` block would have been tidier to read and to
validate. It was rejected because it would have created **two fields that can
disagree about the same fact**, and there is no correct resolution for a document
that says `jewelry.style = "halo"` and `ringFamily.family = "signet"`.

The programme has met this shape twice already and answered it the same way both
times: `JM-FAMILY-001` refuses a family and an arrangement together, and
`JM-SETTING-008` refuses a mode whose family disagrees with `setting.type`.
Neither resolves by precedence, because precedence silently discards half of what
the author wrote.

Extending an existing single-member enum was the additive change
(JEWELRY-ARCH-GOV-008's preference for an adapter over a breaking schema
change), and it left `ringFamily: null` meaning something real: "no variant
declared".

### Consequences

- `JM-RINGFAM-001` refuses a variant belonging to another family, and
  `resolve_ring_family()` raises rather than choosing a winner.
- The frontend mirror recovers the family from the variant's own id prefix rather
  than carrying a per-variant table, so it cannot drift from a list of variants.
- A pre-existing hardcode surfaced: the TypeScript runtime guard tested
  `jewelry['style'] !== 'solitaire'`, which was correct while that was the only
  value and would have rejected every Sprint 28 family. It now checks membership
  in the mirrored enum — the same class of stale literal the JDL schema's
  `{"const": "prong"}` turned out to be for `setting.type` in Sprint 27.

## Decision 3 — the new shank architectures, and why each is shaped as it is

`build_shank()` is a three-way dispatch: **architecture → uniform → tapered**,
with the uniform fast path tried first for every document that has no
architecture. SHANK-GOV-003's byte-identity guarantee is preserved by ordering,
not by a wrapper.

**A split shank is two rails and ONE solid.** They share the band's width — so a
wider separation *narrows* them rather than widening the ring — and are joined
over the bottom span. A ring that is not one connected body is not a ring, and
the builder raises if it produces more than one solid.

**A bypass is ONE open rail, not two arcs.** This was decided by measurement:
two axially separated arcs come out as two disconnected solids. The rail travels
`360 + overlap` degrees with its axial offset interpolated along the sweep, so
its two ends occupy the same angles at different axial positions and pass each
other.

### Consequences

- `BandSpec` gains `architecture` and four separation/span fields, each
  defaulting to the pre-Sprint-28 behaviour.
- `SHANK_ARCHITECTURE_BUILDERS` deliberately has **no `UNIFORM` entry**: the
  uniform path is `_build_uniform_shank()`, and keeping it out of the dispatch is
  what stops it growing a wrapper.
- The Shank capability registry's `split_shank` entry moves from `planned` to a
  real capability, and SHANK-GOV-015's list shrinks accordingly.

## Consequences for the codebase as a whole

- One new resolution point, `resolve_ring_family()`, joining
  `effective_arrangement()` and `resolve_primary_mode()`.
- Five new Forge rules (`JM-RINGFAM-001` … `005`), two mirrored to
  `shared/validation/`. Three are deliberately backend-only, each because it
  needs something the frontend does not have.
- 14 new inspection `FactType` members.
- Three new geometry components: `shoulders`, `signet_body`, and the `band` under
  a non-uniform architecture.
- `_fuse_metal()` gains a result invariant. That was not a ring-family decision
  but a defect this sprint's geometry exposed, and it is recorded in
  [`execution-boundary.md`](../30-ring-families/execution-boundary.md).

## What this ADR does not decide

- **Whether any ring family is manufacturable.** None is reviewed.
- **Whether a halo should have retention metal.** It should, and it does not; the
  `halo` family is honestly PARTIAL and the work is an RFC.
- **How a swept solid along a 3D spline should be built.** Three reserved
  variants wait on it, and it needs its own RFC with real measured verification —
  this sprint found that both a ruled loft and a boolean fuse can fail while
  reporting success.
