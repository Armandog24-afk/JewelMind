---
id: JM-BIBLE-011
title: Target Users
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on: []
related_documents:
  - JM-BIBLE-010
  - JM-BIBLE-012
implementation_status: partial
---

# Target Users

The current MVP's UI and API are built around **primary future users**.
**Secondary future users** are documented so their needs are not lost,
even though the current product does not yet serve them well — this
document's `implementation_status` is `partial` for that reason: the
*users the current UI actually suits* are implemented; the rest are not.

## Primary future users

### Jewelry CAD designers

- **Current problem:** repeating the same construction logic for every
  size/stone variation of a simple solitaire design.
- **Desired outcome:** generate a correct, dimensionally-validated
  starting model in seconds, then refine or hand off.
- **How JewelMind may help:** the parametric pipeline (Problem 1 in
  [`010-user-problems.md`](010-user-problems.md)) and the neutral STEP
  export for further work in their own tools.
- **Professional knowledge still required:** stone setting technique,
  final tolerancing, and manufacturability judgment — JewelMind's
  validation is a first pass, not a substitute (see LAW-010).

### Independent jewelers

- **Current problem:** limited in-house CAD capacity for quick client
  mockups.
- **Desired outcome:** a fast, dimensionally sound starting point to show
  a client or send to a caster.
- **How JewelMind may help:** the browser-based flow requires no CAD
  license or desktop software install (Product Principle 8).
- **Professional knowledge still required:** client-specific sizing,
  final finishing, and casting-house-specific requirements.

### Small jewelry workshops

- **Current problem:** inconsistent internal documentation of a design's
  exact parameters between staff.
- **Desired outcome:** a canonical, shareable JSON definition and a
  readable technical specification per design.
- **How JewelMind may help:** the JSON export and Markdown specification
  are both direct, literal records of the exact parameters used.
- **Professional knowledge still required:** interpreting the
  specification in the context of their own shop's tooling and
  materials.

### Jewelry brands with configurable products

- **Current problem:** offering size/stone/metal variants of one design
  today usually means either many hand-built variants or a bespoke
  internal tool.
- **Desired outcome:** one parametric definition that reliably covers a
  family of variants.
- **How JewelMind may help:** the same `JewelryDefinition` schema
  reproducibly covers ring size, band profile, stone size, prong count,
  and metal choice today.
- **Professional knowledge still required:** brand-specific design
  standards beyond what the sixteen current validation rules check.

## Secondary future users

The current MVP's UI (a desktop-first configurator assuming CAD/technical
familiarity) and API (one-request-at-a-time, no batch mode) do not yet
serve these users well. Listed for completeness, not as a commitment:

### E-commerce configurators

- **Current problem:** customers want to see a product update live as
  they pick size/metal/stone.
- **Desired outcome:** an embeddable, customer-facing configuration
  widget.
- **How JewelMind may help (future):** the same backend generation/
  validation pipeline could sit behind a different, simplified frontend.
- **Professional knowledge still required:** none from the end customer;
  the brand still needs a jeweler to approve each configuration's
  manufacturability.

### Manufacturers

- **Current problem:** turning many customer-submitted definitions into
  production files efficiently.
- **Desired outcome:** batch generation and export.
- **How JewelMind may help (future):** the deterministic, scriptable
  pipeline (see `scripts/generate_example.py` for the current
  single-definition version) is a plausible basis for batch tooling.
- **Professional knowledge still required:** the same manufacturing
  review requirement applies to every unit in a batch.

### Jewelry students

- **Current problem:** learning how parameters relate to a valid,
  buildable design.
- **Desired outcome:** a tool that shows *why* a parameter combination is
  invalid, not just that it is.
- **How JewelMind may help (future):** the existing rule messages
  (`docs/validation-rules.md`) are a foundation; richer educational
  explanation is not yet built.
- **Professional knowledge still required:** this audience is explicitly
  trying to build the professional knowledge JewelMind currently assumes.

### Software integrators

- **Current problem:** wiring jewelry configuration into a larger system
  (e.g. an existing product catalog).
- **Desired outcome:** a stable, documented API to integrate against.
- **How JewelMind may help:** `docs/api.md` and
  [`appendices/api-inventory.md`](../appendices/api-inventory.md)
  already document the current endpoint surface for exactly this purpose.
- **Professional knowledge still required:** none beyond standard API
  integration; jewelry-domain judgment remains with the integrator's own
  users.
