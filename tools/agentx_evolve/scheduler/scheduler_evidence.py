import json
from pathlib import Path

from .scheduler_models import (
    utc_now_iso, new_id, to_dict, sha256_file, sha256_bytes, canonical_json,
    SchedulerEvidenceManifest, SchedulerReviewReport, SchedulerCompletionRecord,
    CENTRAL_STATUS_PASS, CENTRAL_STATUS_NOT_CHECKED, CENTRAL_STATUS_NOT_RUN,
)


RUNTIME_ROOT = ".agentx-init/scheduler"

EVIDENCE_MANIFEST_FILE = "scheduler_evidence_manifest.json"
REVIEW_REPORT_FILE = "scheduler_review_report.json"
COMPLETION_RECORD_FILE = "scheduler_completion_record.json"


class SchedulerEvidenceWriter:
    def __init__(self, evidence_dir: str | Path):
        self.evidence_dir = Path(evidence_dir)
        self.evidence_dir.mkdir(parents=True, exist_ok=True)

    def write_evidence_manifest(
        self,
        validated_commit: str = "",
        commands: list[str] | None = None,
        evidence_files: list[str] | None = None,
        **kwargs,
    ) -> dict:
        manifest = SchedulerEvidenceManifest(
            validated_commit=validated_commit,
            commands=commands or [],
            evidence_files=evidence_files or [],
        )
        data = to_dict(manifest)
        path = self.evidence_dir / EVIDENCE_MANIFEST_FILE
        return self._write_json(path, data)

    def write_review_report(self, **kwargs) -> dict:
        report = SchedulerReviewReport(**kwargs)
        data = to_dict(report)
        self._add_hashes(data)
        path = self.evidence_dir / REVIEW_REPORT_FILE
        return self._write_json(path, data)

    def write_completion_record(self, **kwargs) -> dict:
        record = SchedulerCompletionRecord(**kwargs)
        data = to_dict(record)
        self._add_hashes(data)
        path = self.evidence_dir / COMPLETION_RECORD_FILE
        return self._write_json(path, data)

    def write_all(self, runtime_root: str, validated_commit: str = "") -> dict:
        results = {}
        results["manifest"] = self.write_evidence_manifest(validated_commit=validated_commit)
        results["review_report"] = self.write_review_report(reviewed_commit=validated_commit)
        results["completion_record"] = self.write_completion_record(validated_commit=validated_commit)
        self._compute_final_hashes()
        return results

    def _write_json(self, path: Path, data: dict) -> dict:
        tmp = path.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        tmp.replace(path)
        return {"path": str(path), "status": "written"}

    def _add_hashes(self, data: dict) -> None:
        if "review_report_sha256" in data:
            data["review_report_sha256"] = ""
        if "completion_record_sha256" in data:
            data["completion_record_sha256"] = ""

    def _compute_final_hashes(self) -> None:
        manifest_path = self.evidence_dir / EVIDENCE_MANIFEST_FILE
        review_path = self.evidence_dir / REVIEW_REPORT_FILE
        completion_path = self.evidence_dir / COMPLETION_RECORD_FILE
        if manifest_path.exists():
            m_hash = sha256_file(manifest_path)
        else:
            m_hash = ""
        if review_path.exists():
            with open(review_path, "r", encoding="utf-8") as f:
                review_data = json.load(f)
            review_data["evidence_manifest_sha256"] = m_hash
            review_data["review_report_sha256"] = sha256_file(review_path)
            self._write_json(review_path, review_data)
            r_hash = review_data["review_report_sha256"]
        else:
            r_hash = ""
        if completion_path.exists():
            with open(completion_path, "r", encoding="utf-8") as f:
                completion_data = json.load(f)
            completion_data["evidence_manifest_sha256"] = m_hash
            completion_data["review_report_sha256"] = r_hash
            completion_data["completion_record_sha256"] = sha256_file(completion_path)
            self._write_json(completion_path, completion_data)
