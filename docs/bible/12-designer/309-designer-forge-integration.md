---
id: JM-BIBLE-309
title: Designer Forge Integration
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-308
related_documents:
  - JM-BIBLE-310
implementation_status: current
professional_validation: not_required
normative: true
---

# Designer Forge Integration

## `forgeEvaluation` is always a real `validate_definition()` call

`DesignerProposal.forgeEvaluation` is never invented, approximated, or pre-computed by Designer's own logic. `service.py::_build_proposal()` calls the exact same `jewelmind.validation.engine.validate_definition()` and `has_errors()` that every other entry point in the codebase (manual editing, the `/api/models/validate` route) uses, against the real `candidate` `JewelryDefinition`. Designer contributes nothing to what counts as a rule violation — it only routes a candidate through the one authoritative validator (DESIGNER-GOV-003).

## Real example: an AI-proposed value producing a genuine Forge warning

`backend/tests/test_designer.py::TestForgeIntegration::test_forge_warning_is_surfaced_on_the_proposal` constructs a `RawDesignerResponse` proposing `band.thickness = 1.5`, runs it through `DesignerService(provider=FakeDesignerProvider(response=raw)).interpret(...)`, and asserts `JM-BAND-002` appears in `result.proposal.forgeEvaluation.results`. `JM-BAND-002` is a real Forge rule in `validation/engine.py::_band_rules` — the same rule that would fire if a user typed `1.5` into the band-thickness field by hand. Designer did not know this rule exists; it simply proposed a value, and Forge, run downstream, found the same thing it would find for any other source of that value.

A companion test, `test_forge_error_does_not_block_the_proposal_from_being_returned`, proposes `band.thickness = 0.5` (a Forge error tier) and asserts `forgeEvaluation.hasErrors is True` while `candidateJDL is not None` — the proposal still reaches the user with the violation visible, rather than being suppressed.

## The LLM never decides whether a warning is acceptable

Nothing in `RawDesignerResponse` carries an opinion about a Forge result, and nothing in `_build_proposal()` reads one back from the provider. A Forge warning or error is presented in the proposal's forge summary (`DesignerPanel.tsx`'s "Design rule check: N errors, N warnings" line) purely as information for the user reviewing the proposal — accepting or rejecting it because of that warning remains entirely the user's judgment call, exercised through the ordinary Apply/Cancel review flow described in [`310-user-review-and-acceptance.md`](310-user-review-and-acceptance.md). Designer never auto-adjusts a value to avoid triggering a rule, and never blocks Apply on a Forge warning or error — only `NEEDS_CLARIFICATION` blocks Apply (see [`300-clarification-policy.md`](300-clarification-policy.md)).

## Why Forge runs downstream, never inside Designer

Designer could, in principle, have re-implemented a subset of Forge's numeric thresholds to give faster feedback during interpretation. It deliberately does not: a duplicated threshold is a threshold that can silently drift out of sync with the real one, and jewelry-domain thresholds are Forge's authority alone (ATLAS-GOV-002-style boundary, restated for Designer as DESIGNER-GOV-003/008). Running the same `validate_definition()` call every other entry point runs, on the same candidate, is what guarantees a Designer-originated design is judged by identical rules to a hand-edited one — there is no "AI-assisted" leniency tier.

See [`06-forge/README.md`](../06-forge/README.md) for Forge's own governance, and [`301-unsupported-request-handling.md`](301-unsupported-request-handling.md) for the related but distinct concept of a feature Forge never even gets to see because capability-awareness rejected it first.
