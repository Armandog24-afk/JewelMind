---
id: JM-BIBLE-188
title: Open Alchemist Questions
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-187
related_documents:
  - JM-BIBLE-ALCHEMIST-README
implementation_status: current
professional_validation: not_required
normative: false
---

# Open Alchemist Questions

| ID | Question | Impact | Provisional behavior | Priority | Blocking? | Decision mechanism |
|---|---|---|---|---|---|---|
| `ALCHEMIST-OQ-001` | Should `GeometryPlan` become a persisted artifact? | Affects caching, debuggability, and future component-level regeneration | Not persisted — doesn't exist | Low | No | Design work once a first real need arises (see `ALCHEMIST-GAP-001`) |
| `ALCHEMIST-OQ-002` | Should `GeometryPlan` be publicly inspectable via the API? | Affects transparency for advanced users/tools vs. surface-area growth | N/A — no plan exists to expose | Low | No | Product decision, if `GeometryPlan` is ever implemented |
| `ALCHEMIST-OQ-003` | Should identical `GeometryPlan`s be cached independently of JDL? | Could allow cache hits across two JDL documents that happen to normalize to the same plan | Today, caching is keyed on `definitionHash` (JDL-level), not plan-level | Low | No | Design work once `GeometryPlan` exists |
| `ALCHEMIST-OQ-004` | Should artifact requests be part of `CompilationInput` or separate API calls? | A unified request could reduce round-trips; separate calls are simpler and already correctly decoupled for export | Separate calls today (except preview, which is coupled — see `ALCHEMIST-GAP-004`) | Medium | No | Team discussion, informed by resolving `ALCHEMIST-GAP-004` first |
| `ALCHEMIST-OQ-005` | Should preview generation be part of compilation or downstream? | Directly resolves `ALCHEMIST-GAP-004` | Currently part of compilation (coupled) | High | No | Engineering decision, likely "downstream," given exports already prove the decoupled pattern works |
| `ALCHEMIST-OQ-006` | How should partial success appear in the API? | Affects whether `COMPLETED_WITH_WARNINGS` ever becomes a real, distinct HTTP-visible status | Warnings are returned today but not flagged as a distinct status from a clean success | Low | No | API design decision |
| `ALCHEMIST-OQ-007` | Should compiler capability negotiation occur before validation? | Affects whether an unsupported-capability request fails fast (before Forge runs) or late (after) | No negotiation exists at all today | Low | No | Design work once a capability endpoint exists (`ALCHEMIST-GAP-008`) |
| `ALCHEMIST-OQ-008` | Which versions participate in `compilationHash`? | Directly resolves the exact formula in [`175-definition-hash-vs-compilation-hash.md`](175-definition-hash-vs-compilation-hash.md) | The PROPOSED formula includes definitionHash, compilerVersion, geometryGeneratorVersion, forgeRuleSetVersion — not yet decided as final | Medium | No | ADR, since it's a hashing-contract decision |
| `ALCHEMIST-OQ-009` | How should old JDL documents select historical compilers? | Matters once a second compiler version ever ships | N/A — only one compiler "version" (implicit) has ever existed | Low | No | Design work once a second version ships |
| `ALCHEMIST-OQ-010` | Should compilation be cancellable? | The `CANCELLED` state exists conceptually in [`170-compilation-state-machine.md`](170-compilation-state-machine.md) but is unreachable today | Not cancellable — a request runs to completion or failure | Low | No | Product decision, relevant mainly if generation ever becomes slow enough to matter |
| `ALCHEMIST-OQ-011` | Should future long-running generation become asynchronous? | Affects API shape significantly (polling, webhooks, or async job IDs) | Fully synchronous today; generation for the default definition takes well under a second | Low | No | Revisit if/when generation time becomes a real user-facing problem |
| `ALCHEMIST-OQ-012` | How should component-level regeneration work? | Would let an edit to `setting.prongCount` rebuild only `prongs`, not the whole assembly | Not possible today — every edit triggers a full `build_solitaire_ring()` call | Low | No | Design work, dependent on `GeometryPlan` existing first (`ALCHEMIST-GAP-001`) |

## What this document is not

Not a roadmap and not a set of recommendations disguised as questions — each provisional behavior is exactly what the code does today, so a future decision-maker starts from the true current state.
