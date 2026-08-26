"""Loads the real Golden Suite manifest and per-case fixtures from
`goldens/` — never hand-invented, always read from disk (QUALITY-GOV-002).
"""

from __future__ import annotations

import json
from pathlib import Path

from jewelmind.domain.schema import JewelryDefinition
from jewelmind.geometry_quality.models import GoldenModel

GOLDENS_ROOT = Path(__file__).resolve().parents[3] / "goldens"


def suite_dir(suite_id: str = "solitaire-v1") -> Path:
    return GOLDENS_ROOT / suite_id


def load_manifest(suite_id: str = "solitaire-v1") -> dict:
    path = suite_dir(suite_id) / "manifest.json"
    return json.loads(path.read_text(encoding="utf-8"))


def list_golden_ids(suite_id: str = "solitaire-v1") -> list[str]:
    return [case["goldenId"] for case in load_manifest(suite_id)["goldenIds"]]


def load_design(golden_id: str, suite_id: str = "solitaire-v1") -> JewelryDefinition:
    path = suite_dir(suite_id) / golden_id / "design.json"
    return JewelryDefinition.model_validate_json(path.read_text(encoding="utf-8"))


def load_golden(golden_id: str, suite_id: str = "solitaire-v1") -> GoldenModel:
    path = suite_dir(suite_id) / golden_id / "snapshot.json"
    return GoldenModel.model_validate_json(path.read_text(encoding="utf-8"))


def save_golden(golden: GoldenModel, suite_id: str = "solitaire-v1") -> Path:
    """Writes a GoldenModel to disk. Never called from CI or an automated
    regression run — only from the explicit accept-candidate CLI workflow
    (QUALITY-GOV-003/004)."""

    path = suite_dir(suite_id) / golden.goldenId / "snapshot.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(golden.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return path


def candidate_path(golden_id: str, suite_id: str = "solitaire-v1") -> Path:
    return suite_dir(suite_id) / golden_id / "candidate.json"


def save_candidate(candidate: GoldenModel, suite_id: str = "solitaire-v1") -> Path:
    path = candidate_path(candidate.goldenId, suite_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(candidate.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return path


def load_candidate(golden_id: str, suite_id: str = "solitaire-v1") -> GoldenModel:
    path = candidate_path(golden_id, suite_id)
    return GoldenModel.model_validate_json(path.read_text(encoding="utf-8"))
