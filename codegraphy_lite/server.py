"""FastAPI server for CodeGraphy Lite.

Hosts the interactive React Flow visual graph, REST APIs, WebSocket live sync,
and STDIO/HTTP MCP configuration endpoints.
"""

from __future__ import annotations

import os
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from codegraphy_lite import __version__
from codegraphy_lite.models import (
    GraphState,
    NodeData,
    ReactFlowNode,
    ScanPreviewRequest,
    ScanPreviewResponse,
    TopicLane,
    WorkspaceModel,
)
from codegraphy_lite.scanner import (
    MAX_LITE_FILES,
    build_graph_and_workspace,
    extract_ast_signatures,
    scan_project,
)
from codegraphy_lite.storage import (
    get_active_root,
    get_storage_dir,
    load_graph,
    load_workspace,
    parse_md_to_workspace,
    save_graph,
    save_workspace,
    serialize_workspace_to_md,
    set_active_root,
)


class RootPathPayload(BaseModel):
    root_path: str


class GeneratePromptRequest(BaseModel):
    topic_ids: List[str]


class WorkspaceWsManager:
    def __init__(self) -> None:
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.discard(websocket)

    async def broadcast_update(self, event_type: str = "workspace_updated", extra: Optional[Dict[str, Any]] = None) -> None:
        if not self.active_connections:
            return
        payload = {"type": event_type, "ts": time.time(), **(extra or {})}
        dead: List[WebSocket] = []
        for ws in list(self.active_connections):
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for d in dead:
            self.active_connections.discard(d)


ws_manager = WorkspaceWsManager()


def get_web_dir() -> Path:
    """Returns directory containing built static frontend assets."""
    if getattr(sys, "frozen", False):
        if hasattr(sys, "_MEIPASS"):
            meipass_candidates = [
                Path(sys._MEIPASS) / "codegraphy_lite" / "web",
                Path(sys._MEIPASS) / "web",
            ]
            for c in meipass_candidates:
                if c.exists() and (c / "index.html").exists():
                    return c
        exe_dir = Path(sys.executable).resolve().parent
        exe_candidates = [
            exe_dir / "web",
            exe_dir / "codegraphy_lite" / "web",
            exe_dir / "_internal" / "codegraphy_lite" / "web",
        ]
        for c in exe_candidates:
            if c.exists() and (c / "index.html").exists():
                return c

    packaged = Path(__file__).resolve().parent / "web"
    if packaged.exists() and (packaged / "index.html").exists():
        return packaged
    # Fallback to local paths if running from source checkout
    candidates = [
        Path.cwd() / "web",
        Path.cwd() / "frontend" / "dist",
        Path(__file__).resolve().parent.parent / "web",
    ]
    for c in candidates:
        if c.exists() and (c / "index.html").exists():
            return c
    return packaged


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize workspace and ensure storage folder exists
    get_storage_dir()
    web_dir = get_web_dir()
    assets_dir = web_dir / "assets"
    if assets_dir.exists():
        has_assets = any(getattr(r, "path", None) == "/assets" for r in app.routes)
        if not has_assets:
            app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
    yield


app = FastAPI(title="CodeGraphy Lite API", version=__version__, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/ws/workspace")
async def workspace_ws_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except (WebSocketDisconnect, Exception):
        ws_manager.disconnect(websocket)


@app.get("/health")
@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "edition": "lite",
        "version": __version__,
        "open_source": True,
        "max_scan_files": MAX_LITE_FILES,
    }


@app.get("/api/workspace/root-path")
def get_root_path():
    return {"root_path": str(get_active_root())}


@app.post("/api/workspace/root-path")
def set_root_path_endpoint(payload: RootPathPayload):
    new_root = set_active_root(payload.root_path)
    return {"status": "ok", "root_path": str(new_root)}


@app.get("/api/graph", response_model=GraphState)
def get_graph():
    return load_graph()


@app.post("/api/graph")
def post_graph(graph: GraphState):
    save_graph(graph)
    return {"status": "ok", "nodes_count": len(graph.nodes), "edges_count": len(graph.edges)}


@app.get("/api/workspace", response_model=WorkspaceModel)
def get_workspace():
    return load_workspace()


@app.post("/api/workspace")
def post_workspace(ws: WorkspaceModel):
    save_workspace(ws)
    return {"status": "ok", "topics_count": len(ws.topics)}


@app.get("/api/workspace/export-md", response_class=PlainTextResponse)
def export_workspace_md():
    ws = load_workspace()
    return serialize_workspace_to_md(ws)


@app.post("/api/workspace/import-md")
def import_workspace_md(payload: Dict[str, str]):
    md = payload.get("markdown", "")
    if not md.strip():
        raise HTTPException(status_code=400, detail="Markdown content is required.")
    ws = parse_md_to_workspace(md)
    save_workspace(ws)
    return {"status": "ok", "topics_count": len(ws.topics), "edges_count": len(ws.edges)}


@app.post("/api/workspace/scan-preview", response_model=ScanPreviewResponse)
def scan_preview_endpoint(req: ScanPreviewRequest):
    try:
        target_path = Path(req.root_path).resolve() if req.root_path else get_active_root()
        res = scan_project(target_path)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Scanner error: {str(e)}")


@app.post("/api/lanes")
def save_lanes_endpoint(lanes: List[TopicLane]):
    ws = load_workspace()
    ws.lanes = lanes
    save_workspace(ws)
    return {"status": "ok", "lanes_count": len(lanes)}


@app.post("/api/tasks")
def save_tasks_endpoint(tasks: List[Any]):
    return {"status": "ok", "tasks_count": len(tasks)}


@app.post("/api/topics/assign")
def assign_topic_endpoint(payload: Dict[str, Any]):
    return {"status": "ok"}


# ─── AST Signature Context Compiler ─────────────────────────────────────────

def compile_topic_prompt(topic_id: str, graph: GraphState, root: Path) -> str:
    target_node = next((n for n in graph.nodes if n.id == topic_id or n.data.id == topic_id), None)
    if not target_node:
        raise HTTPException(status_code=404, detail=f"Topic '{topic_id}' not found.")

    # 1-hop connected neighbors
    neighbor_ids = set()
    for e in graph.edges:
        if e.source == target_node.id:
            neighbor_ids.add(e.target)
        elif e.target == target_node.id:
            neighbor_ids.add(e.source)

    neighbors = []
    for n in graph.nodes:
        if n.id in neighbor_ids:
            neighbors.append(f"- **{n.data.label}** (`{n.data.status}`): {n.data.description}")

    neighbors_str = "\n".join(neighbors) if neighbors else "No 1-hop dependencies connected."

    file_sections = []
    for f in target_node.data.attached_files:
        full_p = root / f.filepath
        if full_p.exists() and full_p.is_file():
            try:
                code = full_p.read_text(encoding="utf-8", errors="ignore")
                sigs = extract_ast_signatures(code)
            except Exception as e:
                sigs = f"# Error reading file: {e}"
        else:
            sigs = f"# File not found on disk: {f.filepath}"

        file_sections.append(
            f"### File: `{f.filepath}`\n```python\n{sigs}\n```"
        )

    files_str = "\n\n".join(file_sections) if file_sections else "No attached files."

    return (
        f"# Architecture Context: {target_node.data.label}\n"
        f"**Status:** `{target_node.data.status}`\n\n"
        f"## Description\n{target_node.data.description or 'No description'}\n\n"
        f"## Connected Dependencies (1-Hop)\n{neighbors_str}\n\n"
        f"## File Signatures (AST Extracted)\n{files_str}"
    )


@app.get("/api/generate-prompt/{topic_id}")
def generate_prompt_get(topic_id: str):
    graph = load_graph()
    prompt = compile_topic_prompt(topic_id, graph, get_active_root())
    return {"prompt": prompt}


@app.post("/api/generate-prompt")
def generate_prompt_post(req: GeneratePromptRequest):
    graph = load_graph()
    root = get_active_root()
    prompts = [compile_topic_prompt(tid, graph, root) for tid in req.topic_ids]
    return {"prompt": "\n\n---\n\n".join(prompts)}


# ─── MCP Client Configurations ──────────────────────────────────────────────

@app.get("/api/mcp/configs")
def get_mcp_configs():
    py_exec = sys.executable or "python"
    root_str = str(get_active_root())
    return {
        "claude_code": {
            "mcpServers": {
                "codegraphy": {
                    "command": py_exec,
                    "args": ["-m", "codegraphy_lite.mcp"],
                    "env": {"CODEGRAPHY_ROOT": root_str},
                }
            }
        },
        "cursor": {
            "mcpServers": {
                "codegraphy": {
                    "command": py_exec,
                    "args": ["-m", "codegraphy_lite.mcp"],
                    "env": {"CODEGRAPHY_ROOT": root_str},
                }
            }
        },
    }


@app.get("/api/ai/discover")
def discover_ai_providers():
    return {
        "providers": [
            {
                "id": "ollama",
                "name": "Ollama (Local)",
                "models": ["llama3.2", "qwen2.5-coder", "mistral", "deepseek-r1"],
                "status": "available",
            },
            {
                "id": "lmstudio",
                "name": "LM Studio (Local)",
                "models": ["local-model"],
                "status": "available",
            },
        ]
    }


# ─── Pro Feature Interceptors ───────────────────────────────────────────────

def _pro_required_response(feature_name: str, desc: str) -> JSONResponse:
    return JSONResponse(
        status_code=402,
        content={
            "detail": f"{feature_name} is a CodeGraphy Pro feature.",
            "pro_feature": True,
            "feature": feature_name,
            "description": desc,
            "upgrade_url": "https://github.com/Vindettobkb/Codegraphy-releases/releases/tag/v2.2.0",
        },
    )


@app.get("/api/git/diff")
def get_git_diff_pro():
    return _pro_required_response(
        "Git Architecture Diff Overlay",
        "Calculates visual architecture diffs and detects layer regressions between Git branches.",
    )


@app.post("/api/context/compile")
def post_context_compile_pro():
    return _pro_required_response(
        "AST Smart Context (-85% Tokens)",
        "Proprietary multi-language AST compression that saves 85% of LLM token costs.",
    )


@app.get("/api/tests/impact")
@app.post("/api/tests/run")
def tests_impact_pro():
    return _pro_required_response(
        "Test Impact Analysis",
        "Static dependency mapping maps changed files to affected test suites and runs selective tests.",
    )


@app.post("/api/linter/analyze")
@app.get("/api/linter/report")
@app.get("/api/linter/export")
def linter_pro():
    return _pro_required_response(
        "Enterprise Architecture Linter",
        "Validates strict layer separation rules, cyclic dependency detection, and architectural constraints.",
    )


# ─── Static files & SPA fallback ───────────────────────────────────────────

@app.get("/", response_class=FileResponse)
async def serve_root_index():
    web = get_web_dir()
    index_file = web / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse(
        "<h1>CodeGraphy Lite</h1><p>Web UI bundle is initializing...</p>"
    )


@app.get("/{full_path:path}", response_class=FileResponse)
async def serve_spa_fallback(full_path: str):
    if full_path.startswith("api") or full_path.startswith("ws"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    web = get_web_dir()
    target = web / full_path
    if target.is_file():
        return FileResponse(target)
    index_file = web / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    raise HTTPException(status_code=404, detail="File not found")
