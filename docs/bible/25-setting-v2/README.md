---
id: JM-BIBLE-SETTINGV2-README
title: "Setting System v2 — Advanced Heads & Prongs"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-03
source_of_truth: true
depends_on:
  - JM-BIBLE-SETTING-README
  - JM-BIBLE-STONEV2-README
  - JM-BIBLE-ARRANGE-README
  - JM-BIBLE-ATLAS-README
related_documents:
  - JM-BIBLE-800
implementation_status: current
professional_validation: not_required
normative: true
---

# Setting System v2 — Advanced Heads & Prongs

Sprint 23. The machine-readable half lives at
[`specs/setting/v2/`](../../../specs/setting/v2/README.md). Sprint 19's
[`21-setting/`](../21-setting/README.md) remains accurate for the family
architecture, the Stone→Setting interface and the attachment contract; all 18
`SETTING-GOV` rules still apply in full.

## What this sprint changed

Sprint 19 made stone-setting geometry category-neutral, with one prong body (a
cylinder) and one head (a hollow cylindrical wall built ring-side). This sprint
generalizes both axes and makes the head a Setting concern:

| Axis | Before | Now |
| --- | --- | --- |
| Prong body | one cylinder | 4 styles, registry-dispatched |
| Prong layout | derived from the stone | derived **or** explicit, with per-group style overrides |
| Head | one basket, built ring-side | 4 architectures, built category-neutrally |
| Seat | none | opt-in reference relief |
| Setting → stone | implicit (one stone) | explicit, by instance ID |

## The head is now category-neutral

Head construction moved from `geometry/components/basket.py` into
`jewelmind/setting/head.py`, driven by `HeadSettingDefinition` plus the generic
attachment interface. A future pendant or earring reaching the same structure
gets it without reimplementing anything. `geometry/components/basket.py`
survives as a thin re-export — the pattern `band.py`, `stone.py` and
`prongs.py` already follow.

**The component is still named `basket_support`, for every architecture.** The
name is a structural role ("the support between the attachment plane and the
stone"), and it is wired into `geometry/roles.py`, the inspection
required-component set, every preview manifest, every export list and all 39
Golden baselines. Renaming it per architecture would break all of those to
express something `headArchitecture` already reports.

## Four architectures, four styles, all real geometry

Each is a registered builder producing one valid, connected solid:

- **Heads** — `BASKET` (the preserved straight wall), `PEG_HEAD` (a wall on a
  peg, joined by a conical flare), `MARTINI` (a conical wall), `TULIP` (a
  concave flare, stacked frusta following a quadratic).
- **Prongs** — `ROUND_PRONG` (the preserved cylinder), `TAPERED_PRONG` (a cone
  frustum), `CLAW_PRONG` (a shaft with a tapered head, so the taper is
  concentrated at the tip), `V_PRONG` (a notch cut along the prong's own radial
  direction).

Every architecture spans the same vertical extent, so choosing a martini never
moves the stone. Every taper ratio, notch angle and section count is a
**software construction parameter** — no commercial head or prong proportion is
claimed, and nothing is professionally validated.

`TRELLIS` is deliberately **not** a member: it needs swept curved rails the
current pipeline cannot build verifiably, and a "simplified trellis" that was
really four bent prongs would be a different structure wearing the name. See
[`head-execution-boundary.md`](head-execution-boundary.md).

## Layout: derived, or explicit

`positionSource` chooses. `DERIVED` runs the Sprint 19 strategies and is the
default; `EXPLICIT` takes positions verbatim — the escape hatch for a
configuration no strategy produces, in the same spirit as Stone v2's
`CUSTOM_OUTLINE`.

Never a mix of the two. A caller states every position or none, because a
layout half-derived and half-overridden has no determinate meaning, and the
strategy producing the other half would silently depend on how many were
overridden.

`ProngGroupSpec` labels a subset and may override its style, so "V prongs at
the tip, round elsewhere" needs no second setting.

## Setting → stone, by ID

`SettingGeometryResult.stoneInstanceAssignments` maps each generated component
to the stone instance IDs it serves. A shared prong declares both stones, and
that declaration survives into the geometry metadata where inspection and
Vision can read it — no consumer has to infer sharing from coordinates.

The Setting System **carries** these references and never resolves them: it
must not import the arrangement layer (SETTING-GOV-001), which an AST test
enforces. Shared prong geometry is therefore `PARTIAL`: representable and
reported, not generatable against two stones, because one stone component is
built per model.

## Seat relief: a cut, never a fuse

`SeatMode.REFERENCE_SEAT` uses the real generated stone solid as a **cutting
tool** against production metal, so metal no longer occupies the stone's
volume.

That distinction is the whole reason the feature can exist. LAW-006 and
ATLAS-GOV-011 forbid the stone shape from reaching a fuse of production metal —
a stone unioned in would be exported and quoted as metal. A cut is the opposite
operation: the stone contributes no material and is discarded when the cut
returns. `seat.py` calls `.cut()` and never `.fuse()`, asserted by parsing its
own source.

**It is relief, not a seat.** There is no bearing shoulder, no bright cut, and
no claim that a stone would sit correctly in it — which is why the mode is
`REFERENCE_SEAT` and why `seatSupport` is `PARTIAL` rather than `CURRENT`.
Bearing and cutter geometry remain `PLANNED`: a bearing is sized by a setter
and a cutter is manufacturing tooling, and no sourced professional geometry
exists for either.

Off by default, so every pre-Sprint-23 design keeps its geometry.

## Backward compatibility

Seven additive optional JDL fields, each defaulting to the previous behaviour
(`ROUND_PRONG`, `BASKET`, `seatMode="NONE"`). `schemaVersion` stays `0.1.0` —
the same MINOR judgment Sprint 19 made when `bezel` joined the `type` enum.

Preservation was verified, not assumed:

- `ROUND_PRONG` reproduces the previous inline cylinder character-for-character.
- `_basket()` reproduces the previous wall construction, and the Ring adapter
  passes the **original** bore expression rather than re-deriving it — deriving
  it as `outerRadius − wallThickness` re-associates the same arithmetic and
  lands ~1e-11 mm away, which is harmless numerically and still an avoidable
  change to shipped geometry.
- The default solitaire's fused metal volume is unchanged, and all 39 Golden
  baselines needed **no** update.

## Validation

Three structural rules, `JM-SETTING-005`…`007`: does the requested
architecture have the parameters it needs, is a requested field meaningful for
the family chosen, can the requested operation run against this stone.

None is a professional judgment. There is no rule about whether a prong is
thick enough for a given stone, whether a martini wall is castable, or whether
a seat would hold — each needs sourced professional evidence this project does
not have, so none exists. An unread field is reported as `information`, because
the design is valid and only the value is inert.

The frontend mirror is **complete** here rather than a subset: every check is
local and structural.

## Governance

See [`setting-v2-governance.md`](setting-v2-governance.md) for the full
`SETTINGV2-GOV` rules, and
[`head-execution-boundary.md`](head-execution-boundary.md) for exactly what
does and does not execute.
