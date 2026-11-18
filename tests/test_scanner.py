"""Unit tests for CodeGraphy Lite AST Scanner."""

import os
import tempfile
from pathlib import Path

from codegraphy_lite.scanner import (
    MAX_LITE_FILES,
    build_graph_and_workspace,
    collect_project_files,
    extract_ast_signatures,
    extract_imports_from_js_ts,
    extract_imports_from_python,
    scan_project,
)


def test_extract_ast_signatures():
    sample_code = '''
"""Module docstring."""

class UserService:
    """Service handling users."""
    def __init__(self, db_client: str):
        self.db = db_client

    async def get_user(self, user_id: int) -> dict:
        return {"id": user_id}

def helper_func(x: int) -> bool:
    """Helper check."""
    return x > 0
'''
    signatures = extract_ast_signatures(sample_code)
    assert "class UserService:" in signatures
    assert "def __init__(self, db_client: str): ..." in signatures
    assert "async def get_user(self, user_id: int) -> dict: ..." in signatures
    assert "def helper_func(x: int) -> bool:" in signatures
    assert '"""Module docstring."""' in signatures
    assert '"""Service handling users."""' in signatures


def test_extract_imports_from_python():
    code = """
import os
import sys
from app.models import User, Order
from pathlib import Path
"""
    imports = extract_imports_from_python(code)
    assert "os" in imports
    assert "sys" in imports
    assert "app.models" in imports
    assert "pathlib" in imports


def test_extract_imports_from_js_ts():
    code = """
import React, { useState } from 'react';
import { api } from './api';
const utils = require('../utils/helpers');
"""
    imports = extract_imports_from_js_ts(code)
    assert "react" in imports
    assert "api" in imports or "utils/helpers" in imports


def test_scanner_file_limit():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        # Create 160 dummy python files
        for i in range(160):
            f = tmppath / f"module_{i:02d}.py"
            f.write_text(f"def func_{i}(): pass\n", encoding="utf-8")

        assert MAX_LITE_FILES == 150

        files, _ = collect_project_files(tmppath, max_files=MAX_LITE_FILES)
        assert len(files) == MAX_LITE_FILES
        assert len(files) == 150

        preview = scan_project(tmppath)
        assert preview.total_files == 150
        assert len(preview.topics) == 150
        assert preview.truncated is True
        assert preview.total_discovered_files == 160
        assert preview.indexed_count == 150
        assert preview.skipped_count == 10
        assert len(preview.skipped_files) == 10


def test_scanner_exactly_150_files_no_truncation():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        for i in range(150):
            (tmppath / f"module_{i:03d}.py").write_text("x = 1\n", encoding="utf-8")

        preview = scan_project(tmppath)
        assert preview.truncated is False
        assert preview.total_discovered_files == 150
        assert preview.indexed_count == 150
        assert preview.skipped_count == 0
        assert preview.skipped_files == []


def test_scanner_under_limit_no_truncation():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        for i in range(12):
            (tmppath / f"component_{i:02d}.py").write_text("x = 1\n", encoding="utf-8")

        preview = scan_project(tmppath)
        assert preview.truncated is False
        assert preview.total_discovered_files == 12
        assert preview.indexed_count == 12
        assert preview.skipped_count == 0
        assert preview.skipped_files == []

        graph, ws = build_graph_and_workspace(preview)
        assert graph.truncated is False
        assert graph.total_discovered_files == 12
        assert graph.indexed_count == 12
        assert graph.skipped_files == []
        assert ws.truncated is False
        assert ws.total_discovered_files == 12


def test_scanner_skipped_files_capped_at_100():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        for i in range(260):
            (tmppath / f"file_{i:03d}.py").write_text("pass\n", encoding="utf-8")

        preview = scan_project(tmppath)
        assert preview.truncated is True
        assert preview.total_discovered_files == 260
        assert preview.indexed_count == 150
        assert preview.skipped_count == 110
        assert len(preview.skipped_files) == 100


def test_scanner_build_graph():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        f_models = tmppath / "models.py"
        f_models.write_text("class User: pass\n", encoding="utf-8")

        f_service = tmppath / "service.py"
        f_service.write_text("from models import User\nclass UserService: pass\n", encoding="utf-8")

        preview = scan_project(tmppath)
        assert preview.total_files == 2
        assert len(preview.topics) == 2
        assert len(preview.edges) == 1

        edge = preview.edges[0]
        assert "service" in edge.source_topic_id
        assert "models" in edge.target_topic_id

        graph, ws = build_graph_and_workspace(preview)
        assert len(graph.nodes) == 2
        assert len(graph.edges) == 1
        assert len(ws.topics) == 2
