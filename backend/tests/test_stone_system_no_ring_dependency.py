"""STONE_SYSTEM_NO_RING_DEPENDENCY_TEST (brief section 64) — a static,
import-time-independent guarantee that the Stone System never imports
`jewelmind.ring` (STONE-GOV-001). Ring may depend on Stone; Stone must
never depend on Ring. Uses AST parsing rather than `import` so this stays
true regardless of what has already been imported elsewhere in the test
session (an `import`-based check could pass by accident if the module
were already cached)."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "backend" / "jewelmind"

STONE_SYSTEM_FILES = [
    *sorted((BACKEND_ROOT / "geometry" / "stone").glob("*.py")),
    BACKEND_ROOT / "domain" / "stone_dimensions.py",
]


def _imported_module_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


@pytest.mark.parametrize("path", STONE_SYSTEM_FILES, ids=lambda p: p.name)
def test_stone_system_file_never_imports_ring(path: Path):
    imported = _imported_module_names(path)
    ring_imports = {
        name for name in imported if name == "jewelmind.ring" or name.startswith("jewelmind.ring.")
    }
    assert not ring_imports, f"{path.name} imports jewelmind.ring: {ring_imports}"


def test_at_least_one_stone_system_file_was_actually_checked():
    # A structural guard against this test module silently checking zero
    # files (e.g. a glob pattern that stopped matching anything).
    assert len(STONE_SYSTEM_FILES) >= 5


def test_ring_is_allowed_to_depend_on_stone():
    # The reverse direction is real and expected — `ring/models.py`'s
    # `StoneArrangementDefinition` wraps `StoneSpec` directly.
    imported = _imported_module_names(BACKEND_ROOT / "ring" / "models.py")
    assert any(name.startswith("jewelmind.domain") for name in imported)
