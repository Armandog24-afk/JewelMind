---
id: JM-BIBLE-ADR-008
title: "ADR-008: Monorepo architecture"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on: []
related_documents:
  - JM-BIBLE-020
  - JM-BIBLE-021
implementation_status: current
---

# ADR-008: Monorepo architecture

## Status

Accepted.

## Context

JewelMind consists of one frontend and one backend that must stay tightly
in sync on one thing in particular: the canonical `JewelryDefinition`
shape and its validation rules (see
[ADR-005](ADR-005-canonical-jewelry-definition.md)). They are developed,
tested, and deployed together at this stage.

## Decision

Keep `frontend/`, `backend/`, and `shared/` in **one repository**, with
one root `docker-compose.yml` and one CI workflow — no microservices, no
separate repositories per service.

## Alternatives considered

- **Separate repositories for frontend and backend.** Rejected: would
  require a versioning/publishing step for `shared/` (or its equivalent)
  to keep the two schemas in sync, adding process overhead disproportionate
  to a two-service system with one team.
- **A microservices split** (e.g. separate generation, export, and
  validation services). Rejected: no current requirement for independent
  scaling or independent deployment of these concerns; the added
  operational complexity (service discovery, network boundaries between
  what are today simple function calls) is not justified at this stage.
- **One monorepo, one frontend, one backend (the chosen path).** Selected.

## Positive consequences

- `shared/` can be imported directly by the frontend via a path alias, no
  publishing step (see
  [`024-runtime-and-deployment.md`](../02-architecture/024-runtime-and-deployment.md)
  for how this works in Docker too).
- One CI workflow, one Docker Compose file, one place to look for
  "how do I run this."
- Changes that span both services (e.g. a new schema field) are one
  pull request, not a cross-repository coordination problem.

## Negative consequences

- Cannot version or deploy the frontend and backend independently.
- A single CI run covers both services, so an unrelated frontend failure
  can block a backend-only change's pipeline from going fully green (and
  vice versa) — mitigated by the jobs being independent
  (`backend`/`frontend` run in parallel; `docker-smoke-test` needs both).

## Risks

- If JewelMind grows enough to need independent scaling of backend
  generation load separately from the frontend, this decision would need
  revisiting — a new ADR, given how much of the current developer
  workflow (`docs/development.md`, `Makefile`) assumes the monorepo shape.

## Review trigger

Revisit if independent deployment cadence or scaling becomes a genuine
operational need.

## Related implementation files

Repository root layout; `docker-compose.yml`; `.github/workflows/ci.yml`.

## Related tests

Not directly testable; reflected in the CI workflow structure
(`backend` and `frontend` jobs run independently within one workflow
file).
