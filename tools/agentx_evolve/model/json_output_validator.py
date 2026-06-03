from __future__ import annotations
import json
from typing import Any


class JsonOutputValidator:
    def validate(self, content: str, expected_schema: dict | None = None) -> tuple[bool, dict | None, str]:
        content = content.strip()
        if content.startswith("```"):
            lines = content.split("\n")
            if len(lines) >= 3:
                content = "\n".join(lines[1:-1]).strip()
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            return False, None, f"Invalid JSON: {e}"
        if not isinstance(data, dict):
            return False, None, "JSON root must be an object"
        if expected_schema:
            valid, error = self._validate_schema(data, expected_schema)
            if not valid:
                return False, data, error
        return True, data, ""

    def _validate_schema(self, data: dict, schema: dict) -> tuple[bool, str]:
        required = schema.get("required", [])
        for field in required:
            if field not in data:
                return False, f"Missing required field: {field}"
        props = schema.get("properties", {})
        for key, value in data.items():
            if key not in props:
                continue
            expected_type = props[key].get("type", "")
            if expected_type == "string" and not isinstance(value, str):
                return False, f"Field '{key}' must be a string"
            if expected_type == "integer" and not isinstance(value, int):
                return False, f"Field '{key}' must be an integer"
            if expected_type == "boolean" and not isinstance(value, bool):
                return False, f"Field '{key}' must be a boolean"
            if expected_type == "array" and not isinstance(value, list):
                return False, f"Field '{key}' must be an array"
            if expected_type == "object" and not isinstance(value, dict):
                return False, f"Field '{key}' must be an object"
        return True, ""

    def extract_json_from_text(self, text: str) -> str | None:
        text = text.strip()
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return text[start:end+1]
        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end != -1 and end > start:
            return text[start:end+1]
        return None
