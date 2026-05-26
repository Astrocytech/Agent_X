"""Test 08: Blocked capabilities — manifest declares them, registry must not expose them."""

from __future__ import annotations

from pathlib import Path

import yaml

from tool_gateway.seed_tool_registry import list_seed_tool_names


ROOT = Path(__file__).resolve().parents[2]


def test_blocked_capabilities_declared() -> None:
    manifest = yaml.safe_load((ROOT / "CAPABILITY_MANIFEST.yaml").read_text())

    blocked_ids = {entry["id"] for entry in manifest["blocked_capabilities"]}

    assert "production_self_modification" in blocked_ids
    assert "uncontrolled_network_access" in blocked_ids
    assert "direct_shell_execution" in blocked_ids


def test_l0_seed_registry_contains_only_seed_emit_answer() -> None:
    tool_names = list_seed_tool_names()
    assert set(tool_names) == {"seed.emit_answer"}


def test_l0_seed_registry_does_not_expose_forbidden_tools() -> None:
    tool_names = list_seed_tool_names()

    forbidden_fragments = {
        "shell",
        "bash",
        "cmd",
        "terminal",
        "network",
        "http",
        "request",
        "write_patch",
        "patch",
        "promote",
        "self_modify",
    }

    for name in tool_names:
        lowered = name.lower()
        assert not any(fragment in lowered for fragment in forbidden_fragments), name


def test_seed_gateway_adapter_does_not_register_default_tools() -> None:
    adapter = (ROOT / "CODE/kernel_composition/local_seed_ports/tool_gateway_adapter_port.py").read_text()
    assert "register_default_tools" not in adapter
    assert "register_seed_tools" in adapter
