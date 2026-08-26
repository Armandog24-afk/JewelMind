# Known limitations

JewelMind's first milestone is a **technical prototype**. Generated
geometry, dimensions, tolerances, stone settings, and manufacturing
suitability all require review by a qualified jewelry CAD designer, stone
setter, or manufacturing specialist before any production use. This applies
to every limitation below and to the design as a whole.

## Geometry

- **Stone reference is not a gemological reproduction.** It is a simplified
  lofted approximation (culet → pavilion → girdle → crown → table) sized
  from `stone.diameter`/`stone.depth` using fixed proportion constants
  (`_CROWN_FRACTION = 0.35`, `_PAVILION_FRACTION = 0.65`,
  `_TABLE_TO_GIRDLE_RATIO = 0.56` in
  `backend/jewelmind/geometry/components/stone.py`). It does not represent
  real faceting, optical properties, or actual round-brilliant-cut
  proportions.
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
- **Only round stones and 4/6-prong solitaire settings.** These are the
  only values the geometry pipeline and validation rules support in this
  milestone, per the product spec.
