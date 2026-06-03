from __future__ import annotations
from agentx_evolve.security.security_models import (
    SandboxPolicy, NetworkPolicyResult, STATUS_BLOCKED, STATUS_FAILED,
    utc_now_iso, new_id,
)


def check_network_allowed(
    target: str | None,
    policy: SandboxPolicy,
) -> NetworkPolicyResult:
    if not policy.network_allowed:
        return NetworkPolicyResult(
            result_id=new_id("npr"),
            timestamp=utc_now_iso(),
            target=target,
            status=STATUS_BLOCKED,
            reason="Network access is disabled by policy",
        )

    if not target:
        return NetworkPolicyResult(
            result_id=new_id("npr"),
            timestamp=utc_now_iso(),
            target=target,
            status=STATUS_FAILED,
            reason="Network target is required but was not provided",
        )

    return NetworkPolicyResult(
        result_id=new_id("npr"),
        timestamp=utc_now_iso(),
        target=target,
        status=STATUS_BLOCKED,
        reason="Network target is not in allowlist (v1: all targets blocked)",
    )
