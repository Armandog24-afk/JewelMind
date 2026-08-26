"""Pure scope-matching logic.

A validation scope must never be treated as broader than the evidence it
was actually reviewed under (PROVAL-GOV-015/016/017/018) — see
docs/bible/15-professional-validation/415-validation-scope-model.md. This
is the one real function that decides whether a candidate context (e.g.
"the design currently being reviewed in Studio") falls inside a recorded
scope: every field the scope actually constrains must match; a field the
scope leaves unset (`None`) never narrows the match.
"""

from __future__ import annotations

from jewelmind.professional_validation.schemas import ValidationScope

_SCOPE_FIELDS: tuple[str, ...] = tuple(ValidationScope.model_fields.keys())


def scope_matches(scope: ValidationScope, context: dict[str, str]) -> bool:
    """True if every field `scope` actually constrains equals the same
    field in `context`. A scope field left `None` never restricts the
    match — it simply means the record makes no claim either way about
    that dimension. `context` keys not mentioned by `scope` are ignored."""

    for field in _SCOPE_FIELDS:
        constraint = getattr(scope, field)
        if constraint is None:
            continue
        if context.get(field) != constraint:
            return False
    return True
