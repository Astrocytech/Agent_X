
import subprocess, os, pytest
FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")
VALIDATOR = "tools/agentx_evolve/validators/validate_clean_replay_report.py"

def run(path):
    return subprocess.run(["python3", VALIDATOR, path], capture_output=True, text=True)

def test_missing_replay_id():
    r = run(os.path.join(FIXTURES, "corrupted_replay_missing_id.json"))
    assert r.returncode != 0
    assert "Missing replay_id" in r.stdout

def test_missing_verdict():
    r = run(os.path.join(FIXTURES, "corrupted_replay_missing_verdict.json"))
    assert r.returncode != 0
    assert "Missing verdict" in r.stdout

def test_missing_commit():
    r = run(os.path.join(FIXTURES, "corrupted_replay_missing_commit.json"))
    assert r.returncode != 0
    assert "Missing source_commit" in r.stdout
