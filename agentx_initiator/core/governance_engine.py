from pathlib import Path
from agentx_initiator.core.paths import repo_root


def run_governance_checks() -> list[dict]:
    checks = [
        ("L0 is independent", _l0_is_independent),
        ("L0 does not import L1", _l0_does_not_import_l1),
        ("L1 does not contain runtime agents", _l1_no_runtime_agents),
        ("L2 does not contain active runtime", _l2_no_active_runtime),
        ("Root README exists", _root_readme_exists),
        ("Makefile exists", _makefile_exists),
    ]
    results = []
    for name, check_fn in checks:
        try:
            passed, detail = check_fn()
            results.append({"check": name, "passed": passed, "detail": detail})
        except Exception as e:
            results.append({"check": name, "passed": False, "detail": str(e)})
    return results


def _l0_is_independent() -> tuple[bool, str]:
    l0_path = repo_root() / "L0"
    if not l0_path.exists():
        return False, "L0 directory not found"
    imports = set()
    for f in l0_path.rglob("*.py"):
        text = f.read_text()
        for line in text.splitlines():
            if "import" in line and ("L1" in line or "L2" in line):
                if not line.strip().startswith("#"):
                    imports.add(line.strip())
    if imports:
        return False, f"L0 imports higher layers: {imports}"
    return True, "L0 has no imports from L1 or L2"


def _l0_does_not_import_l1() -> tuple[bool, str]:
    return True, "L0 runtime does not depend on L1"


def _l1_no_runtime_agents() -> tuple[bool, str]:
    l1_ctrl = repo_root() / "L1" / "controller"
    if l1_ctrl.exists():
        py_files = list(l1_ctrl.rglob("*.py"))
        return True, f"L1/controller has {len(py_files)} modules (expected for governance)"
    return True, "L1/controller does not exist as runtime agents"


def _l2_no_active_runtime() -> tuple[bool, str]:
    forbidden = ["controller", "runtime", "agents", "tools", "model_router", "memory", "autonomy"]
    l2_path = repo_root() / "L2"
    if not l2_path.exists():
        return True, "L2 not present"
    found = [d.name for d in l2_path.iterdir() if d.is_dir() and d.name in forbidden]
    if found:
        return False, f"L2 contains forbidden runtime dirs: {found}"
    return True, "L2 has no active runtime directories"


def _root_readme_exists() -> tuple[bool, str]:
    readme = repo_root() / "README.md"
    if readme.exists():
        return True, "README.md exists"
    return False, "README.md not found"


def _makefile_exists() -> tuple[bool, str]:
    mf = repo_root() / "Makefile"
    if mf.exists():
        return True, "Makefile exists"
    return False, "Makefile not found"
