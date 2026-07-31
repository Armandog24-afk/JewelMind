---
id: JM-BIBLE-ADR-010
title: "ADR-010: STEP and STL as the export strategy"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on:
  - JM-BIBLE-ADR-002
related_documents:
  - JM-BIBLE-004
  - JM-BIBLE-026
implementation_status: current
---

# ADR-010: STEP and STL as the export strategy

## Status

Accepted.

## Context

A user needs to take a generated design out of JewelMind and into
whatever downstream tool a manufacturer or another CAD package uses. That
downstream tool is not JewelMind's choice to make, and per
[ADR-002](ADR-002-no-rhino-runtime-dependency.md), JewelMind must not
require any specific commercial CAD package to be part of that path.

## Decision

Export exactly two geometry formats, both vendor-neutral and near-
universally supported: **STEP** (exact B-Rep solid, ISO 10303) for
further CAD work, and **STL** (triangulated mesh) for 3D printing and
generic mesh consumers. No native Rhino (`.3dm`) or MatrixGold project
export exists or is planned for the MVP.

## Alternatives considered

- **Native Rhino (`.3dm`) or MatrixGold export.** Rejected: would tie
  JewelMind's output to a specific vendor's format, working against
  [ADR-002](ADR-002-no-rhino-runtime-dependency.md)'s reasoning even
  though it wouldn't require running that vendor's software to *produce*
  the export — it would still lock the *consumer* into that ecosystem to
  get full fidelity.
- **STL only (no STEP).** Rejected: STL is a mesh approximation; a
  professional doing further exact CAD work needs the real B-Rep solid,
  which only STEP provides.
- **STEP only (no STL).** Rejected: STL is the practical format for 3D
  printing (relevant to the `direct_resin_printing` manufacturing method)
  and for lightweight mesh consumers that don't need exact B-Rep.
- **Both STEP and STL, stone excluded by default (the chosen path).**
  Selected — covers both the "further exact CAD work" and "3D
  printing/mesh" use cases with formats every relevant downstream tool
  already supports.

## Positive consequences

- No JewelMind user is required to own or use any specific downstream CAD
  package to get useful output.
- STEP and STL together cover both major "what happens next" paths
  (further CAD editing, or manufacturing/printing) without extra formats
  to maintain.
- Reusing the same STL export code path for both download and preview
  tessellation (see
  [ADR-007](ADR-007-backend-generated-preview.md)) keeps one code path
  well-tested instead of two similar ones.

## Negative consequences

- A user whose downstream tool works best with a native format (e.g.
  Rhino's `.3dm`) must go through an import step (STEP -> their tool),
  rather than a direct native open.
- No PDF or 2D technical drawing export exists yet (the technical
  specification is Markdown text, not a dimensioned drawing) — see
  [`026-known-technical-limitations.md`](../02-architecture/026-known-technical-limitations.md).

## Risks

- If a specific manufacturing partner requires a format neither STEP nor
  STL satisfies, that would need its own ADR to add — not a quiet new
  exporter.

## Review trigger

Revisit if a concrete, recurring need for a native or additional format
(e.g. `.3dm`, IGES, 3MF) emerges from actual usage.

## Related implementation files

`backend/jewelmind/exporters/step_exporter.py`,
`backend/jewelmind/exporters/stl_exporter.py`.

## Related tests

`backend/tests/test_api.py::test_export_step_returns_nonempty_file`,
`test_export_stl_returns_nonempty_file`;
`backend/tests/test_api_hardening.py` (unique-temp-file and tolerance-
validation tests for both formats).
