import json
import os

BENCHCORE = os.path.join(os.path.dirname(__file__), "..")
FB_DIR = os.path.join(BENCHCORE, "feedback_loop")

REQUIRED_FB_FILES = [
    "feedback_event.schema.json",
    "feedback_policy.json",
    "diagnostics_contract.json",
    "drift_policy.json",
    "exploration_policy.json",
    "rollback_policy.json",
]


class TestFeedbackLoop:

    def test_feedback_loop_directory_exists(self):
        assert os.path.isdir(FB_DIR)

    def test_all_required_files_exist(self):
        for fname in REQUIRED_FB_FILES:
            path = os.path.join(FB_DIR, fname)
            assert os.path.isfile(path), f"Missing: {fname}"
            assert os.path.getsize(path) > 0, f"Empty: {fname}"

    def test_has_6_files(self):
        files = [f for f in os.listdir(FB_DIR) if os.path.isfile(os.path.join(FB_DIR, f))]
        assert len(files) == 6

    def test_feedback_event_schema_is_valid_json(self):
        path = os.path.join(FB_DIR, "feedback_event.schema.json")
        with open(path) as f:
            schema = json.load(f)
        assert "$schema" in schema or "type" in schema

    def test_feedback_policy_is_valid_json(self):
        path = os.path.join(FB_DIR, "feedback_policy.json")
        with open(path) as f:
            policy = json.load(f)
        assert isinstance(policy, dict)
        assert "policy_name" in policy or len(policy) > 0

    def test_diagnostics_contract_is_valid_json(self):
        path = os.path.join(FB_DIR, "diagnostics_contract.json")
        with open(path) as f:
            contract = json.load(f)
        assert isinstance(contract, (dict, list))

    def test_drift_policy_is_valid_json(self):
        path = os.path.join(FB_DIR, "drift_policy.json")
        with open(path) as f:
            drift = json.load(f)
        assert isinstance(drift, (dict, list))

    def test_exploration_policy_is_valid_json(self):
        path = os.path.join(FB_DIR, "exploration_policy.json")
        with open(path) as f:
            policy = json.load(f)
        assert isinstance(policy, (dict, list))

    def test_rollback_policy_is_valid_json(self):
        path = os.path.join(FB_DIR, "rollback_policy.json")
        with open(path) as f:
            policy = json.load(f)
        assert isinstance(policy, (dict, list))

    def test_feedback_event_schema_has_properties(self):
        path = os.path.join(FB_DIR, "feedback_event.schema.json")
        with open(path) as f:
            schema = json.load(f)
        if "properties" in schema:
            props = schema["properties"]
            assert len(props) > 0
