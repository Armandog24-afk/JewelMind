"""API-level tests for POST /api/professional-validation/review-package."""

from __future__ import annotations

import io
import zipfile

import pytest
from fastapi.testclient import TestClient

from jewelmind.api.app import app
from jewelmind.domain.defaults import default_definition


@pytest.fixture()
def client():
    return TestClient(app)


def _generate(client) -> str:
    definition = default_definition().model_dump(mode="json")
    resp = client.post("/api/models/generate", json=definition)
    assert resp.status_code == 200
    return resp.json()["modelId"]


def test_review_package_returns_a_real_zip(client):
    model_id = _generate(client)
    resp = client.post(
        "/api/professional-validation/review-package",
        json={"modelId": model_id, "caseId": "JMCASE001"},
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/zip"
    assert resp.headers["content-disposition"].startswith("attachment")
    assert "x-content-sha256" in resp.headers
    assert "x-package-id" in resp.headers

    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        names = set(zf.namelist())
    assert {"README.md", "manifest.json", "model.step", "model.stl", "review-form.md"} <= names


def test_review_package_defaults_case_id_min_length(client):
    model_id = _generate(client)
    resp = client.post(
        "/api/professional-validation/review-package",
        json={"modelId": model_id, "caseId": ""},
    )
    assert resp.status_code == 422


def test_review_package_with_unknown_model_id_returns_404(client):
    resp = client.post(
        "/api/professional-validation/review-package",
        json={"modelId": "unknown", "caseId": "JMCASE001"},
    )
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "MODEL_NOT_FOUND"


def test_review_package_include_stone_reference_defaults_true(client):
    model_id = _generate(client)
    resp = client.post(
        "/api/professional-validation/review-package",
        json={"modelId": model_id, "caseId": "JMCASE001"},
    )
    assert resp.status_code == 200
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        readme = zf.read("README.md").decode("utf-8")
    assert "IS included" in readme


def test_review_package_can_exclude_stone_reference(client):
    model_id = _generate(client)
    resp = client.post(
        "/api/professional-validation/review-package",
        json={"modelId": model_id, "caseId": "JMCASE001", "includeStoneReference": False},
    )
    assert resp.status_code == 200
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        readme = zf.read("README.md").decode("utf-8")
    assert "NOT included" in readme
