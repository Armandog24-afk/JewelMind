---
id: JM-BIBLE-308
title: Designer Validation Pipeline
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-307
related_documents:
  - JM-BIBLE-309
implementation_status: current
professional_validation: not_required
normative: true
---

# Designer Validation Pipeline

`DesignerService.interpret()` and `_build_proposal()` run a fixed, ordered sequence of stages. No stage is skippable, and no AI output reaches a `candidateJDL` without passing through all of them.

## The ordered stages

1. **Prompt-injection screen** — `normalizer.detect_prompt_injection_risk(request.text)`, before anything else, including before checking whether a provider is even configured. A match raises `DesignerSecurityRejectedError` (400) immediately. See [`313-designer-security-model.md`](313-designer-security-model.md).
2. **Provider-configured check** — `if self._provider is None: raise DesignerProviderUnavailableError`. Only reached if stage 1 passed.
3. **Provider call** — `self._provider.interpret(request, context)`, wrapped so any `AppError` the provider itself raised propagates with its specific code, and any other exception becomes a generic `DesignerProviderError`.
4. **Per-field capability/enum/numeric processing** — for every `RawProposedValue` in `raw.proposedCanonicalValues`: `capability.is_known_field()` gate, then (for enum fields) `normalizer.normalize_enum_token()` producing either a `ClarificationQuestion` (ambiguous), an `UnsupportedFeature` (unrecognized), or a `ProposedField` (resolved); `project.name` handled directly; numeric fields parsed with `float()` or diagnosed as `DESIGNER_PROPOSAL_INVALID`.
5. **Ambiguity/unsupported/clarification folding** — `raw.ambiguities`, `raw.detectedUnsupportedFeatures`, and `raw.clarificationCandidates` are each folded into their respective outbound lists, independent of stage 4's per-field results.
6. **Patch application** — `_apply_patch(base, patch)`: `base.model_dump(mode="python")`, dotted-path assignment into the nested dict, then a real `JewelryDefinition.model_validate(data)` call. A `ValidationError` here returns `None`, which becomes proposal status `INVALID` with no Forge evaluation and no diff (DESIGNER-GOV-002).
7. **Real Forge evaluation** — `validate_definition(candidate)` and `has_errors(validation)` from `jewelmind.validation.engine`, wrapped as `ForgeEvaluationSummary`. Never reimplemented or waived by Designer (DESIGNER-GOV-003). See [`309-designer-forge-integration.md`](309-designer-forge-integration.md).
8. **Diff computation** — `normalizer.compute_diff(request.currentJDL if MODIFY else None, candidate)`, a deterministic dict-diff. See [`311-proposal-diff-model.md`](311-proposal-diff-model.md).
9. **Status resolution** — `_resolve_status()` derives `proposalStatus` from the accumulated clarifications, unsupported features, proposed fields, and unresolved intent — see [`301-unsupported-request-handling.md`](301-unsupported-request-handling.md) and [`300-clarification-policy.md`](300-clarification-policy.md) for the individual rules.

## Why order matters

The security screen running before the provider-configured check means a malicious request is rejected identically whether or not a provider happens to be configured — `DESIGNER_SECURITY_REJECTED` never depends on environment state. Capability/enum processing running before patch application means an unsupported or ambiguous field never reaches `JewelryDefinition.model_validate()` at all; only values that already passed deterministic gating are ever placed in `patch`. Forge evaluation running only after a valid `candidate` exists means Forge is never asked to validate a `None`.

## No stage is short-circuited by a partial success

A request that produces some unsupported features and some valid fields still runs every later stage: patch application still happens with whatever survived gating, Forge still evaluates the resulting candidate, and a diff is still computed — the pipeline never stops early just because part of the request couldn't be honored (see `PARTIALLY_SUPPORTED` in [`301-unsupported-request-handling.md`](301-unsupported-request-handling.md)). The only stages that do stop the pipeline early are the two HTTP-failure checks (1 and 2) and a `candidate is None` result from stage 6, which skips Forge evaluation and diffing entirely because there is nothing valid to evaluate.

See [`305-structured-output-contract.md`](305-structured-output-contract.md) for what stage 3 hands to stage 4, and [`312-designer-error-model.md`](312-designer-error-model.md) for the full diagnostic-code vocabulary these stages emit into.
