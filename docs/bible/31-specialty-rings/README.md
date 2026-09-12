---
id: JM-BIBLE-SPECIALTY-README
title: "Specialty Rings v1"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-12
source_of_truth: true
depends_on:
  - JM-BIBLE-RINGFAM-README
  - JM-BIBLE-PAVE-README
  - JM-BIBLE-FAMILY-GOVERNANCE
related_documents:
  - JM-BIBLE-SPECIALTY-GOVERNANCE
  - JM-BIBLE-SPECIALTY-EXECUTION-BOUNDARY
  - JM-BIBLE-SPECIALTY-COVERAGE-REVIEW
implementation_status: current
---

# Specialty Rings v1

**Sprint 29.** An EXTENSION of
[Ring Families v2](../30-ring-families/README.md), not a layer beside it. The
machine-readable half lives in
[`specs/ring-family/v1/`](../../../specs/ring-family/v1/README.md) — the same
directory, because there is one ring architecture.

## What this sprint actually decided

**Most of what was asked for already existed, spread across layers.** The audit
that opened the sprint found eternity expressible through the Pavé Engine,
cluster and toi-et-moi as *stone* families, and channel/flush/bezel/tension as
*setting* families. So the work was never "build seven engines" — it was to
build the **composition layer** that lets a designer name a ring and have the
existing engines produce it.

That is why the code added here derives JDL and builds nothing: three new
`jewelry.style` members, four new variants, and the derivations that turn them
into a `pave` or a `family` block.

## The three families, and why their statuses differ

| Family | Status | Why |
| --- | --- | --- |
| `eternity` | **CURRENT** | Delegates to the Pavé Engine, the ONE layer whose `settingGeometry` is `true`. Real stones **and** real metal holding them. |
| `cluster` | **PARTIAL** | Delegates to the Multi-Stone Family layer, whose `settingGeometry` is `false` for every family — the accent stones are real and **only the centre is held**. |
| `toi_et_moi` | **PARTIAL** | The same, **plus** a second limit: the two stones cannot differ in CUT. |

**That split is a measurement, not a preference.** It follows from one fact
recorded across two earlier sprints: the Pavé Engine builds retention for every
stone in a field, and the Multi-Stone Family and Halo layers build it only for
the primary. Marking cluster CURRENT would be the exact claim FAMILY-GOV
forbids.

## Measured, not asserted

| Claim | Measurement |
| --- | --- |
| A full eternity is a RELATION, not a preset | Finger size 12 → 24 gives **40 → 48 set stones**: the count follows the band's own circumference |
| Its stones are really held | **134 bead solids** at the default; metal 343.377 mm³ against the 341.443 baseline |
| A half eternity leaves a real unadorned region | 180° of stones leaves a **176.8° gap** |
| Spacing changes the retention TOPOLOGY | 16 stones at 1.6 mm → **64 beads**; at 1.2 mm → **34**, because corners genuinely share |
| A cluster's radius is honoured exactly | radius 3.0 → stones measured at **3.000 mm**; 5.5 → **5.500 mm** |
| Toi-et-moi's two stones are independent | second scale 0.5 → **7.278 mm³** against the first's unchanged **58.221 mm³** |
| Its separation and angle are exact | separation 8.0 → measured **8.000 mm**; 90° rotates the pair onto the other axis |

## One coherent architecture

```
jewelry.style          the FAMILY            (one authority, extended)
  └── ringFamily.variant   the VARIANT       (one authority, extended)
        └── resolve_ring_family()            (one resolution point)
              └── derives pave / family      (the existing engines execute)
```

There is **no `SpecialtyRingGenerator`**, no second dispatch and no second
placement engine — `test_specialty_rings.py` asserts all three structurally.
The specialty families are registered against the *same* `build_solitaire_ring`
generator, because a specialty ring is the same assembly built from a different
derived document.

## Three reservations retired, and one correction

`eternity`, `cluster` and `toi_et_moi` were reserved by Sprint 28 and are live
families now. **One of those reservations was factually wrong**, and the Bible's
rule is to report that rather than let it vanish in a diff:

> Sprint 28 recorded that "the pavé engine's containment policy clips a field at
> the host's declared extent rather than wrapping it, so a 360-degree field is
> not expressible yet."

The code disagreed the whole time. `PaveSpec.angularSpanDeg` is bounded
`le=360.0`, and `pave/compile.py` has an explicit closed-ring branch at
`span >= 360.0` that reuses the resolver's own full-sweep spacing *"so the last
stone does not land on the first"*. Measured before this sprint wrote a line: 68
stones, largest angular gap 5.8°, 134 real bead solids.

The other two reservations were **right about the risk and wrong about the
remedy**. A ring family named `cluster` would indeed be a second authority over
placement *if it placed stones itself*. It does not — it derives
`family.familyType = CLUSTER`, exactly as `THREE_STONE_SYMMETRIC` has done since
Sprint 28.

## What this sprint deliberately did NOT build

Each is reserved with its real technical reason, and
`TestReservedSpecialtyNames` asserts they stay unbuildable:

- **A channel-set band.** `setting/channel.py` builds its walls with
  `oriented_prism()` — straight prisms in the *stone's* frame — so it cannot
  follow the band's curve. Needs a swept wall along the band's centreline, the
  same missing primitive `SPLIT_SHANK_SCULPTED` waits on.
- **A stacking / plain band.** `REQUIRED_COMPONENT_NAMES` is
  `('band', 'stone_reference', 'basket_support')`, so a stone-less ring fails
  inspection *by contract*. An ADR condition, not a parameter — and the same
  blocker means even the eternity band still carries a centre stone and head.
- **A tension-style family.** The `tension` *setting* family already builds
  exactly that geometry. A ring family wrapping it would be a second name for
  one capability; what is missing is the structural model, which needs
  engineering evidence, not a new family.

## Nothing here is professionally validated

Every variant is `NOT_REVIEWED`. No stone spacing, bead size, cluster density or
stone-security judgment is asserted anywhere, and
`test_no_specialty_rule_message_makes_a_manufacturing_claim` reads every rule
message to keep it that way. The two software limits —
`MAX_PAVE_STONES_PER_BAND` and `MAX_CLUSTER_STONES` — exist so a hostile
document cannot request an unbounded expansion, and say so.

## Read next

- [`specialty-ring-governance.md`](specialty-ring-governance.md) — the SPECIALTY-GOV rules.
- [`execution-boundary.md`](execution-boundary.md) — exactly what does and does not execute.
- [`coverage-review.md`](coverage-review.md) — why each deferred family is deferred.
- [`SPRINT-29-VALIDATION-REPORT.md`](SPRINT-29-VALIDATION-REPORT.md) — what was verified, and how.
