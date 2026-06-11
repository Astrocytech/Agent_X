import json
import os

BENCHCORE = os.path.join(os.path.dirname(__file__), "..")
DR_DIR = os.path.join(BENCHCORE, "dynamic_retrieval")

REQUIRED_DR_FILES = [
    "capability_registry_fixture.json",
    "retrieval_query_fixture.jsonl",
    "reranking_policy.json",
    "unsupported_label_cases.jsonl",
]


class TestDynamicRetrieval:

    def test_dynamic_retrieval_directory_exists(self):
        assert os.path.isdir(DR_DIR)

    def test_all_required_files_exist(self):
        for fname in REQUIRED_DR_FILES:
            path = os.path.join(DR_DIR, fname)
            assert os.path.isfile(path), f"Missing: {fname}"
            assert os.path.getsize(path) > 0, f"Empty: {fname}"

    def test_has_4_files(self):
        files = [f for f in os.listdir(DR_DIR) if os.path.isfile(os.path.join(DR_DIR, f))]
        assert len(files) == 4

    def test_capability_registry_fixture_is_valid_json(self):
        path = os.path.join(DR_DIR, "capability_registry_fixture.json")
        with open(path) as f:
            registry = json.load(f)
        assert isinstance(registry, (dict, list))
        if isinstance(registry, dict):
            assert len(registry) > 0
        else:
            assert len(registry) > 0

    def test_retrieval_query_fixture_is_non_empty_jsonl(self):
        path = os.path.join(DR_DIR, "retrieval_query_fixture.jsonl")
        with open(path) as f:
            lines = [l for l in f if l.strip()]
        assert len(lines) > 0
        json.loads(lines[0])

    def test_unsupported_label_cases_is_non_empty_jsonl(self):
        path = os.path.join(DR_DIR, "unsupported_label_cases.jsonl")
        with open(path) as f:
            lines = [l for l in f if l.strip()]
        assert len(lines) > 0
        json.loads(lines[0])

    def test_reranking_policy_is_valid_json(self):
        path = os.path.join(DR_DIR, "reranking_policy.json")
        with open(path) as f:
            policy = json.load(f)
        assert isinstance(policy, (dict, list))

    def test_capability_registry_entries_have_required_fields(self):
        path = os.path.join(DR_DIR, "capability_registry_fixture.json")
        with open(path) as f:
            registry = json.load(f)
        if isinstance(registry, list):
            entries = registry
        elif isinstance(registry, dict):
            entries = list(registry.values())
        else:
            entries = []
        for entry in entries:
            if isinstance(entry, dict):
                has_id = "capability_id" in entry or "id" in entry or "name" in entry
                assert has_id, f"Registry entry missing identifier: {entry}"
