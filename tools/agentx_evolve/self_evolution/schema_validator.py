from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MvpSchemaField:
    name: str
    field_type: str
    required: bool = True
    default: Any = None
    description: str = ""
    valid_values: list[Any] | None = None

    def validate(self, value: Any) -> list[str]:
        errors: list[str] = []
        if value is None:
            if self.required:
                errors.append(f"Field '{self.name}' is required")
            return errors

        type_map = {
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "dict": dict,
            "list": list,
            "any": None,
        }
        expected_type = type_map.get(self.field_type)
        if expected_type is not None and not isinstance(value, expected_type):
            errors.append(
                f"Field '{self.name}' expected {self.field_type}, got {type(value).__name__}"
            )
            return errors

        if self.valid_values is not None and value not in self.valid_values:
            errors.append(
                f"Field '{self.name}' value {value!r} not in valid values: {self.valid_values}"
            )

        return errors


@dataclass
class MvpSchema:
    name: str = ""
    fields: list[MvpSchemaField] = field(default_factory=list)
    description: str = ""

    def validate(self, data: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        for field in self.fields:
            value = data.get(field.name)
            field_errors = field.validate(value)
            errors.extend(field_errors)

        unknown = [k for k in data if k not in {f.name for f in self.fields}]
        for key in unknown:
            errors.append(f"Unknown field '{key}'")

        return errors


def build_schema_from_contract(
    inputs: dict[str, Any],
    outputs: dict[str, Any],
) -> tuple[MvpSchema, MvpSchema]:
    input_fields = [
        MvpSchemaField(name=k, field_type=type(v).__name__, required=True)
        for k, v in inputs.items()
    ]
    output_fields = [
        MvpSchemaField(name=k, field_type=type(v).__name__, required=True)
        for k, v in outputs.items()
    ]

    input_schema = MvpSchema(
        name="input_schema",
        fields=input_fields,
        description="Input fields derived from agent contract",
    )
    output_schema = MvpSchema(
        name="output_schema",
        fields=output_fields,
        description="Output fields derived from agent contract",
    )
    return input_schema, output_schema
