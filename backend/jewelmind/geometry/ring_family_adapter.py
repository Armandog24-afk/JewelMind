"""Ring-side adapter: a ring family's derivations -> an EFFECTIVE definition.

Sprint 28. This module is the ONE place a family's derivations are applied, the
role `geometry/setting_adapter.py` plays for the Setting System and
`geometry/pave_surface.py` for a pavé host. It lives on the geometry side of
the boundary on purpose: the dependency arrow is

    assembly  ->  ring_family_adapter  ->  jewelmind.ring_family  ->  domain

and never the reverse. `jewelmind.ring_family` resolves and derives; it never
learns that a solid exists.

## Why an EFFECTIVE definition rather than mutating the document

The document the author wrote is the design's IDENTITY: `definitionHash` and
`geometryHash` are computed from it, every Golden baseline records it, and every
stored hash means it. A family's derivations are a pure function OF that
document, so the identity still determines the geometry completely — which is
exactly why the derived values must not become part of it.

So the assembly hashes the ORIGINAL and builds from the EFFECTIVE one. A reader
who wants to know what was actually built reads
`GeneratedModel.ring_family_result`, which carries every derivation with the
parameters it came from.

## What is derived, and what is refused

Only the paths the dependency table declares, and only where the document does
not declare them itself. A design that states its own `halo` keeps it and the
family reports that it derived none. The one hard refusal is a `three_stone`
family over an explicit arrangement: the derived stone family and the
arrangement would be two authorities over one set of placements, which
`JM-FAMILY-001` refuses — so the conflict is raised rather than resolved.
"""

from __future__ import annotations

from typing import Any

from jewelmind.domain.schema import JewelryDefinition
from jewelmind.ring_family.resolve import ResolvedRingFamily, resolve_ring_family


def _set_path(data: dict[str, Any], path: str, value: Any) -> bool:
    """Write a dotted path into a plain dict, materializing intermediates.

    Walks the whole path rather than splitting once, for the reason
    `designer/service.py::_apply_patch()` documents: a two-segment split would
    write a literal `"params.sideScale"` key that the schema rejects as an
    unknown field, turning a valid derivation into a silent failure.

    RETURNS WHETHER THE WRITE ACTUALLY CHANGED ANYTHING, which is what lets the
    caller preserve the original document object for a derivation that computes
    the value the document already has. The baseline variant is exactly that
    case: `setting.basketHeight x 1.0 x 1.0` is a real relation worth recording
    as provenance, and it changes nothing.
    """

    segments = path.split(".")
    cursor: Any = data
    for segment in segments[:-1]:
        existing = cursor.get(segment)
        if not isinstance(existing, dict):
            existing = {}
            cursor[segment] = existing
        cursor = existing
    key = segments[-1]
    if key in cursor and cursor[key] == value:
        return False
    cursor[key] = value
    return True


def effective_definition(
    definition: JewelryDefinition,
) -> tuple[JewelryDefinition, ResolvedRingFamily]:
    """The definition the geometry is actually built from, plus the resolution.

    Returns the ORIGINAL object unchanged when a family changes nothing, so a
    document with no ring family — and every pre-Sprint-28 document — reaches
    exactly the same geometry path it always did. Identity is unaffected either
    way: the caller hashes the original.

    NOTHING CHANGED is not the same as NOTHING DERIVED. The baseline variant
    derives `setting.basketHeight` from the document's own basket height times
    two factors of 1.0, which is a real provenance record and a no-op write. So
    the object is preserved by comparing each write's RESULT, not by counting
    derivations — otherwise every existing design would be re-validated and
    rebuilt from a reconstructed document for no reason.
    """

    resolved = resolve_ring_family(definition)
    if not resolved.derivations:
        return definition, resolved

    data = definition.model_dump(mode="python")
    changed = False
    for derivation in resolved.derivations:
        # `ringFamily.*` derivations are RESOLUTION OUTPUTS, not JDL fields:
        # `shoulderArchitecture` and `bodyArchitecture` are carried on the
        # resolved family and read by the assembly directly. Writing them into
        # the document would invent fields the schema does not have.
        if derivation.path.startswith("ringFamily."):
            continue
        if _set_path(data, derivation.path, derivation.value):
            changed = True

    if not changed:
        return definition, resolved

    return JewelryDefinition.model_validate(data), resolved


def ring_family_summary(resolved: ResolvedRingFamily) -> dict[str, Any]:
    """A kernel-neutral summary for an API response.

    Re-exported from the domain layer rather than rebuilt, so the API and a
    report cannot describe one resolution two ways.
    """

    from jewelmind.ring_family.resolve import resolution_summary

    return resolution_summary(resolved)
