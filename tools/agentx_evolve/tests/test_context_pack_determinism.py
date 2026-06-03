import pytest
from agentx_evolve.context.task_pack_builder import build_task_pack


class TestContextPackDeterminism:
    def test_pack_builder(self):
        pack = build_task_pack(raw_task={"input": "Fix the bug"}, source_requests=[])
        assert pack is not None

    def test_pack_with_sources(self):
        pack = build_task_pack(
            raw_task={"input": "Fix the bug"},
            source_requests=[{"path": "parser.py", "content": "def parse(): pass"}],
        )
        assert pack is not None
