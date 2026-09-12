---
id: JM-BIBLE-SPECIALTY-COVERAGE-REVIEW
title: "Specialty Rings — coverage review"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-12
source_of_truth: true
depends_on:
  - JM-BIBLE-SPECIALTY-README
related_documents:
  - JM-BIBLE-SPECIALTY-GOVERNANCE
  - JM-BIBLE-RINGFAM-COVERAGE-REVIEW
implementation_status: current
---

# Specialty Rings — coverage review

Every specialty family the sprint brief asked for, what happened to it, and —
where it was not built — **what would have to exist first**.

The distinction that runs through this document: a name reserved with a real
prerequisite is a decision; a name reserved with the word "planned" is an
omission wearing a label.

## Asked for, and built

| Asked (§) | Built as | Status |
| --- | --- | --- |
| §2.2 eternity / half-eternity | `ETERNITY_FULL`, `ETERNITY_HALF` | **CURRENT** |
| §2.5 cluster | `CLUSTER_ROUND` | **PARTIAL** |
| §2.6 toi-et-moi | `TOI_ET_MOI_BYPASS` | **PARTIAL** |

## Asked for, and deliberately not built

### §2.1 stacking / band ring — **blocked, and honestly so**

A stacking band is a ring with no stone. `REQUIRED_COMPONENT_NAMES` is
`('band', 'stone_reference', 'basket_support')`, so such a ring fails geometry
inspection **by contract rather than by accident**, and changing that set is an
explicit ADR condition.

Deliberately **not given its own reserved name**: `plain_band` already reserves
exactly this capability, and two reserved names for one thing is the duplication
this project refuses everywhere else. `plain_band`'s entry now says so.

*What must exist first:* an ADR generalising the required-component set, plus a
decision about what inspection should assert for an assembly with no stone.

### §2.3 channel-set ring — **blocked on a named primitive**

The brief said to report the limitation rather than fake support if the setting
infrastructure could not carry it. It cannot, and here is precisely why.

`setting/channel.py` builds its walls with `frame.py::oriented_prism()` —
**straight rectangular prisms in the stone's own horizontal frame**. That walls a
run across the top of a ring, which is what the `channel` setting family already
does well (and `ESM-001` already covers). It cannot follow the band's
circumference, so a stone sequence running around a curved band between curved
walls is not expressible.

*What must exist first:* a swept wall along the band's centreline — the **same
missing primitive** `SPLIT_SHANK_SCULPTED`, `SOLITAIRE_TRELLIS` and
`BYPASS_TWIST` all wait on. One piece of work unblocks four capabilities, which
is worth stating as one item rather than four.

### §2.4 flush / bezel-set band — **partly already there, and not duplicated**

A flush-set or bezel-set *sequence* along a band is the same shape of problem as
the channel band: the `flush` and `bezel` setting families build real geometry
for the design's own stone, not a sequence following a curve.

What *is* available today is the eternity band's own retention choice — bead,
shared bead or micro-prong — which is a real, executable answer to "how is this
sequence held". A flush or bezel sequence would need those families to gain a
curve-following form, which is the same prerequisite again.

*Deliberately not reserved as a separate name*, because it would be a third
entry for one prerequisite.

### §2.7 tension-style ring — **already exists one layer down**

The `tension` *setting* family (Sprint 27) already builds exactly the geometry
§2.7 describes: two opposing supports with the stone between them, real solids,
PARTIAL, with `structuralBehaviourModelled: false` and
`SETTING_STRUCTURAL_BEHAVIOUR_MODELLED` reporting it as a geometric fact.

A tension ring *family* would add no capability and one more name for the same
thing, which SPECIALTY-GOV-005 forbids. The brief's own instruction — do not
claim the model is professionally tension-safe — is already satisfied there.

*What is genuinely missing* is the structural model, and that needs real
engineering evidence and a professional-validation record, not a family.

## §3 — additional architectures, audited and declined

The brief asked whether cocktail, dome, bombé, architectural or sculptural rings
could be added, and warned against inflating the registry.

**None was added, and the reason is the same for all five.** Each is defined by a
*surface* — a domed top, a swelling body, a sculpted mass — and JewelMind has no
surface-decoration or freeform-modelling capability. Adding them would produce
five names whose geometry was a band and a head, which is precisely the
catalogue this programme keeps refusing.

They are also Sprint 31 (Decoration & Surface) and Sprint 32 (Organic &
Freeform) territory, and §28 forbids absorbing future sprints.

## What would make each PARTIAL family CURRENT

Stated so the next sprint has an unambiguous target rather than a status to
argue about.

**`cluster` → CURRENT** and **`toi_et_moi` → CURRENT** both require the same
thing: **a setting strategy for a non-primary family member**. The accent stones
are already real geometry in the right places; nothing holds them. Sprint 24
identified this as "the identified next step — do not bypass it", and it remains
an RFC.

The Pavé Engine is the proof it is achievable: it holds every stone in a field
with real beads and micro-prongs. What it does not do is hold a stone placed by
the *arrangement* layer rather than by a pavé lattice, and closing that gap is
the work.

**`toi_et_moi` additionally** needs per-member stone specifications before its
two stones can have different cuts — an oval and a pear, which is the classic
form. Also a Sprint 24 RFC.
