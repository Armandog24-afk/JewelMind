---
id: JM-BIBLE-291
title: Designer Architecture Overview
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-290
related_documents:
  - JM-BIBLE-292
implementation_status: current
professional_validation: not_required
normative: true
---

# Designer Architecture Overview

## The pipeline, stage by stage

```
NaturalLanguageDesignRequest
        │  DesignerService.interpret()
        ▼
1. Security screen        normalizer.detect_prompt_injection_risk()
2. Provider resolution     get_designer_provider() → provider | None
3. Provider call           provider.interpret(request, context) → RawDesignerResponse
4. Field/capability gate   capability.is_known_field() / enum_capability_key()
5. Enum normalization      normalizer.normalize_enum_token()
6. Provenance + confidence tagging   service._build_proposal()
7. Ambiguity / unsupported / clarification folding
8. Candidate JDL construction        service._apply_patch()
9. JDL + Forge validation  JewelryDefinition.model_validate(), validate_definition()
10. Diff computation        normalizer.compute_diff()
11. Status resolution       service._resolve_status()
        ▼
DesignerProposal → DesignerResult
```

Every request runs this full sequence exactly once; there is no partial pipeline, no caching of a prior interpretation, and no server-held state between requests. `backend/jewelmind/designer/service.py::DesignerService.interpret()` is the single entry point, and `POST /api/designer/interpret` in `backend/jewelmind/api/routes.py` is the only caller.

## Module ownership

| Stage | Module |
|---|---|
| Request/response shapes | `backend/jewelmind/designer/schemas.py` |
| Security screening | `backend/jewelmind/designer/normalizer.py::detect_prompt_injection_risk()` |
| Provider abstraction | `backend/jewelmind/designer/provider.py` |
| Prompt construction (only used by the Anthropic provider) | `backend/jewelmind/designer/prompts.py` |
| Capability gating | `backend/jewelmind/designer/capability.py` |
| Enum/synonym normalization, diffing | `backend/jewelmind/designer/normalizer.py` |
| Orchestration, provenance/confidence tagging, status resolution | `backend/jewelmind/designer/service.py` |
| HTTP-level error mapping | `backend/jewelmind/designer/errors.py` |

## Why this is a pipeline, not an agent

Designer is not an agentic loop, does not call tools iteratively, and does not hold a conversation across multiple provider calls. One `NaturalLanguageDesignRequest` produces exactly one provider call and one deterministic pass through steps 4–11. A multi-turn conversation would be a new capability requiring an RFC — see [`321-designer-gap-analysis.md`](321-designer-gap-analysis.md) and DESIGNER-GOV rules in [`290-designer-governance.md`](290-designer-governance.md).

## What each stage can and cannot change

Steps 1–3 are the only stages that touch anything AI-shaped. From step 4 onward, every decision is plain, deterministic Python running against `RawDesignerResponse` — the same code path executes identically whether the response came from `FakeDesignerProvider` in a test or (once configured) `AnthropicDesignerProvider` in production. This is what makes the 62-case test corpus in [`319-designer-test-corpus.md`](319-designer-test-corpus.md) a meaningful proxy for real behavior without ever calling a live model.

## Where this sits relative to the rest of the pipeline

Designer produces a `candidateJDL` that a user must explicitly accept (`useProjectStore.applyDesignerProposal()`) before it becomes `currentDefinition`. From that point forward, the design flows through the exact same JDL → Forge → Alchemist → Atlas pipeline as any manually-edited design — see the README's diagram and [`../08-alchemist/README.md`](../08-alchemist/README.md). Designer has no special-cased downstream behavior once a proposal is applied.

See [`292-natural-language-input-contract.md`](292-natural-language-input-contract.md) for the request shape this pipeline consumes.
