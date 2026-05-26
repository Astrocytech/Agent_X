#!/usr/bin/env python3
"""Prove: Seed kernel boots — KernelService can be instantiated and health() returns success.

Claim ID: boot
Evidence: .local/runtime/proofs/seed_boot.json
"""
import json
import sys
from pathlib import Path

PROOF_DIR = Path(".local/runtime/proofs")
PROOF_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, "CODE")
from core_kernel.public.kernel_service import KernelService

svc = KernelService()
health = svc.health()

required_fields = [
    "runtime_class",
    "runtime_mode",
    "active_profile_id",
    "active_gateway_type",
    "runtime_available",
    "governance_status",
    "memory_status",
    "tool_gateway_status",
    "port_health",
]

missing_fields = [f for f in required_fields if f not in health]
field_checks_passed = len(missing_fields) == 0

readiness_ok = health.get("status") in ("healthy", "degraded")
profile_id_ok = bool(health.get("active_profile_id"))
gateway_type_ok = health.get("active_gateway_type") in ("seed", "platform")
ports_ok = isinstance(health.get("port_health"), dict)
runtime_available = health.get("runtime_available") is True

passed = (
    field_checks_passed
    and readiness_ok
    and profile_id_ok
    and gateway_type_ok
    and ports_ok
    and runtime_available
)

evidence = {
    "claim_id": "boot",
    "claim_text": "It boots",
    "passed": passed,
    "evidence": {
        "runtime_class": health.get("runtime_class"),
        "runtime_mode": health.get("runtime_mode"),
        "status": health.get("status"),
        "active_profile_id": health.get("active_profile_id"),
        "active_gateway_type": health.get("active_gateway_type"),
        "port_health": health.get("port_health"),
        "runtime_available": health.get("runtime_available"),
        "profile_count": health.get("profile_count"),
        "tool_count": health.get("tool_count"),
        "field_checks_passed": field_checks_passed,
        "port_count": len(health.get("port_health", {})),
    },
    "failure_reason": None,
}

if not evidence["passed"]:
    failures = []
    if missing_fields:
        failures.append(f"missing_fields={missing_fields}")
    if not readiness_ok:
        failures.append(f"status={health.get('status')}")
    if not ports_ok:
        failures.append("port_health not a dict")
    if not profile_id_ok:
        failures.append("active_profile_id empty")
    if not gateway_type_ok:
        failures.append(f"active_gateway_type={health.get('active_gateway_type')}")
    if not runtime_available:
        failures.append("runtime_available is False")
    evidence["failure_reason"] = "; ".join(failures)
    print(json.dumps(evidence, indent=2))
    sys.exit(1)

proof_path = PROOF_DIR / "seed_boot.json"
proof_path.write_text(json.dumps(evidence, indent=2))
print(json.dumps(evidence, indent=2))
print(f"\nEvidence written to {proof_path}")
