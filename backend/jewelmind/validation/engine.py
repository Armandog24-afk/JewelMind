"""Deterministic validation engine for a JewelryDefinition.

This is the authoritative validator: the frontend may mirror a subset of
these rules for instant feedback, but the backend re-validates before any
geometry generation or export and rejects on errors regardless of what the
client believes.
"""

from __future__ import annotations

import math

from jewelmind.domain.schema import JewelryDefinition
from jewelmind.domain.stone_dimensions import (
    resolved_depth_mm,
    resolved_length_mm,
    resolved_width_mm,
)
from jewelmind.validation import rules as R
from jewelmind.validation.sizing import eu_size_to_inner_diameter, sizing_consistency


def _ring_rules(d: JewelryDefinition) -> list[R.ValidationResult]:
    out: list[R.ValidationResult] = []

    if not (10 < d.ring.innerDiameter < 30):
        out.append(
            R.ValidationResult(
                ruleId=R.RING_INNER_DIAMETER_RANGE,
                severity="error",
                message="Ring inner diameter must be greater than 10 mm and lower than 30 mm.",
                parameter="ring.innerDiameter",
            )
        )

    if not (1 < d.ring.size < 50):
        out.append(
            R.ValidationResult(
                ruleId=R.RING_SIZE_RANGE,
                severity="error",
                message="EU ring size must be greater than 1 and lower than 50.",
                parameter="ring.size",
            )
        )

    consistency = sizing_consistency(d.ring.size, d.ring.innerDiameter)
    if consistency is not None:
        implied = eu_size_to_inner_diameter(d.ring.size)
        out.append(
            R.ValidationResult(
                ruleId=R.RING_SIZE_DIAMETER_CONSISTENCY,
                severity=consistency,
                message=(
                    f"EU size {d.ring.size:g} implies an inner diameter of "
                    f"{implied:.2f} mm, which differs from the stored "
                    f"{d.ring.innerDiameter:g} mm. Sizing conventions vary; "
                    "review which value should take precedence."
                ),
                parameter="ring.innerDiameter",
                suggestedValue=round(implied, 2),
            )
        )

    return out


def _band_rules(d: JewelryDefinition) -> list[R.ValidationResult]:
    out: list[R.ValidationResult] = []

    if d.band.width < 1.5:
        out.append(
            R.ValidationResult(
                ruleId=R.BAND_WIDTH_MIN,
                severity="error",
                message="Band width below 1.5 mm is not supported.",
                parameter="band.width",
                suggestedValue=1.5,
            )
        )
    elif d.band.width > 12:
        out.append(
            R.ValidationResult(
                ruleId=R.BAND_WIDTH_MAX,
                severity="warning",
                message="Band width above 12 mm is unusually wide for a solitaire band.",
                parameter="band.width",
            )
        )

    if d.band.thickness < 1.4:
        out.append(
            R.ValidationResult(
                ruleId=R.BAND_THICKNESS_MIN,
                severity="error",
                message="Band thickness below 1.4 mm is not supported.",
                parameter="band.thickness",
                suggestedValue=1.4,
            )
        )
    elif d.band.thickness < 1.6:
        out.append(
            R.ValidationResult(
                ruleId=R.BAND_THICKNESS_MIN,
                severity="warning",
                message="Band thickness below 1.6 mm may be structurally fragile.",
                parameter="band.thickness",
                suggestedValue=1.6,
            )
        )

    return out


def _gem_rules(d: JewelryDefinition) -> list[R.ValidationResult]:
    """Gem identity validation (Sprint 21, brief section 26).

    SCOPE: GEM_IDENTITY_ONLY. Every rule here checks a REFERENCE or a
    COHERENCE — does the entry exist, is the declared state self-consistent,
    does the profile resolve. None of them makes a gemological or manufacturing
    claim, and none may be added that does: hardness, durability, heat
    sensitivity, setting suitability and treatment safety all require
    professional evidence this project does not have (GEM-GOV-006).

    A stone with no gem at all produces NO results. That is not an oversight —
    a legacy document is valid, and normalizes to `unknown` rather than being
    reported as broken (brief sections 17/18).
    """

    from jewelmind.gem.models import CUSTOM_GEM_ID
    from jewelmind.gem.registry import GEM_REGISTRY
    from jewelmind.gem.visual import profile_exists

    gem = d.stone.gem
    if gem is None:
        return []

    out: list[R.ValidationResult] = []
    entry = GEM_REGISTRY.get(gem.gemId)

    if entry is None:
        # A WARNING, not an error. A design referencing a removed entry must
        # still load and still generate (brief sections 10/29); refusing it
        # would make a registry change break saved projects.
        out.append(
            R.ValidationResult(
                ruleId=R.GEM_REFERENCE_EXISTS,
                severity="warning",
                message=(
                    f"Gem '{gem.gemId}' is not in the gem registry. The design "
                    "remains usable and the stone is treated as an unspecified "
                    "gem; no substitute has been chosen for you."
                ),
                parameter="stone.gem.gemId",
            )
        )
        return out

    if entry.status == "DEPRECATED":
        superseded = (
            f" It is superseded by '{entry.supersededBy}'."
            if entry.supersededBy
            else ""
        )
        out.append(
            R.ValidationResult(
                ruleId=R.GEM_ENTRY_DEPRECATED,
                severity="warning",
                message=(
                    f"Gem '{gem.gemId}' is deprecated but still resolvable."
                    f"{superseded}"
                ),
                parameter="stone.gem.gemId",
            )
        )

    if gem.origin != "UNKNOWN" and gem.origin not in entry.applicableOrigins:
        out.append(
            R.ValidationResult(
                ruleId=R.GEM_ORIGIN_APPLICABLE,
                severity="error",
                message=(
                    f"Origin '{gem.origin}' is not applicable to "
                    f"{entry.canonicalName}. Applicable: "
                    f"{', '.join(entry.applicableOrigins)}."
                ),
                parameter="stone.gem.origin",
            )
        )

    # Structurally enforced by `JdlGemIdentity` too. Kept as a Forge rule so the
    # requirement is visible in a validation report rather than only as a schema
    # rejection, and so a programmatically-built identity is covered as well.
    if gem.gemId == CUSTOM_GEM_ID and not (gem.customName or "").strip():
        out.append(
            R.ValidationResult(
                ruleId=R.GEM_CUSTOM_COHERENT,
                severity="error",
                message="A custom gem requires a name describing the material.",
                parameter="stone.gem.customName",
            )
        )
    elif gem.gemId != CUSTOM_GEM_ID and gem.customName is not None:
        out.append(
            R.ValidationResult(
                ruleId=R.GEM_CUSTOM_COHERENT,
                severity="error",
                message=(
                    f"A custom name is only meaningful for a custom gem; "
                    f"'{gem.gemId}' already has a canonical name."
                ),
                parameter="stone.gem.customName",
            )
        )

    profile_id = gem.visualProfileId or entry.defaultVisualProfileId
    if not profile_exists(profile_id):
        out.append(
            R.ValidationResult(
                ruleId=R.GEM_VISUAL_PROFILE_RESOLVES,
                severity="warning",
                message=(
                    f"Visual profile '{profile_id}' does not exist; a generic "
                    "fallback appearance will be used. This affects how the "
                    "stone is drawn, never what it is."
                ),
                parameter="stone.gem.visualProfileId",
            )
        )

    seen: set[str] = set()
    for treatment in gem.treatments:
        if treatment.treatment in seen:
            out.append(
                R.ValidationResult(
                    ruleId=R.GEM_TREATMENT_COHERENT,
                    severity="warning",
                    message=(
                        f"Treatment '{treatment.treatment}' is recorded more "
                        "than once. Duplicate records cannot be reconciled "
                        "automatically, so both are preserved."
                    ),
                    parameter="stone.gem.treatments",
                )
            )
        seen.add(treatment.treatment)

    # Asserting both "treated" and "explicitly not treated" is a contradiction
    # a reader cannot resolve, so it is reported rather than silently kept.
    present = {t.treatment for t in gem.treatments if t.status == "PRESENT"}
    absent = {t.treatment for t in gem.treatments if t.status == "NOT_PRESENT"}
    for conflict in sorted(present & absent):
        out.append(
            R.ValidationResult(
                ruleId=R.GEM_TREATMENT_COHERENT,
                severity="error",
                message=(
                    f"Treatment '{conflict}' is recorded as both present and "
                    "not present."
                ),
                parameter="stone.gem.treatments",
            )
        )

    return out


def _arrangement_rules(d: JewelryDefinition) -> list[R.ValidationResult]:
    """Stone Arrangement structural validation (Sprint 22).

    SCOPE: ARRANGEMENT_ONLY, and STRUCTURAL ONLY. Every finding here is about
    whether the declared arrangement is internally consistent and resolvable —
    unique IDs, references that exist, a structure the resolver can evaluate.
    None of them is a jewelry judgment.

    THREE KINDS OF VALIDATION, KEPT APART DELIBERATELY:

    - structural/software (here): does the document resolve at all?
    - geometric (Geometry Inspection): do the resulting solids intersect,
      connect, hold together? Unanswerable until multi-stone geometry exists.
    - professional/manufacturing (unavailable): is this spacing settable, is
      this accent size sensible? Needs sourced expert evidence this project
      does not have, so no such rule exists.

    A design with no arrangement produces NO results — a single-stone document
    is not a broken arrangement, and reporting one would make every
    pre-Sprint-22 project suddenly noisy.
    """

    arrangement = d.arrangement
    if arrangement is None:
        return []

    from jewelmind.arrangement.errors import ArrangementError
    from jewelmind.arrangement.resolve import resolve_arrangement

    out: list[R.ValidationResult] = []

    # Duplicate IDs are checked here rather than only inside the resolver so a
    # caller gets a rule-identified finding instead of only an exception, and
    # so several duplicates are all reported rather than just the first.
    seen: set[str] = set()
    for instance in arrangement.instances:
        if instance.instanceId in seen:
            out.append(
                R.ValidationResult(
                    ruleId=R.ARRANGEMENT_INSTANCE_IDS_UNIQUE,
                    severity="error",
                    message=(
                        f"Stone instance id '{instance.instanceId}' is declared more "
                        "than once. Instance ids are the authoritative identity, so a "
                        "duplicate makes every reference to it ambiguous."
                    ),
                    parameter="arrangement.instances",
                )
            )
        seen.add(instance.instanceId)

    group_ids = {group.groupId for group in arrangement.groups}
    for instance in arrangement.instances:
        group_id = instance.placement.groupId
        if group_id is not None and group_id not in group_ids:
            out.append(
                R.ValidationResult(
                    ruleId=R.ARRANGEMENT_REFERENCES_RESOLVE,
                    severity="error",
                    message=(
                        f"Stone instance '{instance.instanceId}' belongs to group "
                        f"'{group_id}', which is not declared in this arrangement."
                    ),
                    parameter="arrangement.instances",
                )
            )

    for pattern in arrangement.patterns:
        if pattern.sourceInstanceId not in seen:
            out.append(
                R.ValidationResult(
                    ruleId=R.ARRANGEMENT_REFERENCES_RESOLVE,
                    severity="error",
                    message=(
                        f"Pattern '{pattern.patternId}' repeats stone instance "
                        f"'{pattern.sourceInstanceId}', which is not declared in this "
                        "arrangement."
                    ),
                    parameter="arrangement.patterns",
                )
            )
        if pattern.groupId is not None and pattern.groupId not in group_ids:
            out.append(
                R.ValidationResult(
                    ruleId=R.ARRANGEMENT_REFERENCES_RESOLVE,
                    severity="error",
                    message=(
                        f"Pattern '{pattern.patternId}' places its members in group "
                        f"'{pattern.groupId}', which is not declared."
                    ),
                    parameter="arrangement.patterns",
                )
            )

    # A stone reference other than 'primary' names a stone specification that
    # does not exist yet: JDL carries exactly one `stone`. A WARNING, not an
    # error, and the distinction matters — the document is structurally valid
    # and still generates, it simply produces no geometry for that instance.
    for instance in arrangement.instances:
        if instance.stoneRef != "primary":
            out.append(
                R.ValidationResult(
                    ruleId=R.ARRANGEMENT_STONE_REFERENCE_RESOLVES,
                    severity="warning",
                    message=(
                        f"Stone instance '{instance.instanceId}' references stone "
                        f"'{instance.stoneRef}', but this definition declares only the "
                        "primary stone. No geometry will be built for that instance."
                    ),
                    parameter="arrangement.instances",
                )
            )

    # More than one CENTER is not wrong, but it IS ambiguous about which stone
    # the current single-stone pipeline will build, so it is reported rather
    # than resolved silently.
    centers = [i.instanceId for i in arrangement.instances if i.role == "CENTER"]
    if len(centers) > 1:
        out.append(
            R.ValidationResult(
                ruleId=R.ARRANGEMENT_ROLE_COHERENT,
                severity="warning",
                message=(
                    f"{len(centers)} stone instances claim the CENTER role "
                    f"({', '.join(sorted(centers))}). The lowest id is treated as the "
                    "primary stone; give the others a different role to make the "
                    "intent explicit."
                ),
                parameter="arrangement.instances",
            )
        )

    # The authoritative structural check: does the real resolver evaluate this
    # arrangement? Running it here means Forge can never disagree with what
    # generation will do, because it is the same code path.
    try:
        resolved = resolve_arrangement(arrangement)
    except ArrangementError as exc:
        out.append(
            R.ValidationResult(
                ruleId=R.ARRANGEMENT_STRUCTURE_RESOLVES,
                severity="error",
                message=f"The arrangement cannot be resolved: {exc}",
                parameter="arrangement",
            )
        )
        return out

    # The execution boundary, surfaced as an INFORMATION result rather than
    # hidden in a log. A caller must be able to see that a resolved instance
    # produced no solid, and must not be told the design is faulty for it.
    if resolved.instanceCount > 1:
        out.append(
            R.ValidationResult(
                ruleId=R.ARRANGEMENT_GENERATION_PARTIAL,
                severity="information",
                message=(
                    f"This arrangement resolves {resolved.instanceCount} stone "
                    "instances. Multi-stone geometry generation is not yet "
                    "implemented, so one stone is built and the remaining instances "
                    "are reported as placements only."
                ),
                parameter="arrangement.instances",
            )
        )

    return out


def _setting_v2_rules(d: JewelryDefinition) -> list[R.ValidationResult]:
    """Advanced head and prong validation (Sprint 23).

    SCOPE: SETTING_V2, and STRUCTURAL ONLY. Each finding answers one of three
    questions: does the requested architecture have the parameters it needs, is
    a requested field meaningful for the family chosen, and can the requested
    operation actually run against this stone.

    None of them is a professional judgment. There is no rule here about
    whether a prong is thick enough for a 6.5 mm stone, whether a martini wall
    is castable, or whether a seat would hold — every one of those needs
    sourced professional evidence this project does not have, so none exists
    (SETTING-GOV-010).

    A design left on the defaults produces NO results: `ROUND_PRONG`,
    `BASKET` and `seatMode="NONE"` are exactly what every pre-Sprint-23
    document has, and reporting anything for them would make the whole existing
    corpus noisy.
    """

    setting = d.setting
    out: list[R.ValidationResult] = []

    # A PEG_HEAD without peg dimensions cannot be built, and the generator
    # refuses rather than inventing them — so the refusal is surfaced here as a
    # rule result instead of only as a generation-time exception.
    if setting.headArchitecture == "PEG_HEAD":
        missing = [
            name
            for name, value in (
                ("pegDiameter", setting.pegDiameter),
                ("pegHeight", setting.pegHeight),
            )
            if value is None
        ]
        if missing:
            out.append(
                R.ValidationResult(
                    ruleId=R.SETTING_HEAD_PARAMETERS_COMPLETE,
                    severity="error",
                    message=(
                        "A PEG_HEAD requires "
                        + " and ".join(f"setting.{name}" for name in missing)
                        + ". No default is applied, because an invented peg size "
                        "would be a construction choice you did not make."
                    ),
                    parameter=f"setting.{missing[0]}",
                )
            )
        else:
            for name, value in (
                ("pegDiameter", setting.pegDiameter),
                ("pegHeight", setting.pegHeight),
            ):
                if value is not None and value <= 0:
                    out.append(
                        R.ValidationResult(
                            ruleId=R.SETTING_HEAD_PARAMETERS_COMPLETE,
                            severity="error",
                            message=f"setting.{name} must be greater than 0 mm.",
                            parameter=f"setting.{name}",
                        )
                    )
            if (
                setting.pegHeight is not None
                and setting.pegHeight >= setting.basketHeight
            ):
                out.append(
                    R.ValidationResult(
                        ruleId=R.SETTING_HEAD_PARAMETERS_COMPLETE,
                        severity="error",
                        message=(
                            f"setting.pegHeight ({setting.pegHeight} mm) must be "
                            f"less than setting.basketHeight "
                            f"({setting.basketHeight} mm); otherwise no head wall "
                            "remains above the peg."
                        ),
                        parameter="setting.pegHeight",
                    )
                )

    # An unread field is reported rather than silently ignored. INFORMATION,
    # not a warning: the document is perfectly valid, the value simply has no
    # effect, and a user who set it deserves to know which.
    if setting.type != "prong" and setting.prongStyle != "ROUND_PRONG":
        out.append(
            R.ValidationResult(
                ruleId=R.SETTING_FIELD_APPLICABLE,
                severity="information",
                message=(
                    f"setting.prongStyle '{setting.prongStyle}' is not read by a "
                    f"'{setting.type}' setting and has no effect on the generated "
                    "geometry."
                ),
                parameter="setting.prongStyle",
            )
        )
    if setting.headArchitecture != "PEG_HEAD" and (
        setting.pegDiameter is not None or setting.pegHeight is not None
    ):
        out.append(
            R.ValidationResult(
                ruleId=R.SETTING_FIELD_APPLICABLE,
                severity="information",
                message=(
                    f"setting.pegDiameter/pegHeight are read only by a PEG_HEAD; "
                    f"this design uses '{setting.headArchitecture}', so they have "
                    "no effect."
                ),
                parameter="setting.pegDiameter",
            )
        )

    # Seat relief is a boolean CUT against the real generated stone solid. An
    # imported asset may be a mesh, which has no solid to cut with — a real
    # feasibility question, and a WARNING rather than an error because whether
    # a given asset parses to a B-Rep is only knowable after import.
    if setting.seatMode != "NONE" and d.stone.source == "IMPORTED_CAD":
        out.append(
            R.ValidationResult(
                ruleId=R.SETTING_SEAT_FEASIBLE,
                severity="warning",
                message=(
                    f"Seat relief '{setting.seatMode}' cuts the stone volume out "
                    "of the metal, which requires the stone to parse as a solid. "
                    "An imported asset may be a mesh, in which case no relief can "
                    "be cut and generation will report the failure rather than "
                    "silently skipping it."
                ),
                parameter="setting.seatMode",
            )
        )

    return out


def _family_rules(d: JewelryDefinition) -> list[R.ValidationResult]:
    """Multi-stone family validation (Sprint 24).

    SCOPE: FAMILY_ONLY, and STRUCTURAL ONLY. Four questions: does the document
    name one placement authority or two, do the members' roles match the
    family's own rules, does the family actually compile, and do its references
    resolve. Plus one honest report of what a compiled family does NOT get.

    None of them is a jewelry judgment. There is no rule here about how large
    an accent should be relative to a centre, how far apart two stones must
    sit, or whether a twelve-stone cluster could be set — each needs sourced
    professional evidence this project does not have, so none exists. Whether
    two placed stones physically overlap is a GEOMETRIC question for Geometry
    Inspection.

    A design with no family produces NO results, so the entire existing corpus
    stays quiet.
    """

    family = d.family
    if family is None:
        return []

    from jewelmind.family.compile import FAMILY_ROLE_RULES, compile_family
    from jewelmind.family.errors import FamilyError

    out: list[R.ValidationResult] = []

    # TWO AUTHORITIES OVER ONE SET OF PLACEMENTS. A family compiles into an
    # arrangement, so a document carrying both has no determinate resolution.
    # Refused rather than merged, and reported before generation is attempted.
    if d.arrangement is not None:
        out.append(
            R.ValidationResult(
                ruleId=R.FAMILY_SINGLE_PLACEMENT_AUTHORITY,
                severity="error",
                message=(
                    "This design declares both a family and an explicit "
                    "arrangement. A family compiles into an arrangement, so only "
                    "one may be present: remove the arrangement to keep the "
                    "family's semantics, or remove the family for full manual "
                    "control."
                ),
                parameter="family",
            )
        )
        # Compilation cannot proceed meaningfully while the conflict stands, and
        # reporting a second, derived failure would obscure the real one.
        return out

    rules = FAMILY_ROLE_RULES.get(family.familyType, {})
    grouped: dict[str, int] = {}
    for member in family.members:
        grouped[member.role] = grouped.get(member.role, 0) + 1

    for role, count in sorted(grouped.items()):
        if role not in rules:
            out.append(
                R.ValidationResult(
                    ruleId=R.FAMILY_ROLES_VALID,
                    severity="error",
                    message=(
                        f"Role '{role}' is not part of a {family.familyType} "
                        f"family. Accepted roles: {', '.join(sorted(rules))}."
                    ),
                    parameter="family.members",
                )
            )
            continue
        expected = rules[role]
        if expected is not None and count != expected and family.members:
            out.append(
                R.ValidationResult(
                    ruleId=R.FAMILY_ROLES_VALID,
                    severity="error",
                    message=(
                        f"A {family.familyType} family requires exactly "
                        f"{expected} member(s) with role '{role}', found {count}."
                    ),
                    parameter="family.members",
                )
            )

    # A member naming a stone specification other than 'primary' is reported as
    # a WARNING: the document is structurally valid and still generates, and
    # only that member produces no geometry.
    for member in family.members:
        if member.stoneRef != "primary":
            out.append(
                R.ValidationResult(
                    ruleId=R.FAMILY_REFERENCES_RESOLVE,
                    severity="warning",
                    message=(
                        f"Family member '{member.memberId}' references stone "
                        f"'{member.stoneRef}', but this definition declares only "
                        "the primary stone. No geometry will be built for that "
                        "member."
                    ),
                    parameter="family.members",
                )
            )
        if member.settingRef is not None and member.settingRef != d.setting.type:
            out.append(
                R.ValidationResult(
                    ruleId=R.FAMILY_REFERENCES_RESOLVE,
                    severity="warning",
                    message=(
                        f"Family member '{member.memberId}' requests setting "
                        f"'{member.settingRef}', but this design's setting is "
                        f"'{d.setting.type}'. Per-member settings are not "
                        "generated: only the primary stone receives one."
                    ),
                    parameter="family.members",
                )
            )

    # THE AUTHORITATIVE STRUCTURAL CHECK: does the real compiler accept this
    # family? Running it here means Forge can never disagree with what
    # generation will do, because it is the same code path.
    try:
        arrangement = compile_family(family)
    except FamilyError as exc:
        out.append(
            R.ValidationResult(
                ruleId=R.FAMILY_COMPILES,
                severity="error",
                message=f"This family cannot be compiled: {exc}",
                parameter="family",
            )
        )
        return out

    # The remaining limitation, surfaced as INFORMATION rather than hidden in a
    # log. The design is not faulty; a setting is simply built for one stone.
    if arrangement is not None and len(arrangement.instances) + sum(
        p.spec.count - 1 if p.spec.kind == "RADIAL" else 1 for p in arrangement.patterns
    ) > 1:
        out.append(
            R.ValidationResult(
                ruleId=R.FAMILY_SETTING_COVERAGE,
                severity="information",
                message=(
                    f"This {family.familyType} family builds stone geometry for "
                    "every member, but a setting is generated only for the "
                    "primary stone: no accent-setting strategy exists yet."
                ),
                parameter="family",
            )
        )

    return out


def _halo_rules(d: JewelryDefinition) -> list[R.ValidationResult]:
    """Halo validation (Sprint 25).

    SCOPE: HALO_ONLY, and STRUCTURAL ONLY. Five questions: does the centre the
    halo names actually exist in this design's placement, does the halo compose,
    is this family/halo combination one the real compiler supports, do the
    halo's stone and setting references resolve, and what does a composed halo
    NOT get.

    None of them is a jewelry judgment. There is no rule here about how far a
    halo stone must sit from its neighbour, what fraction of the centre a halo
    stone should be, or whether a hidden halo clears the centre's pavilion —
    each needs sourced professional evidence this project does not have, so none
    exists. Whether two placed stones physically overlap is a GEOMETRIC question
    for Geometry Inspection.

    A design with no halo produces NO results, so the entire existing corpus
    stays quiet.
    """

    halo = d.halo
    if halo is None:
        return []

    from jewelmind.family.compile import compile_family
    from jewelmind.family.errors import FamilyError
    from jewelmind.halo.capability import HALO_COMPOSITION
    from jewelmind.halo.compile import compose_halo
    from jewelmind.halo.errors import HaloCenterUnresolvedError, HaloError

    out: list[R.ValidationResult] = []

    # A halo composes onto whatever placement the design declares, so the base
    # must exist before the halo can be judged. A family/arrangement conflict is
    # JM-FAMILY-001's finding; reporting a second, derived failure here would
    # obscure the real one.
    if d.family is not None and d.arrangement is not None:
        return out

    try:
        base = compile_family(d.family) if d.family is not None else d.arrangement
    except FamilyError:
        # The family itself does not compile. JM-FAMILY-003 reports that; the
        # halo's own validity cannot be assessed against a base that does not
        # exist, and inventing a verdict for it would be guesswork.
        return out

    # THE SUPPORT TABLE IS REPORTING, NOT THE GATE. The authoritative check is
    # the real compiler below. This branch exists so an unsupported combination
    # is EXPLAINED rather than merely refused.
    if d.family is not None and halo.centerMemberId is not None:
        composition = HALO_COMPOSITION.get(d.family.familyType)
        if composition is not None and not composition["namedCenter"]:
            out.append(
                R.ValidationResult(
                    ruleId=R.HALO_COMPOSITION_SUPPORTED,
                    severity="error",
                    message=(
                        f"A halo cannot name a centre in a "
                        f"{d.family.familyType} family. {composition['note']}"
                    ),
                    parameter="halo.centerMemberId",
                )
            )
            # The authoritative check below would refuse this too, as an
            # unresolvable centre. Returning here keeps ONE error for one cause:
            # the explanatory message is strictly more useful than "no such
            # instance", and two findings for a single mistake reads as two
            # mistakes.
            return out

    # THE AUTHORITATIVE STRUCTURAL CHECK: does the real compiler accept this
    # halo against this design's real placement? Running it here means Forge can
    # never disagree with what generation will do, because it is the same code
    # path.
    try:
        composed = compose_halo(base, halo)
    except HaloCenterUnresolvedError as exc:
        out.append(
            R.ValidationResult(
                ruleId=R.HALO_CENTER_RESOLVES,
                severity="error",
                message=str(exc),
                parameter="halo.centerMemberId",
            )
        )
        return out
    except HaloError as exc:
        out.append(
            R.ValidationResult(
                ruleId=R.HALO_COMPOSES,
                severity="error",
                message=f"This halo cannot be composed: {exc}",
                parameter="halo",
            )
        )
        return out

    # A ring naming a stone specification other than 'primary' is reported as a
    # WARNING: the document is structurally valid and still generates, and only
    # that ring's stones produce no geometry.
    for ring in halo.rings:
        refs = {ring.stoneRef} | {m.stoneRef for m in ring.members}
        for ref in sorted(refs):
            if ref != "primary":
                out.append(
                    R.ValidationResult(
                        ruleId=R.HALO_REFERENCES_RESOLVE,
                        severity="warning",
                        message=(
                            f"Halo ring '{ring.ringId}' references stone "
                            f"'{ref}', but this definition declares only the "
                            "primary stone. No geometry will be built for those "
                            "halo stones."
                        ),
                        parameter="halo.rings",
                    )
                )
        setting_refs = {ring.settingRef} | {m.settingRef for m in ring.members}
        for setting_ref in sorted(r for r in setting_refs if r is not None):
            if setting_ref != d.setting.type:
                out.append(
                    R.ValidationResult(
                        ruleId=R.HALO_REFERENCES_RESOLVE,
                        severity="warning",
                        message=(
                            f"Halo ring '{ring.ringId}' requests setting "
                            f"'{setting_ref}', but this design's setting is "
                            f"'{d.setting.type}'. No halo setting is generated: "
                            "only the primary stone receives one."
                        ),
                        parameter="halo.rings",
                    )
                )

    # THE REMAINING LIMITATION, surfaced as INFORMATION rather than hidden in a
    # log. The design is not faulty; the halo's stones simply have no metal
    # holding them yet.
    if composed is not None:
        stones = sum(ring.count for ring in halo.rings)
        out.append(
            R.ValidationResult(
                ruleId=R.HALO_SETTING_COVERAGE,
                severity="information",
                message=(
                    f"This {halo.variant} halo builds real stone geometry for "
                    f"all {stones} halo stone(s), but no metal is generated to "
                    "hold them: a setting is built only for the primary stone. "
                    "No halo-setting strategy exists yet."
                ),
                parameter="halo",
            )
        )

    return out


def _pave_rules(d: JewelryDefinition) -> list[R.ValidationResult]:
    """Pave and microsetting validation (Sprint 26).

    SCOPE: PAVE_ONLY. Six questions: does the host surface resolve for this
    design, does the field compile, did it lose cells to the surface edge, do
    its references resolve, is the requested pitch geometrically consistent
    with the stones it must carry, and what does a compiled field NOT include.

    ONLY ONE IS NUMERIC, and it is a MATHEMATICAL CONSTRAINT rather than a
    professional threshold: two stones whose footprints are wider than the
    pitch between them overlap as a matter of arithmetic. There is deliberately
    no minimum pave spacing, no minimum bead diameter, no maximum density and
    no settable seat depth - each needs sourced professional evidence this
    project does not have.

    THE AUTHORITATIVE CHECK RUNS THE REAL COMPILER against the design's real
    resolved surface, so Forge can never disagree with what generation will do.
    That is why this module imports `geometry/pave_surface.py`, which is
    deliberately kernel-free for exactly this reason: Forge must not import
    CadQuery, and it must not resolve a surface differently from the assembly.

    A design with no pave produces NO results, so the entire existing corpus
    stays quiet.
    """

    pave = d.pave
    if pave is None:
        return []

    from jewelmind.domain.stone_dimensions import resolved_width_mm
    from jewelmind.geometry.pave_surface import resolve_pave_surface
    from jewelmind.pave.compile import compile_pave_field, lattice_pitches
    from jewelmind.pave.errors import PaveError, PaveHostUnsupportedError

    out: list[R.ValidationResult] = []

    try:
        surface = resolve_pave_surface(d, pave)
    except PaveHostUnsupportedError as exc:
        out.append(
            R.ValidationResult(
                ruleId=R.PAVE_HOST_RESOLVES,
                severity="error",
                message=str(exc),
                parameter="pave.host",
            )
        )
        return out

    # A field naming a stone specification other than 'primary' is reported as
    # a WARNING: the document is structurally valid and the rest of the design
    # still generates; only that field produces no geometry.
    if pave.stoneRef != "primary":
        out.append(
            R.ValidationResult(
                ruleId=R.PAVE_REFERENCES_RESOLVE,
                severity="warning",
                message=(
                    f"Pave {pave.paveId!r} references stone "
                    f"{pave.stoneRef!r}, but this definition declares only the "
                    "primary stone. No geometry will be built for its stones."
                ),
                parameter="pave.stoneRef",
            )
        )

    try:
        field = compile_pave_field(pave, surface)
    except PaveError as exc:
        out.append(
            R.ValidationResult(
                ruleId=R.PAVE_COMPILES,
                severity="error",
                message=f"This pave cannot be compiled: {exc}",
                parameter="pave",
            )
        )
        return out

    if not field.enabled:
        out.append(
            R.ValidationResult(
                ruleId=R.PAVE_EXECUTION_BOUNDARY,
                severity="information",
                message=(
                    f"Pave {pave.paveId!r} is declared and disabled, so no "
                    "stones and no retention metal are built. Its parameters "
                    "are preserved."
                ),
                parameter="pave.enabled",
            )
        )
        return out

    # CELLS LOST TO THE SURFACE EDGE. A warning rather than an error: a clipped
    # field is a real, buildable design, and the caller chose CLIP. Reported
    # because a field that lost a third of its stones to an edge is a fact the
    # caller needs, not a detail to absorb silently.
    if field.clippedCells:
        out.append(
            R.ValidationResult(
                ruleId=R.PAVE_FIELD_CONTAINMENT,
                severity="warning",
                message=(
                    f"{field.clippedCells} lattice cell(s) of pave "
                    f"{pave.paveId!r} fall outside the {pave.host} surface's "
                    f"declared extent and were clipped; {field.stone_count()} "
                    "stone(s) remain. Reduce the row count, the span or the "
                    "pitch to fit the surface."
                ),
                parameter="pave.spec",
            )
        )

    # THE ONE NUMERIC CHECK, and it is arithmetic. The stone's own resolved
    # footprint, scaled by the field's own scale, against the pitch between
    # centres. Nothing here says how much clearance a setter needs; it says
    # only that below this the stones intersect each other, which is a
    # geometric fact Inspection will then report as one.
    pitch, row_pitch = lattice_pitches(pave)
    stone_width = resolved_width_mm(d.stone)
    footprint = stone_width * pave.stoneScale
    tightest = min(pitch, row_pitch)
    if footprint > tightest:
        out.append(
            R.ValidationResult(
                ruleId=R.PAVE_PITCH_CONSISTENCY,
                severity="warning",
                message=(
                    f"Pave {pave.paveId!r} sets stones {footprint:.3f}mm across "
                    f"at a pitch of {tightest:.3f}mm, so adjacent stones "
                    "overlap as a matter of arithmetic. A GEOMETRIC "
                    "inconsistency, not a manufacturing threshold: JewelMind "
                    "states no minimum pave spacing. Increase the pitch or "
                    "reduce pave.stoneScale."
                ),
                parameter="pave.stoneScale",
                suggestedValue=round(tightest / max(stone_width, 1e-9), 4),
            )
        )

    # WHAT THE FIELD DOES NOT INCLUDE, surfaced as INFORMATION rather than
    # hidden in a log, plus the professional-review statement the brief
    # requires. The design is not faulty.
    boundary: list[str] = []
    if pave.retention.strategy == "NONE":
        boundary.append(
            "retention is 'NONE', so its stones are built with no metal "
            "holding them"
        )
    if pave.seat.mode == "NONE":
        boundary.append(
            "no recess is cut, so its stones sit against the host surface "
            "rather than into it"
        )
    detail = f" This field {', and '.join(boundary)}." if boundary else ""
    out.append(
        R.ValidationResult(
            ruleId=R.PAVE_EXECUTION_BOUNDARY,
            severity="information",
            message=(
                f"This {field.kind} field builds {field.stone_count()} stone(s) "
                f"and {field.retention_count()} retention piece(s) on the "
                f"{pave.host} surface.{detail} No pave dimension, spacing or "
                "retention size in JewelMind is professionally validated: a "
                "qualified jewelry professional must review this field before "
                "production."
            ),
            parameter="pave",
        )
    )

    return out


def _stone_depth_rule_applies(stone) -> bool:
    """Whether STONE_DEPTH_RANGE's premise holds for this stone.

    Returns False where the rule was never calibrated, rather than evaluating it
    against a dimension it does not describe (STONE-GOV-010's discipline).
    """

    if stone.source == "IMPORTED_CAD":
        return False
    if stone.profile == "SPHERICAL_REFERENCE" or stone.shape == "pearl":
        return False
    return True


def _stone_rules(d: JewelryDefinition) -> list[R.ValidationResult]:
    """Stone-domain rules, scoped to the stone sources they were calibrated for.

    Sprint 18: `STONE_DIAMETER_RANGE` is ROUND_ONLY (round was the only shape
    with a `diameter`); `STONE_DEPTH_RANGE` was generalized to the stone's real
    minimum horizontal extent, a genuine structural generalization (depth must
    not exceed the stone's own footprint) rather than a fabricated "equivalent
    diameter".

    Sprint 20 scoping, both found by actually running validation against the new
    sources rather than by reading the code:

    - A SPHERICAL reference (pearl) is exempt from `STONE_DEPTH_RANGE`. A
      sphere's depth IS its horizontal extent, so `depth < min_extent` can never
      hold and the rule fired on every valid pearl. The rule's premise — that a
      stone is wider than it is deep — simply does not describe a sphere. Marked
      REQUIRES_RULE_EVOLUTION rather than "fixed" by loosening the threshold,
      which would have weakened it for every other shape.

    - An IMPORTED stone is exempt from both dimension rules. Its true dimensions
      are a property of the asset, not of the document, so
      `resolved_length_mm()` correctly refuses to answer — and calling it here
      raised `StoneDimensionsUnavailableError` straight out of validation. Its
      real dimensions are reported by Geometry Inspection from the imported
      geometry; interpreting them is future rule work, not something to fake
      from the document.

    `stone.diameter` still has no range rule for `pearl`, and a non-round
    shape's `length`/`width` still have none individually. Both are real,
    recorded gaps — see docs/bible/22-stone-v2/code-mapping-and-gaps.md — not
    solved by inventing a threshold this Sprint (STONEV2-GOV-011).
    """

    out: list[R.ValidationResult] = []

    if d.stone.shape == "round":
        assert d.stone.diameter is not None
        if not (2 <= d.stone.diameter <= 15):
            out.append(
                R.ValidationResult(
                    ruleId=R.STONE_DIAMETER_RANGE,
                    severity="error",
                    message="Stone diameter must be between 2 mm and 15 mm.",
                    parameter="stone.diameter",
                )
            )

    if _stone_depth_rule_applies(d.stone):
        min_extent = min(resolved_length_mm(d.stone), resolved_width_mm(d.stone))
        if not (0.5 < resolved_depth_mm(d.stone) < min_extent):
            out.append(
                R.ValidationResult(
                    ruleId=R.STONE_DEPTH_RANGE,
                    severity="error",
                    message=(
                        "Stone depth must be greater than 0.5 mm and lower than the "
                        "stone's minimum horizontal extent."
                    ),
                    parameter="stone.depth",
                )
            )

    return out


def _prong_rules(d: JewelryDefinition) -> list[R.ValidationResult]:
    """PRONG_ONLY (Sprint 19). Every rule in this function reads a prong
    field, so none of them is meaningful for a bezel setting — a bezel has
    no prongs to count, size, or clear. Evaluating them anyway would block
    a perfectly valid bezel on `setting.prongCount`, which is exactly the
    mis-scoping brief section 32 calls out.

    Classification per rule:
      JM-PRONG-001 (count)             PRONG_ONLY
      JM-PRONG-002 (diameter min)      PRONG_ONLY
      JM-PRONG-003 (count vs size)     PRONG_ONLY + ROUND_ONLY (Sprint 18)
      JM-PRONG-004 (height vs basket)  PRONG_ONLY

    See docs/bible/21-setting/code-mapping-and-gaps.md for the full
    Setting-scoped rule table.
    """

    out: list[R.ValidationResult] = []

    if d.setting.type != "prong":
        return out

    if d.setting.prongCount not in (4, 6):
        out.append(
            R.ValidationResult(
                ruleId=R.PRONG_COUNT,
                severity="error",
                message="Prong count must be exactly 4 or 6.",
                parameter="setting.prongCount",
                suggestedValue=6,
            )
        )

    if d.setting.prongDiameter < 0.8:
        out.append(
            R.ValidationResult(
                ruleId=R.PRONG_DIAMETER_MIN,
                severity="error",
                message="Prong diameter below 0.8 mm is not supported.",
                parameter="setting.prongDiameter",
                suggestedValue=0.8,
            )
        )
    elif d.setting.prongDiameter < 1.0:
        out.append(
            R.ValidationResult(
                ruleId=R.PRONG_DIAMETER_MIN,
                severity="warning",
                message="Prong diameter below 1.0 mm may be structurally fragile.",
                parameter="setting.prongDiameter",
                suggestedValue=1.0,
            )
        )

    # ROUND_ONLY (Sprint 18): tuned for a round stone's diameter; applying
    # it to a non-round shape's length/width would need real, justified
    # generalization this Sprint does not provide — a REQUIRES_RULE_EVOLUTION
    # gap, not silently evaluated against a fake equivalent diameter (brief
    # section 44). See docs/bible/20-stone/578-current-code-mapping-and-gaps.md.
    stone_is_large_round = (
        d.stone.shape == "round" and d.stone.diameter is not None and d.stone.diameter > 8
    )
    if stone_is_large_round and d.setting.prongCount == 4:
        out.append(
            R.ValidationResult(
                ruleId=R.PRONG_COUNT_VS_STONE_SIZE,
                severity="warning",
                message="Stones larger than 8 mm are typically more secure with six prongs.",
                parameter="setting.prongCount",
                suggestedValue=6,
            )
        )

    if not (d.setting.prongHeight > d.setting.basketHeight):
        out.append(
            R.ValidationResult(
                ruleId=R.PRONG_HEIGHT_VS_BASKET,
                severity="error",
                message="Prong height must be greater than basket height.",
                parameter="setting.prongHeight",
            )
        )

    return out


def _bezel_rules(d: JewelryDefinition) -> list[R.ValidationResult]:
    """BEZEL_ONLY (Sprint 19). Deliberately ENGINEERING_INVARIANT rules
    only: both check that a dimension is positive, which is a
    constructibility fact, not a jewelry-domain threshold.

    No minimum bezel wall thickness or height is asserted. Such a minimum
    would be a professional manufacturing threshold, and no sourced value
    exists — inventing one is forbidden by SETTING-GOV-010. This is a real,
    documented gap, not an oversight: see
    docs/bible/21-setting/code-mapping-and-gaps.md.
    """

    out: list[R.ValidationResult] = []

    if d.setting.type != "bezel":
        return out

    if d.setting.bezelWallThickness <= 0:
        out.append(
            R.ValidationResult(
                ruleId=R.BEZEL_WALL_THICKNESS_POSITIVE,
                severity="error",
                message="Bezel wall thickness must be positive.",
                parameter="setting.bezelWallThickness",
            )
        )

    if d.setting.bezelWallHeight <= 0:
        out.append(
            R.ValidationResult(
                ruleId=R.BEZEL_WALL_HEIGHT_POSITIVE,
                severity="error",
                message="Bezel wall height must be positive.",
                parameter="setting.bezelWallHeight",
            )
        )

    return out


def _setting_rules(d: JewelryDefinition) -> list[R.ValidationResult]:
    out: list[R.ValidationResult] = []

    if d.setting.basketHeight <= 0:
        out.append(
            R.ValidationResult(
                ruleId=R.SETTING_BASKET_HEIGHT_POSITIVE,
                severity="error",
                message="Basket height must be positive.",
                parameter="setting.basketHeight",
            )
        )
    elif d.setting.basketHeight > 8:
        out.append(
            R.ValidationResult(
                ruleId=R.SETTING_BASKET_HEIGHT_MAX,
                severity="warning",
                message="Basket height above 8 mm is unusually tall.",
                parameter="setting.basketHeight",
            )
        )

    return out


def _setting_mode_rules(d: JewelryDefinition) -> list[R.ValidationResult]:
    """Extended Setting Modes validation (Sprint 27).

    SCOPE: EXTENDED_SETTING_MODES, and STRUCTURAL, REFERENTIAL or MATHEMATICAL
    only. Six questions: does the declared mode belong to the family the
    document chose, are the parameters it needs present, which parameters is it
    not going to read, is the request geometrically possible, does the mode
    carry a professional-review requirement, and is its status honest.

    NONE OF THEM IS A PROFESSIONAL JUDGMENT. There is no rule here about whether
    a channel wall is thick enough, a bar spacing settable, a flush collar
    strong enough or a tension setting safe. Each needs sourced professional
    evidence this project does not have, so none exists (SETTING-GOV-010).

    A DESIGN WITH NO MODE BLOCK PRODUCES AT MOST THE STATUS RESULT. Every
    pre-Sprint-27 document resolves to `PRONG_ROUND` or `BEZEL_FULL`, both
    CURRENT and neither requiring review, so the whole existing corpus stays
    silent here — the same discipline `_setting_v2_rules` follows for its own
    defaults.

    THE MODE IS RESOLVED BY THE REAL RESOLVER, not re-derived. `_family_rules`,
    `_halo_rules` and `_pave_rules` each run the real compiler for exactly this
    reason: a rule that reimplemented the resolution would eventually disagree
    with the geometry, and the disagreement would surface as a design that
    validates and then fails to build.
    """

    from jewelmind.domain.stone_dimensions import (
        resolved_length_mm,
        resolved_width_mm,
    )
    from jewelmind.setting.capability import setting_modes
    from jewelmind.setting.modes import (
        MODE_PARAMETER_FIELDS,
        SettingModeParameters,
        resolve_primary_mode,
    )

    setting = d.setting
    out: list[R.ValidationResult] = []

    try:
        resolved = resolve_primary_mode(
            setting.type, setting.prongStyle, setting.mode
        )
    except ValueError as exc:
        # The resolver refuses a mode whose family disagrees with `type`, and a
        # HEAD or RETENTION mode declared on the PRIMARY axis. Surfaced as a
        # rule result here rather than only as a generation-time exception, so a
        # caller learns about it from validation like every other refusal.
        out.append(
            R.ValidationResult(
                ruleId=R.SETTING_MODE_FAMILY_MATCHES,
                severity="error",
                message=str(exc),
                parameter="setting.mode.modeId",
            )
        )
        return out

    entry = setting_modes().get(resolved.modeId)
    if entry is None:  # pragma: no cover - closed literal makes this unreachable
        out.append(
            R.ValidationResult(
                ruleId=R.SETTING_MODE_FAMILY_MATCHES,
                severity="error",
                message=(
                    f"setting mode '{resolved.modeId}' has no capability "
                    "registry entry, so nothing is known about what it builds."
                ),
                parameter="setting.mode.modeId",
            )
        )
        return out

    parameters = resolved.parameters
    read_fields = set(MODE_PARAMETER_FIELDS[resolved.modeId])

    # UNREAD PARAMETERS. INFORMATION, not a warning: the document is perfectly
    # valid and the value simply has no effect. Reported only when the author
    # actually SET it — comparing against the model's own defaults rather than
    # listing every field, so a mode with no parameters stays silent.
    if setting.mode is not None and setting.mode.enabled:
        defaults = SettingModeParameters()
        unread = sorted(
            name
            for name in type(parameters).model_fields
            if name not in read_fields
            and getattr(parameters, name) != getattr(defaults, name)
        )
        if unread:
            out.append(
                R.ValidationResult(
                    ruleId=R.SETTING_MODE_PARAMETER_APPLICABLE,
                    severity="information",
                    message=(
                        f"setting mode '{resolved.modeId}' does not read "
                        + ", ".join(f"setting.mode.parameters.{n}" for n in unread)
                        + ". The value is kept in the document and has no effect "
                        "on the geometry."
                    ),
                    parameter=f"setting.mode.parameters.{unread[0]}",
                )
            )

    # A DISABLED MODE. INFORMATION: the parameters stay in the document and the
    # family's default variant is used, which is a state worth naming rather
    # than leaving the author to wonder why nothing changed.
    if setting.mode is not None and not setting.mode.enabled:
        out.append(
            R.ValidationResult(
                ruleId=R.SETTING_MODE_PARAMETER_APPLICABLE,
                severity="information",
                message=(
                    f"setting.mode '{setting.mode.modeId}' is disabled, so the "
                    f"'{setting.type}' family's default variant "
                    f"'{resolved.modeId}' is built and the declared parameters "
                    "are not read."
                ),
                parameter="setting.mode.enabled",
            )
        )

    # REQUIREMENTS. A flush setting's recess IS half its geometry, so relief is
    # a precondition rather than an option — see `flush.py`'s docstring.
    if setting.type == "flush" and setting.seatMode == "NONE":
        out.append(
            R.ValidationResult(
                ruleId=R.SETTING_MODE_REQUIREMENTS_MET,
                severity="error",
                message=(
                    "A flush setting requires setting.seatMode = "
                    "'REFERENCE_SEAT'. Without the recess the collar occupies "
                    "the stone's whole volume, and the result is a solid mass "
                    "with the stone buried inside it rather than a flush "
                    "setting."
                ),
                parameter="setting.seatMode",
                suggestedValue="REFERENCE_SEAT",
            )
        )

    # GEOMETRIC FEASIBILITY. MATHEMATICAL CONSTRAINTS on the document's own
    # requested dimensions, and NECESSARY rather than sufficient: only the built
    # solid knows its measured crown height and its measured extent, so the
    # generator performs the exact check. Both are reported here because
    # catching an impossible request before the kernel is asked for solids is
    # strictly better than catching it after.
    if setting.type == "flush":
        depth = d.stone.depth
        if depth is not None and parameters.rimHeightMm >= depth:
            out.append(
                R.ValidationResult(
                    ruleId=R.SETTING_MODE_GEOMETRY_FEASIBLE,
                    severity="error",
                    message=(
                        f"The flush collar's rim height "
                        f"({parameters.rimHeightMm} mm) is not below the "
                        f"stone's whole depth ({depth} mm), so the stone would "
                        "be entirely buried. The stone's crown is only part of "
                        "its depth, so the generator applies the exact check "
                        "against the measured crown height; this is the "
                        "arithmetic one, checkable from the document alone."
                    ),
                    parameter="setting.mode.parameters.rimHeightMm",
                )
            )

    if setting.type == "tension":
        half_extent = _extent_along(
            resolved_length_mm(d.stone),
            resolved_width_mm(d.stone),
            parameters.gripAxisDeg,
        ) / 2.0
        if parameters.padDepthMm >= half_extent:
            out.append(
                R.ValidationResult(
                    ruleId=R.SETTING_MODE_GEOMETRY_FEASIBLE,
                    severity="error",
                    message=(
                        f"The tension supports' inward reach "
                        f"({parameters.padDepthMm} mm) is not less than half "
                        f"the stone's requested extent along the grip axis "
                        f"({half_extent:.4f} mm), so the two supports would "
                        "meet through the middle of the stone. Arithmetic, not "
                        "a statement about how deeply a stone may be gripped."
                    ),
                    parameter="setting.mode.parameters.padDepthMm",
                )
            )

    # PROFESSIONAL REVIEW. The brief's third severity category, carried as a
    # `warning` because the three severities are a published contract; the
    # rule's own registry entry records `professionalValidationStatus: required`,
    # which is where that distinction already lives.
    if entry.professionalReviewRequirement == "REQUIRED":
        from jewelmind.setting.capability import PROFESSIONAL_REVIEW_REQUIRED

        reason = PROFESSIONAL_REVIEW_REQUIRED.get(setting.type, "")
        out.append(
            R.ValidationResult(
                ruleId=R.SETTING_MODE_PROFESSIONAL_REVIEW,
                severity="warning",
                message=(
                    f"Setting mode '{resolved.modeId}' requires review by a "
                    f"qualified jewelry professional. {reason} JewelMind "
                    "generates the geometry and makes no claim about its "
                    "function."
                ),
                parameter="setting.type",
            )
        )

    # HONEST STATUS. A PARTIAL mode is reported as PARTIAL, with what is missing,
    # so a caller never has to read the capability registry to learn that a mode
    # it just used is not complete.
    if entry.status != "CURRENT":
        out.append(
            R.ValidationResult(
                ruleId=R.SETTING_MODE_STATUS,
                severity="information",
                message=(
                    f"Setting mode '{resolved.modeId}' is {entry.status}, not "
                    f"CURRENT. {entry.description}"
                ),
                parameter="setting.type",
            )
        )

    return out


def _extent_along(length_mm: float, width_mm: float, axis_deg: float) -> float:
    """A box's extent along a horizontal direction.

    The same support-width arithmetic `setting/frame.py::stone_extent_along()`
    applies to the MEASURED box, applied here to the REQUESTED dimensions.
    Stated separately rather than imported because Forge must not depend on a
    module that imports the CAD kernel, and duplicating two absolute values and
    a sum is cheaper than the alternative — the same split
    `geometry/pave_surface.py` documents for the pavé's host resolution.
    """

    radians = math.radians(axis_deg)
    return abs(math.cos(radians)) * length_mm + abs(math.sin(radians)) * width_mm


def _ring_family_rules(d: JewelryDefinition) -> list[R.ValidationResult]:
    """Ring Families validation (Sprint 28).

    SCOPE: RING_FAMILY_ONLY, and STRUCTURAL, REFERENTIAL or MATHEMATICAL only.
    Five questions: does the declared variant belong to the family
    `jewelry.style` names, does its derivation collide with a block the document
    already declares, which parameters is it not going to read, is the requested
    structure geometrically possible, and is the variant's status honest.

    NONE OF THEM IS A PROFESSIONAL JUDGMENT. There is no rule here about whether
    a shank section is strong enough, a shoulder castable, a signet table thick
    enough or a bypass sound. Each needs sourced professional evidence this
    project does not have, so none exists.

    A DESIGN WITH NO RING FAMILY BLOCK PRODUCES AT MOST THE STATUS RESULT.
    Every pre-Sprint-28 document is a `solitaire` with no `ringFamily`, which
    resolves to `SOLITAIRE_CLASSIC` — CURRENT — so the whole existing corpus
    stays silent here.

    THE FAMILY IS RESOLVED BY THE REAL RESOLVER, not re-derived. `_family_rules`,
    `_halo_rules`, `_pave_rules` and `_setting_mode_rules` each do the same, for
    the same reason: a rule that reimplemented the resolution would eventually
    disagree with the geometry, and the disagreement would surface as a design
    that validates and then fails to build.
    """

    from jewelmind.ring_family.capability import ring_family_capabilities
    from jewelmind.ring_family.errors import RingFamilyError
    from jewelmind.ring_family.models import RingFamilyParams, variants_for_family
    from jewelmind.ring_family.resolve import resolve_ring_family

    out: list[R.ValidationResult] = []
    spec = d.ringFamily

    try:
        resolved = resolve_ring_family(d)
    except RingFamilyError as exc:
        # The resolver refuses a variant whose family disagrees with
        # `jewelry.style`, and a derivation that would collide with an explicit
        # arrangement. Surfaced as a rule result here rather than only as a
        # generation-time exception, so a caller learns about it from validation
        # like every other refusal.
        rule = (
            R.RING_FAMILY_DERIVATION_APPLICABLE
            if "arrangement" in str(exc)
            else R.RING_FAMILY_VARIANT_MATCHES
        )
        out.append(
            R.ValidationResult(
                ruleId=rule,
                severity="error",
                message=str(exc),
                parameter="ringFamily.variant",
                suggestedValue=(
                    variants_for_family(d.jewelry.style)[0]
                    if variants_for_family(d.jewelry.style)
                    else None
                ),
            )
        )
        return out

    entry = ring_family_capabilities().get(resolved.variant)
    if entry is None:  # pragma: no cover - the closed literal makes this unreachable
        out.append(
            R.ValidationResult(
                ruleId=R.RING_FAMILY_VARIANT_MATCHES,
                severity="error",
                message=(
                    f"ring family variant '{resolved.variant}' has no capability "
                    "registry entry, so nothing is known about what it builds."
                ),
                parameter="ringFamily.variant",
            )
        )
        return out

    # DERIVATIONS THE DOCUMENT PRE-EMPTED. INFORMATION, not a warning: the
    # document is perfectly valid and its own block is used, which is the
    # correct outcome — but an author who chose a `halo` family and also wrote a
    # halo deserves to be told which one won.
    if resolved.skippedPaths:
        out.append(
            R.ValidationResult(
                ruleId=R.RING_FAMILY_DERIVATION_APPLICABLE,
                severity="information",
                message=(
                    f"The '{resolved.variant}' ring family would derive "
                    + ", ".join(resolved.skippedPaths)
                    + ", and this design declares them itself. The declared "
                    "values are used unchanged; the family derived none."
                ),
                parameter=f"{resolved.skippedPaths[0].split('.')[0]}",
            )
        )

    # UNREAD PARAMETERS. Reported only when the author actually SET one, by
    # comparing against the model's own defaults rather than listing every
    # field, so a variant with few parameters stays silent.
    if spec is not None and spec.enabled and resolved.unreadParameters:
        out.append(
            R.ValidationResult(
                ruleId=R.RING_FAMILY_PARAMETER_APPLICABLE,
                severity="information",
                message=(
                    f"ring family variant '{resolved.variant}' does not read "
                    + ", ".join(
                        f"ringFamily.params.{name}"
                        for name in resolved.unreadParameters
                    )
                    + ". The value is kept in the document and has no effect on "
                    "the geometry."
                ),
                parameter=f"ringFamily.params.{resolved.unreadParameters[0]}",
            )
        )

    # A DISABLED FAMILY BLOCK. INFORMATION: the parameters stay in the document
    # and the family's default variant is used, which is a state worth naming
    # rather than leaving the author to wonder why nothing changed.
    if spec is not None and not spec.enabled:
        out.append(
            R.ValidationResult(
                ruleId=R.RING_FAMILY_PARAMETER_APPLICABLE,
                severity="information",
                message=(
                    f"ringFamily is disabled, so the '{d.jewelry.style}' "
                    f"family's default variant '{resolved.variant}' is built and "
                    "the declared parameters are not read."
                ),
                parameter="ringFamily.enabled",
            )
        )

    # GEOMETRIC FEASIBILITY. A MATHEMATICAL CONSTRAINT: two rails sharing the
    # band's width leave `(width - separation) / 2` of rail between them, so a
    # separation at or above the width leaves none. The rail width comes from
    # the SAME function the builder uses, so this rule cannot stop agreeing with
    # the geometry.
    params = resolved.params if spec is not None and spec.enabled else RingFamilyParams()
    if resolved.shankArchitecture in {"SPLIT", "BYPASS"}:
        separation = (
            params.splitSeparationMm
            if resolved.shankArchitecture == "SPLIT"
            else params.bypassSeparationMm
        )
        rail_width = (d.band.width - separation) / 2.0
        if rail_width <= 0:
            field = (
                "splitSeparationMm"
                if resolved.shankArchitecture == "SPLIT"
                else "bypassSeparationMm"
            )
            out.append(
                R.ValidationResult(
                    ruleId=R.RING_FAMILY_GEOMETRY_FEASIBLE,
                    severity="error",
                    message=(
                        f"A separation of {separation} mm leaves "
                        f"{rail_width:.4f} mm of rail in a {d.band.width} mm "
                        "band. The rails SHARE the band's width, so a wider "
                        "separation narrows them rather than widening the ring — "
                        "arithmetic, not a statement about how thin a rail may "
                        "be."
                    ),
                    parameter=f"ringFamily.params.{field}",
                )
            )

    if resolved.bodyArchitecture == "SIGNET_TABLE":
        # A table narrower than the band would leave the band standing proud of
        # the body it is meant to be part of.
        if params.signetTableWidthMm < d.band.width:
            out.append(
                R.ValidationResult(
                    ruleId=R.RING_FAMILY_GEOMETRY_FEASIBLE,
                    severity="warning",
                    message=(
                        f"The signet table is {params.signetTableWidthMm} mm "
                        f"across a {d.band.width} mm band, so the band stands "
                        "proud of the body it is part of. Geometrically valid "
                        "and probably not what was intended."
                    ),
                    parameter="ringFamily.params.signetTableWidthMm",
                    suggestedValue=d.band.width,
                )
            )

    # HONEST STATUS. A PARTIAL variant is reported as PARTIAL, with what is
    # missing, so a caller never has to read the capability registry to learn
    # that a family it just used is incomplete.
    if entry.status != "CURRENT":
        out.append(
            R.ValidationResult(
                ruleId=R.RING_FAMILY_STATUS,
                severity="information",
                message=(
                    f"Ring family variant '{resolved.variant}' is "
                    f"{entry.status}, not CURRENT. {entry.description}"
                ),
                parameter="jewelry.style",
            )
        )

    return out


def _manufacturing_rules(d: JewelryDefinition) -> list[R.ValidationResult]:
    out: list[R.ValidationResult] = []

    if d.manufacturing.method != "direct_resin_printing":
        return out

    # setting.prongDiameter is excluded here: JM-PRONG-002 already errors
    # below 0.8 mm for prongs regardless of manufacturing method, so this
    # check only needs to cover dimensions with no stricter existing rule.
    structural_params = {
        "band.thickness": d.band.thickness,
        "band.width": d.band.width,
    }
    for parameter, value in structural_params.items():
        if value < 0.8:
            out.append(
                R.ValidationResult(
                    ruleId=R.MANUFACTURING_MIN_FEATURE,
                    severity="warning",
                    message=(
                        f"{parameter} is below 0.8 mm; direct resin printing may not "
                        "reliably resolve features this thin."
                    ),
                    parameter=parameter,
                    suggestedValue=0.8,
                )
            )

    return out


def _geometry_rules(d: JewelryDefinition) -> list[R.ValidationResult]:
    out: list[R.ValidationResult] = []

    outer_diameter = d.ring.innerDiameter + 2 * d.band.thickness
    if d.band.thickness <= 0 or outer_diameter <= d.ring.innerDiameter:
        out.append(
            R.ValidationResult(
                ruleId=R.GEOMETRY_OUTER_BAND_POSITIVE,
                severity="error",
                message="Band thickness must produce a positive outer band dimension.",
                parameter="band.thickness",
            )
        )

    if d.band.width <= 0:
        out.append(
            R.ValidationResult(
                ruleId=R.GEOMETRY_OUTER_BAND_POSITIVE,
                severity="error",
                message="Band width must be positive to produce valid band geometry.",
                parameter="band.width",
            )
        )

    return out


_RULE_GROUPS = (
    _ring_rules,
    _band_rules,
    _stone_rules,
    _gem_rules,
    _arrangement_rules,
    _family_rules,
    _halo_rules,
    _pave_rules,
    _prong_rules,
    _bezel_rules,
    _setting_rules,
    _setting_v2_rules,
    _setting_mode_rules,
    _ring_family_rules,
    _manufacturing_rules,
    _geometry_rules,
)


def validate_definition(definition: JewelryDefinition) -> list[R.ValidationResult]:
    """Run every deterministic validation rule against `definition`.

    Returns the full, deterministically ordered list of results (errors,
    warnings, and information) — never raises for an invalid definition.
    Callers decide whether to block generation/export based on severities.
    """

    results: list[R.ValidationResult] = []
    for group in _RULE_GROUPS:
        results.extend(group(definition))
    return results


def has_errors(results: list[R.ValidationResult]) -> bool:
    return any(r.severity == "error" for r in results)
