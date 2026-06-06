# Backward-compat shim — runtime_limits moved to model_runtime/runtime_limits.py
from __future__ import annotations

from agentx_evolve.model_runtime.runtime_limits import (  # noqa: F401
    estimate_token_count,
    check_context_budget,
    truncate_for_evidence,
)
