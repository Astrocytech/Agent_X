import json
import os

BENCHCORE = os.path.join(os.path.dirname(__file__), "..")
PA_DIR = os.path.join(BENCHCORE, "protocol_architecture")
OR_DIR = os.path.join(BENCHCORE, "operations_reproducibility")

REQUIRED_PA_FILES = [
    "adapter_boundary_contract.md",
    "failure_modes.json",
    "mock_mos_output.schema.json",
    "mock_rest_input.schema.json",
    "rest_mos_mapping_contract.md",
    "semantic_parser_pipeline_contract.md",
]

REQUIRED_OR_FILES = [
    "mysql_restore_boundary.md",
    "remote_log_tailing_boundary.md",
    "wsl_boundary.md",
]


class TestProtocolBoundaries:

    def test_protocol_architecture_directory_exists(self):
        assert os.path.isdir(PA_DIR)

    def test_operations_reproducibility_directory_exists(self):
        assert os.path.isdir(OR_DIR)

    def test_all_pa_files_exist(self):
        for fname in REQUIRED_PA_FILES:
            path = os.path.join(PA_DIR, fname)
            assert os.path.isfile(path), f"Missing: {fname}"
            assert os.path.getsize(path) > 0, f"Empty: {fname}"

    def test_all_or_files_exist(self):
        for fname in REQUIRED_OR_FILES:
            path = os.path.join(OR_DIR, fname)
            assert os.path.isfile(path), f"Missing: {fname}"
            assert os.path.getsize(path) > 0, f"Empty: {fname}"

    def test_pa_has_6_files(self):
        files = [f for f in os.listdir(PA_DIR) if os.path.isfile(os.path.join(PA_DIR, f))]
        assert len(files) == 6

    def test_or_has_3_files(self):
        files = [f for f in os.listdir(OR_DIR) if os.path.isfile(os.path.join(OR_DIR, f))]
        assert len(files) == 3

    def test_failure_modes_is_valid_json(self):
        path = os.path.join(PA_DIR, "failure_modes.json")
        with open(path) as f:
            modes = json.load(f)
        assert isinstance(modes, list)
        assert len(modes) >= 10

    def test_failure_modes_have_required_fields(self):
        path = os.path.join(PA_DIR, "failure_modes.json")
        with open(path) as f:
            modes = json.load(f)
        required = {"mode_id", "name", "description", "category", "severity", "mitigation", "mock_reproducible"}
        for m in modes:
            missing = required - set(m.keys())
            assert not missing, f"{m['mode_id']} missing: {missing}"

    def test_failure_modes_valid_severity(self):
        path = os.path.join(PA_DIR, "failure_modes.json")
        with open(path) as f:
            modes = json.load(f)
        valid = {"high", "medium", "low"}
        for m in modes:
            assert m["severity"] in valid, f"{m['mode_id']} bad severity"

    def test_failure_modes_valid_categories(self):
        path = os.path.join(PA_DIR, "failure_modes.json")
        with open(path) as f:
            modes = json.load(f)
        valid_cats = {"network", "protocol", "data", "timeout"}
        for m in modes:
            assert m["category"] in valid_cats, f"{m['mode_id']} bad category: {m['category']}"

    def test_failure_modes_all_mock_reproducible(self):
        path = os.path.join(PA_DIR, "failure_modes.json")
        with open(path) as f:
            modes = json.load(f)
        for m in modes:
            assert m["mock_reproducible"] is True, f"{m['mode_id']} not mock_reproducible"

    def test_no_duplicate_mode_ids(self):
        path = os.path.join(PA_DIR, "failure_modes.json")
        with open(path) as f:
            modes = json.load(f)
        ids = [m["mode_id"] for m in modes]
        assert len(ids) == len(set(ids))

    def test_mock_rest_input_schema_exists(self):
        path = os.path.join(PA_DIR, "mock_rest_input.schema.json")
        with open(path) as f:
            schema = json.load(f)
        assert isinstance(schema, dict)
        assert len(schema) > 0

    def test_mock_mos_output_schema_exists(self):
        path = os.path.join(PA_DIR, "mock_mos_output.schema.json")
        with open(path) as f:
            schema = json.load(f)
        assert isinstance(schema, dict)
        assert len(schema) > 0

    def test_contract_markdown_files_are_non_empty(self):
        for fname in ["adapter_boundary_contract.md", "rest_mos_mapping_contract.md", "semantic_parser_pipeline_contract.md"]:
            path = os.path.join(PA_DIR, fname)
            assert os.path.getsize(path) > 100, f"{fname} too small"

    def test_operations_boundary_files_are_non_empty(self):
        for fname in REQUIRED_OR_FILES:
            path = os.path.join(OR_DIR, fname)
            assert os.path.getsize(path) > 50, f"{fname} too small"
