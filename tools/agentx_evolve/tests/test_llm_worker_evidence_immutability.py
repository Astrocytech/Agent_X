import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.workers.llm_implementation_worker.worker_models import (
    compute_self_hash,
    sha256_dict,
)


class TestEvidenceImmutability:
    def test_hash_changes_when_data_changes(self):
        data1 = {"a": 1, "b": 2}
        data2 = {"a": 1, "b": 3}
        h1 = sha256_dict(data1)
        h2 = sha256_dict(data2)
        assert h1 != h2

    def test_self_hash_computed_correctly(self):
        data = {
            "a": 1,
            "evidence_manifest_sha256": "old",
            "b": 2,
        }
        h = compute_self_hash(data, "evidence_manifest_sha256")
        expected = sha256_dict({"a": 1, "b": 2})
        assert h == expected

    def test_same_data_same_hash(self):
        data = {"status": "DONE", "task_id": "t-001"}
        h1 = sha256_dict(data)
        h2 = sha256_dict(data)
        assert h1 == h2
