---
id: JM-BIBLE-311
title: Proposal Diff Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-310
related_documents:
  - JM-BIBLE-312
implementation_status: current
professional_validation: not_required
normative: true
---

# Proposal Diff Model

## `compute_diff()` and `flatten_definition()`

`normalizer.py::flatten_definition()` turns a `JewelryDefinition` into a flat `{"section.field": value}` dict by walking `model_dump(mode="json")`'s top-level sections. `compute_diff(before, after)` then builds one `FieldDiff` per path in the flattened `after`, each carrying `path`, `previousValue`, `proposedValue`, and a `changed` boolean. When `before` is `None` (a `CREATE`), every field is reported with `changed=False` against itself, so the diff shape is uniform regardless of interaction mode rather than requiring the caller to branch on it.

This is a plain, exhaustive dict comparison — no heuristics, no semantic weighting of which fields "matter more," and no LLM involvement at any point (see [`311-proposal-diff-model.md`](311-proposal-diff-model.md)'s own module docstring reference in `normalizer.py`: "Never LLM-generated"). It runs identically whether the underlying `RawDesignerResponse` came from `FakeDesignerProvider` or a live provider.

## Where the diff is used today

`DesignerProposal.diff` is populated on every `MODIFY` proposal (and, trivially, every `CREATE` proposal) as part of `_build_proposal()`'s stage 8 (see [`308-designer-validation-pipeline.md`](308-designer-validation-pipeline.md)). `backend/tests/test_designer.py::TestProposalDiff` confirms `test_diff_reports_only_actual_changes` and `test_diff_on_create_reports_nothing_changed`. The data reaches the API response in every `DesignerResult`, and `specs/designer/v1/`'s examples include it.

## Not yet separately rendered — a real, named gap

`diff` is computed and shipped in the API response, but `DesignerPanel.tsx` does not currently render a dedicated "before -> after" diff view from it. Today, the effect of a proposed change is only visible through the "JewelMind understood" field list (each proposed field's new value, with provenance), which folds the same information into a different, less explicit presentation — a user has to already know the previous value to recognize what changed. A richer diff UI (e.g. a two-column before/after table, or inline strikethrough of replaced values) is real future work, not a current capability; it is tracked as a named gap in [`321-designer-gap-analysis.md`](321-designer-gap-analysis.md) rather than implemented speculatively here.

## Determinism as a design choice, not an incidental property

Because `compute_diff()` operates purely on two already-constructed `JewelryDefinition` objects, the same `before`/`after` pair always produces the identical `FieldDiff` list, independent of which provider (fake or real) produced the underlying proposal, and independent of call order or timing. This mirrors the same CAD-determinism discipline CLAUDE.md requires of geometry generation — a diff is a fact about two states, not a judgment call an AI could phrase differently on a re-run.

See [`312-designer-error-model.md`](312-designer-error-model.md) for the diagnostic vocabulary that runs alongside this diff in the same proposal.
