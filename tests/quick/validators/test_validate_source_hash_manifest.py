
import subprocess, os, pytest
FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")
VALIDATOR = "tools/agentx_evolve/validators/validate_source_hash_manifest.py"

def run(path):
    return subprocess.run(["python3", VALIDATOR, path], capture_output=True, text=True)

def test_bad_sha256_length():
    r = run(os.path.join(FIXTURES, "corrupted_source_hash_bad_len.json"))
    assert r.returncode != 0
    assert "invalid sha256" in r.stdout or "length" in r.stdout

def test_missing_sha256():
    r = run(os.path.join(FIXTURES, "corrupted_source_hash_missing.json"))
    assert r.returncode != 0
    assert "missing sha256" in r.stdout
