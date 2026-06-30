from __future__ import annotations

import pytest
from pathlib import Path
from agentx_evolve.adapters.local_tool_adapter import LocalToolAdapter, LOCAL_TOOL_ADAPTER_ID, ALLOWED_TOOLS


class TestLocalToolAdapter:
    def setup_method(self):
        self.adapter = LocalToolAdapter()

    def test_describe_capabilities(self):
        caps = self.adapter.describe_capabilities()
        assert caps["adapter_id"] == LOCAL_TOOL_ADAPTER_ID
        assert caps["read_only"] is True
        assert caps["offline"] is True
        assert caps["deterministic"] is True

    def test_allowed_tools_include_read_repo_info(self):
        assert "read_repo_info" in ALLOWED_TOOLS
        assert "list_repo_files" in ALLOWED_TOOLS
        assert "read_file_content" in ALLOWED_TOOLS

    def test_list_repo_files_returns_files(self):
        result = self.adapter.execute_call({
            "tool_name": "list_repo_files",
            "arguments": {"pattern": "*"},
            "call_id": "c1", "run_id": "r1",
        })
        assert result["status"] == "SUCCESS"
        assert "files" in result["output"]

    def test_read_file_content_blocks_absolute_path(self):
        result = self.adapter.execute_call({
            "tool_name": "read_file_content",
            "arguments": {"file_path": "/etc/shadow"},
            "call_id": "c1", "run_id": "r1",
        })
        assert result["status"] == "DENIED"

    def test_read_repo_info_accepts_dot(self):
        result = self.adapter.execute_call({
            "tool_name": "read_repo_info",
            "arguments": {"path": "."},
            "call_id": "c1", "run_id": "r1",
        })
        assert result["status"] == "SUCCESS"

    def test_unknown_tool_denied(self):
        result = self.adapter.execute_call({
            "tool_name": "write_file",
            "arguments": {"path": "test.txt", "content": "x"},
            "call_id": "c1", "run_id": "r1",
        })
        assert result["status"] == "DENIED"

    def test_normalize_result_returns_normalized(self):
        raw = {"tool_name": "read_repo_info", "call_id": "c1",
               "status": "SUCCESS", "output": {"path": "."},
               "output_hash": "abc", "provenance": {"adapter_id": "local_read_only"}}
        normalized = self.adapter.normalize_result(raw)
        assert normalized["tool_name"] == "read_repo_info"
        assert normalized["output_hash"] == "abc"

    def test_simulate_call_delegates_to_execute(self):
        result = self.adapter.simulate_call({
            "tool_name": "read_repo_info",
            "arguments": {"path": "."},
            "call_id": "c1", "run_id": "r1",
        })
        assert result["status"] == "SUCCESS"
