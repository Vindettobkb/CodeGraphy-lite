"""Data models for CodeGraphy Lite.

Clean, standalone Pydantic models for React Flow graph, workspace domain,
topics, lanes, tasks, and preview scanner payloads.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional, Tuple
from pydantic import BaseModel, Field, model_validator


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str = "") -> str:
    uid = str(uuid.uuid4())
    return f"{prefix}_{uid[:8]}" if prefix else uid


NodeStatus = Literal["todo", "in_progress", "done"]


class FileReference(BaseModel):
    filepath: str


class NodeData(BaseModel):
    id: str
    label: str
    description: str = ""
    status: NodeStatus = "todo"
    lane_id: Optional[str] = None
    task_id: Optional[str] = None
    parent_topic_id: Optional[str] = None
    subtopic_count: int = 0
    done_subtopic_count: int = 0
    progress_percent: int = 0
    attached_files: List[FileReference] = Field(default_factory=list)


class Position(BaseModel):
    x: float = 0.0
    y: float = 0.0


class ReactFlowNode(BaseModel):
    id: str
    type: str = "contextNode"
    position: Position = Field(default_factory=Position)
    data: NodeData


class EdgeData(BaseModel):
    id: str
    source: str
    target: str
    sourceHandle: Optional[str] = None
    targetHandle: Optional[str] = None


class GraphState(BaseModel):
    nodes: List[ReactFlowNode] = Field(default_factory=list)
    edges: List[EdgeData] = Field(default_factory=list)
    total_discovered_files: int = 0
    indexed_count: int = 0
    truncated: bool = False
    skipped_files: List[str] = Field(default_factory=list)
    skipped_count: int = 0


class FileSource(BaseModel):
    id: str = Field(default_factory=lambda: new_id("src"))
    path: str
    type: Literal["file", "directory"] = "file"
    recursive: bool = True
    include: List[str] = Field(default_factory=lambda: [".py", ".ts", ".tsx", ".js", ".md", ".json"])
    exclude: List[str] = Field(
        default_factory=lambda: [
            ".git", "node_modules", "dist", "build", ".venv", "venv",
            "__pycache__", "release", ".codegraphy", ".archflow"
        ]
    )


class TopicLane(BaseModel):
    id: str = Field(default_factory=lambda: new_id("lane"))
    title: str = ""
    name: Optional[str] = None
    order: int = 0
    collapsed: bool = False
    color: str = "#38bdf8"

    @model_validator(mode="before")
    @classmethod
    def sync_name_and_title(cls, data: Any) -> Any:
        if isinstance(data, dict):
            t = data.get("title") or data.get("name") or "Lane"
            data["title"] = t
            data["name"] = t
        return data

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        d = super().model_dump(*args, **kwargs)
        val = d.get("name") or d.get("title") or ""
        d["name"] = val
        d["title"] = val
        return d


class TaskItem(BaseModel):
    id: str = Field(default_factory=lambda: new_id("task"))
    title: str
    description: str = ""
    status: NodeStatus = "todo"
    lane_id: Optional[str] = None
    assigned_user_id: Optional[str] = None
    progress: int = 0
    topic_ids: List[str] = Field(default_factory=list)
    updated_at: str = Field(default_factory=utc_now_iso)


class Topic(BaseModel):
    id: str
    label: str
    description: str = ""
    status: NodeStatus = "todo"
    lane_id: Optional[str] = None
    task_id: Optional[str] = None
    parent_topic_id: Optional[str] = None
    position: Position = Field(default_factory=Position)
    attached_files: List[FileReference] = Field(default_factory=list)
    sources: List[FileSource] = Field(default_factory=list)
    ai_context_settings: Dict[str, Any] = Field(
        default_factory=lambda: {"include_neighbors": True, "strip_bodies": True}
    )
    updated_at: str = Field(default_factory=utc_now_iso)


class WorkspaceModel(BaseModel):
    version: str = "2.0"
    id: str = "default_workspace"
    name: str = "CodeGraphy Workspace"
    root_path: Optional[str] = None
    lanes: List[TopicLane] = Field(
        default_factory=lambda: [
            TopicLane(id="lane_plan", title="Planning", order=0, color="#a855f7"),
            TopicLane(id="lane_dev", title="Development", order=1, color="#38bdf8"),
            TopicLane(id="lane_test", title="Testing", order=2, color="#eab308"),
            TopicLane(id="lane_done", title="Done", order=3, color="#22c55e"),
        ]
    )
    topics: List[Topic] = Field(default_factory=list)
    edges: List[EdgeData] = Field(default_factory=list)
    tasks: List[TaskItem] = Field(default_factory=list)
    file_sources: List[FileSource] = Field(default_factory=list)
    total_discovered_files: int = 0
    indexed_count: int = 0
    truncated: bool = False
    skipped_files: List[str] = Field(default_factory=list)
    skipped_count: int = 0
    updated_at: str = Field(default_factory=utc_now_iso)

    def get_topic_progress(self, topic_id: str) -> Tuple[int, int, int]:
        children = [t for t in self.topics if t.parent_topic_id == topic_id]
        if not children:
            t = next((x for x in self.topics if x.id == topic_id), None)
            pct = 100 if t and t.status == "done" else (50 if t and t.status == "in_progress" else 0)
            return 0, (1 if pct == 100 else 0), pct
        total = len(children)
        done = sum(1 for c in children if c.status == "done")
        pct = int((done / total) * 100) if total else 0
        return total, done, pct


class ScannedEdgePreview(BaseModel):
    source_topic_id: str
    target_topic_id: str
    source_file: str
    target_module: str
    line_number: int = 1


class ScannedTopicPreview(BaseModel):
    id: str
    label: str
    category: str = "module"
    files: List[str] = Field(default_factory=list)
    incoming_count: int = 0
    outgoing_count: int = 0


class ScanPreviewRequest(BaseModel):
    root_path: str
    ignore_dirs: List[str] = Field(
        default_factory=lambda: [
            ".git", ".venv", "venv", "node_modules", "__pycache__",
            "dist", "build", "release", ".codegraphy", ".archflow",
            ".idea", ".vscode", "coverage"
        ]
    )


class ScanPreviewResponse(BaseModel):
    root_path: str
    project_name: str
    total_files: int
    topics: List[ScannedTopicPreview] = Field(default_factory=list)
    edges: List[ScannedEdgePreview] = Field(default_factory=list)
    unresolved_imports: List[str] = Field(default_factory=list)
    ignored_dirs_triggered: List[str] = Field(default_factory=list)
    total_discovered_files: int = 0
    indexed_count: int = 0
    truncated: bool = False
    skipped_files: List[str] = Field(default_factory=list)
    skipped_count: int = 0
