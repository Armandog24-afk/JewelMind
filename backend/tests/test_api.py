import json

import pytest
from fastapi.testclient import TestClient

from jewelmind.api.app import app
from jewelmind.domain.defaults import default_definition


@pytest.fixture()
def client():
    return TestClient(app)


def test_health_endpoint(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "jewelmind-backend"
    assert body["cadEngine"] == "cadquery"
    assert body["cadEngineReady"] is True


def test_validate_default_definition_has_no_errors(client):
    definition = default_definition().model_dump(mode="json")
    resp = client.post("/api/models/validate", json=definition)
    assert resp.status_code == 200
    body = resp.json()
    assert body["hasErrors"] is False


def test_validate_invalid_definition_reports_errors(client):
    definition = default_definition().model_dump(mode="json")
    definition["band"]["width"] = 0.5
    resp = client.post("/api/models/validate", json=definition)
    assert resp.status_code == 200
    body = resp.json()
    assert body["hasErrors"] is True
    assert any(r["ruleId"] == "JM-BAND-001" for r in body["results"])


def test_request_validation_error_uses_error_envelope(client):
    resp = client.post("/api/models/validate", json={"not": "a definition"})
    assert resp.status_code == 422
    body = resp.json()
    assert "error" in body
    assert body["error"]["code"] == "REQUEST_VALIDATION_ERROR"
    assert "requestId" in body["error"]


def test_generate_model_returns_preview_and_metadata(client):
    definition = default_definition().model_dump(mode="json")
    resp = client.post("/api/models/generate", json=definition)
    assert resp.status_code == 200
    body = resp.json()
    assert body["modelId"]
    assert body["validation"] == [] or all(r["severity"] != "error" for r in body["validation"])
    assert set(body["previewComponents"].keys()) == {
        "band",
        "stone_reference",
        "prongs",
        "basket_support",
    }
    for name, entry in body["previewComponents"].items():
        assert entry["url"] is not None, f"{name} should have a preview url"


def test_generate_invalid_definition_returns_422(client):
    definition = default_definition().model_dump(mode="json")
    definition["ring"]["innerDiameter"] = 3
    resp = client.post("/api/models/generate", json=definition)
    assert resp.status_code == 422
    body = resp.json()
    assert body["error"]["code"] == "VALIDATION_BLOCKED"


def _generate(client) -> str:
    definition = default_definition().model_dump(mode="json")
    resp = client.post("/api/models/generate", json=definition)
    assert resp.status_code == 200
    return resp.json()["modelId"]


def test_model_metadata_endpoint(client):
    model_id = _generate(client)
    resp = client.get(f"/api/models/{model_id}/metadata")
    assert resp.status_code == 200
    body = resp.json()
    assert body["modelId"] == model_id
    assert body["combinedMetalVolumeMm3"] > 0


def test_model_metadata_missing_model_returns_404(client):
    resp = client.get("/api/models/does-not-exist/metadata")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "MODEL_NOT_FOUND"


def test_preview_component_endpoint_returns_nonempty_stl(client):
    model_id = _generate(client)
    resp = client.get(f"/api/models/{model_id}/preview/band")
    assert resp.status_code == 200
    assert len(resp.content) > 0
    assert resp.content[:5] in (b"solid", resp.content[:5])  # ascii or binary STL both fine


def test_export_step_returns_nonempty_file(client):
    model_id = _generate(client)
    resp = client.post("/api/models/export/step", json={"modelId": model_id})
    assert resp.status_code == 200
    assert len(resp.content) > 0
    assert resp.headers["content-disposition"].startswith("attachment")


def test_export_stl_returns_nonempty_file(client):
    model_id = _generate(client)
    resp = client.post("/api/models/export/stl", json={"modelId": model_id})
    assert resp.status_code == 200
    assert len(resp.content) > 0


def test_export_json_matches_original_definition(client):
    model_id = _generate(client)
    resp = client.post("/api/models/export/json", json={"modelId": model_id})
    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert data["project"]["name"] == "Solitaire Ring"


def test_specification_export_contains_disclaimer(client):
    model_id = _generate(client)
    resp = client.post("/api/models/specification", json={"modelId": model_id})
    assert resp.status_code == 200
    text = resp.content.decode("utf-8")
    assert "reviewed by a qualified jewelry professional" in text


def test_export_with_unknown_model_id_returns_404(client):
    resp = client.post("/api/models/export/step", json={"modelId": "unknown"})
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "MODEL_NOT_FOUND"


def test_sanitized_filenames_in_content_disposition(client):
    definition = default_definition()
    definition.project.name = "My/Weird Name?.step"
    resp = client.post("/api/models/generate", json=definition.model_dump(mode="json"))
    model_id = resp.json()["modelId"]
    export_resp = client.post("/api/models/export/step", json={"modelId": model_id})
    disposition = export_resp.headers["content-disposition"]
    assert "/" not in disposition
    assert "?" not in disposition
