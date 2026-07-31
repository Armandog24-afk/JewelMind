---
id: JM-BIBLE-010
title: User Problems
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on: []
related_documents:
  - JM-BIBLE-011
  - JM-BIBLE-012
implementation_status: current
---

# User Problems

These are the problems the current solitaire-ring MVP addresses. Problems
listed for [`011-target-users.md`](011-target-users.md)'s secondary
audiences that the current product does not yet address are marked as
such rather than omitted.

## Problem 1 — Repetitive parameter-driven modeling is slow by hand

Building a basic solitaire ring in general-purpose CAD software, or by
hand in wax, requires repeating the same construction steps (band
revolve, prong placement, basket support) for every size/stone/prong
variation, even when the underlying design logic hasn't changed.

**How JewelMind addresses it (current):** the same deterministic pipeline
(`geometry/assemblies/solitaire.py`) regenerates the full model instantly
from any valid parameter set — changing ring size or stone diameter does
not require rebuilding the construction from scratch.

## Problem 2 — Manual dimension checking is error-prone

Checking that a set of dimensions is internally consistent (e.g. prong
height versus basket height, stone size versus prong count) by eye or by
memory is easy to get wrong, especially under time pressure.

**How JewelMind addresses it (current):** the sixteen deterministic
validation rules (`docs/validation-rules.md`) catch these inconsistencies
immediately, both while typing (frontend mirror) and authoritatively
before any generation or export (backend).

## Problem 3 — It's hard to know if a design is "safe" before committing to a physical process

Sending a design to casting or printing without checking minimum feature
sizes risks a failed or fragile piece.

**How JewelMind addresses it (current):** rules like `JM-BAND-002`,
`JM-PRONG-002`, and `JM-MANUFACTURING-001` flag thin features before any
file leaves the system — though this is explicitly not a substitute for
professional review (`JM-BIBLE` LAW-010).

## Problem 4 — Getting a usable, neutral CAD file out of a proprietary tool is not always straightforward

Some CAD workflows lock output into vendor-specific formats.

**How JewelMind addresses it (current):** every export (STEP, STL) uses a
neutral, widely-supported format from the start — see
[ADR-010](../03-decisions/ADR-010-step-and-stl-export-strategy.md).

## Problems not yet addressed (secondary audiences)

The following problems belong to secondary target users (see
[`011-target-users.md`](011-target-users.md)) and are **not** addressed by
the current MVP — listed here so they are not silently forgotten, not
because they are scheduled:

- An e-commerce configurator's need for a customer-facing, guided
  configuration flow (today's UI is desktop-first and assumes CAD
  familiarity).
- A manufacturer's need for batch/bulk generation across many
  definitions at once (today's API generates one model per request).
- A student's need for guided explanations of *why* a rule exists, beyond
  the rule's message text.
