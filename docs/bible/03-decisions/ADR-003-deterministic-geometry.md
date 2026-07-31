---
id: JM-BIBLE-ADR-003
title: "ADR-003: Deterministic geometry generation"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on:
  - JM-BIBLE-ADR-001
related_documents:
  - JM-BIBLE-003
  - JM-BIBLE-004
implementation_status: current
---

# ADR-003: Deterministic geometry generation

## Status

Accepted.

## Context

A CAD tool whose output can silently vary for the same input is
untrustworthy — a user (or a manufacturer downstream) needs to know that
re-generating from the same JSON definition, on any machine, produces the
same physical result. Generative/AI models, by contrast, are naturally
non-deterministic and are increasingly easy to reach for.

## Decision

Geometry generation must be **fully deterministic**: no randomness, no
wall-clock-time dependency, no network calls, and specifically **no LLM
or other generative model** may decide any dimension, shape, or placement
at runtime. The same `JewelryDefinition` must always produce the same
geometry, volumes, and `definitionHash`.

## Alternatives considered

- **Using an LLM to "suggest" or refine dimensions/placement at generation
  time** (e.g. to auto-tune prong placement). Rejected outright — this is
  [LAW-003](../00-foundation/004-jewelmind-constitution.md#LAW-003); it
  was considered as a way to add design flexibility but rejected because
  it would make the same input produce different, unpredictable output
  across runs or model versions.
- **Allowing limited randomness for cosmetic variation** (e.g. slightly
  randomized fillet placement for a "hand-finished" look). Rejected: even
  cosmetic non-determinism breaks reproducibility and definition-hash
  caching (`services/model_service.py`), and was judged not worth the
  cost for a prototype whose main goal is correctness, not stylistic
  variety.
- **Deterministic, fixed CadQuery code paths (the chosen path).**
  Selected.

## Positive consequences

- `definitionHash` (`utils/hashing.py`) can serve as a reliable cache key
  and model identity — regenerating the same input reuses the cached
  model instead of creating a duplicate.
- Geometry is exactly unit-testable: `test_geometry.py` asserts specific
  volumes and bounding boxes, which would be meaningless against
  non-deterministic output.
- A generated file can be trusted to represent exactly what the
  definition describes, every time.

## Negative consequences

- Less "creative" flexibility than a generative approach might offer —
  every variation must be expressed as an explicit parameter or rule,
  not discovered by a model.
- Adding a new stylistic option always requires a new parameter and
  possibly a new validation rule, rather than a prompt tweak.

## Risks

- Future pressure to "just let AI handle the edge cases" in geometry
  construction must be resisted without a new ADR explicitly reversing
  this decision — a high bar, given how central determinism is to every
  other Constitution law and test in the geometry pipeline.

## Review trigger

Revisit only if a future product direction explicitly wants
non-deterministic or AI-assisted geometry as a distinct, clearly-labeled
mode — never as a silent default.

## Related implementation files

`backend/jewelmind/geometry/`, `backend/jewelmind/utils/hashing.py`.

## Related tests

`backend/tests/test_geometry.py::test_definition_hash_is_deterministic`,
`test_definition_hash_changes_with_input`.
