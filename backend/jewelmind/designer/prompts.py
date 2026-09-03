"""Layered prompt construction for a real LLM provider.

See docs/bible/12-designer/306-prompt-architecture.md. Deliberately does
NOT embed the Technical Bible, any secret, or any credential — only the
current JDL schema shape, current capabilities, and the current design
state (when modifying).
"""

from __future__ import annotations

import json

from jewelmind.design_intent.schemas import DesignIntent
from jewelmind.design_intent.vocabulary import CATEGORIES
from jewelmind.designer.capability import KNOWN_JDL_FIELD_PATHS, current_capabilities
from jewelmind.designer.schemas import InteractionMode
from jewelmind.domain.schema import JewelryDefinition

SYSTEM_CONTRACT = """You are JewelMind Designer, a natural-language interpretation layer for a \
parametric jewelry CAD system. You do not design jewelry and you do not decide what is \
manufacturable. Your job has two separate parts, which you must never mix:

PART 1 — TECHNICAL FIELDS: extract values for the fields listed in CURRENT JDL FIELDS below, \
using only the enum values listed in CURRENT CAPABILITIES.

PART 2 — AESTHETIC DESIGN INTENT: extract subjective/aesthetic descriptors (e.g. "delicate", \
"minimal", "classic", "bold") separately, using only the controlled concepts and values listed \
in DESIGN INTENT VOCABULARY below. These NEVER become a numeric dimension — you only classify \
which target (e.g. ring, band, stone) and which concept/value they describe.

Rules you must follow exactly:
- Never invent a field that is not listed in CURRENT JDL FIELDS.
- Never propose an enum value that is not listed in CURRENT CAPABILITIES for that field.
- Never convert an aesthetic descriptor into a numeric CURRENT JDL FIELDS value (e.g. never let \
"delicate" become a band.width number) — report it as a designIntentStatements entry instead.
- If the user names a concept with no field/enum match (e.g. a stone shape, setting type, or \
category not listed), report it in detectedUnsupportedFeatures — never approximate it as a \
supported value.
- If a term names a category of value without picking one supported member of it (e.g. "gold" \
without a color), report it in ambiguities — never guess.
- If an aesthetic word matches one of the DESIGN INTENT VOCABULARY concepts/values, report it in \
designIntentStatements with its target, concept, and value. If it does not clearly match any \
listed concept/value (e.g. "elegant", a genuinely ambiguous or unlisted word), leave it out of \
designIntentStatements and instead put the exact phrase in unresolvedDescriptors verbatim.
- A relative comparison between two components (e.g. "the band should look slim compared with \
the stone") goes in designIntentRelations, using only the controlled predicates listed below —
never as a numeric ratio.
- A gem MATERIAL and a stone CUT are different things. "emerald" and "pearl" name both a cut (stone.shape) and a gem (stone.gem.gemId) — report such a term in ambiguities rather than choosing one. Never infer a gem from geometry: a round stone is not automatically a diamond.
- Origin (natural/synthetic/simulant) and treatment are separate from the gem's identity: a synthetic ruby is still a ruby. Never report a treatment the user did not state, and never convert "treated" into a specific named treatment.
- Never fabricate a professional manufacturing rule or claim manufacturability.
- Never state a gemological, durability, hardness, or treatment-safety claim, and never recommend a setting on the basis of a gem's material.
- Respond only via the structured output tool call. Do not include prose outside of it.
"""


def build_jdl_fields_block() -> str:
    """The dotted paths a provider may reference.

    DERIVED from `capability.KNOWN_JDL_FIELD_PATHS`, not restated. This block
    used to be a hand-written list and had already drifted: it still named the
    seven Stone v1 cuts after Sprint 20 added fourteen more, and omitted the
    bezel fields Sprint 19 added — so the prompt was describing a smaller
    JewelMind than the one enforcing the proposals. The enum values themselves
    are in CURRENT CAPABILITIES, which is likewise generated from live code, so
    they are deliberately not repeated here.
    """

    paths = ", ".join(sorted(KNOWN_JDL_FIELD_PATHS))
    return (
        "CURRENT JDL FIELDS (dotted paths you may reference in proposedCanonicalValues):\n"
        + paths
        + "\nNotes: stone.diameter applies only to a round stone; stone.length and "
        "stone.width are required for every other shape. stone.gem.gemId is the gem "
        "MATERIAL and is independent of stone.shape, which is the CUT."
    )


def build_capabilities_block() -> str:
    return "CURRENT CAPABILITIES (json):\n" + json.dumps(current_capabilities())


def build_intent_vocabulary_block() -> str:
    vocabulary = {concept: list(category.order) for concept, category in CATEGORIES.items()}
    targets = (
        "JEWELRY_PRODUCT, RING, BAND, STONE, SETTING, PRONGS, BASKET, MATERIAL_APPEARANCE, "
        "OVERALL_PROPORTION, VISUAL_HIERARCHY"
    )
    predicates = (
        "NARROWER_THAN, BROADER_THAN, DOMINANT_OVER, SUBORDINATE_TO, DISCREET_RELATIVE_TO, "
        "BALANCED_WITH"
    )
    return (
        "DESIGN INTENT VOCABULARY:\nTargets: "
        + targets
        + "\nConcepts and ordered values (json): "
        + json.dumps(vocabulary)
        + "\nRelation predicates: "
        + predicates
    )


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


def build_current_intent_block(current_intent: DesignIntent | None, mode: InteractionMode) -> str:
    if mode == "CREATE" or current_intent is None:
        return "CURRENT DESIGN INTENT: none preserved yet."
    return (
        "CURRENT DESIGN INTENT (already preserved from earlier requests — only report new or "
        "changed statements; unmentioned ones are kept automatically):\n"
        + current_intent.model_dump_json()
    )


def build_output_schema_block() -> str:
    return (
        "OUTPUT SCHEMA: call the `submit_design_interpretation` tool with an object matching "
        "RawDesignerResponse: proposedCanonicalValues (list of {field, value, sourceText}), "
        "unresolvedDescriptors (list of strings), designIntentStatements (list of "
        "{target, concept, value, strength, sourceText}), designIntentRelations (list of "
        "{subject, predicate, object, strength, sourceText}), detectedUnsupportedFeatures (list "
        "of {feature, sourceText, suggestedSupportedAlternative}), ambiguities (list of "
        "{field, sourceText, candidateValues}), clarificationCandidates (list of "
        "{field, question, options})."
    )


def build_system_prompt(
    current: JewelryDefinition, mode: InteractionMode, current_intent: DesignIntent | None = None
) -> str:
    return "\n\n".join(
        [
            SYSTEM_CONTRACT,
            build_jdl_fields_block(),
            build_capabilities_block(),
            build_intent_vocabulary_block(),
            build_current_design_block(current, mode),
            build_current_intent_block(current_intent, mode),
            build_output_schema_block(),
        ]
    )


def build_user_message(text: str, locale: str | None) -> str:
    locale_note = f" (locale hint: {locale})" if locale else ""
    return f"USER REQUEST{locale_note}:\n{text}"
