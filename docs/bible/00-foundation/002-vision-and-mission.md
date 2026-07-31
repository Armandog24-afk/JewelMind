---
id: JM-BIBLE-002
title: Vision and Mission
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: false
depends_on: []
related_documents:
  - JM-BIBLE-001
  - JM-BIBLE-006
implementation_status: vision
---

# Vision and Mission

> **This document is explicitly marked `source_of_truth: false`.** Nothing
> in this document describes current functionality. For what exists today,
> see [`001-project-overview.md`](001-project-overview.md) and
> [`005-current-product-status.md`](005-current-product-status.md).

## Vision

Transform jewelry design intent into reproducible parametric definitions
and technically inspectable geometry.

## Mission

Reduce repetitive CAD work while preserving human professional control.

## The core distinction this vision depends on

The long-term direction rests on keeping three layers separate, and never
letting one quietly absorb another's responsibility:

1. **Intent capture** — a person (or, eventually, an AI-assisted interface)
   describes what they want. This layer may become more flexible over
   time (forms today; possibly natural language or sketches later).
2. **Deterministic validation and construction** — a fixed, testable,
   non-AI system turns a well-formed intent into a canonical definition,
   validates it against explicit rules, and constructs geometry from it.
   This layer is deterministic by design (see
   [ADR-003](../03-decisions/ADR-003-deterministic-geometry.md)) and does
   not get replaced by making layer 1 smarter.
3. **Professional manufacturing approval** — a qualified jewelry
   professional reviews and approves anything before it goes to
   production. This responsibility does not move to the software at any
   point on this roadmap.

Concretely: AI or natural language may eventually describe *intent*.
Deterministic systems validate and construct *geometry*. Jewelry
professionals retain responsibility for *manufacturing approval*. None of
today's or any future version of JewelMind is intended to collapse these
into one layer.

## What this vision explicitly does not claim

To keep this document honest, it deliberately avoids marketing language.
None of the following claims are made, implied, or intended, now or as a
future goal stated in absolute terms:

- "World's first" anything.
- "Revolutionary."
- "Production-ready" — no version of JewelMind's output should be
  described this way; see [LAW-010](004-jewelmind-constitution.md) and
  the professional-review disclaimer that appears on every export.
- "Replaces professional jewelers."
- "Automatically guarantees manufacturability."

## Relationship to the current MVP

The current solitaire-ring MVP (see
[`001-project-overview.md`](001-project-overview.md)) is a deliberately
narrow, concrete instance of layer 2 above: one product type, one set of
deterministic rules, one geometry pipeline. Expanding it (more settings,
more jewelry types, richer intent capture) is the path toward this vision,
not a departure from the current architecture — see
[`006-scope-and-boundaries.md`](006-scope-and-boundaries.md) for what is
explicitly out of scope for now versus what is a plausible next step.
