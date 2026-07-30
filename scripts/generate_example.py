"""Generate a solitaire ring directly from an example JSON definition,
without going through the HTTP API. Useful as a quick offline smoke test of
the geometry pipeline.

Usage (from the repository root, with the backend virtualenv active):

    python scripts/generate_example.py examples/solitaire-default.json examples/output

Writes model.step, model.stl, and specification.md into the output
directory. Run `python -m pip install -e backend` or add backend/ to
PYTHONPATH first if `jewelmind` cannot be imported directly.
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "backend"))

from jewelmind.domain.schema import JewelryDefinition  # noqa: E402
from jewelmind.exporters.specification import build_specification  # noqa: E402
from jewelmind.exporters.step_exporter import export_step  # noqa: E402
from jewelmind.exporters.stl_exporter import export_stl  # noqa: E402
from jewelmind.geometry.assemblies.solitaire import build_solitaire_ring  # noqa: E402
from jewelmind.validation.engine import has_errors, validate_definition  # noqa: E402


def main() -> None:
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <definition.json> <output-dir>", file=sys.stderr)
        raise SystemExit(1)

    definition_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    output_dir.mkdir(parents=True, exist_ok=True)

    raw = json.loads(definition_path.read_text(encoding="utf-8"))
    definition = JewelryDefinition.model_validate(raw)

    results = validate_definition(definition)
    for result in results:
        print(f"[{result.severity.upper()}] {result.ruleId}: {result.message}")

    if has_errors(results):
        print("Definition has validation errors; not generating.", file=sys.stderr)
        raise SystemExit(1)

    model = build_solitaire_ring(definition)
    generated_at = datetime.now(UTC).isoformat()
    print(f"Generated model {model.definition_hash} in {model.generation_duration_s:.3f}s")
    for warning in model.warnings:
        print(f"[WARNING] {warning}")

    export_step(model, output_dir / "model.step")
    export_stl(model, definition, output_dir / "model.stl")
    (output_dir / "specification.md").write_text(
        build_specification(definition, model, results, generated_at=generated_at),
        encoding="utf-8",
    )

    print(f"Wrote model.step, model.stl, specification.md to {output_dir}")


if __name__ == "__main__":
    main()
