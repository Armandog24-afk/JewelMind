"""Layered prompt construction for a real LLM provider.

See docs/bible/12-designer/306-prompt-architecture.md. Deliberately does
NOT embed the Technical Bible, any secret, or any credential — only the
current JDL schema shape, current capabilities, and the current design
state (when modifying).
"""

from __future__ import annotations

import json

from jewelmind.designer.capability import current_capabilities
from jewelmind.designer.schemas import InteractionMode
from jewelmind.domain.schema import JewelryDefinition

SYSTEM_CONTRACT = """You are JewelMind Designer, a natural-language interpretation layer for a \
parametric jewelry CAD system. You do not design jewelry and you do not decide what is \
manufacturable. Your only job is to extract, from the user's request, values for the fields \
listed in CURRENT JDL FIELDS below, using only the enum values listed in CURRENT CAPABILITIES.

Rules you must follow exactly:
- Never invent a field that is not listed in CURRENT JDL FIELDS.
- Never propose an enum value that is not listed in CURRENT CAPABILITIES for that field.
- If the user names a concept with no field/enum match (e.g. a stone shape, setting type, or \
category not listed), report it in detectedUnsupportedFeatures — never approximate it as a \
supported value.
- If a term names a category of value without picking one supported member of it (e.g. "gold" \
without a color), report it in ambiguities — never guess.
- Preserve non-technical descriptive language (e.g. "delicate", "bold", "elegant") in \
unresolvedDescriptors verbatim — never convert it into a numeric dimension.
- Never fabricate a professional manufacturing rule or claim manufacturability.
- Respond only via the structured output tool call. Do not include prose outside of it.
"""


def build_jdl_fields_block() -> str:
    return (
        "CURRENT JDL FIELDS (dotted paths you may reference in proposedCanonicalValues):\n"
        "project.name, ring.size, ring.innerDiameter, ring.sizeSystem, band.width, "
        "band.thickness, band.profile, stone.diameter, stone.depth, stone.shape, "
        "setting.prongCount, setting.prongDiameter, setting.prongHeight, setting.basketHeight, "
        "setting.type, material.metal, manufacturing.method, jewelry.category, jewelry.style"
    )


def build_capabilities_block() -> str:
    return "CURRENT CAPABILITIES (json):\n" + json.dumps(current_capabilities())


def build_current_design_block(current: JewelryDefinition, mode: InteractionMode) -> str:
    if mode == "CREATE":
        return (
            "INTERACTION MODE: CREATE — there is no existing design to modify. Only propose "
            "fields the user's text actually specifies or clearly implies; unspecified fields "
            "will keep JewelMind's own system defaults, which you do not need to restate."
        )
    return (
        "INTERACTION MODE: MODIFY — the user is changing an existing design, shown below as "
        "canonical JSON. Only propose fields the new request text actually changes; do not "
        "restate unchanged fields.\nCURRENT DESIGN (json):\n"
        + current.model_dump_json()
    )


def build_output_schema_block() -> str:
    return (
        "OUTPUT SCHEMA: call the `submit_design_interpretation` tool with an object matching "
        "RawDesignerResponse: proposedCanonicalValues (list of {field, value, sourceText}), "
        "unresolvedDescriptors (list of strings), detectedUnsupportedFeatures (list of "
        "{feature, sourceText, suggestedSupportedAlternative}), ambiguities (list of "
        "{field, sourceText, candidateValues}), clarificationCandidates (list of "
        "{field, question, options})."
    )


def build_system_prompt(current: JewelryDefinition, mode: InteractionMode) -> str:
    return "\n\n".join(
        [
            SYSTEM_CONTRACT,
            build_jdl_fields_block(),
            build_capabilities_block(),
            build_current_design_block(current, mode),
            build_output_schema_block(),
        ]
    )


def build_user_message(text: str, locale: str | None) -> str:
    locale_note = f" (locale hint: {locale})" if locale else ""
    return f"USER REQUEST{locale_note}:\n{text}"
