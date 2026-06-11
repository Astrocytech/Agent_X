from __future__ import annotations

import json
from pathlib import Path

REUSE_MAP: list[dict] = [
    {
        "functional_component": "RuntimeContext",
        "existing_component_found": True,
        "existing_path": "tools/agentx_evolve/runtime/runtime_profile.py",
        "decision": "new",
        "reason": "Existing runtime has profile/config but no deterministic clock or seeded randomness. Need MvpRuntimeContext.",
        "compatibility_tests": ["tools/agentx_evolve/tests/test_runtime_context.py"],
    },
    {
        "functional_component": "WorkspaceManager",
        "existing_component_found": False,
        "existing_path": "",
        "decision": "new",
        "reason": "No existing workspace isolation component. Need MvpWorkspaceManager.",
        "compatibility_tests": ["tools/agentx_evolve/tests/test_workspace_manager.py"],
    },
    {
        "functional_component": "ArtifactStore",
        "existing_component_found": True,
        "existing_path": "tools/agentx_evolve/patch_execution/patch_evidence.py",
        "decision": "wrap",
        "reason": "Existing append-only evidence writer can be wrapped as the first artifact-store backend.",
        "compatibility_tests": ["tools/agentx_evolve/tests/test_artifact_store.py"],
    },
    {
        "functional_component": "ResultEnvelope",
        "existing_component_found": False,
        "existing_path": "",
        "decision": "new",
        "reason": "No typed I/O envelope exists. Need MvpResultEnvelope.",
        "compatibility_tests": ["tools/agentx_evolve/tests/test_io_envelope.py"],
    },
    {
        "functional_component": "RuntimeProfile",
        "existing_component_found": True,
        "existing_path": "tools/agentx_evolve/runtime/runtime_profile.py",
        "decision": "new",
        "reason": "Existing RuntimeProfile is complex with GPU/resource fields. Need minimal MvpRuntimeProfile with STRICT/DRY_RUN/REPLAY/AUDIT_ONLY.",
        "compatibility_tests": ["tools/agentx_evolve/tests/test_runtime_profile.py"],
    },
    {
        "functional_component": "ReadinessCheck",
        "existing_component_found": False,
        "existing_path": "",
        "decision": "new",
        "reason": "No readiness check component exists.",
        "compatibility_tests": ["tools/agentx_evolve/tests/test_readiness.py"],
    },
    {
        "functional_component": "StateStore",
        "existing_component_found": True,
        "existing_path": "tools/agentx_evolve/runtime/artifacts.py",
        "decision": "new",
        "reason": "Existing ArtifactWriter handles file writes but no JSONL state store with query-by-run/action/goal. Need MvpStateStore.",
        "compatibility_tests": ["tools/agentx_evolve/tests/test_state_store.py"],
    },
    {
        "functional_component": "EventBus",
        "existing_component_found": True,
        "existing_path": "tools/agentx_evolve/evidence/event_logger.py",
        "decision": "wrap",
        "reason": "Existing event_logger has hash-chain append-only pattern. Can wrap as MvpEventBus with in-memory dispatch + persisted JSONL.",
        "compatibility_tests": ["tools/agentx_evolve/tests/test_event_bus.py"],
    },
    {
        "functional_component": "ActionLifecycle",
        "existing_component_found": True,
        "existing_path": "tools/agentx_evolve/runtime/session.py",
        "decision": "new",
        "reason": "Existing RunSession has 12 states but MVP requires 13 specific states with different transition rules. Need MvpActionLifecycle.",
        "compatibility_tests": ["tools/agentx_evolve/tests/test_action_lifecycle.py"],
    },
    {
        "functional_component": "ContractRegistry",
        "existing_component_found": False,
        "existing_path": "",
        "decision": "new",
        "reason": "No minimal contract registry exists.",
        "compatibility_tests": ["tools/agentx_evolve/tests/test_contract_registry.py"],
    },
    {
        "functional_component": "CapabilityGraph",
        "existing_component_found": True,
        "existing_path": "tools/agentx_evolve/models/model_models.py",
        "decision": "new",
        "reason": "Existing ModelCapabilityProfile is model-focused. Need MvpCapabilityGraph for agent-action-target resolution.",
        "compatibility_tests": ["tools/agentx_evolve/tests/test_capability_graph.py"],
    },
    {
        "functional_component": "PolicyRuleEngine",
        "existing_component_found": True,
        "existing_path": "tools/agentx_evolve/policy/",
        "decision": "new",
        "reason": "Existing policy system is extensive. Need minimal MvpPolicyRuleEngine with deterministic ALLOW/DENY/ESCALATE/REQUIRE_MORE_CHECKS.",
        "compatibility_tests": ["tools/agentx_evolve/tests/test_policy_rule_engine.py"],
    },
    {
        "functional_component": "DecisionGate",
        "existing_component_found": True,
        "existing_path": "tools/agentx_evolve/orchestrator/gate_controller.py",
        "decision": "new",
        "reason": "Existing gate controller is orchestrator-specific. Need MvpDecisionGate that aggregates policy+capability+invariant+simulation.",
        "compatibility_tests": ["tools/agentx_evolve/tests/test_decision_gate.py"],
    },
    {
        "functional_component": "InvariantEngine",
        "existing_component_found": False,
        "existing_path": "",
        "decision": "new",
        "reason": "No explicit invariant engine exists.",
        "compatibility_tests": ["tools/agentx_evolve/tests/test_invariant_engine.py"],
    },
    {
        "functional_component": "SecurityEnvelope",
        "existing_component_found": False,
        "existing_path": "",
        "decision": "new",
        "reason": "No security envelope component exists.",
        "compatibility_tests": ["tools/agentx_evolve/tests/test_security_envelope.py"],
    },
    {
        "functional_component": "TransactionManager",
        "existing_component_found": False,
        "existing_path": "",
        "decision": "new",
        "reason": "No transaction manager exists.",
        "compatibility_tests": ["tools/agentx_evolve/tests/test_transaction_manager.py"],
    },
    {
        "functional_component": "SimulationEngine",
        "existing_component_found": False,
        "existing_path": "",
        "decision": "new",
        "reason": "No simulation engine exists.",
        "compatibility_tests": ["tools/agentx_evolve/tests/test_simulation_engine.py"],
    },
    {
        "functional_component": "ReportGenerationExecutor",
        "existing_component_found": True,
        "existing_path": "tools/agentx_evolve/patch_execution/patch_execution_service.py",
        "decision": "new",
        "reason": "Existing patch execution is for code patches. Need MvpReportGenerationExecutor for artifact report generation.",
        "compatibility_tests": ["tools/agentx_evolve/tests/test_report_generation_executor.py"],
    },
    {
        "functional_component": "Observer",
        "existing_component_found": False,
        "existing_path": "",
        "decision": "new",
        "reason": "No observation component exists.",
        "compatibility_tests": ["tools/agentx_evolve/tests/test_observer.py"],
    },
    {
        "functional_component": "RollbackController",
        "existing_component_found": True,
        "existing_path": "tools/agentx_evolve/patch_execution/rollback_manager.py",
        "decision": "new",
        "reason": "Existing rollback is patch-specific. Need MvpRollbackController for generic action rollback.",
        "compatibility_tests": ["tools/agentx_evolve/tests/test_rollback_controller.py"],
    },
    {
        "functional_component": "CircuitBreaker",
        "existing_component_found": False,
        "existing_path": "",
        "decision": "new",
        "reason": "No circuit breaker component exists.",
        "compatibility_tests": ["tools/agentx_evolve/tests/test_circuit_breaker.py"],
    },
    {
        "functional_component": "ReviewInterface",
        "existing_component_found": True,
        "existing_path": "tools/agentx_evolve/review/review_interface.py",
        "decision": "new",
        "reason": "Existing HumanReviewInterface has complex approval model. Need MvpReviewInterface with minimal packet/decision pattern.",
        "compatibility_tests": ["tools/agentx_evolve/tests/test_review_interface.py"],
    },
    {
        "functional_component": "PromotionGate",
        "existing_component_found": True,
        "existing_path": "tools/agentx_evolve/promotion/promotion_gate.py",
        "decision": "new",
        "reason": "Existing promotion gate is complex with 30+ failure classes. Need MvpPromotionGate with review+evidence+observation+gate+invariant requirements.",
        "compatibility_tests": ["tools/agentx_evolve/tests/test_promotion_gate.py"],
    },
    {
        "functional_component": "ScenarioRunner",
        "existing_component_found": False,
        "existing_path": "",
        "decision": "new",
        "reason": "No scenario runner exists.",
        "compatibility_tests": ["tools/agentx_evolve/tests/test_scenario_runner.py"],
    },
    {
        "functional_component": "FunctionalOrchestrator",
        "existing_component_found": True,
        "existing_path": "tools/agentx_evolve/orchestrator/orchestrator_engine.py",
        "decision": "new",
        "reason": "Existing orchestrator is complex with 25+ steps. Need MvpFunctionalOrchestrator for the minimal MVP loop.",
        "compatibility_tests": ["tools/agentx_evolve/tests/test_functional_orchestrator.py"],
    },
    {
        "functional_component": "FunctionalAcceptance",
        "existing_component_found": True,
        "existing_path": "tools/agentx_evolve/final_acceptance/generate_artifacts.py",
        "decision": "new",
        "reason": "Existing acceptance runner is a monolithic script. Need MvpFunctionalAcceptance as a modular component.",
        "compatibility_tests": ["tools/agentx_evolve/tests/test_functional_acceptance.py"],
    },
]

OUTPUT_DIR = Path(".agentx-init/reports")


def generate_reuse_map() -> list[dict]:
    return list(REUSE_MAP)


def write_reuse_map() -> tuple[str, str]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    md_lines = ["# Functional Runtime MVP — Reuse Map", "", "| Component | Decision | Reason |", "|---|---|---|"]
    for row in REUSE_MAP:
        md_lines.append(f"| {row['functional_component']} | {row['decision']} | {row['reason']} |")
    md = "\n".join(md_lines)
    md_path = str(OUTPUT_DIR / "functional_runtime_reuse_map.md")
    Path(md_path).write_text(md, encoding="utf-8")

    js = json.dumps(REUSE_MAP, indent=2)
    js_path = str(OUTPUT_DIR / "functional_runtime_reuse_map.json")
    Path(js_path).write_text(js, encoding="utf-8")
    return md_path, js_path


if __name__ == "__main__":
    md_p, js_p = write_reuse_map()
    print(f"Reuse map written to {md_p} and {js_p}")
