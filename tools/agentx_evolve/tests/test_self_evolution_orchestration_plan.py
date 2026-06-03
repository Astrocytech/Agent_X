import sys
import pytest
sys.path.insert(0, ".")
pytest.main(["-x", "tools/agentx_evolve/tests/test_task_decomposer.py", "--tb=short"])
