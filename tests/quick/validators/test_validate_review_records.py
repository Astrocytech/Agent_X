
import subprocess, os, pytest
FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")
VALIDATOR = "tools/agentx_evolve/validators/validate_review_records.py"

def run(path):
    return subprocess.run(["python3", VALIDATOR, path], capture_output=True, text=True)

def test_missing_review_id():
    r = run(os.path.join(FIXTURES, "corrupted_review_no_id.json"))
    assert r.returncode != 0
    assert "missing review_id" in r.stdout

def test_missing_decision():
    r = run(os.path.join(FIXTURES, "corrupted_review_no_decision.json"))
    assert r.returncode != 0
    assert "missing decision" in r.stdout
