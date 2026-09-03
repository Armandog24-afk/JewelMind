# Setting System v2 — machine-readable specification

Advanced heads and prongs. Sprint 19's
[`specs/setting/v1/`](../v1/README.md) remains the family architecture, the
Stone→Setting interface and the attachment contract; this directory adds the
head, prong-style, layout and seat contracts on top.

Narrative half: [`docs/bible/25-setting-v2/`](../../../docs/bible/25-setting-v2/README.md).

## What executes

Four head architectures and four prong styles, each a registered builder
producing a real valid solid. Explicit prong layouts, per-group style
overrides, a deterministic setting→stone-instance mapping, and opt-in reference
seat relief.

What does **not** execute: `TRELLIS` (and three other reserved architectures),
support rails, shared prong geometry against two stones, bearing and cutter
geometry. Each absence has a recorded reason in
[`head-execution-boundary.md`](../../../docs/bible/25-setting-v2/head-execution-boundary.md).

## What this is not

- **Not professionally validated.** Every registry entry is `NOT_REVIEWED`. No
  taper ratio, notch angle or wall dimension is a professional recommendation.
- **Not a seat.** `REFERENCE_SEAT` is metal relief — a boolean CUT of the stone
  out of the metal. There is no bearing shoulder, and no claim that a stone
  would sit correctly in it. That is why `seatSupport` is `PARTIAL`.
- **Not commercial proportions.** `MARTINI` and `TULIP` are software reference
  silhouettes; no commercial head proportion is claimed.

## Files

| File | Contents |
| --- | --- |
| `head-setting-definition.schema.json` | Head parameters: architecture, radii, height, taper, peg. |
| `seat-setting-definition.schema.json` | Seat mode and its geometric clearance. |
| `prong-setting-definition-v2.schema.json` | Prong parameters, extended with style, layout source, groups. |
| `prong-position.schema.json` | One explicit prong, with the stone instances it serves. |
| `prong-group.schema.json` | A named subset carrying a style override. |
| `setting-definition-v2.schema.json` | The whole setting request, now with `head` and `seat`. |
| `setting-geometry-result-v2.schema.json` | The outcome, now with style, architecture, seat mode and the stone mapping. |
| `head-architecture-registry.json` | Architectures and reserved names, from live code. |
| `prong-style-registry.json` | Styles, construction parameters and reserved capabilities. |
| `seat-registry.json` | Seat modes and the kernel operation each performs. |
| `test-vectors/registry-consistency-vectors.json` | Registries vs. builders, both directions. |

Every artifact was produced by running the real code, and
`backend/tests/test_setting_v2.py` re-derives the registries on every test run.

## The component name is fixed

Every architecture produces a component named **`basket_support`**. The name is
a structural role — "the support between the attachment plane and the stone" —
and it is wired into `geometry/roles.py`, the inspection required-component
set, every preview manifest, every export list and all 39 Golden baselines. The
architecture is reported in the result and in the component metadata, never in
the name.

## Backward compatibility

Seven additive optional JDL fields on `setting`, each defaulting to the
pre-Sprint-23 behaviour (`ROUND_PRONG`, `BASKET`, `seatMode: "NONE"`).
`schemaVersion` stays `0.1.0`.

`ROUND_PRONG` and `BASKET` reproduce their previous constructions
character-for-character, and the Ring adapter passes the original basket bore
expression rather than re-deriving it — deriving it re-associates the same
arithmetic and lands ~1e-11 mm away. The default solitaire's metal volume is
unchanged and no Golden baseline was updated.

## Forge rules

| Rule | Checks | Severity |
| --- | --- | --- |
| `JM-SETTING-005` | the requested head architecture has the parameters it needs | error |
| `JM-SETTING-006` | a requested field is meaningful for the family chosen | information |
| `JM-SETTING-007` | seat relief can run against this stone source | warning |

None is a professional judgment: nothing here decides whether a prong is thick
enough, whether a head wall is castable, or whether a seat would hold. The
frontend mirror is complete rather than a subset, because every check is local
and structural.
