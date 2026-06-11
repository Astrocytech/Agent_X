
import subprocess, json, os, pytest
FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")
VALIDATOR = "tools/agentx_evolve/validators/validate_five_document_matrix.py"

def run(path):
    return subprocess.run(["python3", VALIDATOR, path], capture_output=True, text=True)

def test_corrupted_matrix_missing_status():
    r = run(os.path.join(FIXTURES, "corrupted_matrix_missing_status.json"))
    assert r.returncode != 0
    assert "missing status" in r.stdout

def test_corrupted_matrix_invalid_status():
    r = run(os.path.join(FIXTURES, "corrupted_matrix_invalid_status.json"))
    assert r.returncode != 0
    assert "invalid status" in r.stdout

def test_corrupted_matrix_bad_pass():
    r = run(os.path.join(FIXTURES, "corrupted_matrix_bad_pass.json"))
    assert r.returncode != 0
    assert "PASS but no implementation" in r.stdout

def test_corrupted_matrix_mandatory_blocked():
    r = run(os.path.join(FIXTURES, "corrupted_matrix_mandatory_blocked.json"))
    assert r.returncode != 0
    assert "mandatory requirement" in r.stdout

def test_empty_json():
    r = run(os.path.join(FIXTURES, "empty.json"))
    assert r.returncode != 0
    assert "Missing" in r.stdout or "missing" in r.stdout

def test_not_json():
    r = run(os.path.join(FIXTURES, "not_json.txt"))
    assert r.returncode != 0
