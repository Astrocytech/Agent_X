from agentx_evolve.self_evolution.schema_validator import (
    MvpSchema,
    MvpSchemaField,
    build_schema_from_contract,
)


class TestMvpSchemaField:
    def test_required_field_missing(self):
        field = MvpSchemaField(name="name", field_type="str", required=True)
        errors = field.validate(None)
        assert "required" in errors[0]

    def test_optional_field_missing(self):
        field = MvpSchemaField(name="name", field_type="str", required=False)
        errors = field.validate(None)
        assert errors == []

    def test_type_mismatch(self):
        field = MvpSchemaField(name="count", field_type="int")
        errors = field.validate("not_an_int")
        assert "expected int" in errors[0]

    def test_valid_value(self):
        field = MvpSchemaField(name="mode", field_type="str", valid_values=["a", "b"])
        errors = field.validate("a")
        assert errors == []

    def test_invalid_value(self):
        field = MvpSchemaField(name="mode", field_type="str", valid_values=["a", "b"])
        errors = field.validate("c")
        assert "not in valid values" in errors[0]


class TestMvpSchema:
    def test_schema_validates_all_fields(self):
        schema = MvpSchema(name="test", fields=[
            MvpSchemaField(name="name", field_type="str"),
            MvpSchemaField(name="count", field_type="int"),
        ])
        errors = schema.validate({"name": "hello", "count": 42})
        assert errors == []

    def test_schema_detects_unknown_fields(self):
        schema = MvpSchema(name="test", fields=[
            MvpSchemaField(name="name", field_type="str"),
        ])
        errors = schema.validate({"name": "hello", "extra": "value"})
        assert any("Unknown" in e for e in errors)

    def test_schema_detects_missing_required(self):
        schema = MvpSchema(name="test", fields=[
            MvpSchemaField(name="name", field_type="str", required=True),
            MvpSchemaField(name="count", field_type="int", required=True),
        ])
        errors = schema.validate({"name": "hello"})
        assert any("count" in e for e in errors)

    def test_schema_type_validation(self):
        schema = MvpSchema(name="test", fields=[
            MvpSchemaField(name="count", field_type="int"),
            MvpSchemaField(name="active", field_type="bool"),
        ])
        errors = schema.validate({"count": "42", "active": True})
        assert any("int" in e for e in errors)

    def test_empty_schema(self):
        schema = MvpSchema(name="empty")
        errors = schema.validate({})
        assert errors == []


class TestBuildSchemaFromContract:
    def test_builds_input_schema(self):
        input_schema, output_schema = build_schema_from_contract(
            {"query": "test", "limit": 10},
            {"results": []},
        )
        assert input_schema.name == "input_schema"
        field_names = {f.name for f in input_schema.fields}
        assert "query" in field_names
        assert "limit" in field_names

    def test_builds_output_schema(self):
        input_schema, output_schema = build_schema_from_contract(
            {"query": "test"},
            {"results": [], "count": 0},
        )
        assert output_schema.name == "output_schema"
        field_names = {f.name for f in output_schema.fields}
        assert "results" in field_names
        assert "count" in field_names
