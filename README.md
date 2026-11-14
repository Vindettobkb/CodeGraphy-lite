# CodeGraphy Lite 🌐

[![PyPI](https://img.shields.io/pypi/v/codegraphy-lite.svg?color=blue)](https://pypi.org/project/codegraphy-lite/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![MCP Spec](https://img.shields.io/badge/MCP-2024--11--05-green.svg)](https://modelcontextprotocol.io/)

**CodeGraphy Lite** is the standalone open-source distribution of CodeGraphy. It provides an interactive visual architecture canvas, living dependency graphs, and Model Context Protocol (MCP) server for Python and modern software codebases.

Built for developers and AI agents (Claude Code, Cursor, Windsurf, Cline), CodeGraphy Lite turns messy codebases into an intuitive, navigable 2D architectural map.

---

## ✨ Features (1:1 Visual Parity)

- 🗺️ **Unified Architecture Graph**: Interactive React Flow graph displaying modules, services, and dependency edges with real-time drag-and-drop layout.
- 🗂️ **Split Layers & Lanes**: Group architectural topics by workflow stage (`Planning`, `Development`, `Testing`, `Done`).
- 🔍 **Semantic Zoom**: Multi-level zoom with automatic Level-of-Detail (LOD)—zoom in to inspect function signatures and attached files, zoom out for high-level module topology.
- 📝 **Portable `.cg.md` Workspaces**: Human-readable Markdown workspace specification format with two-way import/export.
- ⚡ **Lightweight AST Scanner**: Fast project scanner using Python's standard library `ast.parse()` and regex import matching (scans up to 35 files).
- 🤖 **STDIO MCP Server (`codegraphy-mcp`)**: Exposes 3 essential architectural intelligence tools to AI assistants via JSON-RPC 2.0.
- 🔒 **100% Local-First & Private**: No cloud telemetry, no code uploads. Your codebase never leaves your machine.

---

## ⚖️ Lite vs Pro Comparison

CodeGraphy Lite is fully open-source (MIT). For enterprise repositories, multi-language AST pruning, and deep impact analysis, check out **CodeGraphy Pro**:

| Capability | CodeGraphy Lite (Open Source) | CodeGraphy Pro (Commercial) |
| :--- | :---: | :---: |
| **License** | **MIT (Open Source)** | Commercial / Enterprise |
| **Visual Architecture Canvas** | ✅ Full Visual UI | ✅ Full Visual UI |
| **Split Layers & Semantic Zoom** | ✅ Yes | ✅ Yes |
| **`.cg.md` Workspace Import/Export** | ✅ Yes | ✅ Yes |
| **Max Scanned Files** | **35 files** | **Unlimited** (Multi-repo) |
| **AST Parser** | Python stdlib `ast.parse()` | Proprietary Polyglot AST Engine (PY/TS/GO/RS/C#/JAVA) |
| **Token Optimization** | Standard AST Signatures | **AST Smart Context (-85% Token Reduction)** |
| **Context Inspector** | Basic Preview | **Hybrid Context Inspector (Full / AST / Exclude)** |
| **Blast Radius Analysis** | — *(PRO Badge)* | ✅ Reverse Call Graph Impact Scoring |
| **Test Impact Engine** | — *(PRO Badge)* | ✅ Selective Test Discovery & Safe Runner |
| **Git Architecture Diff** | — *(PRO Badge)* | ✅ Branch/PR Visual Architecture Diff Overlay |
| **MCP Tools** | **3 Core Tools** | **Full 11-Tool Suite** |

---

## 🚀 Quickstart

### 1. Installation

Install via pip:

```bash
pip install codegraphy-lite
```

Or install from source for development:

```bash
git clone https://github.com/codegraphy-dev/codegraphy-lite.git
cd codegraphy-lite
pip install -e .
```

### 2. Launch the Web UI

Run `codegraphy-lite` pointing to any project directory:

```bash
# Scan and visualize the current directory
codegraphy-lite

# Or specify a directory and custom port
codegraphy-lite /path/to/my-project --port 8000
```

The server automatically scans the project (up to 35 files) and opens `http://127.0.0.1:8000` in your default web browser.

---

## 🤖 Model Context Protocol (MCP) Setup

CodeGraphy Lite includes a built-in MCP server that communicates over STDIO using the `codegraphy-mcp` CLI.

### Available MCP Tools

1. `list_workspace_topics`: Lists all architectural topics, status, lane, files count, and descriptions.
2. `get_topic_context`: Fetches topic details, 1-hop connected dependencies, and AST-extracted class/function signatures.
3. `get_architecture_summary`: Returns project architecture metrics, dependency statistics, and status distribution.

### Configuration for Claude Code

Add the following to your Claude Code configuration (`~/.claude.json` or project `.mcp.json`):

```json
{
  "mcpServers": {
    "codegraphy": {
      "command": "codegraphy-mcp",
      "env": {
        "CODEGRAPHY_ROOT": "/absolute/path/to/your/project"
      }
    }
  }
}
```

### Configuration for Cursor

In Cursor settings (`Cursor Settings -> Features -> MCP -> Add new MCP server`):

- **Name**: `codegraphy`
- **Type**: `command`
- **Command**: `codegraphy-mcp`

Or add to your Cursor configuration file:

```json
{
  "mcpServers": {
    "codegraphy": {
      "command": "codegraphy-mcp"
    }
  }
}
```

---

## 🛠️ CLI Reference

```
usage: codegraphy-lite [-h] [--port PORT] [--host HOST] [--no-browser] [--scan] [-v] [path]

CodeGraphy Lite — Standalone Open-Source Visual Architecture Graph & MCP Server

positional arguments:
  path                  Target project directory to visualize (default: current directory)

options:
  -h, --help            Show this help message and exit
  --port PORT           HTTP server port (default: 8000)
  --host HOST           HTTP server bind host (default: 127.0.0.1)
  --no-browser          Do not automatically launch the browser
  --scan                Force automatic project directory scan on startup (up to 35 files)
  -v, --version         Show program's version number and exit
```

---

## 📁 Repository Structure

```
codegraphy-lite/
├── LICENSE                 # MIT License
├── README.md               # Documentation
├── pyproject.toml          # PEP 517/621 package metadata & entrypoints
├── MANIFEST.in             # Manifest for sdist packaging
├── .gitignore              # Git ignore rules
├── codegraphy_lite/        # Core Python package
│   ├── __init__.py         # Version definition (1.0.0)
│   ├── cli.py              # `codegraphy-lite` CLI entrypoint
│   ├── mcp.py              # `codegraphy-mcp` STDIO JSON-RPC 2.0 server
│   ├── models.py           # Pydantic models for graph & workspace
│   ├── scanner.py          # Safe stdlib AST scanner (max 35 files)
│   ├── server.py           # FastAPI REST & WebSocket server
│   ├── storage.py          # Local persistence & .cg.md codec
│   └── web/                # Bundled visual UI assets
│       ├── index.html
│       ├── assets/
│       │   ├── codegraphy-lite-ui.js   # Pro features & modal controller
│       │   ├── codegraphy-lite-ui.css  # Pro badges & modal styling
│       │   └── ...                     # Built React Flow assets
└── tests/                  # Unit test suite
    ├── test_scanner.py
    ├── test_mcp.py
    └── test_server.py
```

---

## 🧪 Running Tests

```bash
pip install -e ".[test]"
pytest tests/ -v
```

---

## 📄 License

CodeGraphy Lite is licensed under the [MIT License](LICENSE).
