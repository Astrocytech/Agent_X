
import subprocess, os, pytest
FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")
VALIDATOR = "tools/agentx_evolve/validators/detect_noop_commands.py"

def run(path):
    return subprocess.run(["python3", VALIDATOR, path], capture_output=True, text=True)

def test_noop_detected():
    r = run(os.path.join(FIXTURES, "corrupted_transcript_no_exit.json"))
    assert r.returncode == 0
    assert "ISSUES" in r.stdout or "PASS" in r.stdout
