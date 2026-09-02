---
id: JM-BIBLE-600
title: "Stone System v2 Governance"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-02
source_of_truth: true
depends_on:
  - JM-BIBLE-STONEV2-README
  - JM-BIBLE-560
related_documents:
  - JM-BIBLE-SETTING-GOV
implementation_status: current
professional_validation: not_required
normative: true
---

# Stone System v2 Governance

The 18 `STONEV2-GOV` rules. These extend, and never replace, the 16
`STONE-GOV` rules in
[`../20-stone/560-stone-governance.md`](../20-stone/560-stone-governance.md) —
every one of those still applies.

---

## STONEV2-GOV-001 — Stone System is category-neutral

Nothing under `backend/jewelmind/stone/`, `backend/jewelmind/geometry/stone/`
or `backend/jewelmind/domain/stone_dimensions.py` may import `jewelmind.ring`,
`jewelmind.earring`, `jewelmind.pendant`, `jewelmind.bracelet`,
`jewelmind.necklace` or `jewelmind.jewelry_category`.

Additionally, nothing in the **core** (`backend/jewelmind/stone/`) may import
`JewelryDefinition`, which would carry an entire category domain across in one
import. `geometry/stone/builder.py` is the sanctioned PLACEMENT adapter and may
read the document to decide where the girdle plane sits — the same division
Sprint 19 drew for `geometry/setting_adapter.py`.

**Enforced by** `backend/tests/test_stone_v2_no_category_dependency.py`, using
AST parsing rather than `import`, so it cannot pass by accident on a module
another test already imported.

**Also enforced:** `build_stone_geometry(stone, girdle_z_mm)` must remain a
category-neutral entry point. Before Sprint 20 the only way to build a stone
was to hand the builder an entire `JewelryDefinition`, which meant no other
category — and no test — could build a stone without fabricating a ring
around it.

---

## STONEV2-GOV-002 — The Stone System must not depend on a finite shape list

After Sprint 20, at least these three escape hatches must remain structurally
present and reachable: `CUSTOM_OUTLINE`, `MEASURED`, `IMPORTED_CAD`.

A change that makes a named-enum cut the only way to obtain stone geometry is a
regression against this sprint's stated objective, regardless of how many cuts
the enum contains.

---

## STONEV2-GOV-003 — Never claim gemological accuracy or a commercial cut

No shape, profile or source models a real facet arrangement, optical behaviour,
commercial cutting proportion, or gemological certification.
`isGemologicalReproduction` is always `false`.

Specifically forbidden: describing `radiant` as the radiant brilliant facet
pattern, `asscher` as the Asscher step cut, `heart` as a commercial heart-cut
proportion, or `CABOCHON_REFERENCE` as a gemological cabochon.

---

## STONEV2-GOV-004 — Software construction constants are never industry standards

Every ratio in `geometry/stone/outline.py` and `geometry/stone/profile.py` is a
fixed SOFTWARE REFERENCE CONSTRUCTION parameter, verified only to produce
robust, deterministic CAD geometry:

| Constant | Value | What it is |
|---|---|---|
| `_RADIANT_CORNER_CLIP_RATIO` | 0.14 | Corner clip fraction |
| `_ASSCHER_CORNER_CLIP_RATIO` | 0.22 | Corner clip fraction |
| `_EMERALD_CORNER_CLIP_RATIO` | 0.18 | Corner clip fraction (Sprint 18) |
| `_TRILLION_BULGE_RATIO` | 0.18 | Side bow fraction |
| `_HEART_LOBE_RADIUS_RATIO` | 0.55 | Lobe circle radius fraction |
| `_SHIELD_SHOULDER_RATIO` etc. | 0.2 / 0.75 / 0.45 | Shield silhouette |
| `_KITE_SHOULDER_RATIO` | 0.25 | Widest-span height |
| `_HEXAGON_SHOULDER_RATIO` | 0.5 | Flank height |
| `CABOCHON_DOME_FRACTION` | 0.75 | Dome height fraction |
| `CABOCHON_DOME_SECTIONS` | 16 | Chosen from a measured convergence run |

The radiant, asscher and emerald clips are deliberately DIFFERENT from each
other so the three shapes stay visually distinguishable. That is a software
choice, not a cut specification.

---

## STONEV2-GOV-005 — Shared geometry never merges two shape identities

Several cuts share a construction primitive:

- `emerald`, `radiant` and `asscher` all use `_clipped_rectangle`
- `baguette` and `princess` are geometrically identical rectangles
- `tapered_baguette` and `trapezoid` both use `_tapered_quadrilateral`

They remain **distinct canonical shape IDs**. A future change to one must not
silently move the other, and a shape must never be aliased away because another
shape happens to build the same geometry today.

---

## STONEV2-GOV-006 — Never invent a missing measurement

A `MEASURED` stone with an absent measurement raises
`MEASURED_STONE_INSUFFICIENT_DATA`. JewelMind never infers a dimension, a
measurement source, a measurement date, or an operator note.

A reference built from dimensions alone is labelled
`MEASURED_DIMENSION_REFERENCE` and must never be presented as the real surface
of the physical stone.

---

## STONEV2-GOV-007 — Generation, setting compatibility and validation are three axes

`generationSupported`, `prongCompatibility`/`bezelCompatibility`, and
`professionalValidationStatus` are independent. A shape that generates real
geometry is not, by that fact, settable; neither implies professional
validation.

The clearest case is `pearl`: it generates a real sphere
(`generationSupported: true`) and both setting families refuse it
(`UNSUPPORTED`), because a sphere has no girdle outline for the current
outline-driven contracts to grip.

Every entry is `NOT_REVIEWED` and must stay so until a real `ValidationRecord`
with real evidence exists (PROVAL-GOV-006).

---

## STONEV2-GOV-008 — Stone shape is a CUT, never a gem species

`stone.shape = "emerald"` is the clipped-corner rectangular outline. The gem
species emerald is a different concept entirely, arriving in Sprint 21.

For the same reason the rhombus is named `lozenge` and never `diamond`. No
shape synonym may resolve a gem species name to a cut, and `StoneSpec` carries
no material or species field.

**Enforced by** `test_stone_v2.py::TestShapeVersusGemIdentity`.

---

## STONEV2-GOV-009 — Anchors are geometric facts, never prong positions

A `StoneAnchor` records where a feature of the outline is. The Setting System
decides whether to put metal there.

Anchors are derived from the REAL normalized outline points, never from nominal
dimensions — which matters for a shape whose extreme is not at a vertex
(`half_moon`'s elliptical arc) and for custom outlines, where nominal
dimensions do not exist.

An anchor a shape genuinely does not have is ABSENT, never approximated. A
custom outline has no deterministic TIP; a pearl has no anchors at all.

---

## STONEV2-GOV-010 — Never silently substitute geometry

- An imported asset IS the stone. It is placed, never replaced by a native
  approximation.
- A shape × profile combination the shape does not support raises
  `STONE_SHAPE_PROFILE_COMBINATION_UNSUPPORTED` when the profile was
  **explicitly requested**.
- A profile left at its schema default MAY be resolved to the shape's single
  supported profile — but only then, and the resolution is recorded in
  `normalizationOperations` as `PROFILE_DEFAULTED:<from>-><to>`. A recorded
  default is disclosure; an unrecorded one is substitution.
- A construction failure raises `STONE_SHAPE_GENERATION_FAILED`, never a
  fallback to a different shape.

---

## STONEV2-GOV-011 — Never invent a professional threshold, and scope rules honestly

A Forge rule is evaluated only where its premise holds. Sprint 20 scoped two:

- `STONE_DEPTH_RANGE` is skipped for `SPHERICAL_REFERENCE`. A sphere's depth IS
  its horizontal extent, so the rule could never pass for a valid pearl. It was
  scoped away rather than loosened, which would have weakened it for every
  other shape.
- Both dimension rules are skipped for `IMPORTED_CAD`, whose true dimensions
  are a property of the asset rather than of the document.

Real, recorded gaps that must NOT be closed by inventing a number: `pearl` has
no diameter-range rule, and a non-round shape's `length`/`width` still have none
individually.

---

## STONEV2-GOV-012 — Requested dimensions must equal measured dimensions

Every native outline is built so its real bounding box equals the request.
Reporting a nominal dimension while building something else is forbidden.

Three shapes violated this during Sprint 20 development and each was fixed at
the source, not by adjusting the report: `shield` (an arc-based lower boundary
measured 6.05mm for a 6.00mm request), `trillion` (7.63mm for 7.00mm),
`half_moon` (7.50mm for 6.00mm), and `heart` (an unconverged normalization left
an 8×6 heart 3.3e-4mm too wide).

**Enforced by**
`test_stone_v2.py::test_requested_dimensions_equal_measured_dimensions` for
every shape.

---

## STONEV2-GOV-013 — Every outline is centred on the local origin

The canonical stone frame places the outline's bounding-box centre at the local
origin. That is the frame `_apply_orientation()` rotates about and the frame
`StoneSettingReference.centerXMm/centerYMm` reports. An off-centre outline
silently displaces the stone and every component built around it.

`half_moon` genuinely violated this: `ellipseArc(..., startAtCurrent=False)`
centres the ellipse on the CURRENT point, so the outline sat entirely below the
origin while still reporting a correct bounding-box SIZE. Checking size alone
would have missed it.

**Enforced by**
`test_stone_v2.py::test_outline_is_centred_on_the_local_origin`.

---

## STONEV2-GOV-014 — B-Rep and mesh capabilities are never conflated

An `IMPORTED_CAD` asset reports its real `StoneRepresentation`, determined by
PARSING the asset rather than from its extension.

A `MESH` import has zero solids, no reliable volume, and no B-Rep operations.
`supportsBrepOperations` reports that from the real parsed result. An STL must
never be described as having the capabilities of a STEP solid.

**A mesh must also be TRANSFORMED node by node.** Neither
`cadquery.Shape.scale()` nor `BRepBuilderAPI_Transform` moves a triangulation
attached to an otherwise-empty face — measured on a real STL, both returned an
unchanged bounding box after a requested 10× scale.

---

## STONEV2-GOV-015 — Provenance must be true, and must be stable

`StoneSourceProvenance.normalizationOperations` records every operation
ACTUALLY applied. An entry claiming an operation the geometry did not receive is
a worse defect than a missing entry, and Sprint 20 shipped exactly that bug
briefly for mesh unit conversion.

Provenance carries **no wall-clock timestamp**. It participates in
`definitionHash` and in Golden snapshots, so a clock reading would make
identical geometry hash differently between runs. A caller-supplied
`measurementDate` is a stable data value and is allowed.

`sourceAssetHash` is a content hash, never a filesystem path
(FOUNDRY-GOV-011).

---

## STONEV2-GOV-016 — Imported assets are untrusted input

Every safeguard exists because a stone file arrives from outside JewelMind:

- assets are addressed by CONTENT HASH, validated as hexadecimal, so path
  traversal is structurally impossible rather than merely filtered;
- file size, triangle count and face count are bounded, checked AFTER parsing
  as well as before, because a small file can expand into a large mesh;
- every parser exception becomes a structured error whose message contains no
  stack trace, no library output and no server path;
- an unsupported format is refused at STORE time, with the real per-format
  reason;
- nothing in a stone file is ever executed. Only geometry is read.

---

## STONEV2-GOV-017 — Preserve Stone v1 exactly

Every Stone v1 capability must keep working, and `round`'s plain faceted
parametric path must keep producing byte-identical geometry through
`_build_round_stone()`.

Round's fast path is a GEOMETRY guarantee, not a performance note: its culet
radius is ABSOLUTE (0.05mm) while the shared pipeline's is PROPORTIONAL, which
makes the shared body about 1.8% larger. Routing round through the shared
pipeline "for consistency" would silently change every existing round model.

Target and result: **zero** Stone v1 Golden baseline updates.

---

## STONEV2-GOV-018 — New capability requires registry, inspection, test and Golden coverage

A new shape, profile or source mode requires, in the same change:

1. an entry in `jewelmind/stone/capability.py` with honest status;
2. the mirrored `specs/stone/v2/` registry regenerated from it;
3. real Geometry Inspection facts;
4. tests, including a requested-equals-measured dimension assertion;
5. its own NEW Golden case — never a retrofit of an existing one;
6. an entry in `specs/capabilities/jewelmind-capabilities.json`.

A capability marked `CURRENT` without a real generator AND real tests is a
governance violation.

---

## When an ADR is required

- Changing the LENGTH/WIDTH/DEPTH axis mapping or the orientation convention.
- Replacing the outline-plus-profile model with a different construction model.
- Moving `domain/stone_dimensions.py` out of the `domain/` layer.
- Introducing a `FACETED_GEM_MODEL` or `SCANNED_MESH` layer.
- Letting the Stone System write to a JDL path directly.
- Any change violating STONEV2-GOV-001 through 018 without superseding this
  document first.

## When an RFC is required

- A new stone shape beyond the 21 implemented (see `RESERVED_STONE_SHAPES`).
- Multi-stone arrangements (halo, pavé, three-stone).
- A new import format, or a real scan-processing pipeline.
- Curve-segment or SVG custom outline input.
