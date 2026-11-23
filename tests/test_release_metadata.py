"""Release metadata, MCP description, and CLI contract tests."""

import json
import sys
import tempfile
from pathlib import Path

import pytest

from codegraphy_lite import cli, mcp
from codegraphy_lite.models import FileReference, GraphState, NodeData, Position, ReactFlowNode
from codegraphy_lite.storage import save_graph


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_glama_manifest_is_valid_json():
    data = json.loads((REPO_ROOT / "glama.json").read_text(encoding="utf-8"))
    assert data["$schema"] == "https://glama.ai/mcp/schemas/server.json"
    assert "maintainers" in data


def test_glama_manifest_maintainers_are_non_empty_strings():
    data = json.loads((REPO_ROOT / "glama.json").read_text(encoding="utf-8"))
    maintainers = data["maintainers"]
    assert isinstance(maintainers, list)
    assert maintainers
    assert all(isinstance(item, str) and item.strip() for item in maintainers)


def test_mcp_tool_descriptions_are_short_and_complete():
    for tool in mcp.TOOLS_MANIFEST:
        description = tool["description"].strip()
        assert description, f"{tool['name']} has an empty description"
        assert len(description) <= 160, f"{tool['name']} description is {len(description)} chars"
        assert description.endswith("."), f"{tool['name']} description should be a sentence"


def test_mcp_tool_descriptions_do_not_repeat_schema_arguments():
    for tool in mcp.TOOLS_MANIFEST:
        properties = tool["inputSchema"].get("properties", {})
        for argument in properties:
            assert argument not in tool["description"], (
                f"{tool['name']} description repeats schema argument '{argument}'"
            )


def test_mcp_initialize_exposes_instructions():
    server = mcp.CodeGraphyLiteMCP()
    response = server.dispatch({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    assert response is not None
    assert response["result"]["instructions"] == mcp.MCP_INSTRUCTIONS


def test_mcp_initialize_instructions_are_bounded_and_actionable():
    assert 0 < len(mcp.MCP_INSTRUCTIONS) <= 400
    assert "truncated" in mcp.MCP_INSTRUCTIONS
    assert "skipped_files" in mcp.MCP_INSTRUCTIONS


def test_mcp_auto_scans_empty_workspace():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        (tmppath / "service.py").write_text("class Service: pass\n", encoding="utf-8")
        server = mcp.CodeGraphyLiteMCP(root_dir=tmppath)

        data = server.handle_list_workspace_topics({})

        assert data["total_topics"] == 1
        assert data["topics"][0]["label"] == "service"
        assert (tmppath / ".codegraphy" / "graph.json").is_file()


def test_mcp_auto_scan_keeps_existing_graph():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        node = ReactFlowNode(
            id="custom",
            position=Position(x=0, y=0),
            data=NodeData(
                id="custom",
                label="custom-topic",
                description="Existing graph",
                attached_files=[FileReference(filepath="custom.py")],
            ),
        )
        save_graph(GraphState(nodes=[node], edges=[]), tmppath)
        server = mcp.CodeGraphyLiteMCP(root_dir=tmppath)

        data = server.handle_list_workspace_topics({})

        assert data["total_topics"] == 1
        assert data["topics"][0]["label"] == "custom-topic"


def test_cli_defaults_to_mcp(monkeypatch):
    calls = []
    monkeypatch.setattr(sys, "argv", ["codegraphy-lite"])
    monkeypatch.setattr(cli, "mcp_main", lambda: calls.append("mcp"))

    cli.main([])

    assert calls == ["mcp"]


def test_cli_serve_dispatches_to_web_ui(monkeypatch):
    calls = []
    monkeypatch.setattr(sys, "argv", ["codegraphy-lite"])
    monkeypatch.setattr(cli, "_run_serve", lambda argv: calls.append(list(argv)))

    cli.main(["serve", "--port", "9000"])

    assert calls == [["--port", "9000"]]


def test_cli_help_mentions_default_mcp(capsys):
    monkeypatch_argv = sys.argv
    sys.argv = ["codegraphy-lite"]
    try:
        cli.main(["--help"])
    finally:
        sys.argv = monkeypatch_argv

    output = capsys.readouterr().out
    assert "codegraphy-lite" in output
    assert "MCP STDIO server (default)" in output


def test_cli_version_prints_package_version(capsys):
    monkeypatch_argv = sys.argv
    sys.argv = ["codegraphy-lite"]
    try:
        cli.main(["--version"])
    finally:
        sys.argv = monkeypatch_argv

    output = capsys.readouterr().out
    assert "codegraphy-lite" in output
    assert cli.__version__ in output


def test_run_serve_help_exits_zero(capsys):
    with pytest.raises(SystemExit) as exc_info:
        cli._run_serve(["--help"])

    assert exc_info.value.code == 0
    assert "codegraphy-lite serve" in capsys.readouterr().out


def test_run_serve_rejects_missing_directory(capsys):
    with tempfile.TemporaryDirectory() as tmpdir:
        missing = Path(tmpdir) / "missing-project"

        with pytest.raises(SystemExit) as exc_info:
            cli._run_serve([str(missing)])

    assert exc_info.value.code == 1
    assert "does not exist" in capsys.readouterr().err
