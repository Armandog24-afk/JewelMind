---
id: JM-BIBLE-056
title: Domain Extension Strategy
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on:
  - JM-BIBLE-055
related_documents:
  - JM-BIBLE-000
  - JM-BIBLE-ADR-005
implementation_status: current
professional_validation: not_required
---

# Domain Extension Strategy

This document defines **how** JewelMind adds future jewelry capabilities
without breaking the current model — not **what** those capabilities
will look like. No future Jewelry Definition Language (Sprint 3's
subject) is designed here.

## Required workflow for any domain expansion

```mermaid
flowchart LR
    A[Domain proposal] --> B[Professional-review requirement assessment]
    B --> C[RFC]
    C --> D{Architectural?}
    D -->|yes| E[ADR]
    D -->|no| F[Schema change]
    E --> F
    F --> G[Validation design]
    G --> H[Geometry implementation]
    H --> I[Tests]
    I --> J[Bible update]
    J --> K[Release]
```

1. **Domain proposal** — a concrete description of the new concept
   (e.g. "add oval stone shape"), referencing the relevant PLANNED entry
   already logged in this Sprint's documents where one exists.
2. **Professional-review requirement assessment** — using
   [`040-domain-governance.md`](040-domain-governance.md)'s
   classification, decide whether the proposal introduces any
   PRELIMINARY SOFTWARE RULE that should instead wait for professional
   input before shipping (log it in
   [`058-professional-validation-register.md`](058-professional-validation-register.md)
   if so).
3. **RFC** — per
   [`00-foundation/000-bible-governance.md`](../00-foundation/000-bible-governance.md)'s
   future rule: once JewelMind has more than one active maintainer or
   accepts external contributions, this step becomes mandatory before
   implementation. Until then, the proposal + assessment above serve the
   same purpose informally.
4. **ADR** — required if the change meets any "ADR required" condition
   in [`00-foundation/000-bible-governance.md`](../00-foundation/000-bible-governance.md)
   (e.g. a non-additive schema change, moving validation authority,
   changing export defaults).
5. **Schema change** — update
   `backend/jewelmind/domain/schema.py` **and**
   `shared/types/jewelry-definition.ts` together, per
   [ADR-005](../03-decisions/ADR-005-canonical-jewelry-definition.md).
6. **Validation design** — new rule(s) added to both
   `backend/jewelmind/validation/engine.py` and
   `shared/validation/engine.ts`, with a stable `JM-XXX-NNN` ID, per
   `docs/validation-rules.md`'s existing "Adding a new rule" procedure.
7. **Geometry implementation** — a new or modified builder in
   `backend/jewelmind/geometry/`, preserving the coordinate convention
   (`docs/geometry-conventions.md`) and every applicable Constitution law.
8. **Tests** — geometry, validation, and API tests, per the existing
   patterns in `backend/tests/`.
9. **Bible update** — at minimum,
   [`00-foundation/005-current-product-status.md`](../00-foundation/005-current-product-status.md),
   [`appendices/implementation-inventory.md`](../appendices/implementation-inventory.md),
   the relevant `04-jewelry-domain/` document(s), and the four
   jewelry-domain appendices, all in the same change as the code.
10. **Release** — normal commit/push per
    [`00-foundation/000-bible-governance.md`](../00-foundation/000-bible-governance.md).

## Specific expansion scenarios

### Adding a new stone shape (e.g. Oval)

Requires: a schema change from a single `diameter` to (at minimum)
`length`/`width` for non-round shapes — not additive, since `diameter`
alone cannot describe an oval. This likely needs an ADR (schema is not
purely additive) and professional input on proportion conventions per
shape (see [`046-stone-domain.md`](046-stone-domain.md)).

### Adding a new setting type (e.g. Bezel)

Requires: `SettingSpec.type` gains a new `Literal` value, a new geometry
builder (a rim/collar solid rather than discrete prongs), and setting-
type-specific validation rules. Likely additive at the schema level (a
new enum value plus new optional fields), but the geometry assembly logic
in `geometry/assemblies/solitaire.py` currently assumes a prong+basket
shape and would need to branch by setting type.

### Adding a new ring style (e.g. Halo)

Requires: multi-stone-arrangement support, which the current
`JewelryDefinition` does not have any concept of at all (only one
`StoneSpec`) — this is likely the largest single schema change of any
scenario here, almost certainly requiring an ADR given how much of the
current geometry pipeline assumes exactly one center stone.

### Adding multi-stone arrangements generally

The current schema has no concept of a stone *list* — `stone: StoneSpec`
is singular. Any multi-stone feature (halo, trilogy, eternity, cluster —
see [`042-ring-taxonomy.md`](042-ring-taxonomy.md)) depends on this
foundational change happening first, once, rather than being solved
per-style.

### Adding shoulders and heads

Requires new geometry components with no current equivalent (see
[`043-ring-anatomy.md`](043-ring-anatomy.md)) and a schema extension for
their parameters. Additive at the schema level; likely non-trivial at
the geometry-assembly level since the current band/basket connection
assumes no intermediate shoulder structure.

### Adding decorative components (engraving, filigree, milgrain)

Likely additive at the schema level (new optional fields/objects) but
introduces an entirely new geometry category (surface modification
rather than solid construction) not present in any current builder.

### Adding other jewelry categories (earring, pendant, etc.)

See [`041-jewelry-product-taxonomy.md`](041-jewelry-product-taxonomy.md).
Requires `JewelryInfo.category`/`style` to gain new values and an entirely
new set of category-specific components — almost certainly requires an
ADR, given how much of the current schema (`RingSpec`, `BandSpec`) is
ring-specific by name and would need to become one of several possible
category-specific specs rather than always-present fields.

## Schema-version evolution and backward compatibility

- `schemaVersion` is currently locked to `"0.1.0"` — any schema change
  affecting the wire format should bump this, and the strict
  `Literal["0.1.0"]` type means an old or new incompatible version is
  rejected loudly rather than silently misinterpreted (see
  [ADR-005](../03-decisions/ADR-005-canonical-jewelry-definition.md) and
  `docs/known-limitations.md`).
- Migrating existing saved definitions (`localStorage`) across a schema
  version bump is not currently implemented —
  `isValidJewelryDefinition()` in
  `shared/types/jewelry-definition.ts` will simply reject an
  old-version definition and fall back to defaults, rather than
  attempting a migration. A future schema bump would need to decide
  whether to add migration logic or accept this reset-to-default
  behavior.

## Feature flags and experimental domain concepts

No feature-flag mechanism exists in the current codebase. A future
experimental domain concept (e.g. a new stone shape not yet ready for
general use) would need one of:

- A separate, clearly-labeled `planned`/experimental code path not
  reachable from the default UI, or
- An explicit opt-in schema field, documented as experimental in both
  the schema comments and this Bible.

Neither approach is implemented today; this is noted as a gap for
whichever expansion scenario needs it first.
