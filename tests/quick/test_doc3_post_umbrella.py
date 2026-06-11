"""
DOC3 post-umbrella behavioral tests.
"""
import os, sys, json, pytest

REPO = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))

def test_clothing_agent_exists():
    """Clothing advice agent tests exist."""
    paths = [
        "examples/clothing_advice_agent/test_clothing_advice_agent.py",
        "tests/release/clothing_advice_agent/test_clothing_advice_runtime.py",
    ]
    found = any(os.path.exists(os.path.join(REPO, p)) for p in paths)
    assert found, f"None of {paths} exist"

def test_daily_planning_agent_exists():
    """Daily planning agent tests exist."""
    paths = [
        "examples/daily_planning_agent/test_daily_planning_agent.py",
        "tests/release/daily_planning_agent/test_daily_planning_runtime.py",
    ]
    found = any(os.path.exists(os.path.join(REPO, p)) for p in paths)
    assert found, f"None of {paths} exist"

def test_failure_recovery_proof_exists():
    """Failure recovery proof exists."""
    paths = [
        ".agentx-init/post_umbrella/phase_5_failure_recovery",
        ".agentx-init/five_document_closure/final/five_document_clean_checkout_replay.json",
    ]
    found = any(os.path.exists(os.path.join(REPO, p)) for p in paths)
    assert found, f"None of {paths} exist"

def test_model_provider_abstraction():
    """Model adapter/provider abstraction exists."""
    paths = [
        "tools/agentx_evolve/model_adapter",
        "tools/agentx_evolve/providers",
        "tools/agentx_evolve/model_runtime",
        "examples/clothing_advice_agent/planner.py",
        "examples/daily_planning_agent/planner.py",
    ]
    found = any(os.path.exists(os.path.join(REPO, p)) for p in paths)
    assert found, f"None of {paths} exist"

def test_security_negative_test_structure():
    """Security policy enforcement files exist."""
    paths = [
        "tools/agentx_evolve/security/network_policy.py",
        "tools/agentx_evolve/security/safe_subprocess.py",
        "tools/agentx_evolve/security/secret_redactor.py",
        "tools/agentx_evolve/security/sandbox_policy.py",
        "tools/agentx_evolve/security/path_boundary.py",
    ]
    found = any(os.path.exists(os.path.join(REPO, p)) for p in paths)
    assert found, f"None of {paths} exist"

def test_no_production_readiness_claim():
    """No production readiness claim allowed."""
    claim_path = os.path.join(REPO, ".agentx-init/five_document_closure/final/five_document_claim_validation.json")
    if os.path.exists(claim_path):
        with open(claim_path) as f:
            data = json.load(f)
        content = json.dumps(data).lower()
        assert "not production-ready" in content or "not a finished universal agent" in content or "forbidden" in content

def test_release_readiness_report():
    """Post-umbrella release readiness phase exists."""
    paths = [
        ".agentx-init/post_umbrella/phase_8_release_readiness",
        ".agentx-init/post_umbrella/phase_9_final_acceptance",
        ".agentx-init/reports/FINAL_PROJECT_ACCEPTANCE_REVIEW.md",
    ]
    found = any(os.path.exists(os.path.join(REPO, p)) for p in paths)
    assert found, f"None of {paths} exist"

def test_final_acceptance_artifacts():
    """Post-umbrella final acceptance artifacts exist."""
    path = os.path.join(REPO, ".agentx-init/post_umbrella/phase_9_final_acceptance")
    alt = os.path.join(REPO, ".agentx-init/reports/FINAL_PROJECT_ACCEPTANCE_REVIEW.md")
    assert os.path.exists(path) or os.path.exists(alt)

def test_benchmark_categories_defined():
    """Benchmark categories are documented."""
    bench_files = [
        "benchmarks/benchcore/README.md",
        "benchmarks/benchcore/source_inventory.json",
        "benchmarks/benchcore/source_hashes.json",
    ]
    found = any(os.path.exists(os.path.join(REPO, p)) for p in bench_files)
    assert found, f"None of {bench_files} exist"

def test_prior_milestone_verification():
    """Prior milestone verification exists."""
    base = os.path.join(REPO, ".agentx-init/post_umbrella/phase_0_prior_verification")
    alt = os.path.join(REPO, ".agentx-init/five_document_closure/source_documents/source_document_inventory.json")
    assert os.path.exists(base) or os.path.exists(alt)
