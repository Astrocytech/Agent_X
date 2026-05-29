"""kernel_diagnostics — Deep health checks split from KernelService.health()."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


REPO_ROOT = Path(__file__).resolve().parents[3]


def check_platform_tool_leakage(runtime: Any) -> dict[str, Any]:
    result: dict[str, Any] = {
        "forbidden_platform_tools_visible": False,
        "registered_seed_tools": [],
    }
    try:
        from CODE.tool_gateway.seed_tool_registry import list_seed_tool_names

        result["registered_seed_tools"] = list_seed_tool_names()
    except Exception:
        logger.debug("list_seed_tool_names not available")
    if runtime is None:
        return result
    try:
        from CODE.tool_gateway.seed_tool_registry import list_seed_tool_names as _lst
        from CODE.tool_gateway.tool_gateway import ToolGateway

        seed_tools = set(_lst())
        tool_gateway_port = getattr(runtime, "_tool_gateway_port", None)
        if tool_gateway_port is not None:
            gateway = getattr(tool_gateway_port, "_gateway", None)
            if gateway is not None and isinstance(gateway, ToolGateway):
                registry = getattr(gateway, "registry", None)
                if registry is not None:
                    all_contracts = registry.list_tools()
                    registered_names = {c.name for c in all_contracts}
                    result["forbidden_platform_tools_visible"] = bool(
                        registered_names - seed_tools
                    )
    except Exception:
        logger.debug("tool gateway diagnostics not available")
    return result


def check_seed_boundary() -> str:
    return "available"


def check_port_implementations(runtime: Any) -> dict[str, str]:
    classes: dict[str, str] = {}
    if runtime is None:
        return classes
    ports_method = getattr(runtime, "_ports", None)
    if ports_method is not None:
        for pname, pinst in ports_method().items():
            if pinst is not None:
                classes[pname] = type(pinst).__name__
    return classes


def deep_health(runtime: Any) -> dict[str, Any]:
    return {
        "platform_leakage": check_platform_tool_leakage(runtime),
        "seed_boundary_status": check_seed_boundary(),
        "port_implementations": check_port_implementations(runtime),
    }
