---
id: JM-BIBLE-619
title: "Open Stone v2 Questions"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-02
source_of_truth: true
depends_on:
  - JM-BIBLE-600
related_documents:
  - JM-BIBLE-618
implementation_status: current
professional_validation: not_required
normative: false
---

# Open Stone v2 Questions

Decisions Sprint 20 deliberately did NOT make. Each is recorded so a future
sprint inherits the question rather than the accident.

## 1. Should there be a stone-only Golden category?

**Today:** the Golden suite builds complete rings, so `pearl` and `imported`
stones — which no current setting will grip — have no Golden case.

**The question:** add a Golden category that snapshots a stone in isolation, or
accept that unsettable stones are covered by unit tests only?

**Leaning:** yes, eventually. A stone's geometry is a real artifact whose
regression matters independently of whether a ring can be built around it. It
needs a harness change, so it is not a drive-by.

## 2. What is the right representation for a curve-based custom outline?

**Today:** ordered points only. A curved outline must be pre-sampled by the
caller.

**The question:** accept arcs and splines, and if so, in what representation?

**Constraints that will not move:** no executable geometry, ever; and whatever
is accepted must reduce deterministically to something the kernel can build.

**Note:** this interacts with Sprint 32's freeform modelling. Deciding it here
would likely be deciding it twice.

## 3. Should an imported outline be projected, and how?

**Today:** imported stones report no outline, which is why they are
`UNSUPPORTED` for both settings.

**The question:** project the girdle silhouette from imported geometry —
and if so, at what Z, with what tolerance, and what happens when the result is
non-simple?

**Why it was not done:** a projection needs a defensible answer for "which
plane is the girdle" on arbitrary geometry, and there is no obvious one. A
fabricated outline would place metal against a silhouette the stone does not
have (brief section 44).

**Impact if solved:** this single change moves imported stones from
`UNSUPPORTED` to at least `EXPERIMENTAL` for both families.

## 4. Should a measured stone be allowed no shape at all?

**Today:** `MeasuredStoneSource.shape` is optional in the source model, but the
JDL path requires a named shape or an outline, because reference geometry has to
be built from *something*.

**The question:** allow `shape: null` with dimensions only, and build a neutral
reference body (an ellipsoid, say)?

**Tension:** a neutral body is honest about not knowing the cut, and is also a
shape JewelMind invented. `MEASURED_DIMENSION_REFERENCE` already labels the
approximation; the question is whether a *shapeless* approximation is more or
less honest than a named one.

## 5. Where do custom outlines live?

**Today:** a custom outline is embedded in the JDL document.

**The question:** should a reusable outline become a first-class stored asset,
addressed like an imported file?

**Argument for:** a jeweller with a signature outline repeats it across designs,
and embedding duplicates it.

**Argument against:** embedding keeps a design self-contained, and
`definitionHash` covers it for free. An external reference introduces the
resolution and invalidation problems imported assets already have.

## 6. Should `narrowWidth` generalize?

**Today:** it exists only for `tapered_baguette` and `trapezoid`.

**The question:** is there a general "second width" concept — a kite's shoulder
width, a shield's waist — or is per-shape parameterization correct?

**Leaning:** per-shape. A general second dimension would mean different things
for different shapes, which is exactly the kind of overloading that makes a
schema field untrustworthy.

## 7. Does the cabochon profile need a shape allowlist at all?

**Today:** `CABOCHON_REFERENCE` is allowed for round, oval, heart, half_moon and
custom outlines.

**The question:** the builder is genuinely outline-agnostic, so the restriction
is a *design* judgement (a domed princess is odd) rather than a construction
limit. Should it be lifted and left to the user?

## 8. When is a custom outline too complex to manufacture?

**Today:** `MAX_OUTLINE_POINTS` is 10,000, a resource safeguard.

**The question:** a 9,999-point outline is structurally valid and certainly
unmanufacturable. What is the real limit?

**Blocked on:** a sourced threshold. Inventing one is forbidden
(STONEV2-GOV-011), so this stays open until a professional review supplies it.

## 9. How should Studio expose the three new sources?

**Today:** Studio offers parametric shapes and profiles. Custom, measured and
imported are backend capabilities with no UI.

**Why:** brief section 58 says not to show fake UI, and section 59 explicitly
defers a curve editor. Shipping the runtime capability first is the honest
order.

**The question:** what is the minimum honest UI — a JSON paste box for an
outline, a numeric form for measurements, a file upload for an asset?

## 10. Should `definitionHash` stop changing on additive schema changes?

**Today:** every additive field changes the hash for every document. Fourth
consecutive sprint.

**The question:** version the hash, or exclude defaulted fields from the
canonical form?

**Status:** needs an ADR. Recorded in
[`../appendices/jdl-version-compatibility-matrix.md`](../appendices/jdl-version-compatibility-matrix.md)
as a structural tension, and now genuinely predictable rather than surprising.

## Cross-references

- [`code-mapping-and-gaps.md`](code-mapping-and-gaps.md) — gaps that are
  understood, versus these questions which are undecided.
- [`stone-v2-governance.md`](stone-v2-governance.md) — which of these need an
  ADR and which need an RFC.
