"""Unit tests for CodeGraphy Lite MCP STDIO server."""

import json
import tempfile
from pathlib import Path

from codegraphy_lite.mcp import CodeGraphyLiteMCP, scrub_secrets
from codegraphy_lite.models import EdgeData, FileReference, GraphState, NodeData, Position, ReactFlowNode
from codegraphy_lite.storage import save_graph


def test_scrub_secrets():
    raw = "Stripe key is sk_test_1234567890abcdef123 and OpenAI sk-proj-1234567890abcdef123"
    scrubbed = scrub_secrets(raw)
    assert "[REDACTED_SECRET]" in scrubbed
    assert "sk_test_1234567890abcdef123" not in scrubbed


def test_mcp_initialize():
    server = CodeGraphyLiteMCP()
    req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {},
    }
    res = server.dispatch(req)
    assert res is not None
    assert res["id"] == 1
    assert res["result"]["serverInfo"]["name"] == "codegraphy-lite-mcp"
    assert res["result"]["protocolVersion"] == "2024-11-05"


def test_mcp_tools_list():
    server = CodeGraphyLiteMCP()
    req = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {},
    }
    res = server.dispatch(req)
    assert res is not None
    tools = res["result"]["tools"]
    tool_names = [t["name"] for t in tools]
    assert len(tools) == 3
    assert "list_workspace_topics" in tool_names
    assert "get_topic_context" in tool_names
    assert "get_architecture_summary" in tool_names


def test_mcp_tools_call_workflow():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        f = tmppath / "auth.py"
        f.write_text("class Authenticator:\n    def login(self, u, p): pass\n", encoding="utf-8")

        node = ReactFlowNode(
            id="auth",
            position=Position(x=0, y=0),
            data=NodeData(
                id="auth",
                label="auth",
                description="Authentication module",
                status="done",
                attached_files=[FileReference(filepath="auth.py")],
            ),
        )
        graph = GraphState(nodes=[node], edges=[])
        save_graph(graph, tmppath)

        server = CodeGraphyLiteMCP(root_dir=tmppath)

        # 1. list_workspace_topics
        call_req = {
            "jsonrpc": "2.0",
            "id": 10,
            "method": "tools/call",
            "params": {
                "name": "list_workspace_topics",
                "arguments": {},
            },
        }
        res = server.dispatch(call_req)
        assert res is not None
        assert not res["result"]["isError"]
        content = json.loads(res["result"]["content"][0]["text"])
        assert content["total_topics"] == 1
        assert content["topics"][0]["label"] == "auth"

        # 2. get_topic_context
        ctx_req = {
            "jsonrpc": "2.0",
            "id": 11,
            "method": "tools/call",
            "params": {
                "name": "get_topic_context",
                "arguments": {"topic": "auth"},
            },
        }
        res_ctx = server.dispatch(ctx_req)
        assert res_ctx is not None
        assert not res_ctx["result"]["isError"]
        ctx_data = json.loads(res_ctx["result"]["content"][0]["text"])
        assert ctx_data["label"] == "auth"
        assert "class Authenticator:" in ctx_data["attached_files"][0]["signatures"]

        # 3. get_architecture_summary
        sum_req = {
            "jsonrpc": "2.0",
            "id": 12,
            "method": "tools/call",
            "params": {
                "name": "get_architecture_summary",
                "arguments": {},
            },
        }
        res_sum = server.dispatch(sum_req)
        assert res_sum is not None
        sum_data = json.loads(res_sum["result"]["content"][0]["text"])
        assert sum_data["total_topics"] == 1
        assert "CodeGraphy Lite" in sum_data["edition"]

        # 4. Proprietary tool rejected
        pro_req = {
            "jsonrpc": "2.0",
            "id": 13,
            "method": "tools/call",
            "params": {
                "name": "calculate_blast_radius",
                "arguments": {},
            },
        }
        res_pro = server.dispatch(pro_req)
        assert res_pro is not None
        assert res_pro["result"]["isError"]
        assert "CodeGraphy Pro" in res_pro["result"]["content"][0]["text"]


def test_mcp_truncation_under_35_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        for i in range(5):
            (tmppath / f"service_{i}.py").write_text(f"def s_{i}(): pass\n", encoding="utf-8")

        from codegraphy_lite.scanner import build_graph_and_workspace, scan_project
        preview = scan_project(tmppath)
        graph, ws = build_graph_and_workspace(preview)
        save_graph(graph, tmppath)

        server = CodeGraphyLiteMCP(root_dir=tmppath)

        # 1. list_workspace_topics
        call_req = {
            "jsonrpc": "2.0",
            "id": 20,
            "method": "tools/call",
            "params": {
                "name": "list_workspace_topics",
                "arguments": {},
            },
        }
        res = server.dispatch(call_req)
        data = json.loads(res["result"]["content"][0]["text"])
        assert data["truncated"] is False
        assert data["indexed_count"] == 5
        assert data["total_discovered_files"] == 5
        assert "skipped_files" not in data

        # 2. get_topic_context for non-existent topic
        ctx_req = {
            "jsonrpc": "2.0",
            "id": 21,
            "method": "tools/call",
            "params": {
                "name": "get_topic_context",
                "arguments": {"topic": "ghost_module"},
            },
        }
        res_ctx = server.dispatch(ctx_req)
        assert res_ctx["result"]["isError"] is True
        err_msg = res_ctx["result"]["content"][0]["text"]
        assert "Topic 'ghost_module' not found in workspace." in err_msg
        assert "limit reached" not in err_msg


def test_mcp_truncation_over_35_files_and_actionable_error():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        # Create 40 files, with subpackage
        sub = tmppath / "billing"
        sub.mkdir()
        (sub / "invoice_service.py").write_text("class InvoiceService: pass\n", encoding="utf-8")
        (sub / "payment_gateway.py").write_text("class PaymentGateway: pass\n", encoding="utf-8")

        for i in range(38):
            (tmppath / f"mod_{i:02d}.py").write_text(f"def f_{i}(): pass\n", encoding="utf-8")

        from codegraphy_lite.scanner import build_graph_and_workspace, scan_project
        preview = scan_project(tmppath)
        assert preview.truncated is True
        assert preview.total_discovered_files == 40
        assert preview.indexed_count == 35

        graph, ws = build_graph_and_workspace(preview)
        save_graph(graph, tmppath)

        server = CodeGraphyLiteMCP(root_dir=tmppath)

        # 1. list_workspace_topics has truncation metadata
        call_req = {
            "jsonrpc": "2.0",
            "id": 30,
            "method": "tools/call",
            "params": {
                "name": "list_workspace_topics",
                "arguments": {},
            },
        }
        res = server.dispatch(call_req)
        data = json.loads(res["result"]["content"][0]["text"])
        assert data["truncated"] is True
        assert data["indexed_count"] == 35
        assert data["total_discovered_files"] == 40
        assert data["skipped_count"] == 5
        assert len(data["skipped_files"]) == 5

        # 2. get_architecture_summary has truncation metadata
        sum_req = {
            "jsonrpc": "2.0",
            "id": 31,
            "method": "tools/call",
            "params": {
                "name": "get_architecture_summary",
                "arguments": {},
            },
        }
        res_sum = server.dispatch(sum_req)
        sum_data = json.loads(res_sum["result"]["content"][0]["text"])
        assert sum_data["truncated"] is True
        assert sum_data["indexed_count"] == 35
        assert sum_data["total_discovered_files"] == 40
        assert len(sum_data["skipped_files"]) == 5

        # 3. get_topic_context with topic that matches skipped file
        # Pick one file from skipped_files
        skipped_first = data["skipped_files"][0]
        query_token = Path(skipped_first).stem

        ctx_req_skipped = {
            "jsonrpc": "2.0",
            "id": 32,
            "method": "tools/call",
            "params": {
                "name": "get_topic_context",
                "arguments": {"topic": query_token},
            },
        }
        res_skipped = server.dispatch(ctx_req_skipped)
        assert res_skipped["result"]["isError"] is True
        msg_skipped = res_skipped["result"]["content"][0]["text"]
        assert "CodeGraphy Lite 35-file limit reached" in msg_skipped
        assert "Found matching unindexed file" in msg_skipped
        assert query_token in msg_skipped
        assert "re-scope your root path (CODEGRAPHY_ROOT)" in msg_skipped

        # 4. get_topic_context with non-matching query when truncated is True
        ctx_req_unmatched = {
            "jsonrpc": "2.0",
            "id": 33,
            "method": "tools/call",
            "params": {
                "name": "get_topic_context",
                "arguments": {"topic": "completely_unrelated_xyz"},
            },
        }
        res_unmatched = server.dispatch(ctx_req_unmatched)
        assert res_unmatched["result"]["isError"] is True
        msg_unmatched = res_unmatched["result"]["content"][0]["text"]
        assert "CodeGraphy Lite 35-file limit reached" in msg_unmatched
        assert "re-scope your root path (CODEGRAPHY_ROOT)" in msg_unmatched
