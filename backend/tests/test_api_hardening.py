"""Hardening tests: health-check degradation, error-code mapping, export
temp-file uniqueness/cleanup, and specification timestamp stability.
"""

from __future__ import annotations

import glob
import os
import re
import tempfile

import pytest
from fastapi.testclient import TestClient

import jewelmind.api.routes as routes_module
import jewelmind.services.cad_engine as cad_engine_module
from jewelmind.api.app import app
from jewelmind.domain.defaults import default_definition
from jewelmind.services.model_service import model_service


@pytest.fixture()
def client():
    return TestClient(app)


def _generate(client) -> str:
    definition = default_definition().model_dump(mode="json")
    resp = client.post("/api/models/generate", json=definition)
    assert resp.status_code == 200
    return resp.json()["modelId"]


# -- health endpoint degradation ----------------------------------------------


def test_health_reports_503_when_cad_engine_not_ready(client, monkeypatch):
    monkeypatch.setattr(routes_module, "cad_engine_ready", lambda: False)
    monkeypatch.setattr(routes_module, "cad_engine_error", lambda: "simulated failure")
    resp = client.get("/api/health")
    assert resp.status_code == 503
    body = resp.json()
    assert body["cadEngineReady"] is False
    assert body["status"] == "degraded"
    assert body["cadEngineError"] == "simulated failure"


def test_health_reports_200_when_cad_engine_ready(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["cadEngineReady"] is True
    assert body["cadEngineError"] is None


def test_probe_cad_engine_succeeds_in_this_environment():
    ready, error = cad_engine_module.probe_cad_engine()
    assert ready is True
    assert error is None


def test_probe_cad_engine_reports_failure_without_raising(monkeypatch):
    import cadquery as cq

    def _boom(*args, **kwargs):
        raise RuntimeError("simulated OpenCascade failure")

    monkeypatch.setattr(cq, "Workplane", _boom)
    ready, error = cad_engine_module.probe_cad_engine()
    assert ready is False
    assert error is not None
    assert "simulated OpenCascade failure" in error


# -- error code mapping ---------------------------------------------------------


def test_generation_failure_maps_to_model_generation_failed(client, monkeypatch):
    def _boom(definition):
        raise RuntimeError("simulated geometry crash")

    # Sprint 16: geometry generation is dispatched by jewelry.category
    # through jewelmind.ring.families.RING_FAMILY_GENERATORS, a dict
    # built once at import time — patch the dict entry itself, not the
    # module-level function name, or the registered reference (captured
    # at import time) would not change (see
    # docs/bible/18-ring-architecture/532-ring-generation-contract.md).
    import jewelmind.ring.families as ring_families

    monkeypatch.setitem(ring_families.RING_FAMILY_GENERATORS, "solitaire", _boom)
    definition = default_definition().model_dump(mode="json")
    resp = client.post("/api/models/generate", json=definition)
    assert resp.status_code == 500
    body = resp.json()
    assert body["error"]["code"] == "MODEL_GENERATION_FAILED"
    assert "requestId" in body["error"]
    # no raw Python traceback leaked to the client
    assert "Traceback" not in resp.text


def test_step_export_failure_maps_to_step_export_failed(client, monkeypatch):
    model_id = _generate(client)

    def _boom(*args, **kwargs):
        raise RuntimeError("simulated STEP writer crash")

    monkeypatch.setattr("jewelmind.services.model_service.export_step", _boom)
    resp = client.post("/api/models/export/step", json={"modelId": model_id})
    assert resp.status_code == 500
    body = resp.json()
    assert body["error"]["code"] == "STEP_EXPORT_FAILED"
    assert "requestId" in body["error"]
    assert "Traceback" not in resp.text


def test_stl_export_failure_maps_to_stl_export_failed(client, monkeypatch):
    model_id = _generate(client)

    def _boom(*args, **kwargs):
        raise RuntimeError("simulated STL tessellation crash")

    monkeypatch.setattr("jewelmind.services.model_service.export_stl", _boom)
    resp = client.post("/api/models/export/stl", json={"modelId": model_id})
    assert resp.status_code == 500
    body = resp.json()
    assert body["error"]["code"] == "STL_EXPORT_FAILED"
    assert "Traceback" not in resp.text


def test_cad_engine_unavailable_returns_503(client, monkeypatch):
    monkeypatch.setattr(routes_module, "_model_service_instance", None)

    def _boom_import(name, *args, **kwargs):
        if name == "jewelmind.services.model_service":
            raise ImportError("simulated missing cadquery")
        return _real_import(name, *args, **kwargs)

    import builtins

    _real_import = builtins.__import__
    monkeypatch.setattr(builtins, "__import__", _boom_import)
    definition = default_definition().model_dump(mode="json")
    resp = client.post("/api/models/generate", json=definition)
    assert resp.status_code == 503
    assert resp.json()["error"]["code"] == "CAD_ENGINE_UNAVAILABLE"


# -- export temp-file uniqueness and cleanup ------------------------------------


def _matching_export_temp_files(model_id: str) -> list[str]:
    pattern = os.path.join(tempfile.gettempdir(), f"jewelmind_{model_id}_export_*")
    return glob.glob(pattern)


def test_step_and_stl_exports_use_distinct_unique_temp_files():
    definition = default_definition()
    record = model_service.generate(definition)

    path_a = model_service.export_step_file(record.model_id, include_stone=False)
    path_b = model_service.export_step_file(record.model_id, include_stone=True)
    assert path_a != path_b, "two export calls must not reuse the same temp file"
    path_a.unlink(missing_ok=True)
    path_b.unlink(missing_ok=True)


def test_export_temp_file_is_deleted_after_http_response(client):
    model_id = _generate(client)
    before = _matching_export_temp_files(model_id)

    resp = client.post("/api/models/export/step", json={"modelId": model_id})
    assert resp.status_code == 200
    assert len(resp.content) > 0

    after = _matching_export_temp_files(model_id)
    assert after == before, f"export temp file(s) were not cleaned up: {after}"


def test_export_temp_file_is_cleaned_up_on_failure(monkeypatch):
    definition = default_definition()
    record = model_service.generate(definition)

    def _boom(*args, **kwargs):
        raise RuntimeError("simulated failure mid-export")

    monkeypatch.setattr("jewelmind.services.model_service.export_step", _boom)
    with pytest.raises(RuntimeError):
        model_service.export_step_file(record.model_id, include_stone=False)

    leftover = _matching_export_temp_files(record.model_id)
    assert leftover == [], f"a failed export left temp files behind: {leftover}"


# -- STL tolerance validation ----------------------------------------------------


@pytest.mark.parametrize("bad_value", [0, -0.1, "not-a-number"])
def test_export_stl_rejects_invalid_mesh_tolerance(client, bad_value):
    model_id = _generate(client)
    resp = client.post(
        "/api/models/export/stl",
        json={"modelId": model_id, "meshTolerance": bad_value},
    )
    assert resp.status_code == 422


def test_export_stl_rejects_non_finite_mesh_tolerance(client):
    import json as jsonlib

    model_id = _generate(client)
    raw = jsonlib.dumps({"modelId": model_id, "meshTolerance": 0.1}).replace(
        '"meshTolerance": 0.1', '"meshTolerance": Infinity'
    )
    resp = client.post(
        "/api/models/export/stl",
        content=raw,
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code == 422


def test_export_stl_accepts_valid_tolerance_override(client):
    model_id = _generate(client)
    resp = client.post(
        "/api/models/export/stl",
        json={"modelId": model_id, "meshTolerance": 0.05, "angularTolerance": 0.1},
    )
    assert resp.status_code == 200
    assert len(resp.content) > 0


# -- specification timestamp stability -------------------------------------------


def test_specification_uses_original_generation_timestamp_not_download_time(client):
    definition = default_definition().model_dump(mode="json")
    gen_resp = client.post("/api/models/generate", json=definition)
    model_id = gen_resp.json()["modelId"]
    generated_at = gen_resp.json()["generatedAt"]

    spec_resp_1 = client.post("/api/models/specification", json={"modelId": model_id})
    spec_resp_2 = client.post("/api/models/specification", json={"modelId": model_id})

    assert spec_resp_1.status_code == 200
    assert spec_resp_2.status_code == 200
    text_1 = spec_resp_1.text
    text_2 = spec_resp_2.text

    match_1 = re.search(r"Generated at: (\S+)", text_1)
    match_2 = re.search(r"Generated at: (\S+)", text_2)
    assert match_1 and match_2
    assert match_1.group(1) == match_2.group(1) == generated_at
