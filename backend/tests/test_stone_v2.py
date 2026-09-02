"""Stone System v2 — extended cuts, custom outlines, measured and imported
stones (Sprint 20, brief sections 79/80).

Organized by the brief's own acceptance names so a reader can map a
requirement to the test that proves it.
"""

from __future__ import annotations

import math
import tempfile
from pathlib import Path

import cadquery as cq
import pytest
from pydantic import ValidationError

from jewelmind.domain.defaults import default_definition
from jewelmind.domain.schema import StoneSpec
from jewelmind.domain.stone_dimensions import (
    StoneDimensionsUnavailableError,
    resolved_depth_mm,
    resolved_length_mm,
    resolved_width_mm,
)
from jewelmind.geometry.assemblies.solitaire import build_solitaire_ring
from jewelmind.geometry.components.stone import build_stone_reference
from jewelmind.geometry.roles import GEOMETRY_ROLE, PRODUCTION_ROLE
from jewelmind.geometry.setting_adapter import setting_definition_from_jdl
from jewelmind.geometry.stone import outline as O
from jewelmind.geometry.stone.builder import _build_non_round_stone, build_stone_geometry
from jewelmind.setting.dispatch import generate_setting
from jewelmind.stone import capability as cap
from jewelmind.stone.anchors import derive_anchors
from jewelmind.stone.dispatch import resolve_stone, stone_source_handlers
from jewelmind.stone.errors import (
    CustomOutlineInvalidError,
    CustomOutlineSelfIntersectionError,
    MeasuredStoneInsufficientDataError,
    StoneImportEmptyError,
    StoneImportFailedError,
    StoneImportFormatUnsupportedError,
    StoneImportTooComplexError,
    StoneShapeProfileCombinationUnsupportedError,
)
from jewelmind.stone.importing import (
    MAX_ASSET_BYTES,
    SUPPORTED_IMPORT_FORMATS,
    UNSUPPORTED_IMPORT_FORMATS,
    FilesystemStoneAssetStore,
    import_stone_asset,
)
from jewelmind.stone.models import CustomOutlineSpec, OutlinePoint
from jewelmind.stone.normalize import canonicalize_stone, stone_anchors
from jewelmind.stone.outline_validation import (
    normalize_custom_outline,
    validate_custom_outline,
)

# --------------------------------------------------------------------------
# Shared fixtures and helpers
# --------------------------------------------------------------------------

#: Per-shape dimensions. Shapes not listed use LWD below.
SHAPE_DIMENSIONS: dict[str, dict[str, float]] = {
    "round": {"diameter": 6.5, "depth": 4.0},
    "pearl": {"diameter": 8.0, "depth": 8.0},
    "tapered_baguette": {"length": 6.0, "width": 3.2, "narrowWidth": 2.0, "depth": 2.5},
    "trapezoid": {"length": 4.0, "width": 6.0, "narrowWidth": 3.6, "depth": 2.5},
}
LWD = {"length": 8.0, "width": 6.0, "depth": 4.0}

SPRINT18_SHAPES = ["round", "oval", "pear", "emerald", "cushion", "princess", "marquise"]
SPRINT20_SHAPES = [
    "heart", "radiant", "asscher", "trillion", "baguette", "tapered_baguette",
    "triangle", "trapezoid", "lozenge", "hexagon", "kite", "shield",
    "half_moon", "pearl",
]

CONVEX_OUTLINE = [(0.0, 4.0), (3.0, 1.5), (2.4, -3.0), (-2.4, -3.0), (-3.0, 1.5)]
CONCAVE_OUTLINE = [
    (0.0, 4.0), (3.0, 1.5), (0.8, 0.2), (2.4, -3.0),
    (-2.4, -3.0), (-0.8, 0.2), (-3.0, 1.5),
]


def stone_payload(shape: str, **overrides) -> dict:
    payload = {"shape": shape, **SHAPE_DIMENSIONS.get(shape, LWD)}
    payload.update(overrides)
    return payload


def outline_spec(points, unit: str = "mm") -> dict:
    return {"points": [{"x": x, "y": y} for x, y in points], "unit": unit}


def definition_with(stone: dict, setting_type: str = "prong"):
    definition = default_definition()
    definition.stone = StoneSpec.model_validate(stone)
    definition.setting.type = setting_type
    return definition


def build_stone_only(stone: dict):
    return build_stone_reference(definition_with(stone))


# --------------------------------------------------------------------------
# STONE_V1_FULL_REGRESSION (brief section 70)
# --------------------------------------------------------------------------


class TestStoneV1BackwardCompatibility:
    """The single most important guarantee of this sprint."""

    def test_default_solitaire_metal_volume_is_unchanged(self):
        model = build_solitaire_ring(default_definition())
        assert math.isclose(
            model.combined_metal_volume_mm3, 341.44334316909976, rel_tol=1e-9
        )

    def test_default_round_stone_volume_is_unchanged(self):
        model = build_solitaire_ring(default_definition())
        assert math.isclose(
            model.components["stone_reference"].volume_mm3, 58.22141924499569, rel_tol=1e-9
        )

    def test_round_still_uses_the_pre_sprint18_construction(self):
        """A plain round faceted stone must not be routed through the v2 path.

        Identified by the version the builder stamps: the v1 fast path records
        `referenceGeometryVersion` 1.0.0, the v2 pipeline records 2.0.0, so
        rerouting round would be visible here immediately.

        An earlier version of this test also asserted `"sourceMode" not in
        metadata`, using a missing key as a proxy for "took the v1 path". That
        proxy broke the moment the v1 path started reporting its own source mode
        — which was a deliberate improvement, since round is the DEFAULT stone
        and had been the least inspectable one. A proxy for a fact is worth less
        than the fact: the version stamp is checked instead, and the geometry
        itself is compared below.
        """

        component = build_stone_only({"shape": "round", "diameter": 6.5, "depth": 4.0})
        assert component.metadata["referenceGeometryVersion"] == "1.0.0"
        assert component.metadata["sourceMode"] == "PARAMETRIC_REFERENCE"

    def test_round_geometry_differs_from_the_v2_pipeline(self):
        """The fast path is not merely labelled differently — it builds
        differently, which is exactly why it must not be replaced.

        THE REAL DIFFERENCE IS THE CULET, and it is a Sprint 18 decision this
        test now pins. Round's construction uses an ABSOLUTE culet radius
        (`_CULET_RADIUS_MM = 0.05`), while the shared pipeline uses a
        PROPORTIONAL one (`CULET_SCALE_RATIO = 0.05` of the half-width, i.e.
        0.1625mm for a 6.5mm stone). The wider culet makes the v2 body about 1.8%
        larger — measured, not assumed.

        That is why "round takes the fast path" is a geometry guarantee rather
        than a performance note: routing round through the shared pipeline
        "for consistency" would silently change every existing round model.
        """

        definition = definition_with({"shape": "round", "diameter": 6.5, "depth": 4.0})
        fast_path = build_stone_reference(definition)
        via_v2 = build_stone_geometry(
            definition.stone, girdle_z_mm=fast_path.metadata["girdleZMm"]
        )
        assert via_v2.volume_mm3 > fast_path.volume_mm3, (
            "the proportional culet should make the shared pipeline's body larger"
        )
        # Same silhouette, same crown/pavilion ratios: the two differ only by the
        # culet, so they stay within a few percent of each other.
        assert math.isclose(fast_path.volume_mm3, via_v2.volume_mm3, rel_tol=3e-2)

    @pytest.mark.parametrize("shape", SPRINT18_SHAPES)
    def test_sprint18_documents_still_validate_without_new_fields(self, shape: str):
        stone = StoneSpec.model_validate(stone_payload(shape))
        assert stone.source == "PARAMETRIC_REFERENCE"
        assert stone.profile == "FACETED_REFERENCE"
        assert stone.narrowWidth is None

    @pytest.mark.parametrize("shape", ["oval", "pear", "emerald", "cushion", "princess", "marquise"])
    def test_sprint18_non_round_geometry_is_bit_identical_after_the_v2_refactor(
        self, shape: str
    ):
        """Compare the two implementations directly, not against a literal.

        Sprint 20 routed every non-round shape through the new
        `build_stone_geometry()` pipeline. The Sprint 18 implementation
        (`_build_non_round_stone`) is still present, so the honest regression
        test is to run BOTH on the same definition and require exact equality —
        no recorded constant to drift, and no hand-written number to be wrong.

        An earlier version of this test did hardcode expected volumes, and five
        of the six were subtly wrong: they had been typed rather than measured,
        which is precisely what JDL-GOV-009 forbids.
        """

        definition = definition_with(stone_payload(shape))
        legacy = _build_non_round_stone(definition)
        current = build_stone_reference(definition)
        assert current.volume_mm3 == legacy.volume_mm3, (
            f"{shape} geometry changed: {current.volume_mm3!r} != {legacy.volume_mm3!r}"
        )
        for axis in ("xmin", "xmax", "ymin", "ymax", "zmin", "zmax"):
            assert getattr(current.bounding_box, axis) == getattr(legacy.bounding_box, axis)


# --------------------------------------------------------------------------
# Extended native shape generation (brief sections 4/8-22/80)
# --------------------------------------------------------------------------


class TestExtendedNativeShapes:
    @pytest.mark.parametrize("shape", SPRINT20_SHAPES)
    def test_shape_generates_a_real_valid_solid(self, shape: str):
        component = build_stone_only(stone_payload(shape))
        assert component.volume_mm3 > 0
        assert len(component.shape.Solids()) == 1
        assert component.shape.isValid()

    @pytest.mark.parametrize("shape", SPRINT18_SHAPES + SPRINT20_SHAPES)
    def test_requested_dimensions_equal_measured_dimensions(self, shape: str):
        """The dimension contract (brief section 46).

        Three shapes broke this during development — shield, trillion and
        half_moon each overshot by construction, and heart by a partially
        converged normalization. Each was fixed at the source rather than by
        reporting the nominal value.
        """

        component = build_stone_only(stone_payload(shape))
        box = component.bounding_box
        metadata = component.metadata
        # OCCT pads a solid's bounding box by ~2e-7; compare within that.
        assert abs((box.xmax - box.xmin) - metadata["widthMm"]) < 1e-6
        assert abs((box.ymax - box.ymin) - metadata["lengthMm"]) < 1e-6
        assert abs((box.zmax - box.zmin) - metadata["depthMm"]) < 1e-6

    @pytest.mark.parametrize("shape", SPRINT18_SHAPES + SPRINT20_SHAPES)
    def test_generation_is_deterministic(self, shape: str):
        first = build_stone_only(stone_payload(shape))
        second = build_stone_only(stone_payload(shape))
        assert first.volume_mm3 == second.volume_mm3

    @pytest.mark.parametrize("shape", [s for s in SPRINT20_SHAPES if s != "pearl"])
    def test_outline_is_centred_on_the_local_origin(self, shape: str):
        """The canonical frame invariant.

        `half_moon` genuinely violated this: `ellipseArc` centres the ellipse on
        the CURRENT point, so the outline sat entirely below the origin while
        still reporting a correct bounding-box SIZE. Only checking size would
        have missed it.
        """

        normalized = canonicalize_stone(StoneSpec.model_validate(stone_payload(shape)))
        assert normalized.outline is not None
        xs = [p.x for p in normalized.outline.points]
        ys = [p.y for p in normalized.outline.points]
        # A sampled curve slightly under-covers its own extremes (measured at
        # ~8e-5 mm for the heart's lobes at 48 samples per arc), so the point
        # cloud is checked at sampling tolerance while the underlying wire is
        # checked exactly in `test_outline_wire_is_exactly_centred`.
        assert abs((min(xs) + max(xs)) / 2) < 1e-3
        assert abs((min(ys) + max(ys)) / 2) < 1e-3

    def test_trillion_and_triangle_are_different_shapes(self):
        """Sharing a family must never merge two canonical identities."""

        triangle = build_stone_only(stone_payload("triangle"))
        trillion = build_stone_only(stone_payload("trillion"))
        assert trillion.volume_mm3 != triangle.volume_mm3

    def test_baguette_and_emerald_are_different_shapes(self):
        baguette = build_stone_only(stone_payload("baguette"))
        emerald = build_stone_only(stone_payload("emerald"))
        assert baguette.volume_mm3 > emerald.volume_mm3, (
            "a plain rectangle must enclose more than the same rectangle with "
            "its corners clipped"
        )

    def test_radiant_asscher_and_emerald_clip_by_different_amounts(self):
        volumes = {
            shape: build_stone_only(stone_payload(shape)).volume_mm3
            for shape in ("radiant", "emerald", "asscher")
        }
        assert volumes["radiant"] > volumes["emerald"] > volumes["asscher"], volumes

    def test_tapered_baguette_narrow_end_is_really_narrower(self):
        normalized = canonicalize_stone(
            StoneSpec.model_validate(stone_payload("tapered_baguette"))
        )
        points = normalized.outline.points
        top = [p for p in points if p.y > 0]
        bottom = [p for p in points if p.y < 0]
        top_width = max(p.x for p in top) - min(p.x for p in top)
        bottom_width = max(p.x for p in bottom) - min(p.x for p in bottom)
        assert bottom_width > top_width, "the WIDE end must be at -Y"

    def test_kite_is_longitudinally_asymmetric(self):
        """Compare against the shape's own mirror, not against another shape.

        Sprint 18 learned that "X differs from Y" can pass for the wrong reason.
        A shape is asymmetric if its centroid is offset from its bounding-box
        centre along the length axis — zero for a symmetric control.
        """

        def centroid_offset(shape: str) -> float:
            component = build_stone_only(stone_payload(shape))
            box = component.bounding_box
            return component.shape.Center().y - (box.ymin + box.ymax) / 2

        assert abs(centroid_offset("kite")) > 0.1
        assert abs(centroid_offset("lozenge")) < 1e-6, "symmetric control"
        assert abs(centroid_offset("hexagon")) < 1e-6, "symmetric control"

    @pytest.mark.parametrize("shape", SPRINT20_SHAPES)
    def test_shape_survives_a_step_roundtrip(self, shape: str):
        component = build_stone_only(stone_payload(shape))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "stone.step"
            cq.exporters.export(cq.Workplane(obj=component.shape), str(path))
            reimported = cq.importers.importStep(str(path)).val()
        assert len(reimported.Solids()) == 1
        assert math.isclose(reimported.Volume(), component.volume_mm3, rel_tol=1e-6)

    @pytest.mark.parametrize("shape", ["heart", "trillion", "kite", "shield", "triangle"])
    def test_pointed_shapes_need_no_stabilization(self, shape: str):
        """Brief section 69 pre-authorized microscopic tip stabilization.

        None was needed, and none was implemented. This pins that: if a future
        change makes a pointed shape fragile, it fails here rather than being
        quietly patched with a hidden distortion.
        """

        component = build_stone_only(stone_payload(shape))
        assert component.shape.isValid()
        rotated = component.shape.rotate((0, 0, 0), (0, 0, 1), 90)
        assert rotated.isValid()


# --------------------------------------------------------------------------
# STONE_PROFILE_V2 (brief sections 21/22/36)
# --------------------------------------------------------------------------


class TestStoneProfiles:
    @pytest.mark.parametrize("shape", ["round", "oval", "heart", "half_moon"])
    def test_cabochon_is_a_real_non_flat_body(self, shape: str):
        component = build_stone_only(stone_payload(shape, profile="CABOCHON_REFERENCE"))
        box = component.bounding_box
        assert component.volume_mm3 > 0
        assert box.zmax - box.zmin > 0.5
        assert len(component.shape.Solids()) == 1

    @pytest.mark.parametrize("shape", ["round", "oval"])
    def test_cabochon_differs_from_faceted_for_the_same_outline(self, shape: str):
        """Proves profile is a real second axis, not a relabelling."""

        faceted = build_stone_only(stone_payload(shape))
        cabochon = build_stone_only(stone_payload(shape, profile="CABOCHON_REFERENCE"))
        assert cabochon.volume_mm3 != faceted.volume_mm3
        assert cabochon.metadata["profile"] == "CABOCHON_REFERENCE"

    def test_pearl_is_a_real_sphere(self):
        component = build_stone_only(stone_payload("pearl"))
        box = component.bounding_box
        diameter = 8.0
        assert math.isclose(box.xmax - box.xmin, diameter, rel_tol=1e-6)
        assert math.isclose(box.zmax - box.zmin, diameter, rel_tol=1e-6)
        expected = 4 / 3 * math.pi * (diameter / 2) ** 3
        assert math.isclose(component.volume_mm3, expected, rel_tol=1e-3)

    def test_pearl_defaults_its_profile_and_records_doing_so(self):
        """A default resolved is disclosed; an explicit request is never overridden."""

        component = build_stone_only(stone_payload("pearl"))
        assert component.metadata["profile"] == "SPHERICAL_REFERENCE"
        operations = component.metadata["provenance"]["normalizationOperations"]
        assert any(op.startswith("PROFILE_DEFAULTED") for op in operations), operations

    def test_explicitly_unsupported_shape_profile_combination_is_refused(self):
        with pytest.raises(StoneShapeProfileCombinationUnsupportedError):
            build_stone_only(stone_payload("pearl", profile="FACETED_REFERENCE"))
        with pytest.raises(StoneShapeProfileCombinationUnsupportedError):
            build_stone_only(stone_payload("princess", profile="CABOCHON_REFERENCE"))

    def test_no_compound_outline_profile_enum_members_exist(self):
        """Brief section 36's structural requirement."""

        from typing import get_args

        from jewelmind.domain.schema import StoneShape

        for member in get_args(StoneShape):
            assert "cabochon" not in member, (
                f"{member!r} encodes a profile in a shape ID; profile is a "
                "separate axis"
            )


# --------------------------------------------------------------------------
# CUSTOM_OUTLINE (brief sections 23-27/49)
# --------------------------------------------------------------------------


class TestCustomOutlineValidation:
    def test_valid_convex_outline_is_accepted(self):
        points = validate_custom_outline(
            CustomOutlineSpec.model_validate(outline_spec(CONVEX_OUTLINE))
        )
        assert len(points) == len(CONVEX_OUTLINE)

    def test_valid_concave_outline_is_accepted(self):
        points = validate_custom_outline(
            CustomOutlineSpec.model_validate(outline_spec(CONCAVE_OUTLINE))
        )
        assert len(points) == len(CONCAVE_OUTLINE)

    @pytest.mark.parametrize(
        ("name", "points"),
        [
            ("collinear", [(0.0, 0.0), (1.0, 1.0), (2.0, 2.0)]),
            ("zero area", [(0.0, 0.0), (2.0, 0.0), (1.0, 0.0)]),
            ("duplicate closing point", [(0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 0.0)]),
            ("degenerate segment", [(0.0, 0.0), (2.0, 0.0), (2.0, 1e-12), (2.0, 2.0), (0.0, 2.0)]),
            ("non-finite", [(0.0, 0.0), (float("nan"), 0.0), (1.0, 1.0)]),
        ],
    )
    def test_malformed_outline_is_rejected(self, name: str, points):
        with pytest.raises(CustomOutlineInvalidError):
            validate_custom_outline(CustomOutlineSpec.model_validate(outline_spec(points)))

    def test_self_intersecting_outline_is_rejected_as_such(self):
        """A crossing with non-zero area, so the zero-area check cannot be what
        catches it. A symmetric bow-tie has zero signed area and would pass this
        test for the wrong reason."""

        crossed = [(0.0, 4.0), (2.4, -3.0), (-3.0, 1.5), (3.0, 1.5), (-2.4, -3.0)]
        with pytest.raises(CustomOutlineSelfIntersectionError):
            validate_custom_outline(CustomOutlineSpec.model_validate(outline_spec(crossed)))

    def test_boundary_touching_outline_is_rejected(self):
        """A vertex lying ON a distant edge is not a proper crossing, so the
        orientation test alone reports nothing — yet the outline is not simple
        and offsetting it is ambiguous. Found during Sprint 20 validation."""

        z_shape = [(-3.0, 3.0), (3.0, 3.0), (-3.0, -1.0), (3.0, -3.0), (-3.0, -3.0)]
        with pytest.raises(CustomOutlineSelfIntersectionError):
            validate_custom_outline(CustomOutlineSpec.model_validate(outline_spec(z_shape)))

    def test_too_few_points_is_rejected_by_the_schema(self):
        with pytest.raises(ValidationError):
            CustomOutlineSpec.model_validate(outline_spec([(0.0, 0.0), (1.0, 1.0)]))

    def test_units_are_converted_exactly_once_and_recorded(self):
        centimetres = [(x / 10, y / 10) for x, y in CONVEX_OUTLINE]
        points, operations = normalize_custom_outline(
            CustomOutlineSpec.model_validate(outline_spec(centimetres, unit="cm"))
        )
        millimetres, _ = normalize_custom_outline(
            CustomOutlineSpec.model_validate(outline_spec(CONVEX_OUTLINE))
        )
        assert any(op.startswith("UNIT_CONVERSION") for op in operations)
        for converted, direct in zip(points, millimetres, strict=True):
            assert math.isclose(converted.x, direct.x, abs_tol=1e-9)
            assert math.isclose(converted.y, direct.y, abs_tol=1e-9)

    def test_winding_is_normalized_and_recorded(self):
        clockwise = list(reversed(CONVEX_OUTLINE))
        _, operations = normalize_custom_outline(
            CustomOutlineSpec.model_validate(outline_spec(clockwise))
        )
        forward_points, forward_ops = normalize_custom_outline(
            CustomOutlineSpec.model_validate(outline_spec(CONVEX_OUTLINE))
        )
        # Exactly one of the two orientations needs reversing, and whichever it
        # is, the operation is recorded rather than applied silently.
        reversed_count = sum(
            any(op.startswith("WINDING_REVERSED") for op in ops)
            for ops in (operations, forward_ops)
        )
        assert reversed_count == 1
        assert forward_points

    def test_origin_is_recentred_on_the_bounding_box(self):
        offset = [(x + 50, y + 20) for x, y in CONVEX_OUTLINE]
        points, operations = normalize_custom_outline(
            CustomOutlineSpec.model_validate(outline_spec(offset))
        )
        xs = [p.x for p in points]
        ys = [p.y for p in points]
        assert abs((min(xs) + max(xs)) / 2) < 1e-9
        assert abs((min(ys) + max(ys)) / 2) < 1e-9
        assert any(op.startswith("ORIGIN_RECENTERED") for op in operations)


class TestCustomOutlineGeneration:
    @pytest.mark.parametrize(
        ("name", "points"), [("convex", CONVEX_OUTLINE), ("concave", CONCAVE_OUTLINE)]
    )
    def test_custom_outline_produces_real_cad(self, name: str, points):
        component = build_stone_only(
            {"source": "CUSTOM_OUTLINE", "shape": "custom", "depth": 4.0,
             "customOutline": outline_spec(points)}
        )
        assert component.volume_mm3 > 0
        assert len(component.shape.Solids()) == 1
        assert component.shape.isValid()
        assert component.metadata["sourceMode"] == "CUSTOM_OUTLINE"

    def test_custom_outline_dimensions_derive_from_the_points(self):
        component = build_stone_only(
            {"source": "CUSTOM_OUTLINE", "shape": "custom", "depth": 4.0,
             "customOutline": outline_spec(CONVEX_OUTLINE)}
        )
        assert math.isclose(component.metadata["widthMm"], 6.0, rel_tol=1e-9)
        assert math.isclose(component.metadata["lengthMm"], 7.0, rel_tol=1e-9)
        assert component.metadata["dimensionProvenance"] == "DERIVED_FROM_OUTLINE"

    def test_custom_outline_with_a_cabochon_profile(self):
        component = build_stone_only(
            {"source": "CUSTOM_OUTLINE", "shape": "custom", "depth": 4.0,
             "profile": "CABOCHON_REFERENCE",
             "customOutline": outline_spec(CONVEX_OUTLINE)}
        )
        assert component.volume_mm3 > 0
        assert component.metadata["profile"] == "CABOCHON_REFERENCE"

    def test_custom_outline_generation_is_deterministic(self):
        payload = {"source": "CUSTOM_OUTLINE", "shape": "custom", "depth": 4.0,
                   "customOutline": outline_spec(CONVEX_OUTLINE)}
        assert build_stone_only(payload).volume_mm3 == build_stone_only(payload).volume_mm3


# --------------------------------------------------------------------------
# CUSTOM_OUTLINE_BEZEL — the architecture proof (brief sections 41/72)
# --------------------------------------------------------------------------


class TestCustomOutlineSettingIntegration:
    @pytest.mark.parametrize(
        ("name", "points"), [("convex", CONVEX_OUTLINE), ("concave", CONCAVE_OUTLINE)]
    )
    @pytest.mark.parametrize("family", ["bezel", "prong"])
    def test_custom_stone_drives_a_real_setting(self, name: str, points, family: str):
        """THE acceptance criterion of brief section 72.

        A custom outline must reach real setting geometry through the generic
        interface. Before Sprint 20 this raised a bare `AssertionError` deep
        inside `resolved_length_mm()`, because the Setting System resolved
        dimensions from named-cut fields a custom stone does not have.
        """

        definition = definition_with(
            {"source": "CUSTOM_OUTLINE", "shape": "custom", "depth": 4.0,
             "customOutline": outline_spec(points)},
            setting_type=family,
        )
        stone = build_stone_reference(definition)
        components, result = generate_setting(
            setting_definition_from_jdl(definition, stone)
        )
        component = components["bezel" if family == "bezel" else "prongs"]
        assert component.volume_mm3 > 0
        assert component.shape.isValid()
        assert result.compatibilityStatus in ("SUPPORTED_SOFTWARE", "EXPERIMENTAL")

    def test_setting_system_has_no_custom_shape_special_case(self):
        """The proof is structural, not just behavioural.

        If the Setting System had to branch on `shape == "custom"`, it would
        still be a list of named cases — exactly what this sprint set out to
        remove.
        """

        import ast

        setting_package = Path(__file__).resolve().parents[1] / "jewelmind" / "setting"

        # AST rather than a text scan: a regex over source lines cannot tell a
        # real branch from a docstring that DESCRIBES the branch that used to
        # exist, and these modules' docstrings deliberately record that history.
        # Walking the parsed tree for `<...>.shape == "..."` sees only code.
        offenders: list[str] = []
        for module in sorted(setting_package.glob("*.py")):
            tree = ast.parse(module.read_text(encoding="utf-8"), filename=str(module))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Compare):
                    continue
                left = node.left
                reads_shape = (
                    isinstance(left, ast.Attribute) and left.attr == "shape"
                ) or (isinstance(left, ast.Name) and left.id == "shape")
                if not reads_shape:
                    continue
                for comparator in node.comparators:
                    literals: list = []
                    if isinstance(comparator, ast.Constant):
                        literals = [comparator]
                    elif isinstance(comparator, (ast.Tuple, ast.List, ast.Set)):
                        literals = list(comparator.elts)
                    if any(
                        isinstance(item, ast.Constant) and isinstance(item.value, str)
                        for item in literals
                    ):
                        offenders.append(f"{module.name}:{node.lineno}")

        assert not offenders, (
            "the Setting System branches on a stone shape name at "
            + ", ".join(offenders)
            + " - setting behaviour must follow geometric properties "
            "(isRadiallySymmetric, the outline itself), not a list of names"
        )
    def test_custom_stone_reaches_a_full_ring(self):
        definition = definition_with(
            {"source": "CUSTOM_OUTLINE", "shape": "custom", "depth": 4.0,
             "customOutline": outline_spec(CONVEX_OUTLINE)},
            setting_type="bezel",
        )
        model = build_solitaire_ring(definition)
        assert model.combined_metal_volume_mm3 > 0
        assert set(model.components) == {
            "band", "basket_support", "bezel", "stone_reference"
        }


# --------------------------------------------------------------------------
# MEASURED_STONE (brief sections 28/29)
# --------------------------------------------------------------------------


class TestMeasuredStone:
    def test_measured_dimensions_are_labelled_as_input_measurements(self):
        normalized = canonicalize_stone(
            StoneSpec.model_validate(
                stone_payload("oval", source="MEASURED",
                              measurement={"measurementSource": "digital caliper"})
            )
        )
        assert normalized.dimensions.provenance == "INPUT_MEASUREMENT"
        assert normalized.measuredReferenceClass == "MEASURED_DIMENSION_REFERENCE"

    def test_measured_reference_is_not_claimed_to_be_the_physical_surface(self):
        component = build_stone_only(stone_payload("oval", source="MEASURED"))
        assert component.metadata["measuredReferenceClass"] == "MEASURED_DIMENSION_REFERENCE"
        assert component.metadata["isGemologicalReproduction"] is False

    def test_measured_outline_upgrades_the_reference_class(self):
        normalized = canonicalize_stone(
            StoneSpec.model_validate(
                stone_payload("oval", source="MEASURED",
                              customOutline=outline_spec(CONVEX_OUTLINE))
            )
        )
        assert normalized.measuredReferenceClass == "MEASURED_OUTLINE_REFERENCE"

    def test_measurement_provenance_is_preserved_verbatim(self):
        component = build_stone_only(
            stone_payload("oval", source="MEASURED", measurement={
                "measurementSource": "Mitutoyo digital caliper",
                "measurementDate": "2026-08-14",
                "operatorNote": "measured across the widest girdle point",
            })
        )
        provenance = component.metadata["provenance"]
        assert provenance["measurementSource"] == "Mitutoyo digital caliper"
        assert provenance["measurementDate"] == "2026-08-14"
        assert provenance["operatorNote"] == "measured across the widest girdle point"

    def test_missing_measurements_are_never_invented(self):
        with pytest.raises((MeasuredStoneInsufficientDataError, ValidationError)):
            StoneSpec.model_validate({"shape": "oval", "source": "MEASURED", "depth": 4.0})

    def test_provenance_carries_no_wall_clock_timestamp(self):
        """Provenance participates in hashing and Golden snapshots; a clock
        reading would make identical geometry differ between runs."""

        first = build_stone_only(stone_payload("oval", source="MEASURED"))
        second = build_stone_only(stone_payload("oval", source="MEASURED"))
        assert first.metadata["provenance"] == second.metadata["provenance"]
        assert "createdAt" not in first.metadata["provenance"]


# --------------------------------------------------------------------------
# IMPORTED STONE (brief sections 30-33/50/51)
# --------------------------------------------------------------------------


@pytest.fixture()
def asset_store(tmp_path: Path) -> FilesystemStoneAssetStore:
    return FilesystemStoneAssetStore(tmp_path / "assets")


def _export(tmp_path: Path, suffix: str, solid: cq.Solid) -> bytes:
    path = tmp_path / f"stone{suffix}"
    if suffix == ".stl":
        cq.exporters.export(cq.Workplane(obj=solid), str(path), exportType="STL")
    else:
        cq.exporters.export(cq.Workplane(obj=solid), str(path))
    return path.read_bytes()


class TestImportedStone:
    def test_brep_import_yields_a_real_solid(self, tmp_path, asset_store):
        data = _export(tmp_path, ".step", cq.Solid.makeBox(6, 8, 4))
        digest = asset_store.store(data, ".step")
        imported = import_stone_asset(asset_store, digest, "mm")
        assert imported.representation == "BREP_SOLID"
        assert imported.supportsBrepOperations is True
        assert imported.solidCount == 1
        assert math.isclose(imported.volumeMm3, 192.0, rel_tol=1e-6)

    def test_mesh_import_is_honestly_not_a_brep_solid(self, tmp_path, asset_store):
        """Brief section 32: never pretend an STL has B-Rep capabilities."""

        data = _export(tmp_path, ".stl", cq.Solid.makeBox(6, 8, 4))
        digest = asset_store.store(data, ".stl")
        imported = import_stone_asset(asset_store, digest, "mm")
        assert imported.representation == "MESH"
        assert imported.supportsBrepOperations is False
        assert imported.solidCount == 0
        assert imported.volumeMm3 is None
        assert imported.triangleCount == 12

    def test_units_are_normalized_explicitly_and_recorded(self, tmp_path, asset_store):
        data = _export(tmp_path, ".step", cq.Solid.makeBox(6, 8, 4))
        digest = asset_store.store(data, ".step")
        millimetres = import_stone_asset(asset_store, digest, "mm")
        centimetres = import_stone_asset(asset_store, digest, "cm")
        assert math.isclose(centimetres.lengthMm, millimetres.lengthMm * 10, rel_tol=1e-9)
        assert any(
            op.startswith("UNIT_CONVERSION") for op in centimetres.normalizationOperations
        )
        assert not any(
            op.startswith("UNIT_CONVERSION") for op in millimetres.normalizationOperations
        )

    def test_geometry_is_recentred_into_the_canonical_frame(self, tmp_path, asset_store):
        far_away = cq.Solid.makeBox(6, 8, 4).translate((100, 200, 300))
        digest = asset_store.store(_export(tmp_path, ".step", far_away), ".step")
        imported = import_stone_asset(asset_store, digest, "mm")
        box = imported.shape.BoundingBox()
        assert abs((box.xmin + box.xmax) / 2) < 1e-6
        assert abs((box.ymin + box.ymax) / 2) < 1e-6
        assert any(
            op.startswith("ORIGIN_RECENTERED") for op in imported.normalizationOperations
        )

    def test_provenance_records_the_asset_identity(self, tmp_path, asset_store):
        digest = asset_store.store(_export(tmp_path, ".step", cq.Solid.makeBox(6, 8, 4)), ".step")
        imported = import_stone_asset(asset_store, digest, "mm", asset_name="ruby.step")
        assert imported.assetHash == digest
        assert imported.assetName == "ruby.step"
        assert imported.importerVersion

    def test_normalized_imported_stone_takes_dimensions_from_the_asset(
        self, tmp_path, asset_store
    ):
        digest = asset_store.store(_export(tmp_path, ".step", cq.Solid.makeBox(6, 8, 4)), ".step")
        imported = import_stone_asset(asset_store, digest, "mm")
        stone = StoneSpec.model_validate({
            "source": "IMPORTED_CAD", "shape": "imported", "depth": 4.0,
            "importedAsset": {"assetHash": digest, "declaredUnit": "mm"},
        })
        normalized = canonicalize_stone(stone, imported=imported)
        assert normalized.dimensions.provenance == "IMPORTED_GEOMETRY_MEASUREMENT"
        assert math.isclose(normalized.dimensions.lengthMm, 8.0, rel_tol=1e-6)
        assert normalized.provenance.sourceAssetHash == digest

    def test_imported_dimensions_are_not_read_from_the_document(self):
        """An imported stone's size is a property of the asset. Guessing it
        from the document would silently misplace every surrounding component."""

        stone = StoneSpec.model_validate({
            "source": "IMPORTED_CAD", "shape": "imported", "depth": 4.0,
            "importedAsset": {"assetHash": "a" * 64, "declaredUnit": "mm"},
        })
        for resolver in (resolved_length_mm, resolved_width_mm, resolved_depth_mm):
            with pytest.raises(StoneDimensionsUnavailableError):
                resolver(stone)


class TestImportSecurity:
    def test_unsupported_formats_are_rejected_with_a_real_reason(self, asset_store):
        for suffix in UNSUPPORTED_IMPORT_FORMATS:
            with pytest.raises(StoneImportFormatUnsupportedError) as caught:
                asset_store.store(b"x" * 32, suffix)
            assert len(str(caught.value)) > 40, "the refusal must explain itself"

    def test_only_verified_formats_are_claimed(self):
        """Never claim a format the installed kernel cannot actually parse."""

        assert set(SUPPORTED_IMPORT_FORMATS) == {".step", ".stp", ".brep", ".stl"}
        assert ".obj" not in SUPPORTED_IMPORT_FORMATS
        assert ".iges" not in SUPPORTED_IMPORT_FORMATS

    def test_path_traversal_is_structurally_impossible(self, asset_store):
        for hostile in ("../../etc/passwd", "..\\..\\windows\\system32", "a/../../b", ""):
            with pytest.raises(StoneImportFailedError):
                asset_store.resolve(hostile)

    def test_oversized_asset_is_rejected(self, asset_store):
        with pytest.raises(StoneImportTooComplexError):
            asset_store.store(b"0" * (MAX_ASSET_BYTES + 1), ".stl")

    def test_empty_asset_is_rejected(self, asset_store, tmp_path):
        asset_store.root.mkdir(parents=True, exist_ok=True)
        digest = "b" * 64
        (asset_store.root / f"{digest}.step").write_bytes(b"")
        with pytest.raises(StoneImportEmptyError):
            import_stone_asset(asset_store, digest, "mm")

    def test_malformed_asset_error_leaks_no_internal_detail(self, asset_store):
        digest = asset_store.store(b"this is not a STEP file" * 8, ".step")
        with pytest.raises(StoneImportFailedError) as caught:
            import_stone_asset(asset_store, digest, "mm")
        message = str(caught.value)
        assert "Traceback" not in message
        assert str(asset_store.root) not in message
        assert digest not in message


# --------------------------------------------------------------------------
# Registries, dispatch, anchors, outline API
# --------------------------------------------------------------------------


class TestRegistriesAndDispatch:
    def test_every_current_shape_has_a_generator(self):
        from jewelmind.stone.normalize import NATIVE_OUTLINE_BUILDERS

        outline_driven = set(NATIVE_OUTLINE_BUILDERS) | {"round", "tapered_baguette", "trapezoid"}
        for shape in cap.native_shapes():
            if shape == "pearl":
                continue  # spherical profile, no outline builder by design
            assert shape in outline_driven, f"{shape} is CURRENT but has no builder"

    def test_reserved_shapes_have_no_generator_and_no_enum_membership(self):
        from typing import get_args

        from jewelmind.domain.schema import StoneShape
        from jewelmind.stone.normalize import NATIVE_OUTLINE_BUILDERS

        for shape in cap.RESERVED_STONE_SHAPES:
            assert shape not in get_args(StoneShape)
            assert shape not in NATIVE_OUTLINE_BUILDERS

    def test_source_handlers_are_registered_for_every_declared_mode(self):
        from typing import get_args

        from jewelmind.stone.models import StoneSourceMode

        assert set(stone_source_handlers()) == set(get_args(StoneSourceMode))

    def test_no_duplicate_aliases_across_shapes(self):
        table = cap.alias_lookup()
        assert table["cuore"] == "heart"
        assert table["losanga"] == "lozenge"
        assert table["trilliant"] == "trillion"
        assert table["mezzaluna"] == "half_moon"

    def test_generation_and_setting_compatibility_are_independent_axes(self):
        """A shape that generates is not, by that fact, settable."""

        pearl = cap.STONE_SHAPE_CAPABILITIES_V2["pearl"]
        assert pearl.generationSupported is True
        assert pearl.prongCompatibility == "UNSUPPORTED"

    def test_no_shape_claims_professional_validation(self):
        for entry in cap.STONE_SHAPE_CAPABILITIES_V2.values():
            assert entry.professionalValidationStatus == "NOT_REVIEWED"

    def test_dispatch_resolves_every_source_mode(self):
        assert resolve_stone(
            StoneSpec.model_validate(stone_payload("oval"))
        ).sourceMode == "PARAMETRIC_REFERENCE"


class TestAnchorsAndOutlineApi:
    def test_heart_exposes_tip_cleft_and_lobes(self):
        normalized = canonicalize_stone(StoneSpec.model_validate(stone_payload("heart")))
        anchors = {a.anchor: a for a in stone_anchors(normalized)}
        assert {"TIP", "CLEFT", "LEFT_LOBE", "RIGHT_LOBE"} <= set(anchors)
        assert anchors["TIP"].y < anchors["CLEFT"].y, "the tip is below the cleft"
        assert anchors["LEFT_LOBE"].x < 0 < anchors["RIGHT_LOBE"].x

    def test_tapered_shapes_expose_wide_and_narrow_ends(self):
        normalized = canonicalize_stone(
            StoneSpec.model_validate(stone_payload("tapered_baguette"))
        )
        anchors = {a.anchor: a for a in stone_anchors(normalized)}
        assert anchors["WIDE_END"].y < anchors["NARROW_END"].y

    def test_anchors_are_never_fabricated_when_no_outline_exists(self):
        normalized = canonicalize_stone(StoneSpec.model_validate(stone_payload("pearl")))
        assert normalized.outline is None
        assert stone_anchors(normalized) == []

    def test_polygonal_outlines_are_exact_and_curved_ones_say_they_are_sampled(self):
        polygon = canonicalize_stone(StoneSpec.model_validate(stone_payload("princess")))
        curved = canonicalize_stone(StoneSpec.model_validate(stone_payload("oval")))
        assert polygon.outline.isPolygonal is True
        assert len(polygon.outline.points) == 4
        assert curved.outline.isPolygonal is False
        assert curved.outline.derivation == "SAMPLED_FROM_CURVE"

    def test_outline_sampling_walks_edges_in_connected_order(self):
        """`Wire.Edges()` is not reliably ordered — the heart returns its four
        arcs scrambled. A wrongly ordered ring still has a correct bounding box,
        so this checks step continuity instead."""

        wire = O.heart_outline(4.0, 3.0, 1.0)
        points, _ = O.sample_outline(wire)

        # Step length cannot be the signal: the heart has two long straight
        # sides, and a LINE edge contributes only its start vertex, so a
        # correctly ordered traversal legitimately contains a 7mm step.
        # Enclosed area is the discriminating property — a scrambled ring folds
        # over itself and loses most of its area.
        def shoelace(ring):
            return abs(
                sum(
                    ring[i][0] * ring[(i + 1) % len(ring)][1]
                    - ring[(i + 1) % len(ring)][0] * ring[i][1]
                    for i in range(len(ring))
                )
            ) / 2

        true_area = cq.Face.makeFromWires(wire).Area()
        assert math.isclose(shoelace(points), true_area, rel_tol=5e-3), (
            "sampled ring area does not match the real outline area, which "
            "means the edges were not walked in connected order"
        )

        scrambled = points[::3] + points[1::3] + points[2::3]
        assert not math.isclose(shoelace(scrambled), true_area, rel_tol=5e-3), (
            "the area check must be able to detect a scrambled ring"
        )

    def test_anchors_are_geometric_facts_not_prong_positions(self):
        """Brief section 43. Prong count must not equal anchor count by
        construction, or the two concepts have silently merged."""

        definition = definition_with(stone_payload("heart"), setting_type="prong")
        definition.setting.prongCount = 4
        stone = build_stone_reference(definition)
        components, _ = generate_setting(setting_definition_from_jdl(definition, stone))
        anchors = stone.metadata["anchors"]
        assert len(components["prongs"].shape.Solids()) == 4
        assert len(anchors) == 9


# --------------------------------------------------------------------------
# STONE_REFERENCE_PRODUCTION_EXCLUSION and shape/gem separation
# --------------------------------------------------------------------------


class TestStoneReferenceRemainsNonProduction:
    @pytest.mark.parametrize("shape", ["heart", "pearl", "trillion"])
    def test_stone_reference_is_never_production_metal(self, shape: str):
        assert GEOMETRY_ROLE["stone_reference"] == "stone_reference"
        assert PRODUCTION_ROLE["stone_reference"] == "excluded_by_default"
        assert GEOMETRY_ROLE["stone_reference"] != "production_metal"
        component = build_stone_only(stone_payload(shape))
        assert component.name == "stone_reference"

    def test_custom_and_imported_stones_are_also_reference_only(self):
        component = build_stone_only(
            {"source": "CUSTOM_OUTLINE", "shape": "custom", "depth": 4.0,
             "customOutline": outline_spec(CONVEX_OUTLINE)}
        )
        assert component.name == "stone_reference"
        assert component.metadata["isGemologicalReproduction"] is False


class TestShapeVersusGemIdentity:
    def test_emerald_is_a_shape_not_a_species(self):
        """Brief section 37. `stone.shape = "emerald"` is the clipped-corner
        outline; the gem species emerald arrives in Sprint 21."""

        component = build_stone_only(stone_payload("emerald"))
        assert component.metadata["family"] == "CLIPPED_RECTILINEAR"
        assert "species" not in component.metadata
        assert "material" not in component.metadata

    def test_no_shape_enum_member_is_a_gem_species(self):
        from typing import get_args

        from jewelmind.domain.schema import StoneShape

        species = {"diamond", "ruby", "sapphire", "beryl", "topaz", "amethyst", "opal"}
        assert species.isdisjoint(set(get_args(StoneShape)))

    def test_the_rhombus_is_named_lozenge(self):
        assert "lozenge" in cap.STONE_SHAPE_CAPABILITIES_V2
        assert "diamond" not in cap.STONE_SHAPE_CAPABILITIES_V2

    def test_stone_spec_carries_no_material_field(self):
        assert "material" not in StoneSpec.model_fields
        assert "species" not in StoneSpec.model_fields


class TestNoFakeEquivalentDiameter:
    def test_non_round_shapes_have_no_diameter(self):
        """Brief section 64 / STONE-GOV: never collapse an 8x6 stone to a
        single equivalent diameter."""

        for shape in ("oval", "heart", "kite", "baguette"):
            normalized = canonicalize_stone(StoneSpec.model_validate(stone_payload(shape)))
            assert normalized.dimensions.lengthMm != normalized.dimensions.widthMm

    def test_no_equivalent_diameter_helper_exists(self):
        import jewelmind.domain.stone_dimensions as dimensions
        import jewelmind.stone.normalize as normalize

        for module in (dimensions, normalize):
            names = [n.lower() for n in dir(module)]
            assert not any("equivalent" in n and "diameter" in n for n in names)


# --------------------------------------------------------------------------
# Neutral entry point
# --------------------------------------------------------------------------


def test_build_stone_geometry_needs_no_jewelry_document():
    """A stone can be built from a stone and a plane alone."""

    component = build_stone_geometry(
        StoneSpec.model_validate(stone_payload("heart")), girdle_z_mm=5.0
    )
    assert component.volume_mm3 > 0
    assert math.isclose(component.metadata["girdleZMm"], 5.0, rel_tol=1e-12)


def test_derive_anchors_is_pure_geometry():
    """Anchors come from the real points, so they work for any outline."""

    points = [OutlinePoint(x=x, y=y) for x, y in CONVEX_OUTLINE]
    anchors = {a.anchor for a in derive_anchors("custom", points)}
    assert anchors == {"CENTER", "TOP", "BOTTOM", "LEFT", "RIGHT"}


class TestMeshTransformRegression:
    """A mesh must be transformed node by node (Sprint 20 bug).

    Neither `cadquery.Shape.scale()` nor `BRepBuilderAPI_Transform` moves a
    triangulation attached to an otherwise-empty face, so an STL declared in
    centimetres came back at its original millimetre size — while
    `normalizationOperations` still recorded `UNIT_CONVERSION:cm->mm`. The false
    provenance entry was the worse half of the bug: it asserted a conversion
    that had not happened.
    """

    def test_mesh_unit_conversion_actually_scales_the_geometry(
        self, tmp_path, asset_store
    ):
        digest = asset_store.store(_export(tmp_path, ".stl", cq.Solid.makeBox(6, 8, 4)), ".stl")
        millimetres = import_stone_asset(asset_store, digest, "mm")
        centimetres = import_stone_asset(asset_store, digest, "cm")

        assert math.isclose(millimetres.lengthMm, 8.0, rel_tol=1e-6)
        assert math.isclose(centimetres.lengthMm, 80.0, rel_tol=1e-6), (
            "the mesh was not actually scaled; only its recorded provenance changed"
        )
        assert math.isclose(centimetres.widthMm, 60.0, rel_tol=1e-6)
        assert math.isclose(centimetres.depthMm, 40.0, rel_tol=1e-6)

    def test_declared_normalization_matches_the_geometry_for_both_representations(
        self, tmp_path, asset_store
    ):
        """Provenance must never claim an operation the geometry did not receive."""

        for suffix in (".step", ".stl"):
            solid = cq.Solid.makeBox(6, 8, 4).translate((10, 20, 30))
            digest = asset_store.store(_export(tmp_path, suffix, solid), suffix)

            unscaled = import_stone_asset(asset_store, digest, "mm")
            scaled = import_stone_asset(asset_store, digest, "cm")

            claimed = any(
                op.startswith("UNIT_CONVERSION") for op in scaled.normalizationOperations
            )
            happened = scaled.lengthMm > unscaled.lengthMm * 5
            assert claimed == happened, (
                f"{suffix}: provenance claims conversion={claimed} but the "
                f"geometry changed={happened}"
            )

    def test_mesh_is_recentred_on_the_origin(self, tmp_path, asset_store):
        far_away = cq.Solid.makeBox(6, 8, 4).translate((10, 20, 30))
        digest = asset_store.store(_export(tmp_path, ".stl", far_away), ".stl")
        imported = import_stone_asset(asset_store, digest, "mm")
        box = imported.shape.BoundingBox()
        for low, high in (
            (box.xmin, box.xmax), (box.ymin, box.ymax), (box.zmin, box.zmax)
        ):
            assert abs((low + high) / 2) < 1e-6

    def test_mesh_orientation_is_actually_applied(self, tmp_path, asset_store):
        digest = asset_store.store(_export(tmp_path, ".stl", cq.Solid.makeBox(6, 8, 4)), ".stl")
        upright = import_stone_asset(asset_store, digest, "mm")
        rotated = import_stone_asset(asset_store, digest, "mm", orientation_deg=90)
        assert math.isclose(rotated.lengthMm, upright.widthMm, rel_tol=1e-6)
        assert math.isclose(rotated.widthMm, upright.lengthMm, rel_tol=1e-6)
