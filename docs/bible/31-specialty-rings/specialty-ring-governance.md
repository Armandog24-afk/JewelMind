---
id: JM-BIBLE-SPECIALTY-GOVERNANCE
title: "Specialty Ring governance rules"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-12
source_of_truth: true
depends_on:
  - JM-BIBLE-SPECIALTY-README
related_documents:
  - JM-BIBLE-RINGFAM-GOVERNANCE
  - JM-BIBLE-FAMILY-GOVERNANCE
  - JM-BIBLE-PAVE-GOVERNANCE
implementation_status: current
---

# Specialty Ring governance rules

Ten rules. Each is enforced by a real test in
`backend/tests/test_specialty_rings.py`; a rule with no test is a wish.

**The 14 RINGFAM-GOV rules apply in full and are not restated here.** A
specialty ring IS a ring family, so every one of them already binds it.

---

## SPECIALTY-GOV-001 — Extend Ring Families; never parallel them

A specialty family is a `jewelry.style` member and its variants are
`RingFamilyVariantId` members. There is no `SpecialtyRingGenerator`, no second
dispatch and no second resolution point.

*Enforced by* `TestExtendsRingFamiliesRatherThanParalleling`, including
`test_there_is_no_separate_specialty_generator`, which asserts structurally that
no such module exists at all.

## SPECIALTY-GOV-002 — Delegate the stones; compute no placement

An eternity band derives a `pave` block; a cluster and a toi-et-moi derive a
`family` block. This layer computes no position, no lattice and no outline.

*Enforced by* `TestDelegation`, including
`test_the_derived_stone_family_is_the_existing_one`, which asserts the derived
`familyType` is a live Sprint 24 `FamilyType` member rather than a new name.

## SPECIALTY-GOV-003 — Status follows `settingGeometry`, not ambition

A family may be CURRENT only if the layer it delegates to actually holds its
stones. The Pavé Engine does (`settingGeometry: true`); the Multi-Stone Family
and Halo layers do not.

*Enforced by* `TestPartialFamiliesAreHonest`, which asserts the statuses AND
measures the consequence: a stone-only family's combined metal is EXACTLY the
baseline's, because nothing was added to hold anything.

## SPECIALTY-GOV-004 — A PARTIAL description must say what is missing

"PARTIAL" alone is not a status, it is a shrug. Every PARTIAL specialty entry
names the absent capability and points at the layer that would provide it.

*Enforced by* `test_the_partial_descriptions_say_what_is_missing` and
`test_toi_et_moi_records_the_shared_cut_limitation`.

## SPECIALTY-GOV-005 — Never give one capability two names

A ring family that would only rename an existing capability is not added. This
is why there is no `tension_style` ring family — the `tension` setting family
already builds that geometry — and why the stacking band shares `plain_band`'s
reservation rather than getting a second entry.

*Enforced by* `TestReservedSpecialtyNames`.

## SPECIALTY-GOV-006 — Two specs, two questions

A full eternity states a PITCH and its stone count follows from the band's
circumference; a half eternity states a COUNT and a spacing. Neither variant may
read the other's parameters, because offering a control that does nothing is the
silently-ignored field ARRANGE-GOV-011 forbids.

*Enforced by* `parameters_read_by()`, `JM-RINGFAM-003`, and in the interface by
`test_offers_the_eternity_controls_the_chosen_variant_actually_reads`.

## SPECIALTY-GOV-007 — A relation, never a stored value

Every specialty parameter must modulate something the document already states.
The set stones' size is a multiple of the design's own stone; the halo-like
cluster radius is a real distance the resolver honours exactly; the second
toi-et-moi stone is a multiple of the first.

*Enforced by* `TestSpecialtyParametrics`, which measures each one against the
REQUEST rather than merely asserting "something changed" — radius 3.0 must
produce stones at 3.000 mm.

## SPECIALTY-GOV-008 — Reject, never repair, never substitute

An unsupported retention strategy, an impossible spacing, a reserved variant, a
non-finite value: each raises. An unsupported setting is never silently replaced
with a supported one.

*Enforced by* `TestNegative`.

## SPECIALTY-GOV-009 — Never invent a professional threshold

No stone spacing, bead size, cluster density, stone-security or settability
judgment exists anywhere in this sprint. `MAX_PAVE_STONES_PER_BAND` and
`MAX_CLUSTER_STONES` are software safety limits and say so; both sit at or below
the limit the delegated engine already enforces.

*Enforced by* `test_no_specialty_rule_message_makes_a_manufacturing_claim`,
which reads every rule message a specialty design produces.

## SPECIALTY-GOV-010 — Record a limitation where a reader will meet it

A boundary belongs in the capability description, the golden's
`knownLimitations` and the Studio panel — not only in a document nobody opens
while designing.

*Enforced by* the PARTIAL notes in `RingFamilySection.tsx` (asserted by
`test_states_what_is_missing_for_the_PARTIAL_specialty_families`) and by every
`SR-*` golden's `knownLimitations`.

---

## When an ADR is required

- Letting a specialty family compute a placement, an outline or a solid.
- Adding a specialty dispatch, generator or resolution point separate from
  `resolve_ring_family()`.
- Changing `REQUIRED_COMPONENT_NAMES` to allow a stone-less ring — which is what
  a true eternity band and every stacking band need.
- Promoting `cluster` or `toi_et_moi` to CURRENT, which requires the
  non-primary retention that does not exist.

## When an RFC is required

- **Any specialty family beyond the three implemented — including every reserved
  name.**
- A swept wall along the band's centreline, the prerequisite for a channel-set
  band.
- Per-member stone specifications, the prerequisite for a toi-et-moi whose two
  stones have different cuts. Sprint 24 already identified this.
- A setting strategy for a non-primary family member, which is what would make
  cluster and toi-et-moi CURRENT. Sprint 24 identified this as "the identified
  next step — do not bypass it".
- Any professional threshold on stone spacing, bead size or cluster density.
