# Known limitations

JewelMind's first milestone is a **technical prototype**. Generated
geometry, dimensions, tolerances, stone settings, and manufacturing
suitability all require review by a qualified jewelry CAD designer, stone
setter, or manufacturing specialist before any production use. This applies
to every limitation below and to the design as a whole.

## Geometry

- **Stone reference is not a gemological reproduction.** It is a simplified
  lofted approximation (culet → pavilion → girdle → crown → table) sized
  from the stone's resolved LENGTH/WIDTH/DEPTH using fixed proportion
  constants (`_CROWN_FRACTION = 0.35`, `_PAVILION_FRACTION = 0.65`,
  `_TABLE_TO_GIRDLE_RATIO = 0.56` in
  `backend/jewelmind/geometry/stone/builder.py`). It does not represent
  real faceting, optical properties, or actual commercial-cut proportions,
  for **any** of the 7 shapes. `isGemologicalReproduction` is always
  `false`. The shape names (`emerald`, `princess`, `marquise`, …) denote
  the *outline*, never a certified cut — an `emerald` reproduces the
  clipped-corner silhouette but none of the stepped faceting that defines
  a real emerald cut. See `docs/bible/20-stone/README.md`.
- **Only round stones have a setting designed for them.** All 7 shapes
  generate real geometry, but `currentSettingCompatibility` is
  `EXPERIMENTAL` for oval, pear, emerald, cushion, princess, and marquise:
  the current prong layout is a generic circular placement derived from
  the stone's width, so marquise/pear tips and angular-stone corners are
  left unsupported. A shape generating correctly is **not** a claim that
  its setting is valid. See
  `docs/bible/20-stone/575-stone-capability-model.md`.
- **Pear's outline is a simplified non-tangent silhouette** — two straight
  sides meeting a rounded end at a non-zero angle, rather than the smooth
  continuous curve of a real pear.
- **Prongs are simplified vertical cylinders**, not tapered/shaped
  prongs as a bench jeweler would cut them, and their contact with the
  stone is geometric overlap, not a modeled seat or bearing cut.
- **Basket support is a plain cylindrical shell**, not a decorative or
  weight-optimized structure. It was chosen for robustness (guaranteed
  valid, guaranteed connected geometry) over decorative accuracy — see
  `docs/geometry-conventions.md`.
- **Band fillets can silently fall back.** The flat profile's optional
  outer-rim fillet is wrapped in a try/except; if OpenCascade's fillet
  operation fails for a given combination of parameters, the builder falls
  back to sharp unfilleted edges and records a warning in the generated
  model's `warnings` list (and in the technical specification export).
  Comfort-fit's inner arc does not use a fillet and has no such fallback
  path.
- **Tapered bands never apply the outer-rim fillet.** When a real width
  and/or thickness taper is requested (`band.widthTaper`/
  `band.thicknessTaper`, Sprint 17), the shank is built as a
  multi-section loft rather than a solid of revolution, so there is no
  single "circle at radius X" to select for a fillet. This is a real v1
  limitation, always recorded (`filletApplied: false`, an explicit
  `filletSkippedReason`) — see
  `docs/bible/19-shank/545-section-profile-contract.md`.
- **No manufacturing-grade tolerancing.** Wall thicknesses, minimum
  feature sizes, and draft angles are not validated against any specific
  casting house's or printer's process capabilities beyond the conservative
  thresholds in `docs/validation-rules.md`.
- **Metal choice is cosmetic only.** `material.metal` changes the preview
  color; it does not change density, shrinkage, or casting behavior in any
  exported file.

### Extended Setting Modes (Sprint 27)

- **A tension setting's structural behaviour is not modelled.** JewelMind builds
  the two opposing supports as real solids and computes nothing about the
  elastic response of the metal, the force they apply, or whether the stone
  would be retained under load, wear or impact. That is why the mode is PARTIAL
  rather than CURRENT, why `professionalReviewRequirement` is `REQUIRED`, why
  the component metadata carries `structuralBehaviourModelled: false`, and why
  `JM-SETTING-012` says a qualified professional must review it. No stress
  threshold, spring constant or safety factor exists anywhere, and none may be
  invented: it would be a fabricated professional claim about whether jewelry
  holds a stone.
- **A shared prong's position is stated, not derived.** `PRONG_SHARED` builds
  real prongs at EXPLICIT positions carrying `servesStoneInstanceIds`. Whether
  a shared prong actually reaches both stones it names is a geometric fact for
  inspection rather than a guarantee, because deriving the position from two
  stones' own geometry needs anchor-driven placement, which does not exist. No
  interface authors explicit positions, so Studio, Designer and Conversation
  are PLANNED for this one mode.
- **Metal is generated for the design's own stone only.** A channel or bar row
  spanning arrangement instances records which instances it holds and does not
  build a separate setting per instance
  (`SETTING_COVERAGE_PRIMARY_ONLY`). Closing this needs the setting strategy for
  a non-primary member that Sprint 24 identified as an RFC.
- **No minimum wall, bar, collar, clearance or spacing is enforced anywhere.**
  Every dimension in a setting mode is a software CONSTRUCTION PARAMETER. No
  sourced professional minimum exists for any of them, so none is asserted —
  the same documented gap the bezel has carried since Sprint 19.
- **`REFERENCE_SEAT` relief is not a cut seat.** It removes the stone's own
  volume from the metal. It has no bearing shoulder, and no claim is made that a
  stone would sit correctly in it. `bearingSupport` and `cutterSupport` remain
  PLANNED for all six families.
- **Fifteen setting techniques are reserved, not built** — a trellis head,
  azure piercing, shared-wall and tapered channels, tapered bars, millgrain, an
  open-back bezel, an under-gallery support, retention for a halo's own stones,
  compass-point prongs, and channel/bar as pavé retention. Each has a recorded
  technical reason in `setting/modes.py::RESERVED_SETTING_MODES`, and each is
  refused by the model rather than silently substituted.
- **`GeometryPlan` is still not materialized.** Component provenance lives on
  `SettingGeometryResult` instead. Materializing `GeometryPlan` is an explicit
  ADR condition and nothing in this sprint needed it.


### Ring families (Sprint 28)

- **A halo generates no metal to hold its stones.** The halo stones are real
  solids at real radii, derived from the centre stone; nothing retains them.
  This is why the `halo` ring family is PARTIAL rather than CURRENT, and it is
  Sprint 25's own recorded boundary, unchanged.
- **A signet table is flat and rectangular, and cannot be decorated.** No
  engraving, relief or texture representation exists anywhere in the pipeline.
  The `SIGNET_TABLE_ENGRAVED` inspection fact reports `false` for exactly this
  reason, so a flat table is never mistaken for a finished signet.
- **A shoulder arch cannot span more than 90 degrees.** Past a quarter turn the
  ruled loft's two end sections have rotated past each other and the loft
  self-intersects — silently, because OpenCascade's own validity check passes
  the individual solid and only the ring's combined metal reports invalid. The
  span is refused as a precondition in both the schema and the builder. A wider
  shoulder needs a swept solid along a 3D spline, which does not exist.
- **A bypass at a very small crossing clearance defeats the ring-level boolean
  fuse.** At roughly 0.07 mm the fuse returns a degenerate result — negative
  volumes, components gone — without raising. It is now DETECTED (a union cannot
  be smaller than its largest input) and the export falls back to a real
  multi-solid compound with a warning, so nothing broken ships silently; but the
  single fused solid is not produced for that configuration.
- **Only two rails.** A split shank builds exactly two; three or more need their
  own axial layout and bridge.
- **Nine families and variants are reserved and cannot be built** — `eternity`,
  `toi_et_moi`, `cluster`, `plain_band`, `SOLITAIRE_TRELLIS`,
  `SPLIT_SHANK_SCULPTED`, `BYPASS_TWIST`, `SIGNET_ENGRAVED`,
  `SIGNET_OVAL_TABLE`. Each records its real technical reason; see
  [`docs/bible/30-ring-families/coverage-review.md`](bible/30-ring-families/coverage-review.md).
- **No ring dimension is professionally validated.** No rail width, shoulder
  proportion, signet table thickness or crossing clearance is judged anywhere,
  and every variant is `NOT_REVIEWED`.


### Specialty rings (Sprint 29)

- **No metal holds a cluster's or a toi-et-moi's accent stones.** They are real
  solids in the right places and only the CENTRE stone is set. This is why both
  families are PARTIAL, and it is the Multi-Stone Family layer's own recorded
  boundary from Sprint 24.
- **A toi-et-moi's two stones cannot have different cuts.** They can differ in
  size and in gem identity; both are occurrences of the document's single
  `stone`, because a family member carries no shape. The classic oval-and-pear
  pair therefore is not expressible.
- **An eternity ring still carries a centre stone and a head.** A true eternity
  band has neither, but `REQUIRED_COMPONENT_NAMES` includes `stone_reference`
  and `basket_support`, so a stone-less ring is not representable — the same
  blocker that reserves `plain_band` and the stacking band.
- **No channel-set band.** The setting system's channel walls are straight
  prisms in the stone's own frame and cannot follow the band's curve.
- **No stacking band, and no tension-style family.** The first needs the
  stone-less ring above; the second would only rename the `tension` setting
  family, which already builds that geometry.
- **No specialty dimension is professionally validated.** No stone spacing, bead
  size, cluster density or stone-security judgment is asserted anywhere, and
  every variant is `NOT_REVIEWED`.

## Preview / export

- **GLB export was not implemented.** The preview pipeline was evaluated
  against packaging all components into a single GLB, but CadQuery's GLB
  export path was judged unreliable for this milestone's timeline. Instead,
  each component (band, stone_reference, prongs, basket_support) is
  tessellated to its own binary STL file, tied together by a small JSON
  manifest (`previewComponents` in the generate response). The frontend
  fetches and parses these STL files directly. This is explicitly allowed
  by the product spec as the fallback strategy.
- **Combined STL/STEP metal export depends on a successful boolean fuse.**
  `geometry/assemblies/solitaire.py` tries to fuse band + basket + prongs
  into one solid; if the fuse fails for a given input, it falls back to
  exporting all three as a multi-solid compound in the same file (no
  component is dropped) and records a warning.
- **No manufacturing-readiness claim is ever made.** Every technical
  specification export repeats the professional-review disclaimer
  verbatim.

## API / infrastructure

- **In-memory model cache, not persistent storage.** Generated models
  (and their preview/export temp files) live in server process memory,
  capped at 20 entries (`MAX_CACHED_MODELS` in
  `backend/jewelmind/services/model_service.py`) with LRU eviction.
  Restarting the backend clears all generated models; clients must
  regenerate. There is no database in this milestone.

  The cache is keyed on `compilationHash` (design identity plus the
  compiler, Forge rule-set, generator and kernel/OCP versions), not on
  `definitionHash` alone — see
  [`ADR-012`](bible/03-decisions/ADR-012-compilation-hash-as-cache-key.md).
  That distinction was closed while the cache was still volatile,
  specifically so a future durable cache cannot inherit the ambiguity and
  serve geometry no current code would produce.
- **Docker build has not been executed end-to-end.** Docker was not
  available in the environment this project was built and tested in. The
  backend and frontend were both fully built, tested, and manually verified
  running directly (Python venv + Node dev server) instead. `docker-compose.yml`
  and both Dockerfiles were written and reviewed against that verified
  local setup, but `docker compose up --build` itself has not been run.
  If it fails to build cleanly, the most likely culprits are missing
  system libraries for OCP/VTK in the backend image (see
  `backend/Dockerfile`'s apt package list) — start there.
- **Frontend Docker image runs the Vite dev server**, not a production
  build served by a lightweight web server (e.g. nginx). Fine for this
  milestone; a follow-up should add a multi-stage build that runs
  `npm run build` and serves `dist/` statically.
- **No authentication, multi-user isolation, or persistence.** Out of
  scope by design for this milestone (and explicitly excluded from the
  product spec).

## Domain model

- **No shared-schema codegen.** `backend/jewelmind/domain/schema.py`
  (Pydantic) and `shared/types/jewelry-definition.ts` (TypeScript) are kept
  in sync by hand. A schema change requires updating both, plus
  `shared/validation/*` if it affects validation rules.
- **EU/French sizing convention only.** `ring.sizeSystem` is fixed to
  `"EU"` in this milestone; the size ↔ diameter conversion
  (`size = π·diameter − 40`) assumes the French/EU civil sizing convention,
  not the German convention (where size equals circumference directly) —
  see `docs/validation-rules.md` (JM-RING-003).
- **Six setting families, not two.** Sprint 19 added `bezel` and Sprint 27
  added `channel`, `bar`, `flush` and `tension`, each with a real registered
  generator. Prong counts are still exactly 4 or 6 (`JM-PRONG-001`), and the
  stone shape enum has covered 21 cuts plus custom and imported sources since
  Sprint 20 — this bullet previously said "only round stones and 4/6-prong
  solitaire settings", which had been stale since Sprint 18.
