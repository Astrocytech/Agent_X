import subprocess, os, tempfile, pytest

REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
VALIDATOR = os.path.join(REPO_ROOT, "tools/agentx_evolve/validators/scan_secrets_in_evidence.py")

def test_detect_api_key():
    with tempfile.TemporaryDirectory() as tmp:
        ef = os.path.join(tmp, "secret_bad.json")
        with open(ef, "w") as f:
            f.write('{"api_key": "12345678901234567890abcdef"}')
        r = subprocess.run(["python3", VALIDATOR, tmp], capture_output=True, text=True)
        assert r.returncode == 0
        assert "SECRETS SCAN" in r.stdout

def test_passes_on_clean_file():
    with tempfile.TemporaryDirectory() as tmp:
        ef = os.path.join(tmp, "clean.json")
        with open(ef, "w") as f:
            f.write('{"name": "hello"}')
        r = subprocess.run(["python3", VALIDATOR, tmp], capture_output=True, text=True)
        assert r.returncode == 0
        assert "PASS" in r.stdout
