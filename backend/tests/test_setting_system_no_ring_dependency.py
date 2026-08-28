"""SETTING_SYSTEM_NO_RING_DEPENDENCY_TEST (brief section 48; SETTING-GOV-001/014).

The Setting System is category-neutral: Ring may depend on Setting, Setting
may never depend on Ring. Enforced by AST-parsing every production module
under `jewelmind/setting/` rather than importing it — an import-based check
can pass by accident when the module is already cached from an earlier test
in the same session.

The forbidden surface is deliberately broader than one package name: it
covers `jewelmind.ring` (RingDefinition, RingSizing, RingFamily), the
Shank subsystem, and `jewelmind.jewelry_category`, since a Setting must not
know which jewelry category incorporates it.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[1] / "jewelmind"
SETTING_ROOT = BACKEND_ROOT / "setting"

SETTING_SYSTEM_FILES = sorted(SETTING_ROOT.glob("*.py"))

#: Module prefixes a category-neutral Setting must never import.
FORBIDDEN_PREFIXES = (
    "jewelmind.ring",
    "jewelmind.jewelry_category",
    "jewelmind.geometry.shank",
    "jewelmind.geometry.connection",
    "jewelmind.geometry.setting_adapter",
)


def _imported_module_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


@pytest.mark.parametrize("path", SETTING_SYSTEM_FILES, ids=lambda p: p.name)
def test_setting_system_file_never_imports_ring_or_category(path: Path):
    imported = _imported_module_names(path)
    violations = {
        name
        for name in imported
        for prefix in FORBIDDEN_PREFIXES
        if name == prefix or name.startswith(prefix + ".")
    }
    assert not violations, f"{path.name} imports Ring/category-owned modules: {sorted(violations)}"


def test_at_least_the_expected_setting_modules_were_checked():
    """Guards against the glob silently matching nothing, which would make
    every test above vacuously pass."""

    names = {p.name for p in SETTING_SYSTEM_FILES}
    expected = {
        "__init__.py",
        "errors.py",
        "models.py",
        "capability.py",
        "stone_interface.py",
        "placement.py",
        "prong.py",
        "bezel.py",
        "dispatch.py",
    }
    assert expected <= names, f"missing expected Setting modules: {sorted(expected - names)}"


def test_setting_system_does_not_import_jewelry_definition():
    """`JewelryDefinition` carries `ring`, `band`, and `setting` blocks, so
    importing it into the Setting core would smuggle the whole ring domain
    across the boundary. The adapter (`geometry/setting_adapter.py`) is the
    sanctioned translation point and lives outside `jewelmind/setting/`."""

    for path in SETTING_SYSTEM_FILES:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "jewelmind.domain.schema":
                imported = {alias.name for alias in node.names}
                assert "JewelryDefinition" not in imported, (
                    f"{path.name} imports JewelryDefinition; use the "
                    "StoneSettingReference/SettingAttachmentInterface contracts instead."
                )


def test_ring_side_adapter_is_allowed_to_depend_on_setting():
    """The reverse direction is real and expected — documents the arrow in
    both directions so the boundary is unambiguous."""

    adapter = BACKEND_ROOT / "geometry" / "setting_adapter.py"
    imported = _imported_module_names(adapter)
    assert any(name.startswith("jewelmind.setting") for name in imported)
    assert "jewelmind.domain.schema" in imported


def test_setting_system_may_depend_on_stone_contracts():
    """Setting is explicitly permitted to consume Stone System contracts
    (brief section 2), so this dependency must exist rather than be avoided."""

    imported = _imported_module_names(SETTING_ROOT / "stone_interface.py")
    assert "jewelmind.domain.stone_dimensions" in imported
    assert any(name.startswith("jewelmind.geometry.stone") for name in imported)
