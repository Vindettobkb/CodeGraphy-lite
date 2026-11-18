"""Lightweight, safe directory and file scanner for CodeGraphy Lite.

Uses ONLY Python standard library `ast.parse()` and regex-based import matching
to discover files, extract signatures, and build interactive architecture graphs.
Enforces a hard limit of 150 files (open-source lite edition).
"""

from __future__ import annotations

import ast
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from codegraphy_lite.models import (
    EdgeData,
    FileReference,
    GraphState,
    NodeData,
    Position,
    ReactFlowNode,
    ScannedEdgePreview,
    ScannedTopicPreview,
    ScanPreviewRequest,
    ScanPreviewResponse,
    Topic,
    TopicLane,
    WorkspaceModel,
    new_id,
)

MAX_LITE_FILES = 150
SUPPORTED_EXTENSIONS = {".py", ".ts", ".tsx", ".js", ".jsx", ".json", ".md"}
DEFAULT_IGNORE_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__",
    "dist", "build", "release", ".codegraphy", ".archflow",
    ".idea", ".vscode", "coverage", ".pytest_cache"
}


def extract_ast_signatures(code: str) -> str:
    """Extracts top-level class, function signatures, and docstrings using stdlib ast."""
    try:
        tree = ast.parse(code)
    except Exception:
        # Fallback for syntax errors or non-Python files
        lines = [line.strip() for line in code.splitlines() if line.strip() and not line.strip().startswith("#")]
        return "\n".join(lines[:30]) if lines else "# Empty or unparseable file"

    parts: List[str] = []
    doc = ast.get_docstring(tree)
    if doc:
        parts.append(f'"""{doc.strip()}"""\n')

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            bases = [ast.unparse(b) for b in node.bases]
            bases_str = f"({', '.join(bases)})" if bases else ""
            parts.append(f"class {node.name}{bases_str}:")
            cdoc = ast.get_docstring(node)
            if cdoc:
                parts.append(f'    """{cdoc.strip()}"""')
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    prefix = "async def" if isinstance(item, ast.AsyncFunctionDef) else "def"
                    try:
                        args = ast.unparse(item.args)
                    except Exception:
                        args = "..."
                    returns = f" -> {ast.unparse(item.returns)}" if getattr(item, "returns", None) else ""
                    parts.append(f"    {prefix} {item.name}({args}){returns}: ...")
            parts.append("")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
            try:
                args = ast.unparse(node.args)
            except Exception:
                args = "..."
            returns = f" -> {ast.unparse(node.returns)}" if getattr(node, "returns", None) else ""
            fdoc = ast.get_docstring(node)
            parts.append(f"{prefix} {node.name}({args}){returns}:")
            if fdoc:
                parts.append(f'    """{fdoc.strip()}"""')
            parts.append("    ...")
            parts.append("")

    return "\n".join(parts).strip() if parts else "# No top-level classes or functions found."


def extract_imports_from_python(code: str) -> List[str]:
    """Extracts imported module names using stdlib ast."""
    imported_modules: List[str] = []
    try:
        tree = ast.parse(code)
    except Exception:
        # Fallback to regex
        for match in re.finditer(r"^(?:from\s+([\w\.]+)\s+import|import\s+([\w\.]+))", code, re.MULTILINE):
            m = match.group(1) or match.group(2)
            if m:
                imported_modules.append(m)
        return imported_modules

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported_modules.append(node.module)
    return imported_modules


def extract_imports_from_js_ts(code: str) -> List[str]:
    """Extracts imports from JS/TS using simple regex."""
    imported: List[str] = []
    # match: import ... from '...' or require('...')
    for match in re.finditer(r"""(?:import\s+.*?from\s+['"]([^'"]+)['"]|require\s*\(\s*['"]([^'"]+)['"]\))""", code):
        mod = match.group(1) or match.group(2)
        if mod and not mod.startswith("."):
            imported.append(mod)
        elif mod:
            # relative path: ./foo/bar -> foo/bar
            clean = mod.replace("\\", "/").lstrip("./")
            imported.append(clean)
    return imported


class CollectResult(tuple):
    """Tuple (collected, triggered_ignores) with extra metadata attributes."""
    collected: List[Path]
    triggered_ignores: List[str]
    skipped: List[Path]
    total_discovered: int

    def __new__(cls, collected: List[Path], triggered_ignores: List[str], skipped: Optional[List[Path]] = None):
        inst = super().__new__(cls, (collected, triggered_ignores))
        inst.collected = collected
        inst.triggered_ignores = triggered_ignores
        inst.skipped = skipped or []
        inst.total_discovered = len(collected) + len(inst.skipped)
        return inst


def collect_project_files(root: Path, ignore_dirs: Optional[Set[str]] = None, max_files: int = MAX_LITE_FILES) -> CollectResult:
    """Walks the directory collecting up to max_files matching supported extensions."""
    ignored = set(ignore_dirs) if ignore_dirs else set(DEFAULT_IGNORE_DIRS)
    all_supported_files: List[Path] = []
    triggered_ignores: Set[str] = set()

    for dirpath, dirnames, filenames in os.walk(root):
        # Exclude ignored directories in-place
        removed = [d for d in dirnames if d in ignored or d.startswith(".")]
        for r in removed:
            triggered_ignores.add(r)
            dirnames.remove(r)

        # Sort filenames for deterministic ordering
        filenames.sort()
        for fname in filenames:
            ext = Path(fname).suffix.lower()
            if ext in SUPPORTED_EXTENSIONS:
                all_supported_files.append(Path(dirpath) / fname)

    collected = all_supported_files[:max_files]
    skipped = all_supported_files[max_files:]

    return CollectResult(collected, sorted(triggered_ignores), skipped)


def infer_category(rel_path: str) -> str:
    """Infers an architecture category for a file."""
    p = rel_path.lower().replace("\\", "/")
    if "api" in p or "route" in p or "controller" in p or "endpoint" in p:
        return "api"
    if "model" in p or "schema" in p or "entity" in p or "types" in p:
        return "domain"
    if "service" in p or "engine" in p or "handler" in p or "business" in p:
        return "service"
    if "db" in p or "storage" in p or "repo" in p or "sql" in p or "cache" in p:
        return "data"
    if "test" in p or "spec" in p:
        return "tests"
    if "ui" in p or "component" in p or "view" in p or "page" in p:
        return "ui"
    return "module"


def scan_project(root_dir: str | Path, max_files: int = MAX_LITE_FILES) -> ScanPreviewResponse:
    """Scans project directory and builds ScanPreviewResponse (capped by MAX_LITE_FILES)."""
    root_path = Path(root_dir).resolve()
    if not root_path.exists():
        raise ValueError(f"Directory does not exist: {root_path}")

    collect_res = collect_project_files(root_path, max_files=max_files)
    files = collect_res.collected
    triggered_ignores = collect_res.triggered_ignores
    skipped_paths = collect_res.skipped

    total_discovered_files = len(files) + len(skipped_paths)
    indexed_count = len(files)
    truncated = total_discovered_files > max_files
    skipped_count = len(skipped_paths)
    skipped_files = [p.relative_to(root_path).as_posix() for p in skipped_paths[:100]]

    # 1. Build topics (one topic per file or submodule)
    topics: List[ScannedTopicPreview] = []
    file_to_topic_id: Dict[str, str] = {}
    topic_files_map: Dict[str, List[str]] = {}

    for file_p in files:
        rel_posix = file_p.relative_to(root_path).as_posix()
        # Topic ID based on relative path without extension
        raw_id = rel_posix.replace("/", "_").replace("\\", "_")
        if raw_id.endswith(".py"):
            raw_id = raw_id[:-3]
        elif "." in raw_id:
            raw_id = raw_id.rsplit(".", 1)[0]

        tid = raw_id.strip("_") or "root"
        label = file_p.stem
        cat = infer_category(rel_posix)

        topics.append(
            ScannedTopicPreview(
                id=tid,
                label=label,
                category=cat,
                files=[rel_posix],
            )
        )
        file_to_topic_id[rel_posix] = tid
        topic_files_map[tid] = [rel_posix]

    # 2. Extract dependencies & create edges
    edges: List[ScannedEdgePreview] = []
    seen_edges: Set[Tuple[str, str]] = set()

    for file_p in files:
        rel_posix = file_p.relative_to(root_path).as_posix()
        src_tid = file_to_topic_id.get(rel_posix)
        if not src_tid:
            continue

        try:
            content = file_p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        if file_p.suffix == ".py":
            imports = extract_imports_from_python(content)
        elif file_p.suffix in {".js", ".ts", ".tsx", ".jsx"}:
            imports = extract_imports_from_js_ts(content)
        else:
            imports = []

        for imp in imports:
            # Check if this import matches another scanned file
            tgt_tid = None
            imp_norm = imp.replace(".", "/").lower()
            for other_rel, otid in file_to_topic_id.items():
                if otid == src_tid:
                    continue
                other_norm = other_rel.lower()
                if (
                    imp_norm in other_norm
                    or other_norm.startswith(imp_norm)
                    or Path(other_rel).stem.lower() == imp.split(".")[-1].lower()
                ):
                    tgt_tid = otid
                    break

            if tgt_tid and (src_tid, tgt_tid) not in seen_edges:
                seen_edges.add((src_tid, tgt_tid))
                edges.append(
                    ScannedEdgePreview(
                        source_topic_id=src_tid,
                        target_topic_id=tgt_tid,
                        source_file=rel_posix,
                        target_module=imp,
                    )
                )

    # Count incoming / outgoing degrees
    for edge in edges:
        for t in topics:
            if t.id == edge.source_topic_id:
                t.outgoing_count += 1
            elif t.id == edge.target_topic_id:
                t.incoming_count += 1

    return ScanPreviewResponse(
        root_path=str(root_path),
        project_name=root_path.name or "CodeGraphy Workspace",
        total_files=len(files),
        topics=topics,
        edges=edges,
        unresolved_imports=[],
        ignored_dirs_triggered=triggered_ignores,
        total_discovered_files=total_discovered_files,
        indexed_count=indexed_count,
        truncated=truncated,
        skipped_files=skipped_files,
        skipped_count=skipped_count,
    )


def build_graph_and_workspace(preview: ScanPreviewResponse) -> Tuple[GraphState, WorkspaceModel]:
    """Converts a ScanPreviewResponse into React Flow GraphState and WorkspaceModel."""
    nodes: List[ReactFlowNode] = []
    domain_topics: List[Topic] = []
    edges: List[EdgeData] = []

    # Simple 2D Grid Layout (3 columns, rows down)
    col_width = 320
    row_height = 200
    cols = 3

    for idx, t in enumerate(preview.topics):
        col = idx % cols
        row = idx // cols
        pos = Position(x=float(col * col_width + 50), y=float(row * row_height + 80))

        attached = [FileReference(filepath=f) for f in t.files]
        nd = NodeData(
            id=t.id,
            label=t.label,
            description=f"{t.category.upper()} module · {len(t.files)} file(s)",
            status="todo",
            attached_files=attached,
        )
        nodes.append(ReactFlowNode(id=t.id, position=pos, data=nd))

        domain_topics.append(
            Topic(
                id=t.id,
                label=t.label,
                description=f"{t.category.upper()} module",
                status="todo",
                position=pos,
                attached_files=attached,
            )
        )

    for idx, e in enumerate(preview.edges):
        edges.append(
            EdgeData(
                id=f"edge_{e.source_topic_id}_{e.target_topic_id}_{idx}",
                source=e.source_topic_id,
                target=e.target_topic_id,
            )
        )

    graph = GraphState(
        nodes=nodes,
        edges=edges,
        total_discovered_files=preview.total_discovered_files,
        indexed_count=preview.indexed_count,
        truncated=preview.truncated,
        skipped_files=preview.skipped_files,
        skipped_count=preview.skipped_count,
    )
    ws = WorkspaceModel(
        name=preview.project_name,
        root_path=preview.root_path,
        topics=domain_topics,
        edges=edges,
        total_discovered_files=preview.total_discovered_files,
        indexed_count=preview.indexed_count,
        truncated=preview.truncated,
        skipped_files=preview.skipped_files,
        skipped_count=preview.skipped_count,
    )
    return graph, ws
