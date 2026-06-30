"""
generate_adapter_acceptance_matrix.py

Produces the acceptance matrix for the Adapter MVP vertical slice.
Each row names a requirement, its validator command, and its current status.

Output: tools/agentx_evolve/tests/acceptance/adapter_acceptance_matrix.json
"""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / ".." / ".." / ".agentx-init" / "reports" / "adapter-mvp" / "adapter_acceptance_matrix.json"


REQUIREMENTS = [
    {
        "id": "ADAPTER-1",
        "area": "ModelAdapter interface",
        "requirement": "ModelAdapter ABC defines describe_capabilities, validate_request, generate, normalize_response",
        "validator": "pytest tests/test_model_adapter_interface.py -v",
        "expected": "PASS",
    },
    {
        "id": "ADAPTER-2",
        "area": "DeterministicMockModelAdapter",
        "requirement": "DeterministicMockModelAdapter produces deterministic output per seed, offline/no API key",
        "validator": "pytest tests/test_deterministic_mock_model_adapter.py -v",
        "expected": "PASS",
    },
    {
        "id": "ADAPTER-3",
        "area": "ModelRequest/Response schemas",
        "requirement": "ModelRequest and ModelResponse validate required fields and recognized statuses",
        "validator": "pytest tests/test_model_adapter_interface.py -v",
        "expected": "PASS",
    },
    {
        "id": "ADAPTER-4",
        "area": "PromptContract",
        "requirement": "PromptContract enforces allowed goal types, forbidden claims, and versioned resolution",
        "validator": "pytest tests/test_prompt_contract.py -v",
        "expected": "PASS",
    },
    {
        "id": "ADAPTER-5",
        "area": "PromptContractRegistry",
        "requirement": "Registry resolves by contract_id + version; unknown/wrong-version returns None",
        "validator": "pytest tests/test_prompt_contract.py -v",
        "expected": "PASS",
    },
    {
        "id": "ADAPTER-6",
        "area": "ContextPacket structural/factual split",
        "requirement": "ContextPacket separates structural context (goal_type, forbidden actions) from factual items",
        "validator": "pytest tests/test_context_builder_structural_factual_split.py -v",
        "expected": "PASS",
    },
    {
        "id": "ADAPTER-7",
        "area": "ContextPacket hash stability",
        "requirement": "ContextPacket hash is deterministic and changes with content",
        "validator": "pytest tests/test_context_builder_structural_factual_split.py -v",
        "expected": "PASS",
    },
    {
        "id": "ADAPTER-8",
        "area": "EvidenceBridge",
        "requirement": "EvidenceBridge normalizes, validates, and checks trust for evidence packets",
        "validator": "pytest tests/test_evidence_bridge.py -v",
        "expected": "PASS",
    },
    {
        "id": "ADAPTER-9",
        "area": "Evidence provenance",
        "requirement": "Evidence packets without provenance are rejected",
        "validator": "pytest tests/test_evidence_bridge.py -v",
        "expected": "PASS",
    },
    {
        "id": "ADAPTER-10",
        "area": "AdapterRegistry",
        "requirement": "AdapterRegistry resolves by adapter_id + profile; live adapters blocked under offline profile",
        "validator": "pytest tests/test_adapter_registry.py -v",
        "expected": "PASS",
    },
    {
        "id": "ADAPTER-11",
        "area": "ToolAdapter interface",
        "requirement": "ToolAdapter ABC defines describe_capabilities, validate/simulate/execute/ normalize",
        "validator": "pytest tests/test_tool_adapter_interface.py -v",
        "expected": "PASS",
    },
    {
        "id": "ADAPTER-12",
        "area": "LocalToolAdapter path traversal protection",
        "requirement": "LocalToolAdapter blocks absolute paths and ../ escape for all tools",
        "validator": "pytest tests/test_local_tool_adapter.py -v",
        "expected": "PASS",
    },
    {
        "id": "ADAPTER-13",
        "area": "MCPAdapterShell",
        "requirement": "MCPAdapterShell registers descriptors, validates calls, normalizes results",
        "validator": "pytest tests/test_mcp_shell.py -v",
        "expected": "PASS",
    },
    {
        "id": "ADAPTER-14",
        "area": "ReplayPolicy",
        "requirement": "ReplayPolicy enforces DETERMINISTIC/BLOCKED mode constraints",
        "validator": "pytest tests/test_replay_policy.py -v",
        "expected": "PASS",
    },
    {
        "id": "ADAPTER-15",
        "area": "Failure taxonomy",
        "requirement": "All 8 failure classes map to valid outcomes (BLOCKED, DENIED, RETRYABLE_FAILURE, etc.)",
        "validator": "pytest tests/test_failure_taxonomy.py -v",
        "expected": "PASS",
    },
    {
        "id": "ADAPTER-16",
        "area": "AdapterConformance",
        "requirement": "AdapterConformance schema/capability/security/failure/replay checks all pass",
        "validator": "pytest tests/test_conformance.py -v",
        "expected": "PASS",
    },
    {
        "id": "ADAPTER-17",
        "area": "Mock-to-local-tool scenario",
        "requirement": "Integration scenario: mock model generates, local tool executes, registry filters live adapters",
        "validator": "pytest tests/test_agentx_adapter_mvp_mock_flow.py -v",
        "expected": "PASS",
    },
    {
        "id": "ADAPTER-18",
        "area": "ReadOnlyRepoInfoTool",
        "requirement": "ReadOnlyRepoInfoTool blocks path traversal and returns directory info",
        "validator": "pytest tests/test_read_only_repo_info_tool.py -v",
        "expected": "PASS",
    },
    {
        "id": "ADAPTER-19",
        "area": "Schema JSON files",
        "requirement": "JSON schemas exist for model_request, model_response, context_packet, evidence_packet, adapter_record, tool_call, tool_result, mcp_tool_descriptor, prompt_contract",
        "validator": "test -f schemas/model_request.schema.json && test -f schemas/model_response.schema.json && test -f schemas/context_packet.schema.json && test -f schemas/evidence_packet.schema.json && test -f schemas/adapter_record.schema.json && test -f schemas/tool_call.schema.json && test -f schemas/tool_result.schema.json && test -f schemas/mcp_tool_descriptor.schema.json && test -f schemas/prompt_contract.schema.json",
        "expected": "PASS",
    },
]


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    matrix = {
        "claim": "AGENTX_ADAPTER_MVP",
        "requirements": REQUIREMENTS,
        "summary": {
            "total": len(REQUIREMENTS),
            "passed": 0,
            "failed": 0,
            "status": "PENDING",
        },
    }
    with open(OUT, "w") as f:
        json.dump(matrix, f, indent=2)
    print(f"Generated acceptance matrix at {OUT}")


if __name__ == "__main__":
    main()
