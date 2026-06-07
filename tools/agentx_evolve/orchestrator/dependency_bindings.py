from __future__ import annotations

from pathlib import Path
from typing import Any

from agentx_evolve.orchestrator.orchestrator_config import (
    DEPENDENCY_MODE_REAL,
    DEPENDENCY_MODE_FAKE_FOR_TEST,
    DEPENDENCY_MODE_RESTRICTED,
    DEPENDENCY_MODE_UNAVAILABLE,
)


DEPENDENCY_NAMES = (
    "tool_adapter",
    "model_adapter",
    "policy_registry",
    "prompt_registry",
    "human_approval_adapter",
    "promotion_gate",
    "failure_recovery",
)

FAKE_ADAPTERS: dict[str, dict[str, Any]] = {
    name: {"fn": lambda n=name: {"mode": "fake_for_test", "name": n}}
    for name in DEPENDENCY_NAMES
}

RESOLVED_BINDINGS: dict[str, Any] = {}


def resolve_dependency_bindings(context: dict, repo_root: Path) -> dict:
    resolved: dict[str, dict] = {}
    for name in DEPENDENCY_NAMES:
        mode = context.get(f"{name}_mode", DEPENDENCY_MODE_UNAVAILABLE)
        adapter = context.get(name)
        if mode == DEPENDENCY_MODE_UNAVAILABLE:
            resolved[name] = {"adapter": None, "mode": mode, "available": False}
        elif mode == DEPENDENCY_MODE_RESTRICTED:
            resolved[name] = {"adapter": None, "mode": mode, "available": False}
        elif mode == DEPENDENCY_MODE_FAKE_FOR_TEST:
            fake_adapter = FAKE_ADAPTERS.get(name, {}).get("fn", lambda: {"mode": "fake_for_test"})
            resolved[name] = {"adapter": fake_adapter, "mode": mode, "available": True}
        elif mode == DEPENDENCY_MODE_REAL and callable(adapter):
            resolved[name] = {"adapter": adapter, "mode": mode, "available": True}
        else:
            resolved[name] = {"adapter": None, "mode": DEPENDENCY_MODE_UNAVAILABLE, "available": False}
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
