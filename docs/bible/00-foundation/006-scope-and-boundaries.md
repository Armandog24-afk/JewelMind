---
id: JM-BIBLE-006
title: Scope and Boundaries
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on:
  - JM-BIBLE-001
related_documents:
  - JM-BIBLE-005
  - JM-BIBLE-002
implementation_status: current
---

# Scope and Boundaries

## CURRENT (this MVP)

- Solitaire ring — the only jewelry style supported.
- Round central stone reference — the only stone shape supported.
- Four or six prongs — the only prong counts supported
  (`JM-PRONG-001`, `docs/validation-rules.md`).
- Simplified basket support.
- Flat or comfort-fit band profile — the only two profiles supported.
- Five selectable metals, as display/metadata only — cosmetic in this
  milestone, does not affect geometry or export content
  (`docs/known-limitations.md`).
- Two manufacturing methods, as metadata and validation context
  (`JM-MANUFACTURING-001` applies extra scrutiny for
  `direct_resin_printing`; the method itself does not change the
  geometry).
- STEP, STL, JSON, and Markdown technical specification export.

## OUT OF CURRENT SCOPE

None of the following exist in the current codebase. They are not
scheduled, and their absence is not a defect — see
[`004-jewelmind-constitution.md`](004-jewelmind-constitution.md) LAW-012
and [`000-bible-governance.md`](000-bible-governance.md) for why this list
must not be read as a roadmap:

- Pavé settings.
- Halo settings.
- Trilogy (three-stone) settings.
- Side stones of any kind.
- Engravings.
- Necklaces, earrings, or bracelets — any jewelry category other than a
  ring.
- Image-to-CAD (deriving geometry from a photo or sketch).
- Natural-language design ("describe your ring in words").
- User accounts or authentication.
- Subscriptions or any billing.
- Multi-user collaboration.
- A marketplace.
- Cloud rendering.
- Automatic manufacturing certification.
- Native Rhino (`.3dm`) or MatrixGold project export.

## PLANNED

There is currently no committed near-term roadmap item beyond the
technical hardening already completed (see `AUDIT_FIXES.md` at the
repository root) and this documentation milestone. When a concrete next
feature is committed to, it belongs in this section with its own status
and, if it meets the criteria in
[`000-bible-governance.md`](000-bible-governance.md), a preceding ADR.

## VISION

See [`002-vision-and-mission.md`](002-vision-and-mission.md) for the
long-term direction (more jewelry types, richer intent capture, still
governed by the same deterministic validation/construction core). Nothing
in the vision document is scheduled; it is explicitly `source_of_truth:
false`.

## Why this boundary exists

The MVP scope is narrow by design, not by accident: Product Principle 1
("everything important is parametric") and the Constitution's
determinism laws are far easier to uphold correctly for one well-defined
product (a solitaire ring) than for an open-ended jewelry configurator.
Expanding scope should extend the same architecture — one more geometry
component, one more set of validation rules — rather than bolt on a
parallel, less-disciplined path.
