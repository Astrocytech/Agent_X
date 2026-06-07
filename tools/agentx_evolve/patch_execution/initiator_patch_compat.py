from __future__ import annotations

import json
import subprocess
from pathlib import Path

from agentx_evolve.patch_execution.patch_models import utc_now_iso


class InitiatorPatchCompat:
    def __init__(self, repo_root: Path | None = None) -> None:
        self._repo_root: Path | None = repo_root

    def get_repo_root(self) -> Path:
        if self._repo_root is not None:
            return self._repo_root
        return Path(".")

    def get_runtime_state_root(self) -> Path:
        return self.get_repo_root() / ".agentx-init"

    def load_proposal(self, proposal_id: str) -> dict:
        path = self.get_runtime_state_root() / "proposals" / f"{proposal_id}.json"
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return {"error": f"Proposal {proposal_id} not found", "proposal_id": proposal_id}
        except json.JSONDecodeError as e:
            return {"error": f"Invalid proposal JSON: {e}", "proposal_id": proposal_id}

    def load_governance_decision(self, governance_decision_id: str) -> dict:
        path = self.get_runtime_state_root() / "policies" / f"{governance_decision_id}.json"
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return {
                "error": f"Governance decision {governance_decision_id} not found",
                "governance_decision_id": governance_decision_id,
            }
        except json.JSONDecodeError as e:
            return {
                "error": f"Invalid governance decision JSON: {e}",
                "governance_decision_id": governance_decision_id,
            }

    def validate_schema(self, artifact: dict, schema_id: str) -> dict:
        schema_path = self.get_repo_root() / "schemas" / schema_id
        if not schema_path.exists():
            schema_alt = self.get_repo_root() / ".agentx-init" / "schemas" / schema_id
            if schema_alt.exists():
                schema_path = schema_alt
            else:
                return {
                    "valid": True,
                    "warning": f"Schema {schema_id} not found, skipping validation",
                }
        try:
            import jsonschema

            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            jsonschema.validate(instance=artifact, schema=schema)
            return {"valid": True, "errors": []}
        except ImportError:
            return {"valid": True, "warning": "jsonschema not available, skipping validation"}
        except json.JSONDecodeError:
            return {"valid": True, "warning": f"Schema {schema_id} is invalid JSON, skipping"}
        except jsonschema.ValidationError as e:
            return {"valid": False, "errors": [e.message]}
        except Exception as e:
            return {"valid": False, "errors": [str(e)]}

    def write_json_atomic(self, path: Path, artifact: dict) -> dict:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(".tmp")
            tmp.write_text(json.dumps(artifact, indent=2, default=str), encoding="utf-8")
            tmp.rename(path)
            return {"success": True, "path": str(path)}
        except OSError as e:
            return {"success": False, "error": str(e)}

    def append_jsonl(self, path: Path, artifact: dict) -> dict:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(artifact, default=str) + "\n")
            return {"success": True, "path": str(path)}
        except OSError as e:
            return {"success": False, "error": str(e)}

    def append_audit_event(self, event: dict) -> dict:
        path = self.get_runtime_state_root() / "memory" / "audit_events.jsonl"
        return self.append_jsonl(path, event)

    def run_validation_command(self, command: list[str]) -> dict:
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=60,
            )
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except FileNotFoundError:
            return {"success": False, "error": f"Command not found: {command[0] if command else ''}"}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out after 60 seconds"}
        except Exception as e:
            return {"success": False, "error": str(e)}
