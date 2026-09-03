"""GEM-GOV-001: the Gem System is category-neutral, proved structurally.

AST INSPECTION, NOT `import`. An import-based check can pass by accident — a
module already in `sys.modules` imports fine regardless of what it depends on,
and a cycle that only bites on a cold start would go unnoticed. Parsing the
source answers the question the rule actually asks: does this file *name* a
forbidden dependency, whatever the runtime happens to have cached.

The same discipline as `test_stone_v2_no_category_dependency.py` (Sprint 20) and
`test_setting_system_no_ring_dependency.py` (Sprint 19), for the same reason:
both caught real violations that an import test would have missed.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

GEM_DIR = Path(__file__).resolve().parents[1] / "jewelmind" / "gem"

#: Importing any of these into gem core would make a gem-material concept
#: depend on a jewelry category — the coupling this sprint exists to avoid.
#:
#: `jewelmind.domain.schema` is included for a specific reason: importing
#: `JewelryDefinition` would smuggle the entire ring domain across in one
#: import, exactly as it would have for the Setting System. The dependency runs
#: the other way — `domain/schema.py` imports `jewelmind.gem.models`.
FORBIDDEN_PREFIXES: tuple[str, ...] = (
    "jewelmind.ring",
    "jewelmind.jewelry_category",
    "jewelmind.geometry",
    "jewelmind.setting",
    "jewelmind.domain.schema",
    "jewelmind.validation",
    "jewelmind.designer",
    "jewelmind.conversation",
    "jewelmind.api",
    "jewelmind.services",
    "jewelmind.exporters",
    "cadquery",
    "OCP",
)

GEM_FILES = sorted(GEM_DIR.glob("*.py"))


def _imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            # `level > 0` is a relative import, which can only reach inside
            # `jewelmind.gem` itself and therefore cannot violate the rule.
            if node.level == 0 and node.module:
                found.add(node.module)
    return found


def test_gem_package_is_not_empty():
    """Guards the guard: a passing scan over zero files proves nothing."""

    assert len(GEM_FILES) >= 5, [p.name for p in GEM_FILES]


@pytest.mark.parametrize("path", GEM_FILES, ids=lambda p: p.name)
def test_gem_module_imports_no_category_or_kernel(path: Path):
    violations = sorted(
        module
        for module in _imported_modules(path)
        if any(
            module == prefix or module.startswith(prefix + ".")
            for prefix in FORBIDDEN_PREFIXES
        )
    )
    assert not violations, f"{path.name} imports forbidden module(s): {violations}"


def test_gem_package_init_imports_nothing():
    """`jewelmind/gem/__init__.py` is load-bearing empty.

    `domain/schema.py` imports `jewelmind.gem.models` for its vocabularies. If
    the package init pulled in a submodule that itself imports `domain.schema`,
    the graph would become cyclic at package-init time. The same trap
    `jewelmind/stone/__init__.py` documents (Sprint 20).
    """

    assert _imported_modules(GEM_DIR / "__init__.py") == set()


def test_no_gem_module_reads_a_geometry_field():
    """Gem identity never depends on the stone's geometry.

    A round stone is not a diamond, and a red stone is not a ruby. Naming a
    geometry field here would be the first step toward inferring one from the
    other, so the source is scanned for those attribute names directly.
    """

    geometry_attributes = {
        "diameter",
        "girdleZMm",
        "girdle_z_mm",
        "outline",
        "customOutline",
        "shape",
        "profile",
    }
    offenders: list[str] = []
    for path in GEM_FILES:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and node.attr in geometry_attributes:
                offenders.append(f"{path.name}: .{node.attr}")
    assert not offenders, offenders
