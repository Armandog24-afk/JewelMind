---
id: JM-BIBLE-SPECIALTY-SPRINT-29-REPORT
title: "Sprint 29 Validation Report — Specialty Rings v1"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-12
source_of_truth: true
depends_on:
  - JM-BIBLE-SPECIALTY-README
related_documents:
  - JM-BIBLE-SPECIALTY-GOVERNANCE
  - JM-BIBLE-SPECIALTY-EXECUTION-BOUNDARY
  - JM-BIBLE-SPECIALTY-COVERAGE-REVIEW
implementation_status: current
---

# Sprint 29 Validation Report — Specialty Rings v1

## The question the sprint had to answer

> Can a designer change a meaningful Specialty Ring parameter and receive a
> coherent regenerated ring rather than a different preset?

**Yes, for the three families built.** Every claim below is measured geometry.

## What the audit changed before any code was written

§27 asked for an architectural audit first, and it materially changed the plan.
**Most of what the brief requested already existed, spread across layers:**
eternity was expressible through the Pavé Engine, cluster and toi-et-moi were
already *stone* families, and channel/flush/bezel/tension were already *setting*
families.

So the sprint was never "build seven engines". It was to build the composition
layer — which is what §4 and §7–§9 ask for anyway — and to be honest about the
three capabilities that genuinely could not be built.

The audit also **found a Sprint 28 reservation that was factually wrong**; see
"One correction to the record" below.

## What was built

| | Count |
| --- | --- |
| New families (`jewelry.style` members) | 3 |
| New variants | 4 |
| New specialty parameters | 12 |
| New geometry primitives | **0** — every family delegates |
| New Forge rules | **0** — the five `JM-RINGFAM-*` rules already cover them |
| New Golden cases | 5 |
| Backend tests in `test_specialty_rings.py` | 64 |
| Frontend tests | 20 |

**Zero new geometry primitives and zero new rules is the result, not a
shortfall.** It is what "extend rather than parallel" looks like when it is done
properly.

## Status, decided by measurement

| Family | Status | Decided by |
| --- | --- | --- |
| `eternity` | **CURRENT** | The Pavé Engine's `settingGeometry: true` — real metal holds every stone |
| `cluster` | **PARTIAL** | The Multi-Stone Family layer's `settingGeometry: false` — only the centre is held |
| `toi_et_moi` | **PARTIAL** | The same, **plus** both stones share one cut |

## Measured geometry

| Variant | Combined metal | Stones | Retention solids |
| --- | --- | --- | --- |
| `ETERNITY_FULL` | **343.377** | 44 | **134** |
| `ETERNITY_HALF` | **341.728** | 13 | **48** |
| `CLUSTER_ROUND` | 341.443 | 9 | **0** |
| `TOI_ET_MOI_BYPASS` | 341.443 | 2 | **0** |

The last two carry *exactly* the 341.443 baseline, to the last digit, because
they add stones and no metal. **That equality is the PARTIAL boundary itself**,
not a measurement artefact.

## The parametric claim

| Input changed | Measured consequence |
| --- | --- |
| finger size 12 → 24 | **40 → 48 set stones** — the count follows the band's circumference |
| pitch 2.4 → 1.2 mm | more stones, following the pitch |
| count 8 → 16 | 8 → 16 stones, 32 → 64 beads |
| spacing 1.6 → 1.2 mm | **64 → 34 beads** — corners genuinely share |
| retention `BEAD` → `NONE` | 48 → 0 retention solids, stones unchanged |
| cluster radius 3.0 → 5.5 | stones at **exactly 3.000 → 5.500 mm** |
| cluster scale 0.3 → 0.7 | accent volume **1.572 → 19.970 mm³** |
| toi-et-moi second scale 1.0 → 0.5 | second **58.221 → 7.278 mm³**, first unchanged |
| toi-et-moi separation 3.0 → 8.0 | measured **3.000 → 8.000 mm** |
| toi-et-moi angle 0° → 90° | the pair rotates onto the other axis |

The finger-size row is the sprint's strongest evidence: a stored preset cannot
change its own stone count when the ring size changes.

## One correction to the record

Sprint 28 reserved `eternity` on this reason:

> "The pavé engine's containment policy clips a field at the host's declared
> extent rather than wrapping it, so a 360-degree field is not expressible yet."

**It was false when written.** `PaveSpec.angularSpanDeg` is bounded `le=360.0`
and `pave/compile.py` carries an explicit closed-ring branch at `span >= 360.0`
that spaces the last stone off the first. Measured before this sprint wrote a
line: **68 stones, largest angular gap 5.8°, 134 bead solids, no warnings.**

It is recorded rather than quietly deleted, per the Bible's fundamental rule.
The lesson is the programme's own method: that reservation was written from
reading the containment policy's *description*, and one measurement contradicted
it.

The other two retired reservations — `cluster` and `toi_et_moi` — were **right
about the risk and wrong about the remedy**. A ring family of that name would be
a second authority over placement *if it placed stones itself*; it does not, it
derives the existing stone family, exactly as `THREE_STONE_SYMMETRIC` has since
Sprint 28.

## What was deliberately NOT built

| Asked | Why not, and what must exist first |
| --- | --- |
| §2.1 stacking band | Needs a stone-less ring. `REQUIRED_COMPONENT_NAMES` forces `stone_reference` and `basket_support` — an ADR condition. Shares `plain_band`'s reservation rather than getting a second name. |
| §2.3 channel-set band | `setting/channel.py` builds straight prisms in the *stone's* frame and cannot follow the band's curve. Needs a swept wall along the band's centreline — the same primitive `SPLIT_SHANK_SCULPTED` waits on. |
| §2.4 flush / bezel band | The same prerequisite; not given a third reserved name for one blocker. |
| §2.7 tension-style family | The `tension` SETTING family already builds that geometry. A family would be a second name for one capability. |
| §3 cocktail / dome / bombé / sculptural | Each is defined by a SURFACE, and no surface or freeform capability exists. Sprint 31/32 territory, and §28 forbids absorbing them. |

**The same blocker also limits what was built:** an eternity ring still carries a
centre stone and head, because a stone-less ring is not representable. Every
`SR-001`–`SR-003` golden records that in `knownLimitations`.

## Governance

**No professional threshold was invented.** Every variant is `NOT_REVIEWED`, and
`test_no_specialty_rule_message_makes_a_manufacturing_claim` reads every rule
message a specialty design produces. `MAX_PAVE_STONES_PER_BAND` and
`MAX_CLUSTER_STONES` are software safety limits that sit at or below the
delegated engine's own limit, and say so.

**No second architecture.** `test_there_is_no_separate_specialty_generator`
asserts structurally that no specialty module exists; the specialty families are
registered against the same `build_solitaire_ring` generator, because a specialty
ring is the same assembly built from a different derived document.

**The neutrality guard still holds** — `ring_family/` imports no geometry and no
kernel after the extension, asserted by AST.

## Gates

| Gate | Result |
| --- | --- |
| `ruff check .` | **All checks passed** |
| `test_specialty_rings.py` | **64 passed** |
| `geometry-quality verify-all` | **All 73 goldens PASS**, zero existing baselines modified |
| `npx tsc -b` | **exit 0** |
| `npm run test` | **33 files, 275 tests passed** (plus 6 new specialty panel tests) |
| `pytest -q` (full backend) | **2707 passed, 0 failed** |

Two failures surfaced in the full run and both were real, not noise. The first
was the ring-family fingerprint in a recorded geometry-inspection example: adding
families moves `ring_family_fingerprint()`, which is the point of the field, so
`RING_FAMILY_TAXONOMY_VERSION` moved to `1.1.0` and the mirrors were regenerated.
`definitionHash` did **not** move for any existing document. The second was
Sprint 28's deliberate version tripwire asserting the literal `1.0.0` — it fired
exactly as designed, and was answered by recording the decision in it rather than
by loosening it. `RING_FAMILY_GEOMETRY_VERSION` stays `1.0.0`: no specialty
family constructs geometry of its own.

A third failure appeared only on Linux CI: the recorded-versus-rebuilt volume
for `ETERNITY_FULL` exceeded `rel=1e-9`. `ETERNITY_FULL` fuses 134 retention
solids into the band, so OCCT's per-boolean rounding compounds far past the
~1e-16 relative drift a single-fuse solitaire shows — the same-machine bound was
simply the wrong bound for a recorded-on-one-machine, re-measured-on-another
comparison. It now uses the project's own empirically-measured cross-platform
tolerance (`geometry_quality/version.py`, QUALITY-GOV-006), the same one the
`SR-001` golden already compares this variant with on Linux, so no number was
invented; and the exact structural assertions (component membership, stone
count) were moved ahead of it, so a lost bead still fails as a lost bead.

The backend CI job also gained a failure-reporting step: workflow logs need an
authenticated download, so a backend failure previously reached a reader as a
bare "Process completed with exit code 1". pytest's failure list is now
re-emitted as error annotations and into the job summary. It reports a failure;
it never changes one.

## Artifacts

- `backend/jewelmind/ring_family/` — extended: 3 families, 4 variants, 12
  parameters, the derivations, the dependency rows and the capability rows.
- `specs/ring-family/v1/` — the SAME directory, regenerated: 4 new examples and
  every vector re-measured.
- `docs/bible/31-specialty-rings/` — README, governance (10 SPECIALTY-GOV
  rules), execution boundary, coverage review and this report.
- `goldens/solitaire-v1/SR-001` … `SR-005`, each in the golden-update register.

## Not done, and why

- **Retention for a non-primary family member** — an RFC, and the single change
  that would make both `cluster` and `toi_et_moi` CURRENT.
- **Per-member stone specifications** — an RFC, and what a toi-et-moi with an
  oval and a pear needs.
- **A swept wall along the band's centreline** — an RFC that would unblock the
  channel-set band and three reserved Sprint 28 variants at once.
- **A stone-less ring** — an ADR, and what a true eternity band and every
  stacking band need.
- **Sprint 30's Ring Resizing & Matching Engine** — deliberately untouched.
