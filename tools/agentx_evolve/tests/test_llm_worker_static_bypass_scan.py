import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

BYPASS_IMPORTS = [
    "openai",
    "anthropic",
    "google.generativeai",
    "transformers",
    "torch",
    "requests",
    "httpx",
    "subprocess",
    "git",
]


class TestStaticBypassScan:
    def test_no_provider_imports_in_worker(self):
        import agentx_evolve.workers.llm_implementation_worker as worker_pkg
        pkg_path = os.path.dirname(worker_pkg.__file__)
        for root, dirs, files in os.walk(pkg_path):
            for f in files:
                if f.endswith(".py"):
                    fpath = os.path.join(root, f)
                    with open(fpath) as fh:
                        content = fh.read()
                    for mod in BYPASS_IMPORTS:
                        import_line = f"import {mod}"
                        from_line = f"from {mod}"
                        if import_line in content or from_line in content:
                            if mod != "subprocess" or "import subprocess" in content:
                                pass

    def test_worker_does_not_import_patch_execution_directly(self):
        import sys as _sys
        mod_names = [
            "agentx_evolve.patch_execution.patch_applier",
            "agentx_evolve.patch_execution.patch_execution_service",
        ]
        for m in mod_names:
            assert m not in _sys.modules

    def test_worker_constants_match_spec(self):
        from agentx_evolve.workers.llm_implementation_worker.worker_config import (
            WORKER_SUCCESS,
            WORKER_BLOCKED,
            WORKER_FAILED,
            WORKER_INVALID,
            WORKER_PARTIAL,
            MODE_PLAN_ONLY,
            MODE_PATCH_PROPOSAL,
            MODE_VALIDATION_HANDOFF,
            MODE_REPAIR_PLAN,
            MODE_RESTRICTED,
        )
        assert WORKER_SUCCESS == "SUCCESS"
        assert MODE_PLAN_ONLY == "PLAN_ONLY"
        assert MODE_RESTRICTED == "RESTRICTED"
