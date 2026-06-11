import subprocess, os, tempfile, pytest

REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
VALIDATOR = os.path.join(REPO_ROOT, "tools/agentx_evolve/validators/detect_skipped_or_empty_tests.py")

def test_detect_empty_test():
    with tempfile.TemporaryDirectory() as tmp:
        tf = os.path.join(tmp, "test_empty.py")
        with open(tf, "w") as f:
            f.write("def test_foo():\n    pass\n")
        r = subprocess.run(["python3", VALIDATOR, tmp], capture_output=True, text=True)
        assert r.returncode == 0
        assert "ISSUES" in r.stdout

def test_detect_syntax_error():
    with tempfile.TemporaryDirectory() as tmp:
        tf = os.path.join(tmp, "test_bad.py")
        with open(tf, "w") as f:
            f.write("def test_foo( pass\n")
        r = subprocess.run(["python3", VALIDATOR, tmp], capture_output=True, text=True)
        assert r.returncode == 0
        assert "ISSUES" in r.stdout
