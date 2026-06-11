import json
import os

BENCHCORE = os.path.join(os.path.dirname(__file__), "..")
GV_DIR = os.path.join(BENCHCORE, "grammar_validation")

REQUIRED_GV_FILES = [
    "ast_generation_contract.md",
    "cg_command.schema.json",
    "invalid_examples.jsonl",
    "nlp_to_code_benchmark_contract.md",
    "od_command.schema.json",
    "production_cue.schema.json",
    "quickcode.schema.json",
    "valid_examples.jsonl",
]


class TestGrammarValidation:

    def test_grammar_validation_directory_exists(self):
        assert os.path.isdir(GV_DIR)

    def test_all_required_files_exist(self):
        for fname in REQUIRED_GV_FILES:
            path = os.path.join(GV_DIR, fname)
            assert os.path.isfile(path), f"Missing: {fname}"
            assert os.path.getsize(path) > 0, f"Empty: {fname}"

    def test_has_8_files(self):
        files = [f for f in os.listdir(GV_DIR) if os.path.isfile(os.path.join(GV_DIR, f))]
        assert len(files) == 8

    def test_production_cue_schema_is_valid(self):
        path = os.path.join(GV_DIR, "production_cue.schema.json")
        with open(path) as f:
            schema = json.load(f)
        assert schema.get("$schema")
        assert schema.get("type") == "object"
        assert "properties" in schema
        assert "required" in schema
        assert isinstance(schema["properties"], dict)
        assert len(schema["properties"]) > 0

    def test_production_cue_schema_has_cue_with_maxlength(self):
        path = os.path.join(GV_DIR, "production_cue.schema.json")
        with open(path) as f:
            schema = json.load(f)
        cue = schema["properties"]["cue"]
        assert cue["maxLength"] == 150

    def test_production_cue_schema_has_delimiter_enum(self):
        path = os.path.join(GV_DIR, "production_cue.schema.json")
        with open(path) as f:
            schema = json.load(f)
        delim = schema["properties"]["delimiter"]
        assert "enum" in delim
        assert ":" in delim["enum"]
        assert "=" in delim["enum"]

    def test_production_cue_schema_disallows_additional(self):
        path = os.path.join(GV_DIR, "production_cue.schema.json")
        with open(path) as f:
            schema = json.load(f)
        assert schema.get("additionalProperties") is False

    def test_od_command_schema_exists(self):
        path = os.path.join(GV_DIR, "od_command.schema.json")
        with open(path) as f:
            schema = json.load(f)
        assert isinstance(schema, dict)
        assert len(schema) > 0

    def test_cg_command_schema_exists(self):
        path = os.path.join(GV_DIR, "cg_command.schema.json")
        with open(path) as f:
            schema = json.load(f)
        assert isinstance(schema, dict)
        assert len(schema) > 0

    def test_quickcode_schema_exists(self):
        path = os.path.join(GV_DIR, "quickcode.schema.json")
        with open(path) as f:
            schema = json.load(f)
        assert isinstance(schema, dict)
        assert len(schema) > 0

    def test_valid_examples_is_non_empty_jsonl(self):
        path = os.path.join(GV_DIR, "valid_examples.jsonl")
        with open(path) as f:
            lines = [l for l in f if l.strip()]
        assert len(lines) > 0
        for line in lines:
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_invalid_examples_is_non_empty_jsonl(self):
        path = os.path.join(GV_DIR, "invalid_examples.jsonl")
        with open(path) as f:
            lines = [l for l in f if l.strip()]
        assert len(lines) > 0
        for line in lines:
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_ast_generation_contract_is_non_empty(self):
        path = os.path.join(GV_DIR, "ast_generation_contract.md")
        assert os.path.getsize(path) > 100

    def test_nlp_to_code_benchmark_contract_is_non_empty(self):
        path = os.path.join(GV_DIR, "nlp_to_code_benchmark_contract.md")
        assert os.path.getsize(path) > 100

    def test_valid_and_invalid_examples_have_different_entries(self):
        v_path = os.path.join(GV_DIR, "valid_examples.jsonl")
        i_path = os.path.join(GV_DIR, "invalid_examples.jsonl")
        with open(v_path) as f:
            v_lines = set(f.readlines())
        with open(i_path) as f:
            i_lines = set(f.readlines())
        assert v_lines != i_lines
