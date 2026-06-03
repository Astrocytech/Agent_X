import sys
import pytest
sys.path.insert(0, ".")
pytest.main(["-x", "tools/agentx_evolve/tests/test_tool_invoker.py", "--tb=short"])
