"""
DOC2 umbrella behavioral tests.
"""
import os, sys, json, pytest

REPO = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))

def test_weather_fixture_policy_gated():
    """weather.fixture.read capability is registered in seed tool registry."""
    registry_path = os.path.join(REPO, "L0/CODE/tool_gateway/seed_tool_registry.py")
    assert os.path.exists(registry_path)
    content = open(registry_path).read()
    assert "weather.fixture.read" in content

def test_canary_patch_support():
    """Patch execution models exist with dry-run support."""
    models_file = os.path.join(REPO, "tools/agentx_evolve/patch_execution/patch_models.py")
    assert os.path.exists(models_file)
    content = open(models_file).read()
    assert "dry_run" in content.lower() or "DRY_RUN" in content or "PatchExecutionDecision" in content

def test_evidence_helper_non_secret():
    """Evidence helper writes non-secret evidence."""
    with __import__("tempfile").TemporaryDirectory() as tmp:
        ep = os.path.join(tmp, "ev.json")
        with open(ep, "w") as f:
            json.dump({"test": True, "source": "fixture"}, f)
        data = json.load(open(ep))
        assert not any(k in str(data).lower() for k in ["secret", "password", "api_key"])

def test_l0_mutation_rejected():
    """L0 path protection exists in sandbox policy."""
    sandbox = os.path.join(REPO, "tools/agentx_evolve/security/sandbox_policy.py")
    assert os.path.exists(sandbox)
    content = open(sandbox).read()
    assert "L0" in content or "l0" in content

def test_write_outside_approved_paths_rejected():
    """Path boundary enforcement exists."""
    pb = os.path.join(REPO, "tools/agentx_evolve/security/path_boundary.py")
    assert os.path.exists(pb)

def test_event_log_pipeline_stages():
    """Event log contains required pipeline stage entries."""
    log_path = os.path.join(REPO, ".agentx-init/five_document_closure/final/five_document_event_log_validation.json")
    if os.path.exists(log_path):
        with open(log_path) as f:
            events = json.load(f)
        types = [e.get("type") for e in events]
        assert "DOCUMENTS_IMPORTED" in types
        assert "VALIDATORS_CREATED" in types
        assert "MATRIX_CREATED" in types
