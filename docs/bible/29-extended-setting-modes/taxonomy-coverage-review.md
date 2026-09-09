---
id: JM-BIBLE-ESM-COVERAGE-REVIEW
title: "Extended Setting Modes taxonomy coverage review"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-09
source_of_truth: true
depends_on:
  - JM-BIBLE-ESM-README
implementation_status: current
professional_validation: not_required
normative: false
---

# Taxonomy coverage review

The Sprint 27 brief asked for a targeted check that the architecture has no
structural omissions across the setting families used in contemporary jewelry
CAD, with every capability classified `IMPLEMENT NOW`, `PARTIAL`, `FUTURE` or
`NOT_RELEVANT`, and every deferral justified technically.

**This is an architecture review, not marketing.** It says nothing about which
techniques matter commercially, and nothing here is a professional statement
about any of them.

## The families the brief named

| Family | Verdict | Where it landed |
| --- | --- | --- |
| prong | IMPLEMENT NOW | `PRONG_ROUND/TAPERED/CLAW/V` — CURRENT |
| shared prong | PARTIAL | `PRONG_SHARED` — real metal, stated position |
| bead / grain | IMPLEMENT NOW | `RETENTION_BEAD` — CURRENT. "Grain" reserved: see below |
| shared bead | IMPLEMENT NOW | `RETENTION_SHARED_BEAD` — CURRENT |
| bezel | IMPLEMENT NOW | `BEZEL_FULL` — CURRENT |
| partial bezel | IMPLEMENT NOW | `BEZEL_PARTIAL` — CURRENT (new) |
| channel | IMPLEMENT NOW | `CHANNEL_LINEAR` — CURRENT (new) |
| bar | IMPLEMENT NOW | `BAR_TRANSVERSE` — CURRENT (new) |
| flush / gypsy | IMPLEMENT NOW | `FLUSH_GYPSY` — CURRENT (new) |
| tension | PARTIAL | `TENSION_OPPOSED` — geometry complete, function not modelled |
| basket | IMPLEMENT NOW | `HEAD_BASKET` — CURRENT |
| peg head | IMPLEMENT NOW | `HEAD_PEG` — CURRENT |
| martini | IMPLEMENT NOW | `HEAD_MARTINI` — CURRENT |
| tulip | IMPLEMENT NOW | `HEAD_TULIP` — CURRENT |
| trellis | FUTURE | `HEAD_TRELLIS` reserved — needs a verifiable swept solid |
| azure / open gallery | SPLIT | `HEAD_OPEN_GALLERY` CURRENT (new); `HEAD_AZURE` reserved |
| hidden-halo-related setting | FUTURE | `HALO_HIDDEN_SETTING` reserved — halo has no metal |
| pavé / microsetting retention | IMPLEMENT NOW | four strategies, `SHARED_PRONG` new |

Sixteen of the eighteen named families now have real geometry. The two that do
not are `trellis` and halo-related setting, and each has a named technical
dependency rather than a schedule.

## The deferrals, with their technical reasons

### Split rather than deferred: azure vs open gallery

"Azure" (ajouré) covers arbitrary decorative piercing, whose PATTERN is not
expressible as parameters — a pattern representation would be a new
sub-language, not a new builder. The parametric subset of it is *n* evenly
spaced windows of one angular width through the head wall, and that is what
`HEAD_OPEN_GALLERY` builds. Naming it "azure" would have claimed the general
case from the special one.

*Classification:* open gallery `IMPLEMENT NOW`; azure `FUTURE`, dependent on a
piercing-pattern representation.

### Deferred on a construction primitive: trellis, tapered channel, tapered bar

All three need a swept or lofted solid along a path the pipeline cannot yet
build verifiably. Atlas builds solids of revolution and lofts reliably; a swept
trellis rail, a channel whose clear width narrows along its run, and a bar with
a varying cross-section each need a primitive that is not verified. A
"simplified" version of any of them would be a different structure wearing the
name.

*Classification:* `FUTURE`, dependent on a verified sweep primitive.

### Deferred on anchor-driven placement: compass-point prongs, derived shared prongs

Stone v2 produces real named anchors (tip, cleft, corners). Consuming them needs
a placement strategy that does not exist, so `OUTLINE_CARDINAL` remains the
non-round default and a compass-point request would silently be an
outline-cardinal layout. `PRONG_SHARED` builds real metal at STATED positions
for the same reason.

*Classification:* compass point `FUTURE`; shared prong `PARTIAL`. Both dependent
on anchor-driven placement.

### Deferred on multi-head geometry: rails, double gallery, under-gallery support

A rail joins two or more heads; a double gallery needs two head instances per
setting; an under-gallery support needs one or the other. One setting builds one
head today, which is a contract rather than an oversight —
`SETTINGV2-GOV-002` names the single `basket_support` component and
`::test_the_v2_specs_match_the_live_registries` holds it.

*Classification:* `FUTURE`, dependent on a multi-head contract.

### Deferred on an anchor topology, not a builder: channel and bar as pavé retention

`RETENTION_CHANNEL` and `RETENTION_BAR` are the interesting deferrals, because
the geometry EXISTS — channel walls and bars are built by the PRIMARY families.
What does not fit is the pavé's retention ANCHOR TOPOLOGY: its anchors are
lattice corners, which is right for a bead or a prong and wrong for a rail
running a whole row or a bar at a cell midpoint.

Adding them as strategies would have meant either misusing the corner set or
quietly giving the pavé a second anchor derivation. Neither is acceptable, so
the techniques live where their extent is actually stated.

*Classification:* `FUTURE`, dependent on a retention-topology registry in the
pavé layer — and arguably `NOT_RELEVANT`, since a channel-set row is already
expressible as a channel family plus an arrangement.

### Deferred on surface texturing: millgrain

A milled edge is a surface treatment along a rim. No texturing or knurling
operation exists anywhere in Atlas, and approximating millgrain with a ring of
beads would be a bead ring with a different name.

*Classification:* `FUTURE`, dependent on a texturing operation.

### Deferred because it names an existing solid: grain, open-back bezel

`RETENTION_GRAIN` is reserved not because a grain is hard to build but because
`RETENTION_BEAD`'s hemisphere already IS the deterministic CAD reference for the
volume a grain occupies. A real grain's shape depends on the graining tool and
the setter's hand; a second id mapped to the same solid would imply a difference
that is not there.

`BEZEL_OPEN_BACK` is the same shape of judgment: the generated bezel wall is
already open at both ends, so an "open-back" bezel names no distinct solid here.
A genuine one differs by carrying a pierced seat rail the stone rests on, and no
seat with a bearing shoulder exists.

*Classification:* both `NOT_RELEVANT` as separate modes at present, and each
would become relevant only alongside the capability that distinguishes it (a
tool-shape model; a real cut seat).

### Deferred because it is not a code question: structural tension

`TENSION_COMPRESSION_MODELLED` is reserved with the only reason on this page
that engineering cannot remove: it needs material properties, a validated
elastic model, and then real professional evidence. No amount of geometry work
substitutes for it.

*Classification:* `FUTURE`, dependent on professional and engineering evidence.

## Structural omissions found: none

The review's actual purpose was to check the ARCHITECTURE, not to count
features. Three things were checked and held:

1. **Every technique the brief named has a home** — either an implemented mode
   or a reserved one with a real reason. Nothing fell outside the taxonomy.
2. **No technique needed a fourth axis.** Every one is a primary strategy, a
   head architecture or a field retention, and the three axes accommodated all
   eighteen.
3. **No technique needed a second engine.** Channel and bar looked at first like
   they needed a placement capability, and they did not: the arrangement places
   the stones and the family states its own extent.

One genuine gap in the axis model is recorded rather than closed: the pavé's
retention anchors assume a corner topology, and a technique whose retention runs
along a row cannot be expressed as pavé retention. That is why channel and bar
are PRIMARY families, and it is the one place where the taxonomy's shape
constrained where a capability could live.
