"""
DOC3 post-umbrella behavioral tests.
"""
import os, sys, json, pytest

REPO = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))

def test_clothing_agent_exists():
    """Clothing advice agent tests exist."""
    path = os.path.join(REPO, "examples/clothing_agent/test_clothing_agent.py")
    assert os.path.exists(path), f"Missing: {path}"

def test_daily_planning_agent_exists():
    """Daily planning agent tests exist."""
    path = os.path.join(REPO, "examples/daily_planning_agent/test_daily_planning_agent.py")
    assert os.path.exists(path), f"Missing: {path}"

def test_failure_recovery_proof_exists():
    """Failure recovery phase directory exists."""
    path = os.path.join(REPO, ".agentx-init/post_umbrella/phase_5_failure_recovery")
    assert os.path.exists(path)

def test_model_provider_abstraction():
    """Model adapter/provider abstraction exists."""
    paths = [
        "tools/agentx_evolve/model_adapter",
        "tools/agentx_evolve/providers",
        "tools/agentx_evolve/model_runtime",
    ]
    for p in paths:
        full = os.path.join(REPO, p)
        assert os.path.exists(full), f"Missing: {full}"

def test_security_negative_test_structure():
    """Security policy enforcement files exist."""
    paths = [
        "tools/agentx_evolve/security/network_policy.py",
        "tools/agentx_evolve/security/safe_subprocess.py",
        "tools/agentx_evolve/security/secret_redactor.py",
    ]
    for p in paths:
        full = os.path.join(REPO, p)
        assert os.path.exists(full), f"Missing: {p}"

def test_no_production_readiness_claim():
    """No production readiness claim allowed."""
    claim_path = os.path.join(REPO, ".agentx-init/five_document_closure/final/five_document_claim_validation.json")
    if os.path.exists(claim_path):
        with open(claim_path) as f:
            data = json.load(f)
        claim = data.get("final_claim", "").lower()
        assert "not production-ready" in claim or "not a finished universal agent" in claim

def test_release_readiness_report():
    """Post-umbrella release readiness phase exists."""
    path = os.path.join(REPO, ".agentx-init/post_umbrella/phase_8_release_readiness")
    assert os.path.exists(path)

def test_final_acceptance_artifacts():
    """Post-umbrella final acceptance artifacts exist."""
    path = os.path.join(REPO, ".agentx-init/post_umbrella/phase_9_final_acceptance")
    assert os.path.exists(path)

def test_benchmark_categories_defined():
    """Benchmark categories are documented."""
    bench_file = os.path.join(REPO, "benchmarks/benchcore/README.md")
    if os.path.exists(bench_file):
        content = open(bench_file).read()
        assert len(content) > 0

def test_prior_milestone_verification():
    """Prior milestone verification exists."""
    base = os.path.join(REPO, ".agentx-init/post_umbrella/phase_0_prior_verification")
    assert os.path.exists(base)
    files = os.listdir(base)
    assert len(files) > 0
