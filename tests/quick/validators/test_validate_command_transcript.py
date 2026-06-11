
import subprocess, os, pytest
FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")
VALIDATOR = "tools/agentx_evolve/validators/validate_command_transcript.py"

def run(path):
    return subprocess.run(["python3", VALIDATOR, path], capture_output=True, text=True)

def test_missing_command():
    r = run(os.path.join(FIXTURES, "corrupted_transcript_no_command.json"))
    assert r.returncode != 0
    assert "missing 'command'" in r.stdout

def test_missing_exit_code():
    r = run(os.path.join(FIXTURES, "corrupted_transcript_no_exit.json"))
    assert r.returncode != 0
    assert "missing 'exit_code'" in r.stdout

def test_empty_array():
    r = run(os.path.join(FIXTURES, "empty_array.json"))
    assert r.returncode == 0
