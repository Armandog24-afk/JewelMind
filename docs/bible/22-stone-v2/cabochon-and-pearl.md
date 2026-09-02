---
id: JM-BIBLE-606
title: "Cabochon and Pearl References"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-02
source_of_truth: true
depends_on:
  - JM-BIBLE-605
related_documents:
  - JM-BIBLE-614
implementation_status: current
professional_validation: not_required
normative: true
---

# Cabochon and Pearl References

## Cabochon is a PROFILE, not a shape

Brief section 21 put it directly: *"A cabochon is not simply a new outline. It
is also a distinct 3D profile class."*

That is why there is no `OVAL_CABOCHON` member. An oval cabochon is:

```json
{"shape": "oval", "profile": "CABOCHON_REFERENCE", "length": 8.0, "width": 6.0, "depth": 4.0}
```

An oval cabochon and a faceted oval share their silhouette **exactly** and
differ entirely in their body. Two axes state that; one enum cannot.

### Which outlines currently support it

`round`, `oval`, `heart`, `half_moon`, and **any custom outline**.

The builder never learns which shape it is building — it takes a
`(scale) -> Wire` callable — so extending the list is a registry edit plus a
Golden case, not new code. The four were chosen because a domed body over a
smoothly-curved or single-curve outline is visually coherent; a domed
`princess` would be a cushion-like object with corners, which is a design
decision rather than a construction one, and is deliberately left out until
someone asks for it.

An explicitly requested unsupported combination raises
`STONE_SHAPE_PROFILE_COMBINATION_UNSUPPORTED` rather than silently building a
faceted body.

### Construction

A shallow base below the girdle, then an ellipsoidal dome above it sampled at
16 levels following `scale = sqrt(1 - t²)`, with a small apex scale so the dome
closes without a degenerate point.

```
CABOCHON_DOME_FRACTION  0.75    of total depth, above the girdle
CABOCHON_BASE_FRACTION  0.25    of total depth, below the girdle
CABOCHON_BASE_SCALE     0.55    the base outline's scale
CABOCHON_APEX_SCALE     0.04    the closing level's scale
CABOCHON_DOME_SECTIONS  16      chosen from a measured convergence run
```

Every value is a fixed SOFTWARE REFERENCE CONSTRUCTION parameter. **No
commercial cabochon proportion is claimed** (STONEV2-GOV-003).

The section count came from measuring, not from taste — see
[`stone-profile-v2.md`](stone-profile-v2.md) for the convergence table and for
why `ruled=True` is required.

### Verified

A cabochon is a real, non-flat solid: single solid, positive volume, height
above 0.5mm, exact bounding box, and a volume that genuinely differs from the
same outline's faceted body — which is what proves profile is a real second axis
rather than a relabelling.

## Pearl is geometry, not gemology

`shape: "pearl"` + `profile: "SPHERICAL_REFERENCE"` produces a real sphere.
Verified against the analytic volume `4/3 · π · r³`.

**This is GEOMETRY only.** Whether the stone is an actual pearl — an organic
material with its own properties — is **gem identity**, which arrives in
Sprint 21. The shape name describes a spherical reference solid and nothing
more (brief section 22).

### Why `pearl` is a shape rather than only a profile

The brief noted that `PEARL_REFERENCE` is "primarily geometry/source profile".
It is modelled as a shape because that is how a user asks for it — "a pearl" —
and because it needs shape-level facts a profile alone cannot carry: a single
`diameter` dimension rather than a length/width pair, `RADIAL` symmetry, and its
own setting compatibility.

`SPHERICAL_REFERENCE` is pearl's **only** supported profile, which is what makes
the profile-defaulting rule necessary: `{"shape": "pearl", "diameter": 8}` is a
reasonable request whose `profile` defaults to `FACETED_REFERENCE`, and it used
to fail deep inside the outline builder. It now resolves to
`SPHERICAL_REFERENCE` with `PROFILE_DEFAULTED:...` recorded in provenance.

### A sphere's depth IS its diameter

`resolved_depth_mm()` returns the diameter for a pearl, and
`_parametric_dimensions()` builds it that way. Accepting a different `depth` and
then ignoring it would describe geometry that is not built.

That in turn required scoping Forge's `STONE_DEPTH_RANGE` away from spherical
references: the rule asserts `depth < min(length, width)`, which for a sphere is
`diameter < diameter` — false for every valid pearl. It fired on all of them
until it was scoped (STONEV2-GOV-011).

### A pearl cannot currently be set

`prongCompatibility` and `bezelCompatibility` are both `UNSUPPORTED`, and both
families refuse it explicitly with
`SETTING_STONE_COMBINATION_UNSUPPORTED`.

The reason is structural: a sphere has **no girdle plane**. Both current
families derive their geometry from a planar girdle outline, and a sphere has
none to give — `stone_anchors()` correctly returns an empty list, and the
registry's `anchors` field is deliberately empty to match. Real pearl settings
(a cup-and-post, a half-drilled peg) are a different family entirely, not a
variation of prong or bezel.

This is also why there is no pearl Golden **ring** case: no setting will hold
it, so no ring can be assembled. Pearl geometry is covered by unit tests
instead — see [`stone-v2-golden-strategy.md`](stone-v2-golden-strategy.md).

### What remains PLANNED

Near-round, drop and button pearls. Each needs a non-spherical body, and none
exists. Nothing in `SPHERICAL_REFERENCE` prevents adding them as new profiles
later.

## Cross-references

- [`stone-profile-v2.md`](stone-profile-v2.md)
- [`stone-setting-compatibility-v2.md`](stone-setting-compatibility-v2.md)
- [`../04-jewelry-domain/README.md`](../04-jewelry-domain/README.md)
