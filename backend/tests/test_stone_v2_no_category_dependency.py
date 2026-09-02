"""STONE_V2_NO_CATEGORY_DEPENDENCY (brief section 71; STONEV2-GOV-001).

The Stone System is shared jewelry infrastructure. A ring may position a stone,
a setting may grip one, Vision may render one — none of them owns it, and the
Stone System must know about none of them.

WHY AST PARSING RATHER THAN `import`: importing a module and inspecting
`sys.modules` can pass by accident when another test already imported the
forbidden module, and it cannot see an import that sits inside a function body.
Parsing the source proves the dependency is absent from the code itself. This
mirrors `test_setting_system_no_ring_dependency.py` and
`test_stone_system_no_ring_dependency.py`, which caught real violations in
Sprints 18 and 19.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

STONE_PACKAGE = Path(__file__).resolve().parents[1] / "jewelmind" / "stone"
STONE_GEOMETRY = Path(__file__).resolve().parents[1] / "jewelmind" / "geometry" / "stone"
STONE_DIMENSIONS = (
    Path(__file__).resolve().parents[1] / "jewelmind" / "domain" / "stone_dimensions.py"
)

#: Jewelry categories the Stone System must never depend on. `jewelry_category`
#: is included because importing the category registry would couple Stone to
#: whichever categories happen to exist.
FORBIDDEN_MODULE_PREFIXES = (
    "jewelmind.ring",
    "jewelmind.earring",
    "jewelmind.pendant",
    "jewelmind.bracelet",
    "jewelmind.necklace",
    "jewelmind.jewelry_category",
)

#: Symbols that would drag a whole category domain across in one import.
#: `JewelryDefinition` is the entire ring document; a stone module that reads it
#: has stopped being category-neutral even if it never names a category.
FORBIDDEN_SYMBOLS = ("JewelryDefinition",)


def _stone_modules() -> list[Path]:
    modules = sorted(STONE_PACKAGE.glob("*.py"))
    modules += sorted(STONE_GEOMETRY.glob("*.py"))
    modules.append(STONE_DIMENSIONS)
    return [m for m in modules if m.name != "__pycache__"]


def _imports(path: Path) -> list[tuple[str, str | None]]:
    """Every `(module, symbol)` pair imported anywhere in the file.

    Walks the whole tree, so an import nested inside a function or an
    `if TYPE_CHECKING:` block is found too.
    """

    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: list[tuple[str, str | None]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.append((alias.name, None))
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                found.append((module, alias.name))
    return found


def test_the_module_list_is_not_empty():
    """A guard whose subject list is empty passes vacuously."""

    modules = _stone_modules()
    assert len(modules) >= 10, f"expected the Stone System's modules, found {modules}"


@pytest.mark.parametrize("path", _stone_modules(), ids=lambda p: p.name)
def test_stone_module_does_not_import_a_jewelry_category(path: Path):
    for module, symbol in _imports(path):
        for forbidden in FORBIDDEN_MODULE_PREFIXES:
            assert not module.startswith(forbidden), (
                f"{path.name} imports {module!r} (symbol {symbol!r}). The Stone "
                "System is category-neutral: categories depend on Stone, never "
                "the reverse."
            )


@pytest.mark.parametrize(
    "path", sorted(STONE_PACKAGE.glob("*.py")), ids=lambda p: p.name
)
def test_stone_core_module_does_not_import_the_full_jewelry_definition(path: Path):
    """The CORE must take `StoneSpec`, never the whole jewelry document.

    Scoped to `jewelmind/stone/` deliberately. `geometry/stone/builder.py` is
    the Atlas-layer PLACEMENT adapter: it reads `band_top_z()` and the setting's
    basket height to decide where the girdle plane sits, which is inherently a
    fact about the piece being built rather than about the stone. That is the
    same division Sprint 19 drew for Setting, where `geometry/setting_adapter.py`
    is the sanctioned translation point living outside the neutral package.

    The neutrality claim is kept honest by
    `test_stone_geometry_has_a_category_neutral_entry_point` below: the real
    geometry entry point takes a stone and a plane, so nothing about ring
    assembly is baked into stone construction.
    """

    for module, symbol in _imports(path):
        if symbol in FORBIDDEN_SYMBOLS:
            pytest.fail(
                f"jewelmind/stone/{path.name} imports {symbol!r} from {module!r}. "
                "That is an entire jewelry document; the Stone System core must "
                "take only StoneSpec and its own contracts."
            )


def test_stone_geometry_has_a_category_neutral_entry_point():
    """Stone construction must be expressible without a jewelry document.

    `build_stone_geometry(stone, girdle_z_mm)` is that entry point. Before
    Sprint 20 the only way to build a stone was to hand the builder an entire
    `JewelryDefinition`, which meant no other category — and no test — could
    construct a stone without fabricating a ring around it.
    """

    import inspect

    from jewelmind.geometry.stone.builder import build_stone_geometry

    parameters = list(inspect.signature(build_stone_geometry).parameters)
    assert parameters[:2] == ["stone", "girdle_z_mm"], parameters

    annotations = inspect.get_annotations(build_stone_geometry)
    assert "JewelryDefinition" not in str(annotations.get("stone", "")), (
        "the neutral entry point must accept a StoneSpec, not a jewelry document"
    )


def test_the_reverse_dependency_is_real():
    """Stone being category-neutral is only meaningful if something consumes it.

    Without this, deleting every consumer would make the guard above pass while
    the architecture became meaningless.
    """

    adapter = (
        Path(__file__).resolve().parents[1]
        / "jewelmind" / "geometry" / "setting_adapter.py"
    )
    builder = STONE_GEOMETRY / "builder.py"
    consumers = [m for m, _ in _imports(builder)] + [m for m, _ in _imports(adapter)]
    assert any(m.startswith("jewelmind.stone") for m in consumers), (
        "no consumer imports the Stone System, so its neutrality proves nothing"
    )


def test_stone_package_init_is_non_eager():
    """A non-eager `__init__` is load-bearing, not stylistic.

    `domain/schema.py` imports `jewelmind.stone.models`, while
    `jewelmind.stone.normalize` imports `domain/schema.py`. That is only
    acyclic because importing the package itself pulls in nothing. Sprint 18
    hit exactly this cycle and fixed it the same way.
    """

    init = STONE_PACKAGE / "__init__.py"
    imports = _imports(init)
    assert imports == [], (
        f"jewelmind/stone/__init__.py must import nothing, found {imports}. "
        "Re-exporting a submodule here reintroduces a circular import with "
        "domain/schema.py."
    )
