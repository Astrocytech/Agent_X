import pytest
from pathlib import Path
from agentx_evolve.monitoring.jsonl_reader import read_jsonl, iter_jsonl, count_jsonl, filter_jsonl, read_jsonl_slice


class TestMonitoringJsonlReader:
    def test_read_empty_jsonl(self, tmp_path):
        f = tmp_path / "data.jsonl"
        f.write_text("")
        result = read_jsonl(f)
        assert result == []

    def test_read_single_line(self, tmp_path):
        f = tmp_path / "data.jsonl"
        f.write_text('{"a": 1}\n')
        result = read_jsonl(f)
        assert result == [{"a": 1}]

    def test_count_jsonl(self, tmp_path):
        f = tmp_path / "data.jsonl"
        f.write_text('{"a": 1}\n{"b": 2}\n')
        assert count_jsonl(f) == 2

    def test_filter_jsonl(self, tmp_path):
        f = tmp_path / "data.jsonl"
        f.write_text('{"type": "A"}\n{"type": "B"}\n')
        result = filter_jsonl(f, lambda r: r.get("type") == "A")
        assert result == [{"type": "A"}]

    def test_read_slice(self, tmp_path):
        f = tmp_path / "data.jsonl"
        f.write_text("\n".join(f'{{"i": {i}}}' for i in range(10)))
        result = read_jsonl_slice(f, offset=0, limit=3)
        assert len(result) == 3
