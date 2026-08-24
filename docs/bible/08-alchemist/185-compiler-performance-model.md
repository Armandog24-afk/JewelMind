---
id: JM-BIBLE-185
title: Compiler Performance Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-184
related_documents:
  - JM-BIBLE-148
implementation_status: partial
professional_validation: not_required
normative: false
---

# Compiler Performance Model

Restates and extends Sprint 5's [`07-atlas/148-performance-and-resource-model.md`](../07-atlas/148-performance-and-resource-model.md) at the compiler level.

## Measurable timings, current vs. planned

| Stage | Currently measured? |
|---|---|
| Normalization | No |
| Forge evaluation | No |
| Planning | N/A — no planning stage exists |
| Band construction | No — folded into total `generation_duration_s` |
| Stone construction | No, same reasoning |
| Basket construction | No, same reasoning |
| Prong construction | No, same reasoning |
| Inspection | No |
| Preview tessellation | No |
| STEP export | No |
| STL export | No |
| **Total compilation** | **Yes** — `GeneratedModel.generation_duration_s`, the only current timing measurement anywhere in the pipeline |

## No SLA targets invented

Per this Sprint's explicit instruction, no numeric performance target is proposed anywhere in this document — Sprint 5 already established this discipline (`ATLAS-GAP-016`) and this document does not weaken it.

## Proposed benchmark methodology (not implemented)

A future benchmark suite would wrap each of the stages above in its own timer, run against a fixed set of representative definitions (the default solitaire, plus the boundary-value examples already checked into `specs/jdl/v1/examples/`), and report distributions (not single-sample timings, which are noisy) across multiple runs on the same machine — never compared across different machines/OSes without accounting for the same cross-platform variance already documented in [`07-atlas/137-determinism-and-reproducibility.md`](../07-atlas/137-determinism-and-reproducibility.md).

## No CI thresholds added

Per this Sprint's explicit instruction, no benchmark test with a numeric pass/fail threshold was added — a flaky performance-based CI gate would create exactly the kind of avoidable red-build noise already flagged as a real problem in this project's own recent history.
