
import subprocess, os, pytest
FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")
VALIDATOR = "tools/agentx_evolve/validators/validate_claims.py"

def run(path):
    return subprocess.run(["python3", VALIDATOR, path], capture_output=True, text=True)

def test_forbidden_claim_production():
    r = run(os.path.join(FIXTURES, "corrupted_claims_forbidden.json"))
    assert r.returncode != 0
    assert "forbidden" in r.stdout

def test_forbidden_claim_agi():
    r = run(os.path.join(FIXTURES, "corrupted_claims_forbidden2.json"))
    assert r.returncode != 0
    assert "forbidden" in r.stdout
