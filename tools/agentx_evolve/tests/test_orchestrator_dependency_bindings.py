import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.orchestrator.dependency_bindings import (
    resolve_dependency_bindings,
    get_tool_adapter,
    get_model_adapter,
    get_policy_registry,
    get_prompt_registry,
    get_human_approval_adapter,
    get_promotion_gate,
    get_failure_recovery,
)


def test_resolve_dependency_bindings_defaults_to_unavailable(tmp_path):
    result = resolve_dependency_bindings({}, tmp_path)
    assert isinstance(result, dict)
    tool = get_tool_adapter(result)
    assert tool is None


def test_resolve_dependency_bindings_unavailable_returns_none(tmp_path):
    context = {"tool_adapter_mode": "UNAVAILABLE", "model_adapter_mode": "UNAVAILABLE"}
    result = resolve_dependency_bindings(context, tmp_path)
    tool = get_tool_adapter(result)
    assert tool is None
    model = get_model_adapter(result)
    assert model is None


def test_get_tool_adapter_returns_adapter_when_configured(tmp_path):
    def adapter(**kwargs):
        return {"status": "SUCCESS"}

    result = resolve_dependency_bindings({"tool_adapter_mode": "REAL", "tool_adapter": adapter}, tmp_path)
    fn = get_tool_adapter(result)
    assert fn is adapter


def test_get_model_adapter_returns_adapter_when_configured(tmp_path):
    def adapter(**kwargs):
        return {"status": "SUCCESS"}

    result = resolve_dependency_bindings({"model_adapter_mode": "REAL", "model_adapter": adapter}, tmp_path)
    fn = get_model_adapter(result)
    assert fn is adapter


def test_get_policy_registry_returns_adapter_when_configured(tmp_path):
    def adapter(**kwargs):
        return {"decision": "ALLOW"}

    result = resolve_dependency_bindings({"policy_registry_mode": "REAL", "policy_registry": adapter}, tmp_path)
    fn = get_policy_registry(result)
    assert fn is adapter


def test_get_prompt_registry_returns_adapter_when_configured(tmp_path):
    def adapter(**kwargs):
        return {"status": "AVAILABLE"}

    result = resolve_dependency_bindings({"prompt_registry_mode": "REAL", "prompt_registry": adapter}, tmp_path)
    fn = get_prompt_registry(result)
    assert fn is adapter


def test_get_human_approval_adapter_returns_adapter_when_configured(tmp_path):
    def adapter(**kwargs):
        return {"decision": "APPROVED"}

    result = resolve_dependency_bindings({"human_approval_adapter_mode": "REAL", "human_approval_adapter": adapter}, tmp_path)
    fn = get_human_approval_adapter(result)
    assert fn is adapter


def test_get_promotion_gate_returns_adapter_when_configured(tmp_path):
    def adapter(**kwargs):
        return {"decision": "APPROVED"}

    result = resolve_dependency_bindings({"promotion_gate_mode": "REAL", "promotion_gate": adapter}, tmp_path)
    fn = get_promotion_gate(result)
    assert fn is adapter


def test_get_failure_recovery_returns_adapter_when_configured(tmp_path):
    def adapter(**kwargs):
        return {"action": "RETRY"}

    result = resolve_dependency_bindings({"failure_recovery_mode": "REAL", "failure_recovery": adapter}, tmp_path)
    fn = get_failure_recovery(result)
    assert fn is adapter


def test_unknown_mode_falls_back_to_unavailable(tmp_path):
    result = resolve_dependency_bindings({"tool_adapter_mode": "BOGUS_UNRECOGNIZED"}, tmp_path)
    assert get_tool_adapter(result) is None
