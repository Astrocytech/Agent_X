import pytest
from agentx_evolve.learning.memory_lifecycle import MemoryLifecycle, transition, MC_CANDIDATE, MC_ACTIVE


class TestMemoryRetentionRevocation:
    def test_memory_lifecycle_defaults(self):
        mem = MemoryLifecycle(memory_id="test")
        assert mem.memory_id == "test"
        assert mem.status == MC_CANDIDATE

    def test_transition(self):
        mem = MemoryLifecycle(memory_id="test")
        result = transition(mem, MC_ACTIVE)
        assert result.status == MC_ACTIVE
