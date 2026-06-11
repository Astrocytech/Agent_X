"""Prompt-contract versioning and output validation.

Item 34 (28.1/28.2/28.3): Prompt templates with versioned contract,
expected output schema, and output validation.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


@dataclass
class PromptContract:
    contract_id: str
    version: str = "1.0.0"
    description: str = ""
    prompt_template: str = ""
    input_schema: dict | None = None
    output_schema: dict | None = None
    expected_output_keys: list[str] = field(default_factory=list)
    output_validator: str = ""  # JSON path or regex
    examples: list[dict] = field(default_factory=list)


def check_output_keys(contract: PromptContract, output: dict) -> list[str]:
    missing = [k for k in contract.expected_output_keys if k not in output]
    return missing


def validate_json_output(contract: PromptContract, output: str) -> dict:
    errors = []
    try:
        parsed = json.loads(output)
    except json.JSONDecodeError as e:
        return {"valid": False, "errors": [f"Invalid JSON: {e}"]}

    if not isinstance(parsed, dict):
        return {"valid": False, "errors": ["Output must be a JSON object"]}

    missing = check_output_keys(contract, parsed)
    if missing:
        errors.append(f"Missing keys: {missing}")

    if contract.output_schema:
        for key, expected_type in contract.output_schema.items():
            if key in parsed:
                if not isinstance(parsed[key], eval(expected_type)):
                    errors.append(f"Key '{key}' expected {expected_type}, got {type(parsed[key]).__name__}")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "parsed": parsed,
    }


CONTRACTS: dict[str, PromptContract] = {}


def register_contract(contract: PromptContract) -> None:
    CONTRACTS[contract.contract_id] = contract


def get_contract(contract_id: str) -> PromptContract | None:
    return CONTRACTS.get(contract_id)


umbrella_contract = PromptContract(
    contract_id="umbrella-recommendation",
    version="1.0.0",
    description="Umbrella recommendation given weather data",
    expected_output_keys=["recommendation", "reason", "confidence"],
    output_schema={"recommendation": "str", "reason": "str", "confidence": "float"},
)
register_contract(umbrella_contract)
