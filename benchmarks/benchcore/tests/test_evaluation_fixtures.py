import json
import csv
import os

BENCHCORE = os.path.join(os.path.dirname(__file__), "..")
EVAL_DIR = os.path.join(BENCHCORE, "evaluation")


class TestEvaluationFixtures:

    def test_evaluation_directory_exists(self):
        assert os.path.isdir(EVAL_DIR)

    def test_evaluation_config_schema_exists(self):
        path = os.path.join(EVAL_DIR, "evaluation_config.schema.json")
        assert os.path.isfile(path)
        with open(path) as f:
            schema = json.load(f)
        assert "$schema" in schema
        assert "type" in schema or "properties" in schema

    def test_evaluation_workflow_contract_exists(self):
        path = os.path.join(EVAL_DIR, "evaluation_workflow_contract.md")
        assert os.path.isfile(path)
        assert os.path.getsize(path) > 0

    def test_expected_metrics_fixture_exists(self):
        path = os.path.join(EVAL_DIR, "expected_metrics_fixture.json")
        assert os.path.isfile(path)
        with open(path) as f:
            metrics = json.load(f)
        assert isinstance(metrics, (dict, list))
        assert len(json.dumps(metrics)) > 10

    def test_valid_dataset_fixture_exists(self):
        path = os.path.join(EVAL_DIR, "valid_dataset_fixture.csv")
        assert os.path.isfile(path)
        assert os.path.getsize(path) > 0

    def test_valid_dataset_fixture_is_readable_csv(self):
        path = os.path.join(EVAL_DIR, "valid_dataset_fixture.csv")
        with open(path, newline="") as f:
            reader = csv.reader(f)
            header = next(reader)
            assert len(header) > 0
            rows = list(reader)
            assert len(rows) > 0

    def test_invalid_dataset_bad_ranked_list_exists(self):
        path = os.path.join(EVAL_DIR, "invalid_dataset_bad_ranked_list.csv")
        assert os.path.isfile(path)
        assert os.path.getsize(path) > 0

    def test_invalid_dataset_missing_keys_exists(self):
        path = os.path.join(EVAL_DIR, "invalid_dataset_missing_keys.csv")
        assert os.path.isfile(path)
        assert os.path.getsize(path) > 0

    def test_multiline_output_contract_exists(self):
        path = os.path.join(EVAL_DIR, "multiline_output_contract.md")
        assert os.path.isfile(path)
        assert os.path.getsize(path) > 0

    def test_deployment_gate_contract_exists(self):
        path = os.path.join(EVAL_DIR, "deployment_gate_contract.json")
        assert os.path.isfile(path)
        with open(path) as f:
            gate = json.load(f)
        assert isinstance(gate, (dict, list))

    def test_evaluation_has_at_least_8_files(self):
        files = [f for f in os.listdir(EVAL_DIR) if os.path.isfile(os.path.join(EVAL_DIR, f))]
        assert len(files) >= 8
