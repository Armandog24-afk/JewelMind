# `specs/stone/v2/` — Stone System v2 machine-readable contracts

The machine-readable half of
[`docs/bible/22-stone-v2/`](../../../docs/bible/22-stone-v2/README.md).

Stone System v2 (Sprint 20) extends the Stone System from a finite list of
seven built-in cuts into a **shape-agnostic** gemstone geometry subsystem. The
architectural point of the sprint is the last three source modes below: after
Sprint 20, JewelMind can work with a stone **even when that stone corresponds
to no built-in named cut**.

## The two independent axes

Everything here follows from one decision (see
[`stone-profile-v2.md`](../../../docs/bible/22-stone-v2/stone-profile-v2.md)):

| Axis | Field | Values |
|---|---|---|
| Outline shape | `stone.shape` | 21 named cuts, plus `custom` / `imported` |
| 3D reference profile | `stone.profile` | `FACETED_REFERENCE`, `CABOCHON_REFERENCE`, `SPHERICAL_REFERENCE` |

Modelling these separately is why there is no `OVAL_CABOCHON` shape: an oval
cabochon is `shape=oval` + `profile=CABOCHON_REFERENCE`. Without the split, every
new profile would multiply the shape list.

## The four source modes

| Mode | Status | Geometry comes from |
|---|---|---|
| `PARAMETRIC_REFERENCE` | CURRENT | A named cut plus explicit dimensions |
| `CUSTOM_OUTLINE` | CURRENT | Caller-supplied validated outline points |
| `MEASURED` | CURRENT | Real measurements of a real physical stone |
| `IMPORTED_CAD` | PARTIAL | An external STEP/BREP/STL asset |

`SCANNED_MESH` is deliberately **not** a mode: a scan arrives as a mesh or a
converted CAD file, and adding a fifth mode would duplicate `IMPORTED_CAD`'s
pipeline without adding meaning. Scan-specific processing is `PLANNED`.

## Files

### Schemas

| File | Contract |
|---|---|
| `stone-source.schema.json` | The `StoneSourceMode` enum |
| `stone-profile-v2.schema.json` | The `StoneReferenceProfile` enum |
| `parametric-stone-source.schema.json` | A named cut plus dimensions |
| `custom-outline.schema.json` | A closed 2D outline (ordered points only) |
| `custom-outline-stone.schema.json` | A stone defined by a custom outline |
| `measured-stone.schema.json` | A measured physical stone |
| `imported-stone.schema.json` | An externally supplied asset reference |
| `stone-source-provenance.schema.json` | Where geometry came from |
| `extended-shape-capability.schema.json` | One shape's real capabilities |
| `stone-anchor.schema.json` | A named point on the outline |
| `stone-outline.schema.json` | The normalized outline every consumer reads |
| `normalized-stone-definition.schema.json` | The single canonical internal model |

### Registries

Generated from the live code, never hand-maintained:

- `shape-registry-v2.json` — every shape's real capabilities, plus the
  reserved shapes JewelMind deliberately does not build.
- `stone-source-registry.json` — source modes, the import formats this build
  can genuinely parse (and why the others are refused), and the resource limits
  applied to untrusted input.
- `setting-compatibility-v2.json` — the full Stone × Setting matrix.

### Examples and test vectors

Every example and vector is produced by **running the real implementation**
(JDL-GOV-009). None is hand-typed. `custom-outline-invalid.json` records the
real error code and message for each rejected outline, so the validation
contract cannot drift silently.

## Rules this specification enforces

- **Requested dimensions equal measured dimensions.** Every native outline is
  built so its real bounding box equals the request. Three shapes broke this
  during development (`shield`, `trillion`, `half_moon` overshot by
  construction; `heart` by an unconverged normalization) and each was fixed at
  the source rather than by reporting the nominal value.
- **No fabricated equivalent diameter.** An oval 8 × 6 is never collapsed to a
  single diameter to satisfy a round-only rule.
- **Shape is a cut, never a gem species.** `emerald` is the clipped-corner
  outline; the rhombus is `lozenge`, never `diamond`. Gem identity arrives in
  Sprint 21.
- **No invented measurement.** A measured stone with no supplied measurement is
  an error, never a guess. A dimension-only reference is labelled
  `MEASURED_DIMENSION_REFERENCE` and is explicitly not a model of the physical
  stone's surface.
- **No guessed units.** An imported asset's unit is declared by the caller and
  recorded in provenance.
- **B-Rep and mesh are never conflated.** An STL import reports
  `representation: MESH`, `solidCount: 0` and a null volume — the honest result.
- **Nothing here is professionally validated.** Every shape, profile and source
  is `NOT_REVIEWED`.

## Cross-references

- [`docs/bible/22-stone-v2/README.md`](../../../docs/bible/22-stone-v2/README.md)
  — the authoritative specification.
- [`specs/stone/v1/`](../v1/README.md) — Stone v1, still accurate for the seven
  original shapes.
- [`specs/setting/v1/`](../../setting/v1/README.md) — the Setting System that
  consumes `stone-outline.schema.json`.
