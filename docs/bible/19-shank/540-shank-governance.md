---
id: JM-BIBLE-540
title: Shank Governance
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-SHANK-README
related_documents:
  - JM-BIBLE-120
  - JM-BIBLE-090
  - JM-BIBLE-160
  - JM-BIBLE-460
implementation_status: current
professional_validation: not_required
normative: true
---

# Shank Governance

## SHANK-GOV-001 through SHANK-GOV-015

| ID | Rule |
|---|---|
| **SHANK-GOV-001** | Shank construction must remain deterministic. `geometry/shank/builder.py::build_shank()` never reads wall-clock time, randomness, or external state; the dispatch between the uniform and tapered construction paths depends only on `definition.band.widthTaper.mode`/`thicknessTaper.mode`, never on a heuristic or a prior call's result. |
| **SHANK-GOV-002** | "Shank" is an internal technical term only. It never appears in JDL field names, Studio UI copy, or Designer/Conversation user-facing text — `band` remains the public name (restating STUDIO-GOV-011 for this subsystem). |
| **SHANK-GOV-003** | Uniform-shank geometry must never regress. Any request with `widthTaper.mode == thicknessTaper.mode == "NONE"` uses the byte-identical pre-Sprint-17 `revolve()` construction in `_build_uniform_shank()`, including the outer-rim fillet logic — verified by the unchanged 9 Sprint-15 Golden cases requiring zero baseline updates. |
| **SHANK-GOV-004** | Section-profile generation must never see longitudinal variation. `geometry/shank/profile.py::build_profile()` takes only the already-resolved `inner_r`/`outer_r`/`half_width` for one angular position — taper interpolation happens exclusively in `builder.py`/`taper.py`, never inside a profile builder. |
| **SHANK-GOV-005** | Taper must be a pure function of angular distance from the head. `taper.py::taper_ratio(u, taper)` depends only on `u` and the taper spec — both shoulders (either direction from the head) receive identical behavior automatically; no code path may special-case "left" vs "right" shoulder with separately duplicated parameters. |
| **SHANK-GOV-006** | Reusable geometry infrastructure must stay Ring-agnostic. Nothing under `geometry/shank/` may import `jewelmind.ring`; `geometry/connection.py` (the Shank → RingHead handoff) lives in the Atlas layer specifically because `jewelmind.ring` must depend on Atlas, never the reverse — a real circular import was found and fixed during this Sprint by relocating this exact module (see [`541-shank-architecture-overview.md`](541-shank-architecture-overview.md)). |
| **SHANK-GOV-007** | A construction failure must be a real, raised exception — never a silent fallback. `ShankConstructionError` is raised when a loft fails or produces an invalid/empty solid; nothing in `build_shank()` catches it to silently substitute uniform geometry. |
| **SHANK-GOV-008** | A changed taper default, section count, or angular sampling scheme is a MAJOR change to Shank's generation contract. Changing `SECTION_COUNT`, the head-anchoring convention (`u=0`), or `TOWARD_BOTTOM`'s interpolation formula requires a new Golden case or an explicit, documented Golden baseline update — never a silent numeric drift (mirrors ATLAS-GOV-015/FORGE-GOV-007's versioning discipline for this subsystem). |
| **SHANK-GOV-009** | New Shank capabilities require new Golden cases, never retrofitted old ones. SOL-010/011/012 (width taper, thickness taper, combined taper) were added as new cases in `goldens/solitaire-v1/`; no existing SOL-001 through SOL-009 case was altered to add taper coverage. |
| **SHANK-GOV-010** | The Shank → RingHead connection interface must stay explicit and named. `ShankConnectionInterface` (`topZMm`/`embedMm`/`headCenterRadiusMm`) is the one real contract `prongs.py`/`basket.py` consume; no component builder may reach into `geometry/shank/` internals or hardcode a shank-derived constant independently. |
| **SHANK-GOV-011** | A tapered shank's connection interface must never move. `TOWARD_BOTTOM` always preserves the full base width/thickness exactly at `u=0` (the head) — `topZMm` is identical for every taper configuration, so no taper change can ever require touching prong/basket placement logic. |
| **SHANK-GOV-012** | No professional threshold or subjective descriptor may be invented for taper. No code path in `geometry/shank/` or `design_intent/` may map a word like "more delicate" or "elegant" to an arbitrary `bottomRatio` value; taper is a purely geometric parameter, requested explicitly via JDL, never inferred (restating LAW from [`04-jewelry-domain/040-domain-governance.md`](../04-jewelry-domain/040-domain-governance.md) for this subsystem). |
| **SHANK-GOV-013** | Shank must report geometric facts, distinguishing CONSTRUCTION_PARAMETER from MEASURED_GEOMETRY, never a jewelry-domain judgment. `widthSamplesMm`/`thicknessSamplesMm` on tapered metadata are computed from the same taper function used to build the loft (CONSTRUCTION_PARAMETER, not independently re-measured) and are documented as such — restating INSPECT-GOV-001/002 for this subsystem's own metadata. |
| **SHANK-GOV-014** | An unimplemented capability must be reported as a real, documented limitation, never a silent gap. The tapered path's missing outer-rim fillet sets `filletApplied: false` with an explicit `filletSkippedReason`, and every affected Golden case lists it under `knownLimitations` — restating ATLAS-GOV-004/005 for this subsystem. |
| **SHANK-GOV-015** | The Shank capability registry is the single source of truth for CURRENT vs PLANNED. `geometry/shank/capability.py::SHANK_CAPABILITIES` (mirrored at `specs/shank/v1/capability-registry.json`) is the only place allowed to assert a capability is `current`; no documentation, Designer capability list, or Studio copy may claim a capability this registry marks `planned`. |

## Relationship to Atlas, Ring Architecture, and Inspection governance

This document sits alongside [`07-atlas/120-atlas-governance.md`](../07-atlas/120-atlas-governance.md) (Sprint 5), [`18-ring-architecture/520-jewelry-category-architecture.md`](../18-ring-architecture/520-jewelry-category-architecture.md) (Sprint 16), and [`16-geometry-inspection/460-inspection-governance.md`](../16-geometry-inspection/460-inspection-governance.md) (Sprint 14) — it does not supersede any of them. ATLAS-GOV-002 ("Atlas reports geometric facts; only Forge interprets them") and the Ring/Atlas layering direction from Sprint 16 are the two boundaries SHANK-GOV-006/013 make concrete for this specific subsystem.

## When an ADR is required

Adding a new section-profile type (e.g. knife edge), a new taper mode (e.g. `TOWARD_HEAD` or a non-linear curve), a new centerline path (e.g. Euro shank), multiple rails (split shank), replacing loft with a different construction primitive, or any change that violates SHANK-GOV-001 through 015 without superseding this document first.

## When an RFC is required

A new ring style, setting type, or jewelry category whose geometry depends on Shank changes beyond what this document already reserves — see [`../04-jewelry-domain/056-domain-extension-strategy.md`](../04-jewelry-domain/056-domain-extension-strategy.md). Widening `BandTaperMode` beyond `NONE`/`TOWARD_BOTTOM` requires an RFC even though it is architecturally an additive JDL change, because it changes the taper *model*, not just adds a field.
