import pytest
from agentx_evolve.models.json_output_validator import (
    parse_json_output,
    validate_json_output,
    make_invalid_json_response,
)
from agentx_evolve.models.model_models import ModelRequest, ModelResponse


class TestParseJsonOutput:
    def test_valid_json(self):
        result = parse_json_output('{"key": "value"}')
        assert result == {"key": "value"}

    def test_invalid_json(self):
        result = parse_json_output("not json")
        assert result is None

    def test_code_fence_json(self):
        result = parse_json_output('```json\n{"key": "val"}\n```')
        assert result == {"key": "val"}

    def test_code_fence_no_lang(self):
        result = parse_json_output('```\n{"key": "val"}\n```')
        assert result == {"key": "val"}

    def test_empty_string(self):
        result = parse_json_output("")
        assert result is None

    def test_whitespace_only(self):
        result = parse_json_output("   ")
        assert result is None


class TestValidateJsonOutput:
    def test_valid_against_schema(self):
        schema = {"required": ["name"], "properties": {"name": {"type": "string"}}}
        errors = validate_json_output({"name": "Alice"}, schema)
        assert errors == []

    def test_missing_required_field(self):
        schema = {"required": ["name", "age"], "properties": {"name": {"type": "string"}, "age": {"type": "integer"}}}
        errors = validate_json_output({"name": "Alice"}, schema)
        assert len(errors) >= 1
        assert "required" in errors[0].lower() or "missing" in errors[0].lower()

    def test_none_schema_skips_validation(self):
        errors = validate_json_output({"name": "Alice"}, None)
        assert errors == []

    def test_non_dict_input(self):
        schema = {"required": ["key"]}
        errors = validate_json_output([1, 2, 3], schema)
        assert len(errors) >= 1


class TestMakeInvalidJsonResponse:
    def test_returns_model_response(self):
        req = ModelRequest()
        resp = make_invalid_json_response(req, "could not parse")
        assert isinstance(resp, ModelResponse)
        assert resp.status == "INVALID"

    def test_includes_error(self):
        req = ModelRequest()
        resp = make_invalid_json_response(req, "parse error occurred")
        assert "parse error occurred" in resp.message

    def test_empty_error(self):
        req = ModelRequest()
        resp = make_invalid_json_response(req, "")
        assert resp.status == "INVALID"
