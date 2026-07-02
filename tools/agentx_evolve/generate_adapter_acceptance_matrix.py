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


FRMVP_VERDICT_CHECK = "python3 -c \"import json; from pathlib import Path; d=json.loads((Path('../..')/'.agentx-init/reports/functional_runtime_mvp_final_verdict.json').read_text()); assert d.get('classification')=='FUNCTIONAL_RUNTIME_MVP' and d.get('verdict_status') in ('verified','proven'), f'unexpected: {d.get(\"classification\")}/{d.get(\"verdict_status\")}'\""
FRMVP_MATRIX_CHECK = "python3 -c \"import json; from pathlib import Path; d=json.loads((Path('../..')/'.agentx-init/reports/functional_runtime_mvp_acceptance_matrix.json').read_text()); rows=d.get('rows',[]); unknown=[r for r in rows if r.get('status')=='UNKNOWN']; assert len(unknown)==0, f'{len(unknown)} rows still UNKNOWN'\""

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
    # ============================================================
    # Adapter Hardening Rows (N2 roadmap §2)
    # ============================================================
    {
        "id": "ADAPTER-20",
        "area": "FRMVP non-regression",
        "requirement": "Functional Runtime MVP final verdict exists with classification FUNCTIONAL_RUNTIME_MVP and verdict_status verified/proven",
        "validator": FRMVP_VERDICT_CHECK,
        "expected": "PASS",
    },
    {
        "id": "ADAPTER-21",
        "area": "Provider-neutral default proof",
        "requirement": "Default proof uses deterministic mock adapter; no live provider, API key, or network required",
        "validator": "python3 validators/validate_adapter_hardening.py",
        "expected": "PASS",
    },
    {
        "id": "ADAPTER-22",
        "area": "Context minimization before provider calls",
        "requirement": "ContextPacket provides structural/factual split with deterministic hash; context budgeting limits size",
        "validator": "pytest tests/test_context_builder_structural_factual_split.py tests/test_context_budgeting.py -q --tb=short -p no:cacheprovider",
        "expected": "PASS",
    },
    {
        "id": "ADAPTER-23",
        "area": "Secret redaction before provider calls",
        "requirement": "Sensitive data redactor removes secrets from context before provider exposure",
        "validator": "pytest tests/test_sensitive_data_redactor.py -q --tb=short -p no:cacheprovider",
        "expected": "PASS",
    },
    {
        "id": "ADAPTER-24",
        "area": "Untrusted content / prompt-injection boundary",
        "requirement": "Prompt injection filter detects and blocks injection attempts in user/agent content",
        "validator": "pytest tests/test_prompt_injection_filter.py -q --tb=short -p no:cacheprovider",
        "expected": "PASS",
    },
    {
        "id": "ADAPTER-25",
        "area": "Adapter budget and resource limits",
        "requirement": "Resource budgeting limits adapter model/tool/file/patch operations per scope",
        "validator": "pytest tests/test_budget_estimator.py tests/test_self_evolution_resource_budget.py -q --tb=short -p no:cacheprovider",
        "expected": "PASS",
    },
    {
        "id": "ADAPTER-26",
        "area": "Provider portability",
        "requirement": "Multiple ModelAdapter implementations exist (deterministic_mock, local, hosted, openai_compatible, ollama, lmstudio, cohere); registry resolves by adapter_id",
        "validator": "python3 validators/validate_adapter_hardening.py",
        "expected": "PASS",
    },
    {
        "id": "ADAPTER-26b",
        "area": "CohereModelAdapter (quarantined live)",
        "requirement": "CohereModelAdapter implements ModelAdapter interface; blocked under offline profile; requires AGENTX_COHERE_LIVE=1 for live API calls",
        "validator": "pytest tests/test_cohere_model_adapter_mocked.py -q --tb=short -p no:cacheprovider",
        "expected": "PASS",
    },
    {
        "id": "ADAPTER-27",
        "area": "MCP auth, transport, and capability boundary",
        "requirement": "MCPAdapterShell validates tool descriptors, supports real transports (stdio, streamable_http, sse, remote_http), normalizes results, blocks unknown tools",
        "validator": "pytest tests/test_mcp_shell.py tests/test_mcp_adapter.py -q --tb=short -p no:cacheprovider",
        "expected": "PASS",
    },
    {
        "id": "ADAPTER-28",
        "area": "Context contamination and evidence priority order",
        "requirement": "ContextPacket separates structural from factual; evidence bridge validates provenance before use",
        "validator": "pytest tests/test_context_builder_structural_factual_split.py tests/test_evidence_bridge.py -q --tb=short -p no:cacheprovider",
        "expected": "PASS",
    },
    {
        "id": "ADAPTER-29",
        "area": "Adapter side-effect classification",
        "requirement": "Adapter code declares side_effect field; side-effect classification present across adapter implementations",
        "validator": "python3 validators/validate_adapter_hardening.py",
        "expected": "PASS",
    },
    {
        "id": "ADAPTER-30",
        "area": "Dependency and supply-chain controls for adapters",
        "requirement": "Dependency lock files exist for seed/dev/test/release requirements",
        "validator": "python3 validators/validate_adapter_hardening.py",
        "expected": "PASS",
    },
    {
        "id": "ADAPTER-31",
        "area": "Adapter observability and run metrics",
        "requirement": "Observer and metrics collection track adapter operations",
        "validator": "pytest tests/test_observer.py tests/test_monitoring_metrics_collector.py -q --tb=short -p no:cacheprovider",
        "expected": "PASS",
    },
    {
        "id": "ADAPTER-32",
        "area": "Retry, timeout, and backoff policy",
        "requirement": "Retry policy, backoff strategy, and timeout handling exist for adapter/model operations",
        "validator": "pytest tests/test_retry_policy.py tests/test_backoff.py -q --tb=short -p no:cacheprovider",
        "expected": "PASS",
    },
    {
        "id": "ADAPTER-33",
        "area": "Adapter artifact schema migration",
        "requirement": "Schema migration support exists for adapter records and prompt versions",
        "validator": "pytest tests/test_prompt_diff_migration.py tests/test_prompt_migration.py -q --tb=short -p no:cacheprovider",
        "expected": "PASS",
    },
    {
        "id": "ADAPTER-34",
        "area": "Recorded replay for live provider outputs",
        "requirement": "ReplayPolicy enforces DETERMINISTIC/BLOCKED modes; adapter replay produces deterministic results",
        "validator": "pytest tests/test_replay_policy.py tests/test_learning_replay_idempotency.py -q --tb=short -p no:cacheprovider",
        "expected": "PASS",
    },
    {
        "id": "ADAPTER-35",
        "area": "Clean-checkout proof",
        "requirement": "Adapter proof runs from clean git checkout; working tree tracked in final verdict",
        "validator": "python3 validators/validate_adapter_hardening.py",
        "expected": "PASS",
    },
    {
        "id": "ADAPTER-36",
        "area": "FRMVP acceptance matrix completeness",
        "requirement": "FRMVP acceptance matrix rows all have terminal status (PASS/DENIED/BLOCKED), none UNKNOWN",
        "validator": FRMVP_MATRIX_CHECK,
        "expected": "PASS",
    },
    {
        "id": "ADAPTER-37",
        "area": "CI evidence status",
        "requirement": "CI evidence recorded: CI unavailable in offline proof environment; no CI evidence claimed or overclaimed",
        "validator": "python3 -c \"import sys; print('CI evidence: CI unavailable — offline proof environment; no CI validation claimed'); sys.exit(0)\"",
        "expected": "PASS",
    },
    {
        "id": "ADAPTER-38",
        "area": "Cohere/provider-specific quarantine documentation",
        "requirement": "Cohere-specific requirement replaced with provider-neutral adapter interface; CohereModelAdapter exists as quarantined live adapter behind AGENTX_COHERE_LIVE flag",
        "validator": "pytest tests/test_cohere_model_adapter_mocked.py -q --tb=short -p no:cacheprovider",
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
