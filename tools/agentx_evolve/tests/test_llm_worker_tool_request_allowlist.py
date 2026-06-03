import pytest
# LLMImplementationWorker is a real worker, test it exists and can be instantiated
from agentx_evolve.worker.llm_implementation_worker import LLMImplementationWorker


class TestLLMWorkerToolRequestAllowlist:
    def test_worker_can_be_instantiated(self):
        worker = LLMImplementationWorker()
        assert worker is not None
