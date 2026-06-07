from __future__ import annotations

from pathlib import Path
from typing import Any

from agentx_evolve.orchestrator.orchestrator_config import (
    DEPENDENCY_MODE_REAL,
    DEPENDENCY_MODE_FAKE_FOR_TEST,
    DEPENDENCY_MODE_RESTRICTED,
    DEPENDENCY_MODE_UNAVAILABLE,
    ALL_DEPENDENCY_MODES,
)


RESOLVED_BINDINGS: dict[str, Any] = {}


def _fake_tool_adapter(**kwargs: Any) -> dict:
    return {"status": "SUCCESS", "results": [], "mode": "fake_for_test"}


def _fake_model_adapter(**kwargs: Any) -> dict:
    return {
        "status": "SUCCESS",
        "safe_summary": "test model response",
        "raw_response_ref": '{"implementation_summary":"test","steps":[]}',
        "usage_summary": {},
        "mode": "fake_for_test",
    }


def _fake_policy_registry(**kwargs: Any) -> dict:
    return {"decision": "ALLOW", "mode": "fake_for_test"}


def _fake_prompt_registry(**kwargs: Any) -> dict:
    return {"status": "AVAILABLE", "mode": "fake_for_test"}


def _fake_human_approval_adapter(**kwargs: Any) -> dict:
    return {"decision": "APPROVED", "mode": "fake_for_test"}


def _fake_promotion_gate(**kwargs: Any) -> dict:
    return {"decision": "APPROVED", "mode": "fake_for_test"}


def _fake_failure_recovery(**kwargs: Any) -> dict:
    return {"action": "RETRY", "max_retries": 1, "mode": "fake_for_test"}


FAKE_ADAPTERS: dict[str, Any] = {
    "tool_adapter": {"fn": _fake_tool_adapter, "mode": DEPENDENCY_MODE_FAKE_FOR_TEST},
    "model_adapter": {"fn": _fake_model_adapter, "mode": DEPENDENCY_MODE_FAKE_FOR_TEST},
    "policy_registry": {"fn": _fake_policy_registry, "mode": DEPENDENCY_MODE_FAKE_FOR_TEST},
    "prompt_registry": {"fn": _fake_prompt_registry, "mode": DEPENDENCY_MODE_FAKE_FOR_TEST},
    "human_approval_adapter": {"fn": _fake_human_approval_adapter, "mode": DEPENDENCY_MODE_FAKE_FOR_TEST},
    "promotion_gate": {"fn": _fake_promotion_gate, "mode": DEPENDENCY_MODE_FAKE_FOR_TEST},
    "failure_recovery": {"fn": _fake_failure_recovery, "mode": DEPENDENCY_MODE_FAKE_FOR_TEST},
}


def resolve_dependency_bindings(context: dict, repo_root: Path) -> dict:
    resolved: dict[str, dict] = {}
    for name, cfg in FAKE_ADAPTERS.items():
        mode = context.get(f"{name}_mode", DEPENDENCY_MODE_UNAVAILABLE)
        if mode == DEPENDENCY_MODE_UNAVAILABLE:
            resolved[name] = {"adapter": None, "mode": mode, "available": False}
        elif mode == DEPENDENCY_MODE_RESTRICTED:
            resolved[name] = {"adapter": None, "mode": mode, "available": False}
        else:
            resolved[name] = {
                "adapter": cfg["fn"],
                "mode": cfg["mode"],
                "available": True,
            }
    global RESOLVED_BINDINGS
    RESOLVED_BINDINGS = resolved
    return resolved


def get_tool_adapter(binding_context: dict) -> Any | None:
    entry = binding_context.get("tool_adapter", {})
    return entry.get("adapter")


def get_policy_registry(binding_context: dict) -> Any | None:
    entry = binding_context.get("policy_registry", {})
    return entry.get("adapter")


def get_model_adapter(binding_context: dict) -> Any | None:
    entry = binding_context.get("model_adapter", {})
    return entry.get("adapter")


def get_prompt_registry(binding_context: dict) -> Any | None:
    entry = binding_context.get("prompt_registry", {})
    return entry.get("adapter")


def get_human_approval_adapter(binding_context: dict) -> Any | None:
    entry = binding_context.get("human_approval_adapter", {})
    return entry.get("adapter")


def get_promotion_gate(binding_context: dict) -> Any | None:
    entry = binding_context.get("promotion_gate", {})
    return entry.get("adapter")


def get_failure_recovery(binding_context: dict) -> Any | None:
    entry = binding_context.get("failure_recovery", {})
    return entry.get("adapter")
