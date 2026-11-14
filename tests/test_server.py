"""Unit tests for CodeGraphy Lite FastAPI server & REST API."""

import tempfile
from pathlib import Path
from fastapi.testclient import TestClient

from codegraphy_lite.models import GraphState, NodeData, Position, ReactFlowNode, WorkspaceModel
from codegraphy_lite.server import app
from codegraphy_lite.storage import set_active_root


client = TestClient(app)


def test_health_check():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["edition"] == "lite"
    assert data["open_source"] is True
    assert data["max_scan_files"] == 35


def test_workspace_root_path():
    with tempfile.TemporaryDirectory() as tmpdir:
        res = client.post("/api/workspace/root-path", json={"root_path": tmpdir})
        assert res.status_code == 200
        assert res.json()["status"] == "ok"

        res_get = client.get("/api/workspace/root-path")
        assert res_get.status_code == 200
        assert Path(res_get.json()["root_path"]).resolve() == Path(tmpdir).resolve()


def test_graph_endpoints():
    with tempfile.TemporaryDirectory() as tmpdir:
        set_active_root(tmpdir)
        graph = GraphState(
            nodes=[
                ReactFlowNode(
                    id="topic_1",
                    position=Position(x=10, y=20),
                    data=NodeData(id="topic_1", label="Topic 1", description="Test"),
                )
            ],
            edges=[],
        )
        res_save = client.post("/api/graph", json=graph.model_dump())
        assert res_save.status_code == 200
        assert res_save.json()["nodes_count"] == 1

        res_get = client.get("/api/graph")
        assert res_get.status_code == 200
        data = res_get.json()
        assert len(data["nodes"]) == 1
        assert data["nodes"][0]["data"]["label"] == "Topic 1"


def test_workspace_endpoints():
    with tempfile.TemporaryDirectory() as tmpdir:
        set_active_root(tmpdir)
        ws = WorkspaceModel(name="Custom Project")
        res_save = client.post("/api/workspace", json=ws.model_dump())
        assert res_save.status_code == 200

        res_get = client.get("/api/workspace")
        assert res_get.status_code == 200
        assert res_get.json()["name"] == "Custom Project"


def test_export_and_import_md():
    with tempfile.TemporaryDirectory() as tmpdir:
        set_active_root(tmpdir)
        res_exp = client.get("/api/workspace/export-md")
        assert res_exp.status_code == 200
        assert "format: codegraphy-workspace" in res_exp.text

        sample_md = """---
format: codegraphy-workspace
version: 2.0
name: Imported Workspace
---

# Workspace: Imported Workspace

## Topics
### Topic: API Gateway `api_gw`
- status: `todo`

## Dependencies
- `api_gw` -> `auth_service`
"""
        res_imp = client.post("/api/workspace/import-md", json={"markdown": sample_md})
        assert res_imp.status_code == 200
        assert res_imp.json()["topics_count"] >= 1


def test_pro_features_interception():
    # Verify that Pro feature routes return 402 with pro_feature: true
    for route in ["/api/git/diff", "/api/context/compile", "/api/tests/impact", "/api/linter/analyze"]:
        if route in ["/api/context/compile", "/api/linter/analyze"]:
            res = client.post(route, json={})
        else:
            res = client.get(route)
        assert res.status_code == 402
        body = res.json()
        assert body.get("pro_feature") is True
        assert "CodeGraphy Pro" in body.get("detail", "")
        assert "upgrade_url" in body


def test_serve_root_ui():
    res = client.get("/")
    assert res.status_code == 200
    assert "CodeGraphy" in res.text
