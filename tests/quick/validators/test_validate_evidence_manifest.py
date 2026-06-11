
import subprocess, os, pytest
FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")
VALIDATOR = "tools/agentx_evolve/validators/validate_evidence_manifest.py"

def run(path):
    return subprocess.run(["python3", VALIDATOR, path], capture_output=True, text=True)

def test_missing_path():
    r = run(os.path.join(FIXTURES, "corrupted_manifest_no_path.json"))
    assert r.returncode != 0
    assert "missing 'path'" in r.stdout

def test_empty_array():
    r = run(os.path.join(FIXTURES, "empty_array.json"))
    assert r.returncode == 0
