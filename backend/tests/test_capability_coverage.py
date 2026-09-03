"""Capability Coverage Guard consistency tests (brief section 45).

`specs/capabilities/jewelmind-capabilities.json` is one authoritative
cross-product record of what JewelMind can and cannot do. Its whole value
is that it cannot quietly lie, so these tests check it against the real
code wherever the real code can answer.

The central invariant: **CURRENT requires real implementation.** A
capability marked CURRENT whose implementation does not exist is a
documentation defect, not a harmless optimism.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import get_args

import jsonschema

REPO_ROOT = Path(__file__).resolve().parents[2]
CAPS_DIR = REPO_ROOT / "specs" / "capabilities"
REGISTRY = CAPS_DIR / "jewelmind-capabilities.json"
SCHEMA = CAPS_DIR / "jewelmind-capabilities.schema.json"

VALID_STATUSES = {"CURRENT", "PARTIAL", "PLANNED", "BLOCKED", "OUT_OF_SCOPE"}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _entries() -> list[dict]:
    return _load(REGISTRY)["capabilities"]


def _by_key() -> dict[tuple[str, str], dict]:
    return {(e["domain"], e["capability"]): e for e in _entries()}


def test_registry_and_schema_exist_and_validate():
    schema = _load(SCHEMA)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(_load(REGISTRY), schema)


def test_every_status_is_a_recognized_value():
    for entry in _entries():
        assert entry["status"] in VALID_STATUSES, entry


def test_every_entry_has_a_substantive_note():
    """A status with no justification is unauditable."""

    for entry in _entries():
        assert len(entry["note"].strip()) >= 15, entry


def test_no_duplicate_capability_keys():
    keys = [(e["domain"], e["capability"]) for e in _entries()]
    assert len(keys) == len(set(keys))


def test_declared_status_values_match_the_real_set():
    assert set(_load(REGISTRY)["statusValues"]) == VALID_STATUSES


# --- CURRENT must be backed by real code -------------------------------------


def test_current_setting_families_match_the_live_setting_registry():
    from jewelmind.setting.capability import SETTING_CAPABILITIES

    recorded = {
        e["capability"].removesuffix("_setting")
        for e in _entries()
        if e["domain"] == "setting" and e["status"] == "CURRENT" and e["capability"].endswith("_setting")
    }
    assert recorded == set(SETTING_CAPABILITIES)


def test_planned_setting_families_are_not_registered_generators():
    from jewelmind.setting.dispatch import setting_generators

    generators = setting_generators()
    for entry in _entries():
        if entry["domain"] == "setting" and entry["status"] == "PLANNED":
            family = entry["capability"].removesuffix("_setting")
            assert family not in generators, entry


def test_current_stone_shapes_match_the_live_stone_registry():
    """Sprint 20 made the Stone v2 registry authoritative for shape capability.

    The Sprint 18 registry still exists and still describes the seven original
    shapes; `test_stone_v1_and_v2_registries_agree` below pins the two together
    so they cannot drift apart.
    """

    from jewelmind.stone.capability import native_shapes

    recorded = {
        e["capability"] for e in _entries() if e["domain"] == "stone_shape" and e["status"] == "CURRENT"
    }
    assert recorded == set(native_shapes())


def test_stone_v1_and_v2_registries_agree():
    """Two registries describing the same shapes are a drift hazard.

    The Sprint 18 registry is a frozen record of Stone v1 and keeps its own
    field shape; what must never diverge is the FACTS they both state — which
    shapes exist, and whether each generates.
    """

    from jewelmind.geometry.stone.capability import STONE_SHAPE_CAPABILITIES
    from jewelmind.stone.capability import STONE_SHAPE_CAPABILITIES_V2

    for shape, v1 in STONE_SHAPE_CAPABILITIES.items():
        v2 = STONE_SHAPE_CAPABILITIES_V2.get(shape)
        assert v2 is not None, f"{shape} exists in the Stone v1 registry but not in v2"
        assert v2.introducedInStoneV1, f"{shape} is a Stone v1 shape but v2 does not say so"
        assert v1.generationSupported == v2.generationSupported
        assert v1.requiredDimensions == v2.requiredDimensions


def test_planned_stone_shapes_are_not_accepted_by_jdl():
    from jewelmind.domain.schema import StoneShape

    accepted = set(get_args(StoneShape))
    for entry in _entries():
        if entry["domain"] == "stone_shape" and entry["status"] == "PLANNED":
            assert entry["capability"] not in accepted, entry


def test_current_jewelry_categories_match_the_live_category_registry():
    from jewelmind.jewelry_category.registry import CATEGORY_CAPABILITIES

    recorded = {
        e["capability"]
        for e in _entries()
        if e["domain"] == "jewelry_category" and e["status"] == "CURRENT"
    }
    live_generatable = {
        name for name, cap in CATEGORY_CAPABILITIES.items() if cap.generationSupported
    }
    assert recorded == live_generatable


def test_seats_bearings_and_cutters_are_reported_honestly():
    """Sprint 19 asserted all three were PLANNED. That was true then.

    Sprint 23 added real opt-in `REFERENCE_SEAT` relief, so seat support is now
    PARTIAL in both registries — PARTIAL rather than CURRENT because relief is
    not a cut seat with a bearing shoulder. Bearing and cutter must keep saying
    PLANNED: a bearing is sized by a setter, a cutter is manufacturing tooling,
    and no sourced professional geometry exists for either.

    The two registries must agree, which is the whole point of this guard.
    """

    from jewelmind.setting.capability import SETTING_CAPABILITIES

    keys = _by_key()
    assert keys[("setting", "stone_seat")]["status"] == "PARTIAL"
    for capability in ("bearing", "cutter"):
        assert keys[("setting", capability)]["status"] == "PLANNED"
    for capability in SETTING_CAPABILITIES.values():
        assert capability.seatSupport == "PARTIAL"
        assert capability.bearingSupport == "PLANNED"
        assert capability.cutterSupport == "PLANNED"


def test_advanced_head_and_prong_capabilities_match_the_live_registries():
    """A CURRENT head or prong capability must have a real builder behind it."""

    from jewelmind.setting.capability import (
        HEAD_ARCHITECTURE_CAPABILITIES,
        PRONG_STYLE_CAPABILITIES,
    )
    from jewelmind.setting.head import head_architectures
    from jewelmind.setting.prong_styles import prong_solid_builders

    keys = _by_key()
    assert keys[("setting", "prong_style_variants")]["status"] == "CURRENT"
    assert keys[("setting", "head_architectures")]["status"] == "CURRENT"

    # Registry and builders agree in BOTH directions: an entry with no builder
    # advertises a capability that does not exist, and a builder with no entry
    # ships one nobody declared.
    assert set(prong_solid_builders()) == {
        name for name, e in PRONG_STYLE_CAPABILITIES.items() if e.generatable
    }
    assert set(head_architectures()) == {
        name for name, e in HEAD_ARCHITECTURE_CAPABILITIES.items() if e.generatable
    }


def test_trellis_and_rails_are_not_claimed():
    keys = _by_key()
    for capability in (
        "trellis_head",
        "support_rails",
        "anchor_driven_prong_placement",
    ):
        assert keys[("setting", capability)]["status"] == "PLANNED", capability
    # Shared prong geometry resolves and reports, but does not build against two
    # stones — PARTIAL, never CURRENT.
    assert keys[("setting", "shared_prong_geometry")]["status"] == "PARTIAL"


def test_no_professionally_validated_setting_geometry_is_claimed():
    """The single most important honesty invariant in this file."""

    from jewelmind.setting.capability import SETTING_CAPABILITIES

    entry = _by_key()[("professional_validation", "validated_setting_geometry")]
    assert entry["status"] == "PLANNED"
    for capability in SETTING_CAPABILITIES.values():
        assert capability.professionalValidationStatus == "NOT_REVIEWED"


def test_active_professional_validation_registry_is_still_empty():
    """A CURRENT professional-validation *framework* must not be confused
    with actual validated records."""

    registry = _load(
        REPO_ROOT / "specs" / "professional-validation" / "v1" / "current-validation-registry.json"
    )
    records = registry.get("records", registry.get("validationRecords", []))
    assert records == []


def test_escape_hatches_are_recorded():
    """Brief section 46: the cross-product escape hatches must remain
    visible so a future capability is not architecturally blocked."""

    keys = _by_key()
    required = [
        ("setting", "custom_setting"),
        ("setting", "imported_setting_component"),
        ("stone_source_mode", "custom_outline"),
        ("stone_source_mode", "measured_stone"),
        ("component", "user_component"),
        ("component", "imported_cad_component"),
        ("finding", "generic_finding"),
        ("jewelry_category", "custom_category"),
        ("decoration", "custom_pattern"),
        ("material", "external_material_profile"),
        ("manufacturing", "external_manufacturing_profile"),
    ]
    for key in required:
        assert key in keys, f"missing escape hatch: {key}"
        assert keys[key]["status"] in {"PLANNED", "PARTIAL"}, keys[key]


def test_blocked_entries_explain_what_blocks_them():
    blocked = [e for e in _entries() if e["status"] == "BLOCKED"]
    assert blocked, "at least one genuinely blocked capability is expected to be recorded"
    for entry in blocked:
        # "not available" and "not supported" are legitimate phrasings of a
        # real blocker; the vocabulary was widened rather than contorting the
        # notes to contain a keyword.
        assert any(
            word in entry["note"].lower()
            for word in (
                "credential", "blocked", "unavailable", "no ",
                "not available", "not supported", "not present",
            )
        ), entry


def test_coverage_spans_the_expected_domains():
    domains = {e["domain"] for e in _entries()}
    expected = {
        "setting",
        "stone_shape",
        "stone_source_mode",
        "stone",
        "stone_arrangement",
        "ring_family",
        "jewelry_category",
        "shank",
        "finding",
        "component",
        "decoration",
        "material",
        "manufacturing",
        "reporting",
        "interoperability",
        "history",
        "library",
        "studio",
        "vision",
        "designer",
        "conversation",
        "commercial",
        "sdk",
        "collaboration",
        "retail",
        "professional_validation",
        # Sprint 21.
        "gem",
        "gem_visual",
        # Sprint 22.
        "arrangement",
    }
    missing = expected - domains
    assert not missing, f"capability coverage is missing domains: {sorted(missing)}"


def test_current_gem_capabilities_match_the_live_gem_registry():
    """A gem capability marked CURRENT must be backed by real registry content.

    Sprint 20 found three hand-copied capability lists that had already drifted
    and made Designer and Setting misreport what the backend could do; this ties
    the gem entries to the live code instead.
    """

    from jewelmind.gem.registry import GEM_REGISTRY, current_gem_ids
    from jewelmind.gem.visual import GEM_VISUAL_PROFILES

    keys = _by_key()

    registry_entry = keys[("gem", "gem_registry")]
    assert registry_entry["status"] == "CURRENT"
    assert str(len(current_gem_ids())) in registry_entry["note"]

    profiles_entry = keys[("gem_visual", "gem_visual_profiles")]
    assert profiles_entry["status"] == "CURRENT"
    assert str(len(GEM_VISUAL_PROFILES)) in profiles_entry["note"]

    # The two escape hatches must exist as real entries, not merely as prose.
    assert "custom" in GEM_REGISTRY
    assert "unknown" in GEM_REGISTRY
    assert keys[("gem", "custom_material")]["status"] == "CURRENT"
    assert keys[("gem", "unknown_gem")]["status"] == "CURRENT"


def test_no_gem_property_rule_is_claimed_as_current():
    """No hardness, durability or setting-suitability rule exists.

    Each would need professional evidence this project does not have, so the
    capability stays PLANNED and no Forge rule may quietly appear.
    """

    import jewelmind.validation.rules as live_rules

    keys = _by_key()
    assert keys[("gem", "gem_property_rules")]["status"] == "PLANNED"
    assert keys[("gem", "gemological_certification")]["status"] == "OUT_OF_SCOPE"

    gem_rule_ids = {
        value
        for name, value in vars(live_rules).items()
        if isinstance(value, str) and value.startswith("JM-GEM")
    }
    # Six referential/coherence rules and nothing more: a seventh would need to
    # be justified, and a property rule could not be.
    assert len(gem_rule_ids) == 6, sorted(gem_rule_ids)


def test_gem_arrangement_is_not_advertised_as_current():
    keys = _by_key()
    assert keys[("gem", "per_stone_gem_in_a_multi_stone_design")]["status"] == "PLANNED"


def test_current_arrangement_capabilities_match_the_live_registry():
    """An arrangement capability marked CURRENT must be backed by live code.

    The cross-product registry and `arrangement/capability.py` answer the same
    question, so they must agree — the drift Sprint 20 had to remove three
    times.
    """

    from jewelmind.arrangement.capability import ARRANGEMENT_CAPABILITIES

    keys = _by_key()
    live = ARRANGEMENT_CAPABILITIES

    # The boundary, asserted in both registries.
    assert keys[("arrangement", "multi_stone_geometry")]["status"] == "PARTIAL"
    assert live["multi_stone_geometry"].status == "PARTIAL"
    assert live["multi_stone_geometry"].generatable is False

    # Exactly one arrangement capability builds geometry today.
    generatable = [name for name, e in live.items() if e.generatable]
    assert generatable == ["stone_instance"]
    assert keys[("arrangement", "stone_instance")]["status"] == "CURRENT"


def test_no_arrangement_solver_or_professional_rule_is_claimed():
    keys = _by_key()
    for capability in (
        "constraint_solving",
        "professional_arrangement_rules",
        "arrangement_collision_checking",
        "enforced_relationships",
        "path_pattern",
        "full_3d_instance_orientation",
    ):
        assert keys[("arrangement", capability)]["status"] == "PLANNED", capability


def test_the_stone_arrangement_domain_does_not_contradict_the_new_one():
    """The pre-existing `stone_arrangement` domain was a forward-looking
    placeholder. It must not now claim geometry the pipeline cannot build."""

    for entry in _entries():
        if entry["domain"] != "stone_arrangement":
            continue
        if entry["capability"] == "single_center":
            continue
        assert entry["status"] in {"PLANNED", "PARTIAL"}, entry
