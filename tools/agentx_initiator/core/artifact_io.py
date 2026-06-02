from __future__ import annotations
import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from uuid import uuid4
from agentx_initiator.core.schema_validation import validate_instance


@dataclass
class ArtifactWriteResult:
    status: str = "SUCCESS"
    path: Optional[Path] = None
    error: Optional[str] = None
    warning: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "path": str(self.path) if self.path else None,
            "error": self.error,
            "warning": self.warning,
        }


def write_validated_latest(path: Path, obj: dict, schema_name: str) -> ArtifactWriteResult:
    path = path.resolve()
    parent = path.parent
    parent.mkdir(parents=True, exist_ok=True)

    validation = validate_instance(obj, schema_name)
    if not validation.valid:
        return ArtifactWriteResult(
            status="FAILED",
            error=f"Schema validation failed for {schema_name}: {validation.errors}",
        )

    tmp = parent / f"{path.name}.tmp.{uuid4().hex}"
    try:
        tmp.write_text(json.dumps(obj, indent=2, default=str))
        tmp2 = parent / f"{path.name}.tmp2.{uuid4().hex}"
        try:
            re_read = json.loads(tmp.read_text())
            re_validate = validate_instance(re_read, schema_name)
            if not re_validate.valid:
                tmp.unlink(missing_ok=True)
                return ArtifactWriteResult(
                    status="FAILED",
                    error=f"Re-validation failed for {schema_name}: {re_validate.errors}",
                )
            tmp2.write_text(json.dumps(re_read, indent=2, default=str))
            tmp2.replace(path)
        finally:
            tmp.unlink(missing_ok=True)
            tmp2.unlink(missing_ok=True)
    except OSError as e:
        return ArtifactWriteResult(
            status="FAILED",
            error=f"Write error: {e}",
        )

    return ArtifactWriteResult(status="SUCCESS", path=path)
