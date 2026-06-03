import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from agentx_evolve.model_runtime.schema_validator import validate_local_model_runtime_schemas


def _load_examples() -> dict:
    examples = {}

    examples["valid_model_profile_small_q4"] = {
        "schema_id": "local_model_profile.schema.json",
        "model_id": "test-model-q4",
        "model_name": "Test Model Q4",
        "model_family": "test-family",
        "model_format": "gguf",
        "quantization": "Q4",
        "max_context_tokens": 4096,
        "supported_task_types": ["CHAT_COMPLETION"],
        "supported_output_modes": ["text"],
        "supported_runtime_ids": ["test-runtime"],
        "preferred_runtime_ids": ["test-runtime"],
        "enabled": True,
        "priority": 100,
    }

    examples["valid_runtime_profile_cpu"] = {
        "schema_id": "local_runtime_profile.schema.json",
        "runtime_id": "test-runtime",
        "runtime_name": "Test Runtime",
        "runtime_kind": "local",
        "supported_model_formats": ["gguf"],
        "supported_quantizations": ["Q4", "Q8"],
        "supported_devices": ["CPU"],
        "max_context_tokens": 8192,
        "enabled": True,
    }

    examples["valid_hardware_profile_cpu"] = {
        "schema_id": "local_hardware_profile.schema.json",
        "hardware_profile_id": "hw-test",
        "probe_mode": "STATIC_ONLY",
        "conservative_ram_limit_bytes": 8589934592,
        "gpu_present": False,
    }

    examples["valid_model_inventory"] = {
        "schema_id": "local_model_inventory.schema.json",
        "inventory_id": "inv-test",
        "created_at": "2026-01-01T00:00:00Z",
        "approved_model_roots": ["/tmp/models"],
        "models": [{"model_id": "test-model-q4", "model_path": "/tmp/models/test.gguf", "enabled": True}],
    }

    examples["valid_selection_constraints"] = {
        "schema_id": "local_model_selection_constraints.schema.json",
        "local_only": True,
        "max_context_tokens": 8192,
        "max_model_size_bytes": 8589934592,
    }

    examples["valid_request_limits"] = {
        "schema_id": "local_runtime_request_limits.schema.json",
        "max_prompt_tokens": 4096,
        "max_response_tokens": 2048,
        "max_total_context_tokens": 8192,
    }

    examples["valid_eligibility_decision"] = {
        "schema_id": "local_model_eligibility_decision.schema.json",
        "decision_id": "elig-test",
        "timestamp": "2026-01-01T00:00:00Z",
        "eligibility": "ELIGIBLE",
        "runtime_mode": "LOCAL_ONLY",
        "device": "CPU",
    }

    examples["missing_model_id"] = {
        "schema_id": "local_model_profile.schema.json",
        "model_name": "No ID",
        "model_family": "test",
        "model_format": "gguf",
        "quantization": "Q4",
    }

    examples["unknown_quantization"] = {
        "schema_id": "local_model_profile.schema.json",
        "model_id": "bad-quant",
        "model_name": "Bad Quant",
        "model_family": "test",
        "model_format": "gguf",
        "quantization": "Q99",
    }

    examples["negative_context"] = {
        "schema_id": "local_runtime_request_limits.schema.json",
        "max_prompt_tokens": -1,
        "max_response_tokens": 2048,
        "max_total_context_tokens": 0,
    }

    return examples


def main():
    schema_dir = Path(__file__).resolve().parent.parent / "schemas"
    examples = _load_examples()
    result = validate_local_model_runtime_schemas(schema_dir, examples)
    print(f"Schema validation: {'PASS' if result['all_passed'] else 'FAIL'}")
    print(f"  Schemas checked: {result['schema_count']}")
    print(f"  Examples checked: {result['example_count']}")
    print(f"  Summary: {result['summary']}")
    for r in result["results"]:
        status = "PASS" if r["status"] == "PASS" else "FAIL"
        name = r.get("example") or r.get("schema") or "unknown"
        print(f"  [{status}] {name}: {r.get('detail', '')}")
    sys.exit(0 if result["all_passed"] else 1)


if __name__ == "__main__":
    main()
