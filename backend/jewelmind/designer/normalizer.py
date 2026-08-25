"""Deterministic language normalization, diffing, and input screening.

None of this depends on an AI provider — it is plain, testable Python, run
against whatever a provider (real or fake) returns, or directly against
the request text for security screening. See
docs/bible/12-designer/297-supported-language-scope.md and
313-designer-security-model.md.
"""

from __future__ import annotations

from typing import Any

from jewelmind.designer.schemas import FieldDiff
from jewelmind.domain.schema import JewelryDefinition

# Only mappings for values that actually exist in the current schema are
# implemented here — see 298-defaulting-policy.md: Designer may normalize a
# spoken synonym to a real enum value, but must never invent a mapping for
# a concept the schema doesn't define (e.g. "delicate" -> a thickness).
METAL_SYNONYMS: dict[str, str] = {
    "yellow_gold_18k": "yellow_gold_18k",
    "yellow gold": "yellow_gold_18k",
    "yellow gold 18k": "yellow_gold_18k",
    "oro giallo": "yellow_gold_18k",
    "giallo": "yellow_gold_18k",
    "white_gold_18k": "white_gold_18k",
    "white gold": "white_gold_18k",
    "white gold 18k": "white_gold_18k",
    "oro bianco": "white_gold_18k",
    "bianco": "white_gold_18k",
    "rose_gold_18k": "rose_gold_18k",
    "rose gold": "rose_gold_18k",
    "rose gold 18k": "rose_gold_18k",
    "pink gold": "rose_gold_18k",
    "oro rosa": "rose_gold_18k",
    "rosa": "rose_gold_18k",
    "platinum": "platinum",
    "platino": "platinum",
    "silver": "silver",
    "argento": "silver",
}

# Present in the table with a None target: the word alone is a real,
# recognized metal reference but does not map to exactly one supported
# metal, so it must trigger clarification rather than a silent guess.
AMBIGUOUS_METAL_TERMS: frozenset[str] = frozenset({"gold", "oro"})

BAND_PROFILE_SYNONYMS: dict[str, str] = {
    "comfort_fit": "comfort_fit",
    "comfort fit": "comfort_fit",
    "comfort": "comfort_fit",
    "comfortevole": "comfort_fit",
    "confort": "comfort_fit",
    "fascia comfort fit": "comfort_fit",
    "flat": "flat",
    "piatta": "flat",
    "fascia piatta": "flat",
}

STONE_SHAPE_SYNONYMS: dict[str, str] = {
    "round": "round",
    "rotondo": "round",
    "rotonda": "round",
    "tondo": "round",
    "tonda": "round",
}

SETTING_TYPE_SYNONYMS: dict[str, str] = {
    "prong": "prong",
    "griffe": "prong",
    "a griffe": "prong",
}

MANUFACTURING_SYNONYMS: dict[str, str] = {
    "lost_wax_casting": "lost_wax_casting",
    "lost wax casting": "lost_wax_casting",
    "casting": "lost_wax_casting",
    "fusione a cera persa": "lost_wax_casting",
    "direct_resin_printing": "direct_resin_printing",
    "direct resin printing": "direct_resin_printing",
    "resin printing": "direct_resin_printing",
    "stampa in resina": "direct_resin_printing",
}

_ENUM_SYNONYM_TABLES: dict[str, dict[str, str]] = {
    "material.metal": METAL_SYNONYMS,
    "band.profile": BAND_PROFILE_SYNONYMS,
    "stone.shape": STONE_SHAPE_SYNONYMS,
    "setting.type": SETTING_TYPE_SYNONYMS,
    "manufacturing.method": MANUFACTURING_SYNONYMS,
}

# Prong count is numeric in the schema, but requests name it in words —
# only the two currently-supported counts are recognized (see
# capability.py::SUPPORTED_PRONG_COUNTS). A number outside this map is
# left to fail capability checking rather than being silently accepted.
PRONG_COUNT_WORDS: dict[str, int] = {
    "4": 4,
    "four": 4,
    "quattro": 4,
    "6": 6,
    "six": 6,
    "sei": 6,
}


def normalize_enum_token(field: str, raw_value: str) -> tuple[str | None, bool]:
    """Normalize a raw token for an enum field.

    Returns ``(canonical_value, is_ambiguous)``. `canonical_value` is
    `None` when the token doesn't map to anything known. `is_ambiguous` is
    True when the token is a recognized-but-incomplete reference (e.g.
    bare "gold") that must trigger clarification rather than a guess.
    """

    token = str(raw_value).strip().lower()

    if field == "material.metal" and token in AMBIGUOUS_METAL_TERMS:
        return None, True

    if field == "setting.prongCount":
        mapped = PRONG_COUNT_WORDS.get(token)
        return (str(mapped) if mapped is not None else None), False

    table = _ENUM_SYNONYM_TABLES.get(field)
    if table is None:
        return None, False
    return table.get(token), False


_NUMERIC_FIELDS: frozenset[str] = frozenset(
    {
        "ring.size",
        "ring.innerDiameter",
        "band.width",
        "band.thickness",
        "stone.diameter",
        "stone.depth",
        "setting.prongDiameter",
        "setting.prongHeight",
        "setting.basketHeight",
    }
)


def is_numeric_field(field: str) -> bool:
    return field in _NUMERIC_FIELDS


def flatten_definition(definition: JewelryDefinition) -> dict[str, Any]:
    """Dotted-path -> value for every leaf field in a JewelryDefinition."""

    out: dict[str, Any] = {}
    data = definition.model_dump(mode="json")
    for section, fields in data.items():
        if not isinstance(fields, dict):
            continue
        for name, value in fields.items():
            out[f"{section}.{name}"] = value
    return out


def compute_diff(
    before: JewelryDefinition | None, after: JewelryDefinition
) -> list[FieldDiff]:
    """Deterministic before/after diff for the MODIFY review UI.

    Never LLM-generated — see 311-proposal-diff-model.md. When `before` is
    None (a CREATE), every field is reported unchanged against itself so
    the review UI has a uniform shape to render either way.
    """

    before_flat = flatten_definition(before) if before is not None else {}
    after_flat = flatten_definition(after)
    diffs: list[FieldDiff] = []
    for path, proposed_value in after_flat.items():
        previous_value = before_flat.get(path)
        diffs.append(
            FieldDiff(
                path=path,
                previousValue=previous_value,
                proposedValue=proposed_value,
                changed=before is not None and previous_value != proposed_value,
            )
        )
    return diffs


# Phrases that indicate the request text is trying to act on the assistant
# rather than describe a jewelry design — treated as untrusted input per
# the same instruction-source-boundary discipline used everywhere else in
# this project. This is a coarse, explicit denylist, not a claim of
# complete prompt-injection immunity — see 314-prompt-injection-and-untrusted-input.md.
_INJECTION_MARKERS: tuple[str, ...] = (
    "ignore previous instructions",
    "ignore all previous instructions",
    "ignore the system prompt",
    "disregard your instructions",
    "you are now",
    "system prompt",
    "reveal your instructions",
    "print your instructions",
    "environment variable",
    "api key",
    "act as",
    "jailbreak",
)


def detect_prompt_injection_risk(text: str) -> str | None:
    """Returns a human-readable reason if `text` looks like an injection attempt, else None."""

    lowered = text.lower()
    for marker in _INJECTION_MARKERS:
        if marker in lowered:
            return f"Request text contains a suspicious instruction-override phrase: {marker!r}."
    return None
