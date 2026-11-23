"""CLI entrypoint for CodeGraphy Lite.

Usage:
    codegraphy-lite                  Start the MCP STDIO server (default)
    codegraphy-lite mcp              Start the MCP STDIO server
    codegraphy-lite serve [path]     Start the local web UI
"""

from __future__ import annotations

import argparse
import sys
import threading
import time
import webbrowser
from pathlib import Path
from typing import Optional, Sequence

import uvicorn

from codegraphy_lite import __version__
from codegraphy_lite.mcp import main as mcp_main
from codegraphy_lite.scanner import MAX_LITE_FILES, build_graph_and_workspace, scan_project
from codegraphy_lite.server import app
from codegraphy_lite.storage import get_storage_dir, load_graph, save_graph, save_workspace, set_active_root


def open_browser_later(url: str, delay_sec: float = 1.0):
    def _open():
        time.sleep(delay_sec)
        try:
            webbrowser.open(url)
        except Exception:
            pass

    t = threading.Thread(target=_open, daemon=True)
    t.start()


def _build_serve_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="codegraphy-lite serve",
        description="Run the CodeGraphy Lite web UI and REST API.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Target project directory to visualize (default: current directory)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="HTTP server port (default: 8000)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="HTTP server bind host (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not automatically launch the browser",
    )
    parser.add_argument(
        "--scan",
        action="store_true",
        help=f"Force automatic project directory scan on startup (up to {MAX_LITE_FILES} files)",
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"codegraphy-lite {__version__}",
    )
    return parser


def _run_serve(argv: Sequence[str]) -> None:
    parser = _build_serve_parser()
    args = parser.parse_args(list(argv))

    project_root = Path(args.path).resolve()
    if not project_root.exists() or not project_root.is_dir():
        print(f"Error: Directory '{project_root}' does not exist.", file=sys.stderr)
        raise SystemExit(1)

    set_active_root(project_root)

    # Check if graph exists; if not or if --scan requested, run Lite scanner
    get_storage_dir(project_root)
    existing_graph = load_graph(project_root)

    if args.scan or not existing_graph.nodes:
        print(f"[*] Scanning project architecture in '{project_root}' (Lite limit: max {MAX_LITE_FILES} files)...")
        try:
            preview = scan_project(project_root)
            graph, ws = build_graph_and_workspace(preview)
            save_graph(graph, project_root)
            save_workspace(ws, project_root)
            print(f"[+] Discovered {preview.total_files} files, {len(graph.nodes)} topics, {len(graph.edges)} dependency edges.")
        except Exception as e:
            print(f"[!] Warning: Initial project scan skipped ({e})", file=sys.stderr)

    url = f"http://{args.host}:{args.port}"
    print(f"\n=======================================================")
    print(f"  CodeGraphy Lite v{__version__} (Open Source Edition)")
    print(f"  Visual Architecture Canvas & MCP Server")
    print(f"  Project Root: {project_root}")
    print(f"  Web UI:       {url}")
    print(f"=======================================================\n")

    if not args.no_browser:
        open_browser_later(url, delay_sec=0.8)

    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


def _print_help() -> None:
    print(
        "CodeGraphy Lite — open-source architecture graph and MCP server.\n"
        "\n"
        "Usage:\n"
        "  codegraphy-lite                 Start the MCP STDIO server (default)\n"
        "  codegraphy-lite mcp             Start the MCP STDIO server\n"
        "  codegraphy-lite serve [path]    Start the local web UI (default path: .)\n"
        "  codegraphy-lite --version       Show the installed version\n"
        "\n"
        "Run 'codegraphy-lite serve --help' for web UI options."
    )


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = list(sys.argv[1:] if argv is None else argv)

    if "mcp" in Path(sys.argv[0]).stem.lower():
        mcp_main()
        return

    if not args:
        mcp_main()
        return

    command = args[0]
    if command == "mcp":
        if len(args) > 1 and args[1] in ("-h", "--help"):
            print("Usage: codegraphy-lite mcp\n\nStart the MCP STDIO server (JSON-RPC 2.0).")
            return
        mcp_main()
        return
    if command == "--mcp":
        mcp_main()
        return
    if command in ("-h", "--help"):
        _print_help()
        return
    if command in ("-v", "--version"):
        print(f"codegraphy-lite {__version__}")
        return
    if command == "serve":
        _run_serve(args[1:])
        return

    # Backward-compatible legacy invocation: options or a path start the web UI.
    _run_serve(args)


if __name__ == "__main__":
    main()
