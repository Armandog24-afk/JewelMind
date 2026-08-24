---
id: JM-BIBLE-151
title: Open Atlas Questions
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-150
related_documents:
  - JM-BIBLE-ATLAS-README
implementation_status: current
professional_validation: not_required
normative: false
---

# Open Atlas Questions

| ID | Question | Impact | Provisional behavior | Blocking? | Decision mechanism | Required expertise |
|---|---|---|---|---|---|---|
| `ATLAS-OQ-001` | Should Atlas expose a kernel-neutral geometry interface in the future? | A large architectural undertaking — would touch every builder | CadQuery/OpenCascade is used directly throughout; no abstraction layer exists (VISION-tier, not scoped) | No | ADR, if ever pursued | CAD architecture |
| `ATLAS-OQ-002` | Should CadQuery remain directly visible to component builders, or should a thin wrapper layer be introduced? | Affects testability and future kernel independence | Direct CadQuery calls throughout today, with two narrow exceptions (`FlatCircleAtRadius`, the fillet/fuse fallbacks) | No | Team discussion | Backend/CAD |
| `ATLAS-OQ-003` | Should production metal always be fused before STEP export, even if that means rejecting a definition whose fuse fails rather than falling back to a compound? | Would remove the current graceful-degradation guarantee (LAW-005) | Compound fallback is always accepted today — never rejected | No | ADR, since it would weaken an existing LAW-005 guarantee | CAD/manufacturing |
| `ATLAS-OQ-004` | How should disconnected valid multi-solid assemblies be represented in exports/metadata going forward? | Affects `ATLAS_COMPONENT_MISSING`-adjacent error semantics and `combined_metal`'s reported solid count | Currently just "however many solids `Solids()` returns," with a text warning | No | Design work at the time GAP-002 is addressed | Backend/CAD |
| `ATLAS-OQ-005` | How should component identity persist across regeneration, specifically for individual prongs? | See [`138-component-naming-and-identity.md`](138-component-naming-and-identity.md) | No persistent per-prong identity exists | No | Design work if a per-prong feature (e.g. selective prong editing) is ever proposed | Backend |
| `ATLAS-OQ-006` | Which topology checks should run on every generation, once any exist at all? | Determines request-latency cost vs. safety tradeoff | None run today | No | Engineering decision once GAP-001 is addressed | Backend/CAD |
| `ATLAS-OQ-007` | Should preview and STL export use identical tessellation settings and shape graphs? | They currently use the same default tolerance values but tessellate different shape graphs (per-component vs. fused) — see [`129-mesh-model.md`](129-mesh-model.md) | Same tolerance defaults, different shape graphs, by current design | No | Team discussion | Backend |
| `ATLAS-OQ-008` | Should geometry-generator version participate in model identity (i.e., in `definitionHash` or `modelId`)? | Currently `definitionHash` is purely a function of the JDL document, independent of `GENERATOR_VERSION` — two different generator versions could produce a different actual solid for the same hash | Not included today (see [`05-jdl/076-canonicalization-and-definition-hashing.md`](../05-jdl/076-canonicalization-and-definition-hashing.md) for the adjacent JDL-level open question `JDL-OQ-001`) | No | ADR, since it's a hashing-contract change | Backend |
| `ATLAS-OQ-009` | How should OpenCascade kernel-version changes affect reproducibility guarantees? | See [`137-determinism-and-reproducibility.md`](137-determinism-and-reproducibility.md) | Untested; `cadquery>=2.5` is a minimum version pin, not exact | No | Cross-version testing, when resources allow | Backend/CAD |
| `ATLAS-OQ-010` | Should a failed fillet always produce fallback geometry, or should some fillet failures be treated as blocking errors instead? | Currently every fillet failure silently degrades to sharp edges — always, unconditionally | Always falls back today, per [`135-fillets-rounding-and-fallbacks.md`](135-fillets-rounding-and-fallbacks.md) | No | Team discussion | Backend/jewelry design |
| `ATLAS-OQ-011` | Where should local-thickness analysis live — Atlas (as a measurement) or a new shared module? | See `ATLAS-GAP-004` | Does not exist anywhere today | No | Design work when this capability is prioritized | CAD engineering + manufacturing |
| `ATLAS-OQ-012` | How should future stone-seat geometry (a modeled bearing/seat cut, rather than plain cylindrical prong overlap) be represented? | A real future geometry feature per `FORGE-GAP-001`/`FORGE-GAP-002` (Sprint 4) | Prongs are plain cylinders today, with no seat concept | No | RFC, since it's a new geometric feature | Bench jeweler + CAD engineering |

## What this document is not

Not a roadmap and not a set of recommendations disguised as questions — each provisional behavior is exactly what the code does today, so a future decision-maker starts from the true current state.
