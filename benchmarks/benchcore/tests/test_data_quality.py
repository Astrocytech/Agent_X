import json
import os

BENCHCORE = os.path.join(os.path.dirname(__file__), "..")
DQ_DIR = os.path.join(BENCHCORE, "data_quality")

REQUIRED_DQ_FILES = [
    "evidence_fusion_policy.json",
    "field_quality_policy.json",
    "input_output_pairing_contract.md",
    "log_parse_policy.json",
    "sql_mapping_policy.json",
    "xml_cleanup_policy.json",
]

REQUIRED_DQ_SUBDIRS = ["fixtures_clean", "fixtures_invalid", "fixtures_raw"]


class TestDataQuality:

    def test_data_quality_directory_exists(self):
        assert os.path.isdir(DQ_DIR)

    def test_all_required_files_exist(self):
        for fname in REQUIRED_DQ_FILES:
            path = os.path.join(DQ_DIR, fname)
            assert os.path.isfile(path), f"Missing: {fname}"
            assert os.path.getsize(path) > 0, f"Empty: {fname}"

    def test_all_required_subdirs_exist(self):
        for dname in REQUIRED_DQ_SUBDIRS:
            path = os.path.join(DQ_DIR, dname)
            assert os.path.isdir(path), f"Missing subdir: {dname}"

    def test_evidence_fusion_policy_has_required_fields(self):
        path = os.path.join(DQ_DIR, "evidence_fusion_policy.json")
        with open(path) as f:
            policy = json.load(f)
        required = {
            "policy_name", "description", "join_key_required",
            "allowed_join_keys", "sources", "validation_rules",
            "source_ids", "scope", "live_connections",
        }
        missing = required - set(policy.keys())
        assert not missing, f"Missing fields: {missing}"

    def test_evidence_fusion_join_key_required_is_true(self):
        path = os.path.join(DQ_DIR, "evidence_fusion_policy.json")
        with open(path) as f:
            policy = json.load(f)
        assert policy["join_key_required"] is True

    def test_evidence_fusion_live_connections_is_false(self):
        path = os.path.join(DQ_DIR, "evidence_fusion_policy.json")
        with open(path) as f:
            policy = json.load(f)
        assert policy["live_connections"] is False

    def test_evidence_fusion_has_validation_rules(self):
        path = os.path.join(DQ_DIR, "evidence_fusion_policy.json")
        with open(path) as f:
            policy = json.load(f)
        assert isinstance(policy["validation_rules"], list)
        assert len(policy["validation_rules"]) >= 4

    def test_log_parse_policy_exists(self):
        path = os.path.join(DQ_DIR, "log_parse_policy.json")
        with open(path) as f:
            policy = json.load(f)
        assert isinstance(policy, (dict, list))

    def test_field_quality_policy_exists(self):
        path = os.path.join(DQ_DIR, "field_quality_policy.json")
        with open(path) as f:
            policy = json.load(f)
        assert isinstance(policy, (dict, list))

    def test_xml_cleanup_policy_exists(self):
        path = os.path.join(DQ_DIR, "xml_cleanup_policy.json")
        with open(path) as f:
            policy = json.load(f)
        assert isinstance(policy, (dict, list))

    def test_sql_mapping_policy_exists(self):
        path = os.path.join(DQ_DIR, "sql_mapping_policy.json")
        with open(path) as f:
            policy = json.load(f)
        assert isinstance(policy, (dict, list))

    def test_input_output_pairing_contract_is_non_empty(self):
        path = os.path.join(DQ_DIR, "input_output_pairing_contract.md")
        assert os.path.getsize(path) > 100

    def test_fixtures_clean_is_populated(self):
        path = os.path.join(DQ_DIR, "fixtures_clean")
        items = os.listdir(path)
        assert len(items) > 0

    def test_fixtures_raw_is_populated(self):
        path = os.path.join(DQ_DIR, "fixtures_raw")
        items = os.listdir(path)
        assert len(items) > 0

    def test_fixtures_invalid_is_populated(self):
        path = os.path.join(DQ_DIR, "fixtures_invalid")
        items = os.listdir(path)
        assert len(items) > 0

    def test_has_at_least_9_entries_in_directory(self):
        all_entries = os.listdir(DQ_DIR)
        assert len(all_entries) >= 9
