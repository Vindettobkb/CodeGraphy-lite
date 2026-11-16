# CodeGraphy Lite 🌐

[![PyPI](https://img.shields.io/pypi/v/codegraphy-lite.svg?color=blue)](https://pypi.org/project/codegraphy-lite/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![MCP Spec](https://img.shields.io/badge/MCP-2024--11--05-green.svg)](https://modelcontextprotocol.io/)

> 🚀 **Try the Live Interactive Playground in your browser:** [codegraphy.software/#playground](https://codegraphy.software/#playground) *(No install required — runs 100% locally in web assembly)*

**CodeGraphy Lite** is the standalone open-source distribution of CodeGraphy. It provides an interactive visual architecture canvas, living dependency graphs, and Model Context Protocol (MCP) server for Python and modern software codebases.

Built for developers and AI agents (Claude Code, Cursor, Windsurf, Cline), CodeGraphy Lite turns messy codebases into an intuitive, navigable 2D architectural map while slashing LLM context input tokens by **-75.5%**.

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

CodeGraphy Lite includes a built-in MCP server that communicates over STDIO via `codegraphy-mcp` (JSON-RPC 2.0 / MCP 2024-11-05 standard).

### Available MCP Tools

1. `list_workspace_topics`: Lists all architectural topics, status, lane, file counts, and descriptions.
2. `get_topic_context`: Fetches topic details, 1-hop connected dependencies, and AST-extracted class/function signatures.
3. `get_architecture_summary`: Returns project architecture metrics, dependency statistics, and status distribution.

### Configuration for Cursor

In Cursor settings (`Cursor Settings -> Features -> MCP -> Add new MCP server`):

- **Name**: `codegraphy`
- **Type**: `command`
- **Command**: `codegraphy-mcp`

Or add directly to your project's `.cursor/mcp.json` or global configuration:

```json
{
  "mcpServers": {
    "codegraphy": {
      "command": "codegraphy-mcp"
    }
  }
}
```

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

---

## 📊 Empirical Token Benchmark (-75.5% Context Savings)

In an isolated comparative benchmark across 6 real-world closed bugfixes in major Python repositories (`encode/httpx`, `tiangolo/typer`, `Textualize/rich`), **CodeGraphy Lite reduced agent context input tokens by 75.5% (4.08x savings)** compared to standard keyword grep and whole-file reading:

| Mode | Input Tokens (`cl100k_base`) | Context Reduction | Acceptance Pass Rate | Tokens / Solved Task |
| :--- | :---: | :---: | :---: | :---: |
| **Baseline (Grep + Whole Files)** | 144,686 | *0.0% (ref)* | **100.0% (6/6)** | 24,114 |
| **CodeGraphy Lite MCP** | **35,457** | **-75.5% (4.1x savings)** | **100.0% (6/6)** | **5,909** |
| **CodeGraphy Pro (Desktop Ref)**\* | 64,348 | **-55.5% (2.25x savings)** | **100.0% (6/6)** | 10,724 |

*\*CodeGraphy Pro numbers reflect deep symbol graph index lookups and blast-radius impact analysis.*

👉 **Read the full benchmark methodology, task breakdowns, and honest limitations analysis in [benchmarks/BENCHMARK.md](benchmarks/BENCHMARK.md).**

---

## ⚖️ Lite vs Pro Comparison

CodeGraphy Lite is free and open-source (MIT). For larger codebases, polyglot repositories, and architectural drift protection, check out **[CodeGraphy Pro](https://codegraphy.software/#compare)**:

| Capability | CodeGraphy Lite (Free / OSS) | CodeGraphy Pro ($19 Lifetime) |
| :--- | :---: | :---: |
| **Pricing & License** | **Free (MIT License)** | **$19 Lifetime License** |
| **Visual Architecture Canvas** | ✅ Interactive 2D Canvas | ✅ Interactive 2D Canvas |
| **Workspace Export / Import** | ✅ Human-readable `.cg.md` | ✅ Human-readable `.cg.md` |
| **Project File Limit** | **35 files** (Ideal for packages & services) | **Unlimited** (Enterprise mono-repos) |
| **Supported Languages** | Python AST (`ast.parse()`) | **Polyglot** (Python, TS, JS, Go, Rust, C#, Java) |
| **MCP Server Tools** | **3 Core Tools** | **11 Industrial Intelligence Tools** |
| **Blast Radius & Impact Analysis** | ❌ None | ✅ Direct & Transitive Blast Radius Scoring |
| **Symbol Indexer** | Top-level signatures | ✅ Project-wide FQN symbol & reference index |
| **Architecture Linter & Drift** | ❌ None | ✅ Tarjan cycle detection & layer boundary checks |
| **Git Architecture Diff** | ❌ None | ✅ Visual PR & Branch architecture diff overlay |

👉 **Compare all features or get a license at [codegraphy.software/#compare](https://codegraphy.software/#compare).**

---

## ✨ Features

- 🗺️ **Unified Architecture Graph**: Interactive React Flow graph displaying modules, services, and dependency edges with real-time drag-and-drop layout.
- 🗂️ **Split Layers & Lanes**: Group architectural topics by workflow stage (`Planning`, `Development`, `Testing`, `Done`).
- 🔍 **Semantic Zoom**: Multi-level zoom with automatic Level-of-Detail (LOD)—zoom in to inspect function signatures and attached files, zoom out for high-level module topology.
- 📝 **Portable `.cg.md` Workspaces**: Human-readable Markdown workspace specification format with two-way import/export.
- ⚡ **Lightweight AST Scanner**: Fast project scanner using Python's standard library `ast.parse()` and regex import matching (scans up to 35 files).
- 🤖 **STDIO MCP Server (`codegraphy-mcp`)**: Exposes 3 essential architectural intelligence tools to AI assistants via JSON-RPC 2.0.
- 🔒 **100% Local-First & Private**: No cloud telemetry, no code uploads. Your codebase never leaves your machine.

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
├── benchmarks/             # Reproducible architecture benchmarks
│   ├── BENCHMARK.md        # Comprehensive 6-bug benchmark report
│   ├── run_benchmark.py    # Standalone benchmark runner (no machine-specific paths)
│   └── benchmark_results.json
├── codegraphy_lite/        # Core Python package
│   ├── __init__.py         # Version definition (1.0.1)
│   ├── cli.py              # `codegraphy-lite` CLI entrypoint
│   ├── mcp.py              # `codegraphy-mcp` STDIO JSON-RPC 2.0 server
│   ├── models.py           # Pydantic models for graph & workspace
│   ├── scanner.py          # Safe stdlib AST scanner (max 35 files)
│   ├── server.py           # FastAPI REST & WebSocket server
│   ├── storage.py          # Local persistence & .cg.md codec
│   └── web/                # Bundled visual UI assets
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
