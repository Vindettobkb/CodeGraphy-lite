"""Storage and markdown codec for CodeGraphy Lite.

Handles atomic persistence of `.codegraphy/graph.json`, `.codegraphy/workspace.json`,
and import/export of human-readable `.cg.md` workspace specifications.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from codegraphy_lite.models import (
    EdgeData,
    FileReference,
    GraphState,
    NodeData,
    Position,
    ReactFlowNode,
    TaskItem,
    Topic,
    TopicLane,
    WorkspaceModel,
    new_id,
    utc_now_iso,
)

_ACTIVE_ROOT: Path = Path.cwd()


def set_active_root(path: str | Path) -> Path:
    global _ACTIVE_ROOT
    p = Path(path).resolve()
    if p.is_file():
        p = p.parent
    _ACTIVE_ROOT = p
    return _ACTIVE_ROOT


def get_active_root() -> Path:
    return _ACTIVE_ROOT


def get_storage_dir(root: Optional[Path] = None) -> Path:
    r = root or get_active_root()
    d = r / ".codegraphy"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _atomic_write(target_path: Path, content: str) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            dir=str(target_path.parent),
            delete=False,
            encoding="utf-8",
            suffix=".tmp",
        ) as tmp:
            tmp_path = tmp.name
            tmp.write(content)
            tmp.flush()
            os.fsync(tmp.fileno())
        os.replace(tmp_path, str(target_path))
    except Exception as exc:
        if tmp_path and Path(tmp_path).exists():
            os.remove(tmp_path)
        raise exc


def load_graph(root: Optional[Path] = None) -> GraphState:
    gfile = get_storage_dir(root) / "graph.json"
    if gfile.exists():
        try:
            data = json.loads(gfile.read_text(encoding="utf-8"))
            return GraphState.model_validate(data)
        except Exception:
            pass
    return GraphState(nodes=[], edges=[])


def save_graph(graph: GraphState, root: Optional[Path] = None) -> None:
    gfile = get_storage_dir(root) / "graph.json"
    _atomic_write(gfile, graph.model_dump_json(indent=2))


def load_workspace(root: Optional[Path] = None) -> WorkspaceModel:
    wfile = get_storage_dir(root) / "workspace.json"
    if wfile.exists():
        try:
            data = json.loads(wfile.read_text(encoding="utf-8"))
            return WorkspaceModel.model_validate(data)
        except Exception:
            pass
    return WorkspaceModel(root_path=str(root or get_active_root()))


def save_workspace(ws: WorkspaceModel, root: Optional[Path] = None) -> None:
    wfile = get_storage_dir(root) / "workspace.json"
    ws.updated_at = utc_now_iso()
    _atomic_write(wfile, ws.model_dump_json(indent=2))


# ─── .cg.md Markdown Codec ──────────────────────────────────────────────────

def serialize_workspace_to_md(ws: WorkspaceModel) -> str:
    """Serializes WorkspaceModel to standard .cg.md format."""
    lines = [
        "---",
        "format: codegraphy-workspace",
        f"version: {ws.version}",
        f"name: {ws.name}",
        f"updated_at: {ws.updated_at}",
        "---",
        "",
        f"# Workspace: {ws.name}",
        "",
        "## Lanes",
    ]
    for lane in sorted(ws.lanes, key=lambda x: x.order):
        collapsed = "collapsed" if lane.collapsed else "expanded"
        lines.append(f"- [{lane.id}] **{lane.title}** | order={lane.order} | color={lane.color} | {collapsed}")

    lines.extend(["", "## Tasks"])
    if not ws.tasks:
        lines.append("_No tasks defined._")
    for task in ws.tasks:
        topics_str = ", ".join(task.topic_ids) if task.topic_ids else "none"
        lines.append(f"### Task: {task.title} `{task.id}`")
        lines.append(f"- status: `{task.status}`")
        lines.append(f"- linked_topics: `{topics_str}`")
        if task.description:
            lines.append(f"- description: {task.description}")
        lines.append("")

    lines.extend(["## Topics"])
    for topic in ws.topics:
        lines.append(f"### Topic: {topic.label} `{topic.id}`")
        lines.append(f"- status: `{topic.status}`")
        lines.append(f"- lane: `{topic.lane_id or 'none'}`")
        if topic.description:
            lines.append(f"- description: {topic.description}")
        if topic.attached_files:
            lines.append("- files:")
            for f in topic.attached_files:
                lines.append(f"  - `{f.filepath}`")
        lines.append("")

    lines.extend(["## Dependencies"])
    if not ws.edges:
        lines.append("_No dependencies defined._")
    for edge in ws.edges:
        lines.append(f"- `{edge.source}` -> `{edge.target}`")

    return "\n".join(lines)


def parse_md_to_workspace(markdown: str) -> WorkspaceModel:
    """Parses standard .cg.md into WorkspaceModel."""
    ws = WorkspaceModel()
    current_section = None

    for line in markdown.splitlines():
        line_str = line.strip()
        if not line_str or line_str.startswith("---"):
            continue

        if line_str.startswith("# Workspace:"):
            ws.name = line_str.replace("# Workspace:", "").strip()
            continue

        if line_str.startswith("## Lanes"):
            current_section = "lanes"
            continue
        elif line_str.startswith("## Tasks"):
            current_section = "tasks"
            continue
        elif line_str.startswith("## Topics"):
            current_section = "topics"
            continue
        elif line_str.startswith("## Dependencies"):
            current_section = "dependencies"
            continue

        if current_section == "topics" and line_str.startswith("### Topic:"):
            match = re.search(r"### Topic:\s+(.*?)\s+`([^`]+)`", line_str)
            if match:
                lbl, tid = match.group(1), match.group(2)
                ws.topics.append(Topic(id=tid, label=lbl, description=""))
        elif current_section == "dependencies" and "->" in line_str:
            match = re.search(r"`([^`]+)`\s*->\s*`([^`]+)`", line_str)
            if match:
                src, tgt = match.group(1), match.group(2)
                ws.edges.append(EdgeData(id=f"edge_{src}_{tgt}", source=src, target=tgt))

    return ws
