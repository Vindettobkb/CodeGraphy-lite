"""Model Context Protocol (MCP) STDIO Server for CodeGraphy Lite.

Exposes 3 basic workspace/graph architectural tools to Claude Code, Cursor, Windsurf,
and agentic coding assistants via standard JSON-RPC 2.0 over STDIO.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from codegraphy_lite import __version__
from codegraphy_lite.models import GraphState, WorkspaceModel
from codegraphy_lite.scanner import extract_ast_signatures
from codegraphy_lite.storage import get_active_root, load_graph, load_workspace, set_active_root

PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "codegraphy-lite-mcp"
MAX_PAYLOAD_CHARS = 32000

SECRET_PATTERNS = [
    re.compile(r"\b(?:sk|whsec)_[a-zA-Z0-9_\-]{16,}\b"),
    re.compile(r"\bsk-(?:live|test|ant|proj)?[a-zA-Z0-9_\-]{16,}\b"),
    re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b"),
    re.compile(r"\bghp_[0-9a-zA-Z]{36}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
]


def scrub_secrets(val: Any) -> Any:
    """Redacts potential API tokens and keys."""
    if isinstance(val, str):
        text = val
        for pat in SECRET_PATTERNS:
            text = pat.sub("[REDACTED_SECRET]", text)
        return text
    if isinstance(val, dict):
        return {k: scrub_secrets(v) for k, v in val.items()}
    if isinstance(val, list):
        return [scrub_secrets(item) for item in val]
    return val


TOOLS_MANIFEST = [
    {
        "name": "list_workspace_topics",
        "description": "Lists all architectural topics/nodes in the workspace with their status, lanes, attached files, descriptions, and file truncation metadata (35-file limit).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["all", "todo", "in_progress", "done"],
                    "description": "Filter topics by status (default: all)",
                }
            },
        },
    },
    {
        "name": "get_topic_context",
        "description": "Retrieves comprehensive architectural context for a topic, including 1-hop connected dependencies and AST-extracted signatures from attached files.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Topic ID or label to inspect",
                },
                "include_ast": {
                    "type": "boolean",
                    "description": "Whether to include AST-extracted class/function signatures (default: true)",
                    "default": True,
                },
            },
            "required": ["topic"],
        },
    },
    {
        "name": "get_architecture_summary",
        "description": "Returns a high-level architectural overview: total topics, dependency edges, lanes, status distribution, and key architectural modules.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
]


class CodeGraphyLiteMCP:
    def __init__(self, root_dir: Optional[str | Path] = None) -> None:
        if root_dir:
            set_active_root(root_dir)
        elif "CODEGRAPHY_ROOT" in os.environ:
            set_active_root(os.environ["CODEGRAPHY_ROOT"])

    @property
    def root(self) -> Path:
        return get_active_root()

    def _get_truncation_metadata(self, graph: GraphState) -> Tuple[bool, int, int, List[str], int]:
        """Returns (truncated, indexed_count, total_discovered_files, skipped_files, skipped_count)."""
        if graph.total_discovered_files > 0 or graph.truncated:
            return (
                graph.truncated,
                graph.indexed_count or len(graph.nodes),
                graph.total_discovered_files,
                graph.skipped_files,
                graph.skipped_count or len(graph.skipped_files),
            )

        if self.root.exists() and self.root.is_dir():
            try:
                from codegraphy_lite.scanner import MAX_LITE_FILES, collect_project_files
                collect_res = collect_project_files(self.root, max_files=MAX_LITE_FILES)
                total_discovered = collect_res.total_discovered
                indexed = len(graph.nodes) if graph.nodes else len(collect_res.collected)
                truncated = total_discovered > MAX_LITE_FILES
                skipped_paths = collect_res.skipped
                skipped_count = len(skipped_paths)
                skipped_files = [p.relative_to(self.root).as_posix() for p in skipped_paths[:100]]
                return truncated, indexed, total_discovered, skipped_files, skipped_count
            except Exception:
                pass

        total = len(graph.nodes)
        return False, total, total, [], 0

    def handle_list_workspace_topics(self, args: Dict[str, Any]) -> Dict[str, Any]:
        graph = load_graph(self.root)
        status_filter = args.get("status", "all")

        topics = []
        for n in graph.nodes:
            d = n.data
            if status_filter != "all" and d.status != status_filter:
                continue

            incoming = sum(1 for e in graph.edges if e.target == n.id)
            outgoing = sum(1 for e in graph.edges if e.source == n.id)
            files = [f.filepath for f in d.attached_files]

            topics.append({
                "id": n.id,
                "label": d.label,
                "status": d.status,
                "lane_id": d.lane_id,
                "description": d.description,
                "files_count": len(files),
                "files": files,
                "incoming_dependencies": incoming,
                "outgoing_dependencies": outgoing,
            })

        truncated, indexed_count, total_discovered_files, skipped_files, skipped_count = self._get_truncation_metadata(graph)

        res: Dict[str, Any] = {
            "root_path": str(self.root),
            "total_topics": len(topics),
            "topics": topics,
            "truncated": truncated,
            "indexed_count": indexed_count,
            "total_discovered_files": total_discovered_files,
        }
        if truncated:
            res["skipped_files"] = skipped_files
            res["skipped_count"] = skipped_count

        return res

    def handle_get_topic_context(self, args: Dict[str, Any]) -> Dict[str, Any]:
        query = args.get("topic", "").strip().lower()
        if not query:
            raise ValueError("Parameter 'topic' is required.")
        include_ast = args.get("include_ast", True)

        graph = load_graph(self.root)
        target = None
        for n in graph.nodes:
            if n.id.lower() == query or n.data.label.lower() == query:
                target = n
                break

        if not target:
            truncated, indexed_count, total_discovered_files, skipped_files, skipped_count = self._get_truncation_metadata(graph)
            if truncated:
                matching = []
                for p in skipped_files:
                    p_lower = p.lower()
                    stem_lower = Path(p).stem.lower()
                    if query in p_lower or query == stem_lower or query in stem_lower:
                        matching.append(p)

                msg = (
                    f"Topic '{query}' not found in indexed workspace. "
                    f"CodeGraphy Lite 35-file limit reached ({indexed_count}/{total_discovered_files} files indexed, {skipped_count} skipped)."
                )
                if matching:
                    matches_list = ", ".join(f"'{m}'" for m in matching[:5])
                    suggested_dir = Path(matching[0]).parent.as_posix()
                    dir_hint = f"'{suggested_dir}'" if suggested_dir and suggested_dir != "." else "that specific subfolder"
                    msg += (
                        f" Found matching unindexed file(s) in skipped_files: {matches_list}. "
                        f"Please re-scope your root path (CODEGRAPHY_ROOT) to {dir_hint} to index and analyze this subpackage."
                    )
                else:
                    msg += (
                        " The requested module may be among the unindexed files excluded by the 35-file cap. "
                        "Please re-scope your root path (CODEGRAPHY_ROOT) to the specific subpackage/subfolder of interest."
                    )
                raise ValueError(msg)

            raise ValueError(f"Topic '{query}' not found in workspace.")

        # Dependencies
        incoming_ids = [e.source for e in graph.edges if e.target == target.id]
        outgoing_ids = [e.target for e in graph.edges if e.source == target.id]

        def resolve_label(nid: str) -> str:
            m = next((x.data.label for x in graph.nodes if x.id == nid), nid)
            return m

        # Files & AST signatures
        files_data = []
        for f in target.data.attached_files:
            file_info: Dict[str, Any] = {"filepath": f.filepath}
            full_p = self.root / f.filepath
            if full_p.exists() and full_p.is_file():
                file_info["exists"] = True
                if include_ast:
                    try:
                        content = full_p.read_text(encoding="utf-8", errors="ignore")
                        file_info["signatures"] = extract_ast_signatures(content)
                    except Exception as e:
                        file_info["signatures"] = f"# Error extracting AST: {e}"
            else:
                file_info["exists"] = False
                file_info["signatures"] = "# File not found on disk"
            files_data.append(file_info)

        return {
            "topic_id": target.id,
            "label": target.data.label,
            "status": target.data.status,
            "description": target.data.description,
            "connected_dependencies": {
                "incoming": [resolve_label(x) for x in incoming_ids],
                "outgoing": [resolve_label(x) for x in outgoing_ids],
            },
            "attached_files": files_data,
        }

    def handle_get_architecture_summary(self, args: Dict[str, Any]) -> Dict[str, Any]:
        graph = load_graph(self.root)
        ws = load_workspace(self.root)
        truncated, indexed_count, total_discovered_files, skipped_files, skipped_count = self._get_truncation_metadata(graph)

        status_counts = {"todo": 0, "in_progress": 0, "done": 0}
        for n in graph.nodes:
            st = n.data.status
            if st in status_counts:
                status_counts[st] += 1

        degree_map: Dict[str, int] = {}
        for e in graph.edges:
            degree_map[e.source] = degree_map.get(e.source, 0) + 1
            degree_map[e.target] = degree_map.get(e.target, 0) + 1

        top_components = sorted(
            [{"topic_id": k, "degree": v} for k, v in degree_map.items()],
            key=lambda x: x["degree"],
            reverse=True,
        )[:6]

        res = {
            "project_name": ws.name or self.root.name,
            "root_path": str(self.root),
            "edition": "CodeGraphy Lite (Open Source)",
            "total_topics": len(graph.nodes),
            "total_dependencies": len(graph.edges),
            "status_distribution": status_counts,
            "lanes": [l.title for l in ws.lanes],
            "top_connected_topics": top_components,
            "truncated": truncated,
            "indexed_count": indexed_count,
            "total_discovered_files": total_discovered_files,
            "pro_features_available": [
                "AST Smart Context (-85% tokens)",
                "Blast Radius (Reverse Impact)",
                "Test Impact Static Analysis",
                "Git Architecture Diff Overlay",
                "Full 11 MCP Tools Suite",
            ],
        }
        if truncated:
            res["skipped_files"] = skipped_files
            res["skipped_count"] = skipped_count

        return res

    def call_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        if name == "list_workspace_topics":
            return self.handle_list_workspace_topics(args)
        elif name == "get_topic_context":
            return self.handle_get_topic_context(args)
        elif name == "get_architecture_summary":
            return self.handle_get_architecture_summary(args)
        else:
            raise ValueError(
                f"Unknown or proprietary tool '{name}'. "
                "CodeGraphy Lite includes 3 core workspace tools. "
                "Upgrade to CodeGraphy Pro for the full 11-tool suite."
            )

    def dispatch(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        req_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": PROTOCOL_VERSION,
                    "serverInfo": {
                        "name": SERVER_NAME,
                        "version": __version__,
                    },
                    "capabilities": {
                        "tools": {"listChanged": False},
                    },
                },
            }
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": TOOLS_MANIFEST},
            }
        elif method == "tools/call":
            tool_name = params.get("name")
            args = params.get("arguments", {})
            try:
                raw_res = self.call_tool(tool_name, args)
                scrubbed = scrub_secrets(raw_res)
                text_out = json.dumps(scrubbed, indent=2, ensure_ascii=False)
                if len(text_out) > MAX_PAYLOAD_CHARS:
                    text_out = text_out[:MAX_PAYLOAD_CHARS] + "\n... [Payload truncated for Lite MCP]"
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": text_out}],
                        "isError": False,
                    },
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": f"Error: {str(e)}"}],
                        "isError": True,
                    },
                }
        elif method == "ping":
            return {"jsonrpc": "2.0", "id": req_id, "result": {}}
        elif method in ("notifications/initialized", "$/cancelRequest"):
            return None
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        }


def run_stdio_server():
    server = CodeGraphyLiteMCP()
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            req = json.loads(line)
            res = server.dispatch(req)
            if res is not None:
                sys.stdout.write(json.dumps(res, ensure_ascii=False) + "\n")
                sys.stdout.flush()
        except (KeyboardInterrupt, SystemExit):
            break
        except Exception as e:
            err_res = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": f"MCP STDIO Server Error: {str(e)}"},
            }
            sys.stdout.write(json.dumps(err_res) + "\n")
            sys.stdout.flush()


def main():
    run_stdio_server()


if __name__ == "__main__":
    main()
