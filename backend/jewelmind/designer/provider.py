"""Provider abstraction — decouples Designer's service logic from any vendor.

See docs/bible/12-designer/307-provider-abstraction.md. `DesignerProvider`
is the only interface the service depends on; `FakeDesignerProvider` is
the mandatory, test-only implementation (DESIGNER-GOV, "FakeProvider is
mandatory" — never a silent runtime fallback for real end users, see
`get_designer_provider()` below). `AnthropicDesignerProvider` is a real,
complete implementation that has not been exercised against a live API in
this environment — see docs/bible/12-designer/321-designer-gap-analysis.md
for why, and the Sprint 10 validation report for what was and wasn't
verified live.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Protocol

from jewelmind.design_intent.schemas import DesignIntent
from jewelmind.designer.errors import (
    DesignerInvalidResponseError,
    DesignerProviderError,
    DesignerProviderTimeoutError,
    DesignerSchemaViolationError,
)
from jewelmind.designer.prompts import build_system_prompt, build_user_message
from jewelmind.designer.schemas import (
    InteractionMode,
    NaturalLanguageDesignRequest,
    RawDesignerResponse,
)
from jewelmind.domain.schema import JewelryDefinition

DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-5"

_TOOL_NAME = "submit_design_interpretation"

_TOOL_INPUT_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "proposedCanonicalValues": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "field": {"type": "string"},
                    "value": {"type": ["string", "number", "boolean"]},
                    "sourceText": {"type": "string"},
                },
                "required": ["field", "value"],
            },
        },
        "unresolvedDescriptors": {"type": "array", "items": {"type": "string"}},
        "designIntentStatements": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "target": {"type": "string"},
                    "concept": {"type": "string"},
                    "value": {"type": "string"},
                    "strength": {"type": ["string", "null"]},
                    "sourceText": {"type": "string"},
                },
                "required": ["target", "concept", "value"],
            },
        },
        "designIntentRelations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "subject": {"type": "string"},
                    "predicate": {"type": "string"},
                    "object": {"type": "string"},
                    "strength": {"type": ["string", "null"]},
                    "sourceText": {"type": "string"},
                },
                "required": ["subject", "predicate", "object"],
            },
        },
        "detectedUnsupportedFeatures": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "feature": {"type": "string"},
                    "sourceText": {"type": "string"},
                    "suggestedSupportedAlternative": {"type": ["string", "null"]},
                },
                "required": ["feature"],
            },
        },
        "ambiguities": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "field": {"type": "string"},
                    "sourceText": {"type": "string"},
                    "candidateValues": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["field"],
            },
        },
        "clarificationCandidates": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "field": {"type": ["string", "null"]},
                    "question": {"type": "string"},
                    "options": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["question"],
            },
        },
    },
    "required": [
        "proposedCanonicalValues",
        "unresolvedDescriptors",
        "designIntentStatements",
        "designIntentRelations",
        "detectedUnsupportedFeatures",
        "ambiguities",
        "clarificationCandidates",
    ],
}


@dataclass
class DesignerContext:
    currentJDL: JewelryDefinition
    interactionMode: InteractionMode
    currentDesignIntent: DesignIntent | None = None


class DesignerProvider(Protocol):
    """A source of raw design interpretation. Never called directly by routes.py."""

    name: str

    def interpret(
        self, request: NaturalLanguageDesignRequest, context: DesignerContext
    ) -> RawDesignerResponse: ...


@dataclass
class FakeDesignerProvider:
    """Deterministic, preconfigured provider for tests only.

    Never wired up by `get_designer_provider()` — a test constructs
    `DesignerService(provider=FakeDesignerProvider(...))` directly via
    dependency injection, so no automated test ever depends on a live,
    paid external AI call (DESIGNER-GOV, "FakeProvider is mandatory").
    """

    name: str = "fake"
    response: RawDesignerResponse | None = None
    responses_by_text: dict[str, RawDesignerResponse] = field(default_factory=dict)
    raise_error: Exception | None = None

    def interpret(
        self, request: NaturalLanguageDesignRequest, context: DesignerContext
    ) -> RawDesignerResponse:
        if self.raise_error is not None:
            raise self.raise_error
        if request.text in self.responses_by_text:
            return self.responses_by_text[request.text]
        if self.response is not None:
            return self.response
        return RawDesignerResponse()


class AnthropicDesignerProvider:
    """Real Claude-backed provider using tool-use structured output.

    Implemented in full against the documented Anthropic Messages API
    shape, but not exercised against a live endpoint in this development
    environment (no `ANTHROPIC_API_KEY` is configured here) — see
    docs/bible/12-designer/SPRINT-10-VALIDATION-REPORT.md.
    """

    name = "anthropic"

    def __init__(self, api_key: str, model: str | None = None) -> None:
        import anthropic  # imported lazily so the dependency is only required when selected

        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model or os.environ.get("DESIGNER_ANTHROPIC_MODEL", DEFAULT_ANTHROPIC_MODEL)

    def interpret(
        self, request: NaturalLanguageDesignRequest, context: DesignerContext
    ) -> RawDesignerResponse:
        import anthropic

        system_prompt = build_system_prompt(
            context.currentJDL, context.interactionMode, context.currentDesignIntent
        )
        user_message = build_user_message(request.text, request.locale)

        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=2048,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
                tools=[
                    {
                        "name": _TOOL_NAME,
                        "description": "Submit the structured design interpretation.",
                        "input_schema": _TOOL_INPUT_SCHEMA,
                    }
                ],
                tool_choice={"type": "tool", "name": _TOOL_NAME},
            )
        except anthropic.APITimeoutError as exc:
            raise DesignerProviderTimeoutError(f"Anthropic request timed out: {exc}") from exc
        except anthropic.APIError as exc:
            raise DesignerProviderError(f"Anthropic request failed: {exc}") from exc

        tool_uses = [block for block in response.content if getattr(block, "type", None) == "tool_use"]
        if not tool_uses:
            raise DesignerInvalidResponseError(
                "Anthropic response did not include a tool_use block."
            )

        try:
            return RawDesignerResponse.model_validate(tool_uses[0].input)
        except Exception as exc:  # noqa: BLE001 - any shape mismatch is a schema violation
            raise DesignerSchemaViolationError(
                f"Anthropic tool_use input did not match RawDesignerResponse: {exc}"
            ) from exc


def get_designer_provider() -> DesignerProvider | None:
    """Resolve the runtime provider from environment configuration.

    Returns None when no real provider is configured — callers must treat
    that as `DESIGNER_PROVIDER_UNAVAILABLE`, never as "fall back to the
    fake provider" (DESIGNER-GOV-015; see also the explicit instruction in
    Sprint 10's brief: "Do not fake successful live AI integration").
    `"fake"` is deliberately not a recognized value here — the fake
    provider is reached only via direct dependency injection in tests.
    """

    selector = os.environ.get("DESIGNER_PROVIDER", "").strip().lower()
    if selector == "anthropic":
        api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        if not api_key:
            return None
        return AnthropicDesignerProvider(api_key=api_key)
    return None
