
import subprocess, os, pytest
FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")
VALIDATOR = "tools/agentx_evolve/validators/validate_event_log.py"

def run(path):
    return subprocess.run(["python3", VALIDATOR, path], capture_output=True, text=True)

def test_missing_event_id():
    r = run(os.path.join(FIXTURES, "corrupted_event_no_id.json"))
    assert r.returncode != 0
    assert "missing event_id" in r.stdout

def test_missing_timestamp():
    r = run(os.path.join(FIXTURES, "corrupted_event_no_ts.json"))
    assert r.returncode != 0
    assert "missing timestamp_utc" in r.stdout
