"""The Stone Arrangement Engine is category- and kernel-neutral (Sprint 22).

AST INSPECTION, NOT `import`. A module already in `sys.modules` imports fine
regardless of what it depends on, so an import-based check can pass by accident;
parsing the source answers the question the rule actually asks. The same
discipline as `test_gem_no_category_dependency.py` (Sprint 21),
`test_stone_v2_no_category_dependency.py` (Sprint 20) and
`test_setting_system_no_ring_dependency.py` (Sprint 19) — each of which caught a
real violation an import test would have missed.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parents[1]
ARRANGEMENT_DIR = BACKEND / "jewelmind" / "arrangement"

#: Importing any of these would tie an arrangement — a category-neutral concept
#: a future earring or bracelet must reuse unchanged — to the ring domain or to
#: the CAD kernel.
#:
#: `jewelmind.geometry` is forbidden because an arrangement produces NUMBERS,
#: never solids: the moment this package could reach a geometry builder, the
#: declarative/construction boundary the sprint exists to establish would be
#: gone. `cadquery`/`OCP` for the same reason, one level lower.
FORBIDDEN_PREFIXES: tuple[str, ...] = (
    "jewelmind.ring",
    "jewelmind.jewelry_category",
    "jewelmind.geometry",
    "jewelmind.setting",
    "jewelmind.preview",
    "jewelmind.exporters",
    "jewelmind.services",
    "jewelmind.api",
    "jewelmind.validation",
    "jewelmind.designer",
    "jewelmind.conversation",
    "cadquery",
    "OCP",
)

#: `jewelmind.domain.schema` is forbidden for the specific reason Sprint 19 and
#: 21 both documented: importing `JewelryDefinition` smuggles the entire ring
#: domain across in one import. The dependency runs the other way —
#: `domain/schema.py` imports `arrangement.models`.
FORBIDDEN_PREFIXES = FORBIDDEN_PREFIXES + ("jewelmind.domain.schema",)

ARRANGEMENT_FILES = sorted(ARRANGEMENT_DIR.glob("*.py"))


def _imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            # A relative import can only reach inside `jewelmind.arrangement`
            # itself and therefore cannot violate the rule.
            if node.level == 0 and node.module:
                found.add(node.module)
    return found


def test_arrangement_package_is_not_empty():
    """Guards the guard: a passing scan over zero files proves nothing."""

    assert len(ARRANGEMENT_FILES) >= 6, [p.name for p in ARRANGEMENT_FILES]


@pytest.mark.parametrize("path", ARRANGEMENT_FILES, ids=lambda p: p.name)
def test_arrangement_module_imports_no_category_or_kernel(path: Path):
    violations = sorted(
        module
        for module in _imported_modules(path)
        if any(
            module == prefix or module.startswith(prefix + ".")
            for prefix in FORBIDDEN_PREFIXES
        )
    )
    assert not violations, f"{path.name} imports forbidden module(s): {violations}"


def test_arrangement_package_init_imports_nothing():
    """`jewelmind/arrangement/__init__.py` is load-bearing empty.

    `domain/schema.py` imports `jewelmind.arrangement.models` for the
    `arrangement` field's type. If this package's init pulled in a submodule
    that itself reached `domain.schema`, the graph would become cyclic at
    package-init time — the same trap `jewelmind/stone/__init__.py` and
    `jewelmind/gem/__init__.py` already document.
    """

    assert _imported_modules(ARRANGEMENT_DIR / "__init__.py") == set()


def test_no_arrangement_module_constructs_geometry():
    """No CAD construction verbs anywhere in the package.

    Scans for the kernel method names an accidental geometry call would use.
    An arrangement decides WHERE; Atlas decides what solid goes there.
    """

    construction_calls = {
        "fuse",
        "cut",
        "revolve",
        "loft",
        "extrude",
        "fillet",
        "shell",
        "translate",
        "makeCompound",
        "toCompound",
        "Workplane",
    }
    offenders: list[str] = []
    for path in ARRANGEMENT_FILES:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and node.attr in construction_calls:
                offenders.append(f"{path.name}: .{node.attr}")
            if isinstance(node, ast.Name) and node.id in construction_calls:
                offenders.append(f"{path.name}: {node.id}")
    assert not offenders, offenders


def test_no_arrangement_module_invents_a_jewelry_threshold():
    """No professional or manufacturing threshold hides in this package.

    The bounds that DO exist (`MAX_INSTANCES`, `MAX_COORDINATE_MM`,
    `COORDINATE_DECIMALS`) are software limits, and each says so in its own
    comment. What must never appear is a minimum spacing, a clearance, a
    proportion rule or a stone-count limit presented as jewelry knowledge —
    those need sourced professional evidence this project does not have.
    """

    forbidden_names = {
        "MIN_SPACING_MM",
        "MIN_CLEARANCE_MM",
        "MIN_STONE_GAP_MM",
        "MAX_PAVE_DENSITY",
        "MIN_ACCENT_RATIO",
        "RECOMMENDED_SPACING_MM",
    }
    offenders: list[str] = []
    for path in ARRANGEMENT_FILES:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id in forbidden_names:
                offenders.append(f"{path.name}: {node.id}")
    assert not offenders, offenders
