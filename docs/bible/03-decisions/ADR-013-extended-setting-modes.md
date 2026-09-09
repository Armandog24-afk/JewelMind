---
id: JM-BIBLE-ADR-013
title: "ADR-013: the setting-mode taxonomy is a derived registry, and refines setting.type"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-09
source_of_truth: true
depends_on:
  - JM-BIBLE-ESM-README
related_documents:
  - JM-BIBLE-SETTING-GOVERNANCE
  - JM-BIBLE-SETTINGV2-GOVERNANCE
  - JM-BIBLE-PAVE-GOVERNANCE
implementation_status: current
---

# ADR-013: the setting-mode taxonomy is a derived registry, and `setting.mode` refines `setting.type`

## Status

Accepted.

## Why this ADR exists

Sprint 27 introduces a first-class setting-mode taxonomy and four new setting
families. Two of the decisions inside it meet ADR conditions the Setting System
already records — "add capability metadata for every Setting family"
(SETTING-GOV-005) constrains how a registry may be built, and the
one-authority-per-axis principle underlies SETTINGV2-GOV-012's refusal to mix
explicit and derived prong layouts. Both are recorded here before the change
stands.

This ADR decides nothing about professional validation. Nothing in this sprint
is professionally validated, and the tension family's structural behaviour is
explicitly not modelled.

## Context

Before this sprint the Setting System had four independent capability registries
— setting families, prong styles, head architectures, and the pavé's retention
strategies. Each was honest about itself. None of them could answer *which
setting techniques does JewelMind actually build?*, and a reader had to know
that a `SHARED_BEAD` and a `V_PRONG` are the same kind of thing expressed at
different points in the pipeline.

Two failure modes were live:

1. **A fifth registry would drift.** Sprint 20 removed three hand-copied
   registries that had already drifted, and the drift had caused Designer and
   the Setting System to misreport real capabilities to users. A hand-maintained
   "master list of setting modes" is the same artefact with a better name.
2. **A second authority over one setting has no determinate resolution.** If a
   document could name both a family and a mode, and they disagreed, any
   precedence rule would silently discard half of what the author wrote. Sprint
   24 met the same problem with a family and an arrangement and refused it
   (`JM-FAMILY-001`).

## Decision

### 1. The taxonomy is a registry whose geometry axis is MEASURED

`setting/modes.py` declares the mode ids, axes and families;
`setting/capability.py::setting_modes()` builds the capability rows. Each row's
`settingGeometry` is **read from the live builder registries** —
`setting_generators()`, `prong_solid_builders()`, `head_builders()`,
`retention_builders()` — rather than declared in the row.

A mode therefore cannot claim a solid no builder produces, and the guard test
checks the reverse direction too: every builder must be named by exactly one
mode. The four existing registries remain the authority for their own axis; the
mode registry is a derived unification of them, not a replacement.

*Rejected alternative:* declaring `settingGeometry: true` per row. It reads
identically and is exactly the artefact Sprint 20 had to delete three of.

### 2. `setting.mode` refines `setting.type`; a disagreement is REFUSED

`setting.type` names the family and selects the generator. `setting.mode` names
the variant within that family and carries its parameters. `resolve_primary_mode()`
is the single resolution point, and a mode whose family disagrees with `type`
raises — surfaced as `JM-SETTING-008` so a caller learns it from validation.

A document with no mode resolves to the variant its existing
`type`/`prongStyle` fields already meant, which is what keeps every
pre-Sprint-27 design byte-identical.

*Rejected alternative:* letting `setting.mode` alone select the family, with
`type` derived from it. It removes the disagreement by removing a field that is
published, stored in every saved design, and referenced by five Forge rules.

*Rejected alternative:* precedence (mode wins, or type wins). Either silently
discards half of what the author wrote.

### 3. The three axes stay separate, and each has exactly one selector

| Axis | Selector |
| --- | --- |
| PRIMARY | `setting.type` + `setting.mode` |
| HEAD | `setting.headArchitecture` |
| RETENTION | the pavé's `retention.strategy` |

A HEAD or RETENTION mode declared as `setting.mode` is refused. A primary and a
head mode are simultaneously present in one design — they are not alternatives —
so collapsing them into one enum would make "a bezel on a martini"
inexpressible.

This is also why the open gallery's window parameters live on `SettingSpec`
beside the other head fields rather than inside `mode.parameters`: `mode`
declares the PRIMARY mode, and a field in it that only a head reads would be a
parameter that mode never applies.

### 4. `mode.parameters` is one flat model, not a discriminated union

A discriminated union at the JDL layer cannot be reached by a dotted-path patch,
which is precisely the defect Sprint 26 hit when Designer could not create a
pavé. A flat model with per-mode fields keeps every route — a UI control, a
natural-language request, a hand-written document — able to set one value.

The cost is paid explicitly: `MODE_PARAMETER_FIELDS` states which fields each
mode reads, `JM-SETTING-009` reports an unread value as INFORMATION rather than
dropping it silently, and a test asserts that **no field is read by no mode** —
because a parameter nothing reads is the silently ignored field
ARRANGE-GOV-011 forbids.

### 5. Component provenance goes on the setting result, not on a `GeometryPlan`

The requirement was that every setting component be traceable to the mode, the
stone and the placements it came from. `SettingComponentProvenance` records that
on `SettingGeometryResult`, where the component's other facts already live.

`GeometryPlan` is still not materialized. Materializing it is an explicit ADR
condition in `160-alchemist-governance.md`, and inventing an unrequested
compiler stage to hold a fact about a component would have been a speculative
abstraction with an ADR attached.

### 6. Channel and bar are PRIMARY families, not pavé retention strategies

The pavé's retention anchors are lattice CORNERS — where four cells meet. That
is the correct topology for a bead or a micro prong, and the wrong one for a
rail running a whole row or a bar sitting at a cell midpoint.

`RETENTION_CHANNEL` and `RETENTION_BAR` therefore stay reserved, with that as
their recorded reason, and the techniques exist as families where their extent
is actually stated. `SHARED_PRONG` moved the other way for the mirror reason: it
needed the shared-CORNER topology the lattice already computed, not a new solid,
so it reaches the same builder `MICRO_PRONG` does.

## Consequences

- **`definitionHash` changes for every document**, because `SettingSpec` gained
  four fields and defaults participate in canonical JSON. Additive and expected;
  every spec vector and example was regenerated by running the real
  implementation, exactly as Sprints 22, 24, 25 and 26 each did.
- **All 54 pre-existing Golden baselines are untouched**, and seven new cases
  were added — one per real capability. A default prong solitaire's metal volume
  is still `341.44334316909976 mm³`.
- **`SETTING_GEOMETRY_VERSION` moves to 1.2.0** (MINOR: every addition is
  reached only by a document that asks for it) and
  `PAVE_REGISTRY_VERSION` to 1.1.0, while `PAVE_COMPILER_VERSION` stays 1.0.0
  because no pavé arithmetic changed.
- **Two PARTIAL modes are PARTIAL for two different reasons**, and both are
  stated rather than averaged: `TENSION_OPPOSED` has complete geometry and an
  absent engineering model; `PRONG_SHARED` has real metal and a stated rather
  than derived position.
- **Two pre-existing defects were corrected in passing**, each recorded in the
  validation report: the JDL schema declared `setting.type` as
  `{"const": "prong"}` and had therefore rejected every `bezel` document since
  Sprint 19, and Sprint 23's `prongStyle`/`headArchitecture`/`seatMode` had real
  builders and no Studio control at all.
- **A capability the registry marks PARTIAL can no longer be silently CURRENT
  anywhere**, because the capability-coverage guard now compares the recorded
  STATUS of every setting family against the live registry rather than only
  collecting the CURRENT ones.

## Alternatives considered

**Add the four families without a taxonomy.** Rejected: it would have left five
places to look for "what does JewelMind set?", and the fifth (channel, bar,
flush, tension) would have been the only one with no capability metadata at all.

**Make the taxonomy the single source and retire the four axis registries.**
Rejected: each axis registry carries fields the others do not — a prong style's
`preservesLegacyGeometry`, a head's `singleSolid`, a retention strategy's own
description — and flattening them would either lose those or produce a row type
that was mostly nulls.

**Give tension setting a stress model.** Rejected outright, and this is the one
alternative that was not a design trade-off: it would require material
properties and a validated engineering model, and inventing either would be a
fabricated professional claim about whether jewelry holds a stone.
