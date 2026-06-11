import subprocess, os, pytest

REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
VALIDATOR = os.path.join(REPO_ROOT, "tools/agentx_evolve/validators/detect_manual_generated_file_insertion.py")

def test_passes_on_empty_dirs():
    r = subprocess.run(["python3", VALIDATOR], capture_output=True, text=True, cwd=REPO_ROOT)
    assert r.returncode == 0
