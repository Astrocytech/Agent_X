#!/usr/bin/env python3
"""Standalone schema validator for Tool / MCP Adapter Layer schemas.

Usage:
    PYTHONPATH=tools python tools/agentx_evolve/tests/validate_tool_mcp_schemas.py

Returns exit code 0 if all schemas validate, 1 otherwise.
"""
import json
import sys
from pathlib import Path

import jsonschema

SCHEMA_DIR = Path(__file__).parent.parent / "schemas"

TOOL_SCHEMAS = {
    "tool_call.schema.json": {
        "schema_version": "1.0",
        "schema_id": "tool_call.schema.json",
        "tool_call_id": "call_001",
        "timestamp": "2026-06-05T00:00:00Z",
        "source_component": "ToolMCPAdapter",
        "caller_role": "ORCHESTRATOR",
        "tool_name": "agentx_scan",
        "arguments": {"action": "list"},
        "requested_effect": "READ",
        "warnings": [],
        "errors": [],
    },
    "tool_result.schema.json": {
        "schema_version": "1.0",
        "schema_id": "tool_result.schema.json",
        "tool_result_id": "res_001",
        "tool_call_id": "call_001",
        "timestamp": "2026-06-05T00:00:01Z",
        "source_component": "ToolMCPAdapter",
        "tool_name": "agentx_scan",
        "status": "SUCCESS",
        "exit_code": 0,
        "message": "completed",
        "data": {"result": "ok"},
        "failure_class": None,
        "warnings": [],
        "errors": [],
    },
    "tool_definition.schema.json": {
        "schema_version": "1.0",
        "schema_id": "tool_definition.schema.json",
        "tool_name": "agentx_scan",
        "description": "Run Initiator scan",
        "owner_component": "Initiator",
        "trust_tier": "TRUST_TIER_0_READ_ONLY",
        "input_schema_id": "tool_call.schema.json",
        "output_schema_id": "tool_result.schema.json",
        "allowed_roles": ["ORCHESTRATOR"],
        "requested_effects": ["READ"],
        "requires_sandbox_check": False,
        "requires_capability_policy": False,
        "enabled": True,
        "warnings": [],
        "errors": [],
    },
    "tool_registry.schema.json": {
        "schema_version": "1.0",
        "schema_id": "tool_registry.schema.json",
        "registry_id": "reg_001",
        "created_at": "2026-06-05T00:00:00Z",
        "source_component": "ToolRegistry",
        "tools": [],
        "warnings": [],
        "errors": [],
    },
    "tool_permission_decision.schema.json": {
        "schema_version": "1.0",
        "schema_id": "tool_permission_decision.schema.json",
        "decision_id": "pol_001",
        "timestamp": "2026-06-05T00:00:00Z",
        "source_component": "ToolPolicy",
        "tool_name": "agentx_scan",
        "caller_role": "ORCHESTRATOR",
        "requested_effect": "READ",
        "decision": "ALLOW",
        "reason": "All checks passed",
        "warnings": [],
        "errors": [],
    },
    "tool_policy.schema.json": {
        "schema_version": "1.0",
        "schema_id": "tool_policy.schema.json",
        "policy_id": "tp_001",
        "timestamp": "2026-06-05T00:00:00Z",
        "source_component": "ToolPolicy",
        "tool_name": "agentx_scan",
        "decision": "ALLOW",
        "reason": "All checks passed",
        "warnings": [],
        "errors": [],
    },
    "tool_trust_tier.schema.json": {
        "schema_version": "1.0",
        "schema_id": "tool_trust_tier.schema.json",
        "tier_id": "tier_001",
        "tier_name": "TRUST_TIER_0_READ_ONLY",
        "description": "Read-only tools with no mutation capability",
        "warnings": [],
        "errors": [],
    },
    "mcp_tool_manifest.schema.json": {
        "schema_version": "1.0",
        "schema_id": "mcp_tool_manifest.schema.json",
        "manifest_id": "mcp_001",
        "created_at": "2026-06-05T00:00:00Z",
        "source_component": "MCPAdapter",
        "exposed_tools": [],
        "blocked_tools": [],
        "warnings": [],
        "errors": [],
    },
    "invalid_tool_record.schema.json": {
        "schema_version": "1.0",
        "schema_id": "invalid_tool_record.schema.json",
        "record_id": "inv_001",
        "timestamp": "2026-06-05T00:00:00Z",
        "source_component": "InvalidToolHandler",
        "tool_name": "nonexistent",
        "caller_role": "ORCHESTRATOR",
        "reason": "Unknown tool",
        "raw_call": {},
        "warnings": [],
        "errors": [],
    },
    "tool_audit.schema.json": {
        "schema_version": "1.0",
        "schema_id": "tool_audit.schema.json",
        "audit_id": "aud_001",
        "timestamp": "2026-06-05T00:00:00Z",
        "source_component": "ToolMCPAdapter",
        "event_type": "TOOL_CALL",
        "status": "SUCCESS",
        "message": "Tool call completed",
        "warnings": [],
        "errors": [],
    },
}


def main() -> int:
    errors = []
    tested = 0

    for schema_name, valid_instance in TOOL_SCHEMAS.items():
        schema_path = SCHEMA_DIR / schema_name
        if not schema_path.exists():
            errors.append(f"MISSING: {schema_name}")
            continue

        schema = json.loads(schema_path.read_text())

        try:
            jsonschema.validate(valid_instance, schema)
            tested += 1
        except jsonschema.ValidationError as e:
            errors.append(f"VALIDATION FAIL: {schema_name} — {e.message}")

    for schema_name in SCHEMA_DIR.glob("*.schema.json"):
        if schema_name.name not in TOOL_SCHEMAS:
            errors.append(f"UNTESTED: {schema_name.name}")

    total = len(TOOL_SCHEMAS)
    print(f"Schemas tested: {tested}/{total}")
    if errors:
        print(f"Errors ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("All schemas validated successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
