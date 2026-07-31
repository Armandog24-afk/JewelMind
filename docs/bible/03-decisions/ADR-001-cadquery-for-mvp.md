---
id: JM-BIBLE-ADR-001
title: "ADR-001: CadQuery for the MVP geometry engine"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on: []
related_documents:
  - JM-BIBLE-020
  - JM-BIBLE-ADR-002
  - JM-BIBLE-ADR-003
implementation_status: current
---

# ADR-001: CadQuery for the MVP geometry engine

## Status

Accepted.

## Context

JewelMind needs to construct real, exact, exportable solid geometry (not
just a visual mesh) for a parametric ring, headlessly, from a Python
backend, without requiring a licensed desktop CAD application to be
running.

## Decision

Use **CadQuery**, a Python library built on the **OpenCascade** B-Rep
kernel, as the sole geometry engine.

## Alternatives considered

- **A commercial CAD application's scripting API (Rhino/Grasshopper,
  MatrixGold, JewelCAD).** Rejected: requires a licensed, interactive
  desktop application to be running, which is incompatible with a
  headless server and with the goal of not requiring paid CAD software
  for the MVP (see [ADR-002](ADR-002-no-rhino-runtime-dependency.md)).
- **A mesh-only approach (build triangulated meshes directly, e.g. with
  `trimesh` or hand-rolled mesh math).** Rejected: meshes are an
  approximation; exact B-Rep solids are needed for a real STEP export
  and for reliable boolean operations (fusing band/prongs/basket).
- **Writing directly against the OpenCascade Python bindings (OCP/pythonOCC)
  without CadQuery's higher-level API.** Rejected for the MVP: CadQuery's
  fluent `Workplane` API is significantly faster to write and read
  correctly than raw OCP calls, at negligible cost since CadQuery is
  itself a thin, well-tested layer over the same bindings.

## Positive consequences

- Headless, no GUI, no license required — installs via plain `pip install
  cadquery`, verified directly to pull prebuilt wheels with no compilation
  step (`docs/development.md`).
- Real B-Rep solids, so STEP export is exact, not an approximation.
- Same category of geometry kernel used inside professional CAD systems,
  lending real technical credibility to the output.

## Negative consequences

- CadQuery/OpenCascade has a learning curve and idiosyncratic boolean
  operation behavior (see the embedding technique in
  `geometry/constants.py::EMBED_MM`, needed because tangent-touching
  solids don't fuse cleanly).
- Larger dependency footprint (CadQuery pulls in VTK and other
  transitive dependencies) than a pure-mesh approach would need.

## Risks

- OpenCascade/VTK's native shared-library dependencies must be present in
  any deployment environment (see the apt package list in
  `backend/Dockerfile` and the CI job in
  [`024-runtime-and-deployment.md`](../02-architecture/024-runtime-and-deployment.md)).
  If missing, the CAD engine fails to load — handled explicitly by
  `services/cad_engine.py`, not treated as a crash.

## Review trigger

Revisit if CadQuery's OpenCascade wheel availability becomes unreliable
on a target platform, or if a future jewelry-type expansion needs geometry
CadQuery cannot express reasonably.

## Related implementation files

`backend/jewelmind/geometry/`, `backend/requirements.txt`,
`backend/jewelmind/services/cad_engine.py`.

## Related tests

`backend/tests/test_geometry.py` (14 tests); CadQuery readiness:
`backend/tests/test_api_hardening.py::test_probe_cad_engine_succeeds_in_this_environment`.
