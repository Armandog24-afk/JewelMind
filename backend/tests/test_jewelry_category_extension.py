"""JEWELRY_CATEGORY_REGISTRY_TEST, RING_CATEGORY_CAPABILITY_TEST,
PLANNED_CATEGORY_NOT_GENERATABLE_TEST, CATEGORY_DISPATCH_TEST,
UNSUPPORTED_CATEGORY_TEST, and the mandatory architectural proof:
NON_RING_TEST_CATEGORY_EXTENSION_TEST / NON_RING_NO_RING_FIELD_ACCESS_TEST.

The dummy category defined here exists ONLY in this test file — it is
never added to `CATEGORY_CAPABILITIES`, `CATEGORY_GENERATORS`, any
Designer capability, or the JDL schema (brief section 42).
"""

from __future__ import annotations

import pytest
from pydantic import BaseModel

from jewelmind.jewelry_category.dispatch import generate_for_category, generate_jewelry
from jewelmind.jewelry_category.errors import (
    JewelryCategoryNotGeneratableError,
    JewelryCategoryUnsupportedError,
)
from jewelmind.jewelry_category.models import CategoryCapability
from jewelmind.jewelry_category.registry import CATEGORY_CAPABILITIES, get_capability, is_generation_supported


class TestJewelryCategoryRegistry:
    def test_ring_is_current_and_generation_supported(self):
        ring = get_capability("ring")
        assert ring.status == "current"
        assert ring.generationSupported is True
        assert "solitaire" in ring.supportedFamilies

    @pytest.mark.parametrize("category", ["earring", "pendant", "bracelet", "necklace", "charm"])
    def test_reserved_future_categories_are_planned_and_not_generatable(self, category):
        capability = get_capability(category)
        assert capability is not None
        assert capability.status == "planned"
        assert capability.generationSupported is False
        assert capability.supportedFamilies == []

    def test_unknown_category_returns_none(self):
        assert get_capability("brooch") is None

    def test_is_generation_supported_matches_capability_flag(self):
        assert is_generation_supported("ring") is True
        assert is_generation_supported("earring") is False
        assert is_generation_supported("nonexistent") is False


class TestPlannedCategoryNotGeneratable:
    def test_planned_category_cannot_be_dispatched_through_production_registry(self):
        with pytest.raises(JewelryCategoryNotGeneratableError):
            generate_for_category("earring", object(), registry={})

    def test_unknown_category_is_unsupported_not_not_generatable(self):
        with pytest.raises(JewelryCategoryUnsupportedError):
            generate_for_category("brooch", object(), registry={})


class TestCategoryDispatch:
    def test_generate_for_category_calls_the_registered_generator(self):
        calls = []

        def fake_ring_generator(payload):
            calls.append(payload)
            return "fake-generated-model"

        result = generate_for_category("ring", "the-payload", registry={"ring": fake_ring_generator})
        assert result == "fake-generated-model"
        assert calls == ["the-payload"]

    def test_missing_generator_for_a_supported_category_raises_not_generatable(self):
        with pytest.raises(JewelryCategoryNotGeneratableError):
            generate_for_category("ring", object(), registry={})


# ---------------------------------------------------------------------
# The mandatory non-ring extensibility proof (brief sections 24/42/50).
# ---------------------------------------------------------------------


class DummyPendantDefinition(BaseModel):
    """TEST-ONLY. Deliberately has nothing in common with
    JewelryDefinition/RingDefinition — no ring, band, basket, or setting
    field of any kind."""

    dummyLength: float


class DummyPendantResult(BaseModel):
    kind: str
    dummyLength: float


def _dummy_pendant_generator(payload: DummyPendantDefinition) -> DummyPendantResult:
    """TEST-ONLY generator. Never imports or references anything from
    `jewelmind.ring` or `jewelmind.domain.schema`."""

    # Prove at runtime that only the dummy field is ever touched.
    assert not hasattr(payload, "ring")
    assert not hasattr(payload, "band")
    assert not hasattr(payload, "basket")
    return DummyPendantResult(kind="dummy_pendant", dummyLength=payload.dummyLength)


class TestNonRingCategoryExtension:
    """Proves category registration is extensible, a category-specific
    schema/model can remain fully separate from Ring, and dispatch works
    generically — without ever modifying production registries."""

    def test_a_wholly_unrelated_category_dispatches_through_the_same_generic_function(self):
        test_capabilities = {
            "dummy_pendant": CategoryCapability(
                category="dummy_pendant",
                status="current",
                definitionVersion="0.0.0-test",
                generationSupported=True,
                validationSupported=False,
                previewSupported=False,
                exportSupported=False,
                supportedFamilies=[],
                sharedSystems=[],
                categorySpecificSystems=[],
                message="TEST-ONLY capability, never real product capability.",
            )
        }
        test_registry = {"dummy_pendant": _dummy_pendant_generator}

        result = generate_for_category(
            "dummy_pendant",
            DummyPendantDefinition(dummyLength=42.0),
            registry=test_registry,
            capabilities=test_capabilities,
        )

        assert isinstance(result, DummyPendantResult)
        assert result.dummyLength == 42.0

    def test_dummy_category_definition_never_carries_a_ring_field(self):
        payload = DummyPendantDefinition(dummyLength=7.5)
        assert not hasattr(payload, "ring")
        assert not hasattr(payload, "band")
        assert not hasattr(payload, "basket")
        assert not hasattr(payload, "setting")
        assert not hasattr(payload, "stone")

    def test_dummy_category_is_absent_from_the_real_production_registry(self):
        assert "dummy_pendant" not in CATEGORY_CAPABILITIES

    def test_dummy_category_cannot_be_reached_through_generate_jewelry(self):
        # generate_jewelry() only ever reads a real JewelryDefinition's
        # jewelry.category, which is schema-locked to "ring" — there is
        # no way to make it reach the dummy category above. This test
        # documents that guarantee explicitly rather than assuming it.
        from jewelmind.domain.schema import JewelryDefinition

        definition = JewelryDefinition()
        assert definition.jewelry.category == "ring"
        # generate_jewelry() would dispatch through the real production
        # generator registry, which never contains "dummy_pendant" —
        # confirmed structurally.
        from jewelmind.jewelry_category.dispatch import _category_generators

        assert "dummy_pendant" not in _category_generators()
        assert generate_jewelry.__module__ == "jewelmind.jewelry_category.dispatch"
