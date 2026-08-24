---
id: JM-BIBLE-A28
title: "Appendix: Alchemist State Transition Matrix"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-170
related_documents:
  - JM-BIBLE-169
implementation_status: planned
professional_validation: not_required
normative: true
---

# Appendix: Alchemist State Transition Matrix

From [`08-alchemist/170-compilation-state-machine.md`](../08-alchemist/170-compilation-state-machine.md) — no state is actually stored anywhere in current code; this matrix is the conceptual target.

| From | To | Trigger |
|---|---|---|
| (start) | RECEIVED | HTTP request arrives |
| RECEIVED | NORMALIZING | Pydantic parsing begins |
| NORMALIZING | VALIDATING | `validate_definition()` called |
| VALIDATING | BLOCKED | ≥1 error-severity Forge diagnostic |
| VALIDATING | PLANNING | Zero error-severity diagnostics |
| BLOCKED | (terminal) | — |
| PLANNING | GENERATING | (currently skipped — no plan stage exists) |
| GENERATING | FAILED | Construction exception |
| GENERATING | INSPECTING | `GeneratedModel` returned |
| INSPECTING | ARTIFACT_GENERATION | (implicit — folded into GENERATING today) |
| ARTIFACT_GENERATION | COMPLETED | Every requested artifact succeeded |
| ARTIFACT_GENERATION | COMPLETED_WITH_WARNINGS | A non-required artifact failed |
| FAILED | (terminal) | — |
| COMPLETED | (terminal) | — |
| COMPLETED_WITH_WARNINGS | (terminal) | — |
| RECEIVED | CANCELLED | Not currently reachable |
| CANCELLED | (terminal) | — |

## Build-order cross-reference

See [`08-alchemist/169-component-build-order.md`](../08-alchemist/169-component-build-order.md) for the sub-state machine within GENERATING: `band`, `stone_reference`, `prongs`, `basket_support` have no ordering constraint among themselves; only the final fuse step depends on `band`, `prongs`, and `basket_support` (not `stone_reference`).
