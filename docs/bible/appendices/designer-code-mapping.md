---
id: JM-BIBLE-A62
title: "Appendix: Designer Code Mapping"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-DESIGNER-README
  - JM-BIBLE-290
related_documents: []
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Designer Code Mapping

Maps each Bible doc topic (291 through 322) in `docs/bible/12-designer/` to the real file(s)/function(s) that implement it, mirroring [`studio-code-mapping.md`](studio-code-mapping.md)'s style.

| Doc | Topic | Real file(s) / function(s) |
|---|---|---|
| 291 | Designer architecture overview | `backend/jewelmind/designer/` package as a whole; `backend/jewelmind/api/routes.py::designer_interpret_route` |
| 292 | Natural-language input contract | `designer/schemas.py::NaturalLanguageDesignRequest` |
| 293 | Intent extraction model | `designer/schemas.py::RawDesignerResponse`/`RawProposedValue`; `designer/provider.py::_TOOL_INPUT_SCHEMA` |
| 294 | Design proposal model | `designer/schemas.py::DesignerProposal` |
| 295 | Designer-to-JDL contract | `designer/service.py::_apply_patch`, `DesignerService._build_proposal` |
| 296 | Capability awareness | `designer/capability.py::current_capabilities`, `is_known_field`, `enum_capability_key`, `is_supported_enum_value` |
| 297 | Supported language scope | `designer/normalizer.py`'s synonym tables (`METAL_SYNONYMS`, `BAND_PROFILE_SYNONYMS`, `STONE_SHAPE_SYNONYMS`, `SETTING_TYPE_SYNONYMS`, `MANUFACTURING_SYNONYMS`, `PRONG_COUNT_WORDS`) |
| 298 | Defaulting policy | `designer/service.py::DesignerService.interpret` (base = `JewelryDefinition()` on CREATE, or `currentJDL` on MODIFY) |
| 299 | Ambiguity model | `designer/normalizer.py::AMBIGUOUS_METAL_TERMS`, `normalize_enum_token`; `designer/service.py`'s `RawAmbiguity` handling loop |
| 300 | Clarification policy | `designer/schemas.py::ClarificationQuestion`; `designer/service.py`'s `RawClarification` handling loop; `frontend/src/components/DesignerPanel.tsx::handleClarify` |
| 301 | Unsupported request handling | `designer/capability.py::KNOWN_UNSUPPORTED_CONCEPTS`; `designer/schemas.py::UnsupportedFeature` |
| 302 | Confidence model | `designer/schemas.py::ConfidenceCategory`; the `confidence=` assignments in `designer/service.py::_build_proposal` |
| 303 | Field provenance model | `designer/schemas.py::FieldProvenance`, `ProposedField.provenance` |
| 304 | AI output constraining | `designer/provider.py::_TOOL_INPUT_SCHEMA`, `AnthropicDesignerProvider.interpret`'s `tool_choice` |
| 305 | Structured output contract | `designer/schemas.py::RawDesignerResponse`; `designer/provider.py::AnthropicDesignerProvider.interpret`'s `RawDesignerResponse.model_validate(...)` re-validation |
| 306 | Prompt architecture | `designer/prompts.py::build_system_prompt`, `build_user_message` |
| 307 | Provider abstraction | `designer/provider.py::DesignerProvider`, `FakeDesignerProvider`, `AnthropicDesignerProvider`, `get_designer_provider` |
| 308 | Designer validation pipeline | `designer/service.py::DesignerService._build_proposal` (the full normalize -> capability-check -> provenance -> candidate JDL -> Forge sequence) |
| 309 | Designer-Forge integration | `designer/service.py`'s calls to `jewelmind.validation.engine.validate_definition`/`has_errors`; `designer/schemas.py::ForgeEvaluationSummary` |
| 310 | User review and acceptance | `frontend/src/components/DesignerPanel.tsx::handleApply`; `frontend/src/store/useProjectStore.ts::applyDesignerProposal` |
| 311 | Proposal diff model | `designer/normalizer.py::compute_diff`, `flatten_definition`; `designer/schemas.py::FieldDiff` |
| 312 | Designer error model | `designer/errors.py` (the 11 `DESIGNER_*` codes) |
| 313 | Designer security model | `designer/normalizer.py::detect_prompt_injection_risk`, `_INJECTION_MARKERS`; `designer/errors.py::DesignerSecurityRejectedError` |
| 314 | Prompt injection and untrusted input | Same as 313 — `designer/normalizer.py::detect_prompt_injection_risk` |
| 315 | Privacy and data boundaries | `designer/provider.py::AnthropicDesignerProvider` (request text sent to Anthropic only, no persistence beyond the request/response cycle) |
| 316 | Designer observability | Not separately implemented beyond standard API error responses; no dedicated logging/metrics module exists yet for Designer |
| 317 | Designer cost and latency model | Not implemented as code (no token/cost accounting); `AnthropicDesignerProvider`'s `max_tokens=2048` is the only cost-relevant constant |
| 318 | Designer evaluation framework | `backend/tests/test_designer_corpus.py` (the 62-case corpus functions as the evaluation framework) |
| 319 | Designer test corpus | `backend/tests/test_designer_corpus.py::CASES` |
| 320 | Current Studio integration | `frontend/src/components/DesignerPanel.tsx`; `frontend/src/store/useProjectStore.ts::applyDesignerProposal` |
| 321 | Designer gap analysis | `designer/provider.py::AnthropicDesignerProvider` (implemented but not live-verified); `designer/schemas.py`'s 7 unused `FieldProvenance` values |
| 322 | Open designer questions | No dedicated code — a documentation-only topic |

**Files with no corresponding numbered doc (infrastructure, not a distinct topic):** `designer/errors.py` (312), `designer/prompts.py` (306) — both already listed above; `backend/jewelmind/api/schemas.py`'s re-export of Designer request/response models for the FastAPI route, and `frontend/src/api/client.ts::interpretDesignRequest`/`frontend/src/api/types.ts`'s Designer type mirrors, which have no dedicated topic doc and are covered only by 291's architecture overview.
