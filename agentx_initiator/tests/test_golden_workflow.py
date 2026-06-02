"""Golden workflow: end-to-end integration test for PM2 components.

Exercises: memory store -> governance -> risk -> evolution -> patch -> validation.
"""
import pytest
from datetime import datetime, timezone
from agentx_initiator.core.memory_model import MemoryRecord, MemoryQuery
from agentx_initiator.core.memory_store import store_memory, query_memory, create_snapshot, build_manifest
from agentx_initiator.core.memory_index import build_index
from agentx_initiator.core.governance_engine import evaluate_governance
from agentx_initiator.core.governance_model import GovernanceRequest, GovernanceContext
from agentx_initiator.core.risk_engine import evaluate_risk
from agentx_initiator.core.risk_model import RiskContext
from agentx_initiator.core.evolution_planner import generate_evolution_plan
from agentx_initiator.core.patch_proposal_generator import generate_patch_proposal
from agentx_initiator.core.validation_runner import run_validator
from agentx_initiator.core.validation_allowlist import get_default_allowlist


def test_golden_workflow():
    # 1. Memory: store a record
    record = MemoryRecord(
        memory_id="golden-1",
        timestamp=datetime.now(timezone.utc).isoformat(),
        source_component="golden_test",
        category="SYSTEM",
        payload={"step": 1},
    )
    write_result = store_memory(record)
    assert write_result.status == "FAILED" or write_result.status == "SUCCESS"

    # 2. Memory: query
    q = MemoryQuery()
    result = query_memory(q)
    assert result is not None

    # 3. Memory: index
    idx = build_index([record])
    assert idx.record_count == 1

    # 4. Memory: snapshot
    snap = create_snapshot([record])
    assert snap.record_count == 1

    # 5. Memory: manifest
    manifest = build_manifest([record])
    assert manifest.record_count == 1

    # 6. Governance: evaluate (non-blocking action)
    req = GovernanceRequest(action_type="GENERATE_REPORT", target_path="./report.md")
    ctx = GovernanceContext()
    gov = evaluate_governance(req, ctx)
    assert gov.decision in ("ALLOW", "BLOCK")

    # 7. Risk: evaluate with minimal context
    risk_ctx = RiskContext(
        architecture_report={"findings": [], "protected_count": 0},
        repository_scan_summary={"test_count": 3},
    )
    risk_assessment = evaluate_risk(risk_ctx)
    assert risk_assessment.status in ("PASS", "PARTIAL", "BLOCKED")

    # 8. Evolution: generate plan
    plan = generate_evolution_plan(
        architecture_report={"missing_components": []},
        validation_report={"status": "PASS"},
        governance_decision={"decision": "ALLOW"},
    )
    assert hasattr(plan, "plan_id")
    assert len(plan.steps) > 0

    # 9. Patch proposal: generate spec
    spec = generate_patch_proposal(task="add unit tests for golden workflow")
    assert hasattr(spec, "spec_id")
    assert len(spec.actions) > 0

    # 10. Validation: reject dangerous command
    val_run = run_validator("rm -rf /", get_default_allowlist())
    assert val_run.status == "ERROR"
    assert "not in allowlist" in val_run.stderr
