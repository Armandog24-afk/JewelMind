---
id: JM-BIBLE-FAMILY-BOUNDARY
title: "Multi-stone family execution boundary"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-04
source_of_truth: true
depends_on:
  - JM-BIBLE-FAMILY-README
implementation_status: partial
professional_validation: not_required
normative: true
---

# Multi-stone family execution boundary

What executes, what does not, and why the line moved.

## What Sprint 22 said, and what changed

Sprint 22 recorded three dependencies before multi-stone geometry could be
real. Two are now met:

| Sprint 22 dependency | Status |
| --- | --- |
| A per-instance transform on the stone builder | **done** — `geometry/stone/instance.py` |
| Instance-aware Geometry Inspection | **done** — the stone set comes from the role map |
| A setting strategy for accents (RFC) | **not done**, and deliberately |
| Instance overrides applied to geometry | **done** — scale and orientation reach the solid |

## Executes today

| Capability | Evidence |
| --- | --- |
| Declare a family in JDL | round-trips; validates against `specs/jdl/v1/jdl.schema.json` |
| Compile it into an arrangement | `family/compile.py`; four registered compilers |
| Resolve every member to a placement | the existing arrangement resolver, unchanged |
| Build a stone solid per member | `geometry/stone/instance.py`; one valid solid each |
| Apply per-member scale and orientation | measured: a 0.5 scale gives 0.125 of the volume |
| Name and inspect each stone | `stone_reference.<instanceId>`, required by Inspection |
| Structural validation | `JM-FAMILY-001`…`005` |
| Keep single-stone designs identical | metal volume unchanged; 39 pre-existing Goldens, zero updates |
| Regression coverage for the new scope | 5 new Golden cases (`FAM-001`–`FAM-005`); suite now 44 |

## Does not execute

### A setting for a non-primary member — PLANNED

The one real limitation, and the reason every family is `PARTIAL` rather than
`CURRENT`. A three-stone design builds three stones and **one** setting: the
primary stone's. The side stones are placed, sized and rendered, and nothing
holds them.

This was not implemented because doing it honestly requires deciding *how* an
accent is held — a shared prong, its own miniature head, a bezel collar — and
each of those is real setter geometry with real professional consequences.
Sprint 23 built the contract that a future strategy will use (explicit prong
positions carrying `servesStoneInstanceIds`), and `SETTING-GOV` requires an RFC
before an accent setting family is added. **That RFC is the next step, and this
sprint deliberately did not bypass it.**

Reported through four channels rather than left implicit:

- `JM-FAMILY-005` (`information`) on every multi-member family;
- a note on the compiled arrangement (`"a setting is built only for the
  primary instance"`);
- `settingGeometry: false` on every entry in `family/capability.py`;
- `settingCoverage: "PRIMARY_ONLY"` in every spec test vector.

### A family-aware head — PLANNED

A single head spanning several stones — a three-stone gallery, a cluster
basket. Sprint 23 builds one head per setting, so this needs multi-head
geometry first.

### A member naming another stone specification — PLANNED

`stoneRef` other than `primary` is carried, reported (`JM-FAMILY-004`) and
builds nothing, because JDL declares exactly one `stone`. Allowing several named
specifications is an RFC of its own.

### Interpreting a stone-to-stone overlap — PLANNED

Inspection now *reports* intersections between stone components as geometric
facts. No rule *interprets* them: whether an overlap is acceptable is a
professional question, and no spacing threshold is invented.

### Reserved families — PLANNED

`pave` (needs region fill, not individual placement), `eternity` (needs
placement along the shank's own path — Shank territory), `bypass` (a shank
capability), `channel_row` (needs the rails Sprint 23 recorded as PLANNED). Each
reason is recorded in `RESERVED_FAMILY_TYPES`, and none is a `FamilyType`
member, so a caller naming one is refused rather than given something else.

`halo` was reserved here in Sprint 24 and no longer is: Sprint 25 established
that a halo is not a family but a composable structure, implemented as
`jewelmind.halo` with `FamilyType` unchanged. See
[`../27-halo/halo-rfc.md`](../27-halo/halo-rfc.md).

## What was deliberately not done

- **No accent setting invented.** A prong placed by guesswork at each side
  stone would look like support and would be setter geometry nobody sourced.
- **No fifth family for a halo.** Two ways to express one design eventually
  compile differently. Sprint 25 kept that constraint while implementing a
  halo: it is a composable structure beside `family`, not inside it.
- **No radial pattern for a scaled ring.** A pattern's members inherit their
  source's overrides, so routing accents through one silently dropped their
  scale. The ring is placed explicitly, with the resolver's own arithmetic.
- **No mirror pattern for a toi-et-moi.** A mirror reflects across a principal
  plane, which collapses a pair whose axis runs along Y onto a single point.
- **No relaxed inspection.** The stone set grew; no check was weakened to let
  the new geometry pass.

## Dependency order for what comes next

1. An RFC for an accent setting strategy (`SETTING-GOV` requires it).
2. That strategy implemented, after which families become `CURRENT`.
3. Multi-stone head geometry, enabling a family-aware gallery or basket.
4. Multiple named stone specifications in one document, enabling genuinely
   different stones rather than scaled occurrences of one.

No family may be relabelled `CURRENT` before (2).
