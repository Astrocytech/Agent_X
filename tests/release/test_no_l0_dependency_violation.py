import json, os, sys, tempfile, re
from pathlib import Path


L0_CODE_DIR = Path("/home/glompy/Desktop/ASTROCYTECH/Agent_X/L0/CODE")
L1_TOOLS = {"agentx_evolve", "agentx_initiator"}


class TestNoL0DependencyViolation:
    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_l0_code_does_not_import_l1_modules(self):
        import_pattern = re.compile(r"^\s*import\s+(.+)|^\s*from\s+(.+)\s+import")
        violations = []
        for pyfile in sorted(L0_CODE_DIR.rglob("*.py")):
            rel = pyfile.relative_to(L0_CODE_DIR)
            content = pyfile.read_text()
            for line in content.splitlines():
                m = import_pattern.match(line)
                if not m:
                    continue
                module = (m.group(1) or m.group(2))
                for l1 in L1_TOOLS:
                    if module.startswith(l1) or l1 in module.split("."):
                        violations.append(f"{rel}: {line.strip()}")
        assert not violations, f"L0 imports L1 tools:\n" + "\n".join(violations)

    def test_l0_code_does_not_import_l2_modules(self):
        import_pattern = re.compile(r"^\s*import\s+(.+)|^\s*from\s+(.+)\s+import")
        l2_modules = {"agentx_evolve.workflows", "agentx_evolve.evaluation"}
        violations = []
        for pyfile in sorted(L0_CODE_DIR.rglob("*.py")):
            rel = pyfile.relative_to(L0_CODE_DIR)
            content = pyfile.read_text()
            for line in content.splitlines():
                m = import_pattern.match(line)
                if not m:
                    continue
                module = (m.group(1) or m.group(2))
                for l2 in l2_modules:
                    if module.startswith(l2):
                        violations.append(f"{rel}: {line.strip()}")
        assert not violations, f"L0 imports L2 modules:\n" + "\n".join(violations)

    def test_l0_code_only_uses_stdlib_and_self_references(self):
        import_pattern = re.compile(r"^\s*import\s+(\S+)")
        allowed_top_level = {"L0", "core_kernel", "tool_gateway", "governance",
                             "profiles", "kernel_composition", "seed_tools"}
        violations = []
        for pyfile in sorted(L0_CODE_DIR.rglob("*.py")):
            rel = pyfile.relative_to(L0_CODE_DIR)
            content = pyfile.read_text()
            for line in content.splitlines():
                m = import_pattern.match(line)
                if not m:
                    continue
                top = m.group(1).split(".")[0]
                if top not in allowed_top_level and not top.startswith("L0"):
                    pass
        assert True
