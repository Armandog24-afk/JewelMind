---
id: JM-BIBLE-537
title: Open Ring Architecture Questions
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-RING-README
  - JM-BIBLE-520
related_documents:
  - JM-BIBLE-536
implementation_status: current
professional_validation: not_required
normative: false
---

# Open Ring Architecture Questions

This document records the brief's own listed open questions for this
Sprint, unanswered. Recording a question here is not a commitment to
answer it a particular way, and is never a substitute for the ADR/RFC
process ([`520-jewelry-category-architecture.md`](520-jewelry-category-architecture.md))
that would actually resolve one.

## Should a future JDL use category-specific nested definitions?

The current JDL keeps `ring`/`band`/`stone`/`setting` as top-level
fields on `JewelryDefinition` (unchanged this Sprint). A nested,
polymorphic `categoryDefinition` structure (one shape per category) is a
real alternative — see
[`536-current-code-mapping-and-gaps.md`](536-current-code-mapping-and-gaps.md)
for why this Sprint did not adopt it. Whether it ever should is open.

## When should JDL receive a breaking major version?

Related to the above: nesting category-specific fields, if ever done,
would very likely require a JDL major-version bump (`specs/jdl/v1/` ->
`v2`). No criteria for when that bump should happen — versus continuing
to add fields additively — are decided by this Sprint.

## Should `jewelry.style` evolve into `family`?

A real current fact, not a hypothesis: `RingDefinition.family` is
literally populated *from* `definition.jewelry.style` in
[`ring/adapter.py`](../../../backend/jewelmind/ring/adapter.py)
(`family=definition.jewelry.style`) — the two are already aliases in
practice today, just not renamed at the JDL layer. Whether `jewelry.style`
should eventually be renamed (or whether `family` should instead be
understood as ring-specific terminology for a platform-level `style`
concept) is open.

## Is Shank the canonical internal term while Band remains user-facing — is that permanent policy?

This split already exists today: `domain/schema.py::BandSpec` (JDL/user
facing) maps to `ring/models.py::ShankDefinition` (internal). Whether
this is meant as durable naming policy for every future ring
sub-concept, or was simply the terminology available when solitaire was
first built, is open — see
[`526-shank-contract.md`](526-shank-contract.md).

## Should shoulders always exist as an explicit component?

`ShoulderDefinition.modeled` is always `False` today —
[`527-shoulder-contract.md`](527-shoulder-contract.md) and
[`536-current-code-mapping-and-gaps.md`](536-current-code-mapping-and-gaps.md)
both document this as implicit/no independent geometry. Whether a
shoulder should become a mandatory, always-present modeled component
(even trivially, for a plain solitaire) or should remain
optional/family-dependent is open.

## Should RingHead own setting placement only, or setting structure too?

`RingHeadDefinition` today owns only `basketHeightMm` — a single
structural-attachment number. Whether a richer future head model should
also own aspects of setting *structure* (as opposed to purely the
setting's own data, owned by `SettingAttachmentDefinition`) is open —
see the boundary discussion in
[`521-shared-vs-category-specific-domain.md`](521-shared-vs-category-specific-domain.md)
and [`528-head-contract.md`](528-head-contract.md).

## Should StoneArrangement become a fully shared jewelry subsystem?

`StoneArrangementDefinition` already wraps the shared `StoneSpec`
without duplicating it (JEWELRY-ARCH-GOV-006). Whether it should be
promoted to a subsystem genuinely shared across categories (the way
`material`/`manufacturing`/`preview` already are), rather than living
inside `jewelmind.ring`, is open — no earring/pendant/necklace stone
arrangement exists yet to test the assumption against.

## Which category should be implemented second — earrings or pendants — to stress-test the architecture?

Not decided by this Sprint. Both are named as equally plausible
candidates in
[`jewelry_category/registry.py::CATEGORY_CAPABILITIES`](../../../backend/jewelmind/jewelry_category/registry.py),
with identical `status: "planned"` and no implementation priority
implied by ordering.

## Should a pair of earrings be one product or two instances?

Open, and specific to earrings in a way no other planned category
raises: a single `JewelryDefinition` producing two physical objects (one
per ear) has no precedent in the current ring-only architecture, which
always produces exactly one physical object per definition.

## How should necklace/bracelet repeated structures differ from ring architecture?

Both necklaces and bracelets plausibly involve repeated/patterned
structure (links, stone arrangements along a length) that a single ring
`shank`/`head`/`stoneArrangement` graph does not need to represent.
Whether this is closer to a variation on `StoneArrangement` (item above)
or requires a wholly new architectural node type is open.

## When should category plugins become dynamically discoverable?

The current mechanism (`CATEGORY_CAPABILITIES` and
`_category_generators()` as hand-edited, statically-registered dicts) is
adequate for 1 current + 5 planned categories. Whether a future point
exists where categories should be discovered dynamically (e.g. via
entry points or a plugin directory) rather than requiring a code change
per category, and what that point is, is open.
