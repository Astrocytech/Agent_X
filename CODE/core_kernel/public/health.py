"""Health check logic for KernelService."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PROFILE_DIR = ROOT / "CODE" / "profiles" / "builtin"
SEED_PROOF = ROOT / ".local" / "runtime" / "proofs" / "seed_turn_proof.json"


def _profile_count() -> int:
    if not PROFILE_DIR.exists():
        return 0
    return len(list(PROFILE_DIR.glob("*.yaml")))


def _tool_count(runtime_instance: Any) -> int:
    registry = getattr(runtime_instance, "tool_registry", None)
    if registry is not None and hasattr(registry, "list_tools"):
        try:
            return len(registry.list_tools())
        except Exception:
            return 0
    return 0


def _last_proof_status() -> str:
    if not SEED_PROOF.exists():
        return "missing"
    try:
        payload = json.loads(SEED_PROOF.read_text(encoding="utf-8"))
    except Exception:
        return "unreadable"
    proof = payload.get("proof", {})
    return "pass" if proof.get("valid") else "fail"


def _profile_loading_ok() -> bool:
    if not PROFILE_DIR.exists():
        return False
    profiles = list(PROFILE_DIR.glob("*.yaml"))
    return len(profiles) > 0


def _memory_health(runtime_instance: Any) -> dict[str, Any]:
    result = {
        "write_ok": False,
        "read_ok": False,
    }
    memory_system = getattr(runtime_instance, "memory_system", None)
    if memory_system is None:
        return result
    try:
        writer = getattr(memory_system, "write", None)
        if writer:
            writer("health_check", {"source": "health"})
            result["write_ok"] = True
    except Exception:
        __import__("logging").getLogger(__name__).debug("memory write health failed", exc_info=True)
    try:
        reader = getattr(memory_system, "read", None)
        if reader:
            reader("health_check")
            result["read_ok"] = True
    except Exception:
        result["read_ok"] = False
    return result


def _trace_health(runtime_instance: Any) -> bool:
    trace_manager = getattr(runtime_instance, "trace_manager", None)
    if trace_manager is None:
        trace_manager = getattr(runtime_instance, "_trace_manager", None)
    if trace_manager is None:
        return False
    try:
        writer = getattr(trace_manager, "write", None)
        if writer is None:
            writer = getattr(trace_manager, "record", None)
        if writer:
            writer({"health_check": True})
            return True
    except Exception:
        return False
    return False


def _gateway_catalog_ok(runtime_instance: Any) -> bool:
    registry = getattr(runtime_instance, "tool_registry", None)
    if registry is None:
        return False
    try:
        lister = getattr(registry, "list_tools", None)
        if lister:
            tools = lister()
            return len(tools) > 0
    except Exception:
        return False
    return False


def build_health(
    runtime_instance: Any,
    default_profile_id: str = "generalist",
    mode: str = "production",
) -> dict[str, Any]:
    runtime_class = runtime_instance.__class__.__name__ if runtime_instance else "None"
    mem = _memory_health(runtime_instance)
    profile_ok = _profile_loading_ok()
    mem_write_ok = mem["write_ok"]
    mem_read_ok = mem["read_ok"]
    trace_ok = _trace_health(runtime_instance)
    gateway_ok = _gateway_catalog_ok(runtime_instance)
    runtime_ok = runtime_instance is not None
    if hasattr(runtime_instance, "port_health"):
        ports = runtime_instance.port_health()
        all_ports_ok = all(ports.values())
    else:
        ports = {}
        all_ports_ok = runtime_ok
    sub_indicators = [profile_ok, mem_write_ok, mem_read_ok, trace_ok, gateway_ok, all_ports_ok]
    if not runtime_ok:
        status = "fail"
    elif all(sub_indicators):
        status = "ok"
    else:
        status = "degraded"
    return {
        "status": status,
        "service": "KernelService",
        "mode": mode,
        "runtime_class": runtime_class,
        "profile_loading_ok": profile_ok,
        "memory_write_ok": mem_write_ok,
        "memory_read_ok": mem_read_ok,
        "trace_write_ok": trace_ok,
        "gateway_catalog_ok": gateway_ok,
        "runtime_authority": "seed",
        "runtime_available": runtime_ok,
        "default_profile_id": default_profile_id,
        "governance_status": "loaded" if runtime_instance else "not_available",
        "governance_mode": "kernel_strict",
        "memory_status": "available",
        "tool_gateway_status": "available",
        "evolution_availability": False,
        "profile_count": _profile_count(),
        "tool_count": _tool_count(runtime_instance),
        "last_proof_status": _last_proof_status(),
        "port_health": ports,
    }
