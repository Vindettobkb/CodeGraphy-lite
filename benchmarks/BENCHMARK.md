# CodeGraphy Lite vs Baseline: Empirical Architecture Benchmark

Empirical evaluation of LLM context token consumption, bug localization efficiency, and pytest pass rates across **6 real-world bugfixes** in major Python repositories (`encode/httpx`, `tiangolo/typer`, `Textualize/rich`).

---

## 📊 Executive Summary

| Mode | Total Input Tokens (`cl100k_base`) | Context Reduction vs Baseline | Acceptance Pass Rate | Tokens / Solved Task | Avg Tool Calls / Task | Avg Iterations |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline (Grep + Whole Files)** | 144,686 | *0.0% (Reference)* | **100.0% (6/6)** | 24,114 | 7.7 | 1.0 |
| **CodeGraphy Lite MCP (Open Source)** | **35,457** | **-75.5% (4.08x savings)** | **100.0% (6/6)** | **5,909** | **6.7** | 1.0 |
| **CodeGraphy Pro (Desktop Reference)**\* | 64,348 | **-55.5% (2.25x savings)** | **100.0% (6/6)** | 10,724 | 8.5 | 1.0 |

*\*Note: CodeGraphy Pro numbers are reference results from the commercial desktop engine, which runs deep symbol graph indexing (`find_symbol`), afferent/efferent contract analysis (`get_module_context`), and blast radius calculation (`analyze_impact`).*

---

## 🔬 Benchmark Methodology

Modern AI agents (Claude Code, Cursor, Windsurf, Cline) typically locate and fix bugs in codebases using one of three workflows:

1. **Mode A: Baseline (Unstructured Text Search)**
   - The agent inspects the failing pytest error message.
   - It performs broad keyword `grep` searches across the workspace.
   - It reads entire candidate `.py` files into the context window (monolithic 300–1,500 line files).
   - *Result*: Massive context window flooding with irrelevant implementation details.

2. **Mode B: CodeGraphy Lite MCP (AST Skeletons & 1-Hop Graph)**
   - The agent queries `list_workspace_topics` to discover module hierarchy.
   - It retrieves compact AST signatures via `get_topic_context(topic=..., include_ast=True)` (extracts function/class signatures, parameters, and docstrings).
   - It reads only surgical ~60-line code blocks around the target signature rather than the entire file.
   - *Result*: **-75.5% token reduction** with identical 100% bug resolution.

3. **Mode C: CodeGraphy Pro (Desktop Reference)**
   - Leverages full symbol indexing across unlimited files, bidirectional dependency cruiser, and blast radius calculation before code modification.

### Strict Isolation Rules
- Every test run starts with a clean `git checkout -f <parent_commit>` (pre-fix code).
- Only the newly added/modified acceptance test file (`test_*.py`) from the fix commit is present.
- Every pre-fix test **MUST FAIL** before any context gathering or patch application.
- All tokens are calculated using OpenAI's `tiktoken` library with `cl100k_base` encoding.

---

## 🎯 Test Tasks (6 Real-World Closed Bugs)

| Task ID | Repository | Commit Hash | Title & Root Cause | Affected Source Files | Acceptance Pytest Suite |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **HTTPX-1** | `encode/httpx` | [`1e11096`](https://github.com/encode/httpx/commit/1e110964736a95d822144390b99d7ecf17fca527) | **Fixed `iter_text` adding an empty string (#2998)**<br>`TextChunker.decode("")` returned `[""]` instead of `[]`. | `httpx/_decoders.py`<br>`httpx/_models.py` | `tests/test_decoders.py::test_streaming_text_decoder` |
| **HTTPX-2** | `encode/httpx` | [`ba2e512`](https://github.com/encode/httpx/commit/ba2e51215e4e619540f2a24282b84ed8a738e6fd) | **Review urlescape percent-safe set, form spaces (#3373)**<br>Form space encoding in query params switched from `%20` to `+`. | `httpx/_urlparse.py`<br>`httpx/_urls.py` | `tests/models/test_url.py::test_param_with_space` |
| **TYPER-1** | `tiangolo/typer` | [`1edb599`](https://github.com/tiangolo/typer/commit/1edb5992937bd777bd8dddc0c72d9bb66534dada) | **Fix `TYPER_USE_RICH` parsing to disable Rich (#1539)**<br>Boolean env var parsing failed on `"0"`, `"False"`, `"false"`. | `typer/core.py`<br>`typer/utils.py` | `tests/test_rich_markup_mode.py::test_rich_markup_mode_envvar` |
| **TYPER-2** | `tiangolo/typer` | [`23665f4`](https://github.com/tiangolo/typer/commit/23665f4046afa9ac75f8851affaab2541d74825a) | **Ensure default `rich_markup_mode` is interpreted correctly (#1304)**<br>`Default(DEFAULT_MARKUP_MODE)` stored `DefaultPlaceholder` instead of `"rich"`. | `typer/main.py`<br>`typer/rich_utils.py` | `tests/test_rich_markup_mode.py::test_markup_mode_default` |
| **RICH-1** | `Textualize/rich` | [`59b1aca`](https://github.com/Textualize/rich/commit/59b1aca63bf9ec69ada93af960d8b2a7bd920477) | **Fix double-width characters disappearing when wrapping (#3180)**<br>Double-width CJK characters folded mid-cell were dropped. | `rich/_wrap.py`<br>`rich/cells.py` | `tests/test_text.py::test_wrap_cjk_mixed` |
| **RICH-2** | `Textualize/rich` | [`32def19`](https://github.com/Textualize/rich/commit/32def19a2a9f8bf9333a9b41ecbdc23b98b9765a) | **Fix default `ensure_ascii` value to match docs (#2566)**<br>`print_json` defaulted to `ensure_ascii=True`, escaping emojis like 💩. | `rich/__init__.py`<br>`rich/console.py`<br>`rich/json.py` | `tests/test_console.py::test_print_json_with_default_ensure_ascii` |

---

## 📈 Detailed Token Breakdown by Task (`cl100k_base`)

| Task ID | Baseline (Grep + Whole Files) | CodeGraphy Lite MCP | Lite Savings vs Baseline | CodeGraphy Pro (Reference) |
| :--- | :---: | :---: | :---: | :---: |
| **HTTPX-1** | 25,993 | **5,996** | **-76.9%** | 8,367 |
| **HTTPX-2** | 25,073 | **6,019** | **-76.0%** | 18,262 |
| **TYPER-1** | 27,211 | **4,849** | **-82.2%** | 5,639 |
| **TYPER-2** | 22,171 | **3,948** | **-82.2%** | 6,959 |
| **RICH-1** | 13,615 | **5,327** | **-60.9%** | 11,621 |
| **RICH-2** | 30,623 | **9,318** | **-69.6%** | 13,500 |
| **TOTAL** | **144,686** | **35,457** | **-75.49%** | **64,348** |

---

## ⚠️ Known Limitations of Static AST Architecture Graphs

While AST-based graphs cut context costs by **4.1x**, static analysis alone has inherent boundaries. During this benchmark, two concrete limitations were observed:

### 1. Dynamic Environment Variables & In-Function Lazy Imports
- **Case Study**: Typer Task 1 (`#1539`)
- **What happened**: Terminal rendering in `typer` depends dynamically on `os.environ.get("TYPER_USE_RICH")` inside `typer/utils.py`. Meanwhile, `typer/core.py` performs in-function deferred imports (`from . import rich_utils` inside command handlers) rather than top-level module imports.
- **The Blind Spot**: A purely static AST import crawler inspects module-level `import` statements. Because the connection between `typer/utils.py` and `typer/core.py` is mediated by a runtime environment variable and deferred function calls, static AST edge detection cannot infer that modifying environment variable parsing impacts command formatting without dynamic runtime tracing.

### 2. The Open-Source 35-File Safety Limit (`MAX_LITE_FILES`)
- **Case Study**: Rich Task 2 (`#2566`)
- **What happened**: `Textualize/rich` is a large repository containing over 80+ `.py` modules and numerous localized `README.*.md` files. CodeGraphy Lite includes a safety cap (`MAX_LITE_FILES = 35`) designed for small-to-medium modules.
- **The Blind Spot**: When scanning from repository root alphabetically, Lite encountered documentation and early module files (`_cell_widths.py` through `diagnose.py`), reaching its 35-file ceiling before indexing `rich/json.py`. When an agent asked for `get_topic_context(topic='json')`, Lite responded with `Topic 'json' not found in workspace`.
- **The Solution**: For large multi-file packages and monorepos, point `codegraphy-lite` directly at the specific package subfolder (e.g. `codegraphy-lite rich/`), or use **CodeGraphy Pro**, which removes the file limit, indexes unlimited files, and supports fuzzy symbol indexing across entire workspaces.

---

## 🔁 Reproducing This Benchmark

You can reproduce these exact metrics locally with zero external dependencies:

```bash
# 1. Clone codegraphy-lite and install dependencies
git clone https://github.com/codegraphy-dev/codegraphy-lite.git
cd codegraphy-lite
pip install -e ".[test]"
pip install tiktoken

# 2. Run the reproducible benchmark suite
# (Clones httpx, typer, and rich into a local ./benchmark_repos folder)
python benchmarks/run_benchmark.py --setup
```

The runner generates `benchmarks/benchmark_results.json` containing raw token counts, tool invocations, and pytest logs.
