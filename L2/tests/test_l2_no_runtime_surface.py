"""L2 no-runtime-surface tests — verifies no runtime directories or claims exist."""
import os

L2_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROHIBITED_RUNTIME_DIRS = [
    "controller", "runtime", "agents", "tools", "model_router", "memory",
    "autonomy", "executors", "patchers",
]


def test_prohibited_runtime_dirs_absent_or_placeholder():
    for d in PROHIBITED_RUNTIME_DIRS:
        full = os.path.join(L2_DIR, d)
        if os.path.isdir(full):
            files = []
            for root, dirs, fnames in os.walk(full):
                for f in fnames:
                    if f.endswith((".py", ".sh", ".js", ".ts", ".ipynb")):
                        files.append(os.path.join(root, f))
            assert not files, f"Executable files in prohibited dir {d}: {files}"


def test_no_implementation_allowed_in_profiles():
    profiles_dir = os.path.join(L2_DIR, "profiles")
    for fname in os.listdir(profiles_dir):
        if not fname.endswith(".yaml"):
            continue
        fp = os.path.join(profiles_dir, fname)
        with open(fp) as fh:
            content = fh.read()
        assert "implementation_allowed: true" not in content, (
            f"{fname} has implementation_allowed: true"
        )
        assert "direct_runtime_allowed: true" not in content, (
            f"{fname} has direct_runtime_allowed: true"
        )


def test_generated_files_marked_not_release_evidence():
    gen_dir = os.path.join(L2_DIR, "generated")
    for fname in os.listdir(gen_dir):
        fp = os.path.join(gen_dir, fname)
        if os.path.isfile(fp) and not fname.startswith("."):
            with open(fp) as fh:
                content = fh.read()
            has_marker = "release_evidence: false" in content or "bootstrap-placeholder-not-release-evidence" in content
            assert has_marker, f"Generated file {fname} missing release_evidence marker"


def test_sib_handoff_no_implementation_authority():
    hp = os.path.join(L2_DIR, "sib", "sib-l1-handoff-map.yaml")
    if os.path.isfile(hp):
        with open(hp) as fh:
            content = fh.read()
        assert "implementation_allowed_by_l2: true" not in content, (
            "SIB handoff map grants implementation authority"
        )


def test_eqc_no_runtime_authority():
    for sub in ["procedures", "operators"]:
        d = os.path.join(L2_DIR, "eqc", sub)
        if not os.path.isdir(d):
            continue
        for fname in os.listdir(d):
            if not fname.endswith((".md", ".eqc.md")):
                continue
            fp = os.path.join(d, fname)
            with open(fp) as fh:
                content = fh.read()
            assert "Runtime Authority: granted" not in content, (
                f"{sub}/{fname} claims runtime authority"
            )
            assert "Implementation Authority: granted" not in content, (
                f"{sub}/{fname} claims implementation authority"
            )
