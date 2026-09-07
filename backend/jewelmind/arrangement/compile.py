"""The arrangement -> compilation boundary (Sprint 22).

WHERE THE DECLARATIVE LAYER MEETS THE GEOMETRY PIPELINE, and nowhere else.
`resolve.py` turns an arrangement into explicit placements and has no opinion
about what can be built; this module answers the separate question "which of
these placements does the CURRENT pipeline actually emit as geometry?", and
records the answer per instance.

WHY THE TWO ARE SEPARATE FUNCTIONS. Resolution must stay a pure function of the
arrangement, so its output is stable across pipeline versions and can be stored,
compared and fingerprinted. Generation capability changes as JewelMind grows.
Fusing them would make a stored resolution depend on which release resolved it.

THE HONEST EXECUTION BOUNDARY, as it stands after Sprint 24. Every instance
resolving the primary stone specification now builds REAL geometry: the primary
one keeps the historical `stone_reference` component and each additional one
gets `stone_reference.<instanceId>`, placed by `geometry/stone/instance.py`.

What is still not built is a SETTING for a non-primary instance. No accent
setting strategy exists, and inventing one would mean inventing setter
geometry — so a multi-stone model reports that limitation in `notes` rather
than implying every stone is held. An instance whose `stoneRef` names a stone
specification other than `primary` still produces no geometry, because JDL
carries exactly one `stone`.

Nothing is silently dropped and no placeholder solid is invented. See
docs/bible/26-multi-stone-families/execution-boundary.md.

KERNEL-FREE, LIKE THE REST OF THE PACKAGE. This module decides names and
statuses. It never imports CadQuery, never builds a shape, and never calls a
geometry builder — Atlas does that, using the plan this module produces.
"""

from __future__ import annotations

from jewelmind.arrangement.capability import ARRANGEMENT_CAPABILITIES
from jewelmind.arrangement.models import (
    ArrangementDefinition,
    ResolvedArrangement,
    ResolvedInstance,
)
from jewelmind.arrangement.resolve import resolve_arrangement

#: The component name a generated primary stone takes.
#:
#: UNCHANGED from every previous sprint, and that is the point: a single-stone
#: design must keep producing a component called exactly `stone_reference`, or
#: every Golden baseline, preview manifest, exporter, inspection check and
#: frontend consumer would need to change at once.
PRIMARY_STONE_COMPONENT = "stone_reference"

#: How an additional instance's component would be named once multi-stone
#: emission exists. Defined HERE rather than at the point of emission so the
#: naming contract is fixed and testable before any geometry depends on it, and
#: so `geometry/roles.py` can classify such a name correctly the moment one
#: appears.
STONE_INSTANCE_COMPONENT_PREFIX = f"{PRIMARY_STONE_COMPONENT}."


def stone_component_name(instance_id: str, *, is_primary: bool) -> str:
    """The geometry component name for a resolved instance.

    The primary instance keeps the bare, historical name. Any other instance
    gets `stone_reference.<instanceId>`, which is:

    - traceable — the component names the instance it came from, so identity is
      never positional (INSPECT-GOV-015);
    - classifiable — `geometry/roles.py` recognizes the prefix, so an additional
      stone is a stone_reference and stays excluded from production exports by
      default (LAW-006), rather than falling through to the
      `production_metal` default and being fused into metal;
    - stable — derived from the authoritative ID, so it does not change when the
      instance list is reordered.
    """

    if is_primary:
        return PRIMARY_STONE_COMPONENT
    return f"{STONE_INSTANCE_COMPONENT_PREFIX}{instance_id}"


def _primary_instance(resolved: ResolvedArrangement) -> ResolvedInstance | None:
    """The one instance the current pipeline can build.

    Selection is deterministic and does NOT use list position: the first
    `CENTER`-role instance by sorted ID, or the first instance by sorted ID when
    no instance claims that role. Choosing `instances[0]` would make the built
    geometry depend on serialization order, which is exactly the dependency this
    layer exists to remove.
    """

    if not resolved.instances:
        return None
    centers = [i for i in resolved.instances if i.role == "CENTER"]
    pool = centers or list(resolved.instances)
    return min(pool, key=lambda i: i.instanceId)


def compile_arrangement(
    definition: ArrangementDefinition | None,
) -> ResolvedArrangement | None:
    """Resolve an arrangement and mark what the current pipeline generates.

    Returns `None` for `None`, which is the whole backward-compatibility story
    in one line: a design with no arrangement compiles to no arrangement and
    behaves exactly as it did before this sprint. It does NOT synthesize a
    one-instance arrangement for a single-stone design, because that would
    invent a declaration the document never made.
    """

    if definition is None:
        return None

    resolved = resolve_arrangement(definition)
    primary = _primary_instance(resolved)

    instances: list[ResolvedInstance] = []
    generated = 0
    notes: list[str] = []

    for instance in resolved.instances:
        is_primary = primary is not None and instance.instanceId == primary.instanceId

        # EVERY instance resolving the primary stone specification now builds
        # real geometry (Sprint 24). Sprint 22 generated only the primary one
        # because the stone builder placed a stone on the design axis and took
        # no offset; `geometry/stone/instance.py` now applies each resolved
        # instance's own transform, scale and orientation, so an additional
        # stone is genuinely placeable.
        #
        # The primary instance keeps the bare historical component name and
        # every other gets `stone_reference.<instanceId>` — unchanged from the
        # naming contract Sprint 22 fixed before any such geometry existed.
        if instance.stoneRef == "primary":
            instances.append(
                instance.model_copy(
                    update={
                        "generationStatus": "GENERATED",
                        "generationNote": None,
                        "componentName": stone_component_name(
                            instance.instanceId, is_primary=is_primary
                        ),
                    }
                )
            )
            generated += 1
            continue

        # An unresolved stone reference is reported here rather than raised:
        # the arrangement is structurally fine, and Forge's JM-ARRANGE rules
        # are where an unresolvable reference becomes a validation finding.
        note = (
            f"Instance {instance.instanceId!r} references stone "
            f"{instance.stoneRef!r}; only 'primary' resolves today, so no "
            "geometry was built for it."
        )

        instances.append(
            instance.model_copy(
                update={
                    "generationStatus": "NOT_GENERATED",
                    "generationNote": note,
                    "componentName": None,
                }
            )
        )
        notes.append(note)

    # THE REMAINING BOUNDARY, reported per model rather than left implicit.
    # Stone geometry is built for every resolved instance; a SETTING is built
    # only for the primary one, because no setting strategy for accent stones
    # exists. Saying so here means a caller sees the limitation on the same
    # object that reports the successes.
    if generated > 1:
        notes.append(
            f"{generated} stone instances were generated. A setting is built "
            "only for the primary instance: no accent-setting strategy exists "
            "yet. See docs/bible/26-multi-stone-families/execution-boundary.md."
        )

    return resolved.model_copy(
        update={
            "instances": instances,
            "generatedCount": generated,
            "notes": notes,
        }
    )


def multi_stone_generation_status() -> str:
    """The capability status the rest of the system should report.

    Read from `capability.py` rather than restated, so a future sprint that
    implements emission flips this everywhere by changing one registry entry.
    """

    return ARRANGEMENT_CAPABILITIES["multi_stone_geometry"].status
