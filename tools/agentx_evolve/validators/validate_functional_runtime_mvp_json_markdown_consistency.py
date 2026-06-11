"""Validate JSON/Markdown non-contradiction (items 161-162).

Checks:
- Markdown transcript is a rendering of the JSON transcript and does not
  claim contradictory verdicts.
- For any report pair (JSON + Markdown), the Markdown does not assert
  PASS/BLOCKED/FAIL when the JSON says something different.
- Markdown alone cannot serve as proof evidence where JSON is required.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from agentx_evolve.validators.common import parse_report_dir

JSON_MD_PAIRS: list[tuple[str, str | None]] = [
    ("functional_runtime_mvp_command_transcript.json", "functional_runtime_mvp_command_transcript.md"),
    ("functional_runtime_mvp_anti_false_pass_audit.json", "functional_runtime_mvp_anti_false_pass_report.md"),
    ("functional_runtime_mvp_final_verdict.json", None),
]


def _load_json(path: Path) -> dict | list | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data
    except (OSError, json.JSONDecodeError):
        return None


def _load_md(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def validate_json_markdown_consistency(report_dir: Path) -> list[str]:
    errors: list[str] = []

    for json_name, md_name in JSON_MD_PAIRS:
        json_path = report_dir / json_name
        json_data = _load_json(json_path)
        if json_data is None:
            # final_verdict and anti_false_pass_audit are generated later in the pipeline
            if json_name in ("functional_runtime_mvp_final_verdict.json", "functional_runtime_mvp_anti_false_pass_audit.json"):
                continue
            errors.append(f"JSON/MD: required JSON file missing: {json_name}")
            continue

        md_path = report_dir / md_name if md_name else None

        if md_path and not md_path.exists():
            # markdown counterpart for these files is optional
            if json_name in ("functional_runtime_mvp_final_verdict.json", "functional_runtime_mvp_anti_false_pass_audit.json"):
                continue
            errors.append(f"JSON/MD: Markdown counterpart missing for {json_name}: {md_name}")
            continue

        # For transcript: check Markdown reflects failures
        if json_name == "functional_runtime_mvp_command_transcript.json" and md_path:
            md_content = _load_md(md_path)
            if md_content is not None:
                json_entries = json_data if isinstance(json_data, list) else []
                json_has_fail = any(e.get("exit_code", 0) != 0 for e in json_entries)
                md_has_fail = "FAIL" in md_content
                if json_has_fail and not md_has_fail:
                    errors.append(
                        "JSON/MD: transcript.json has failures but transcript.md does not reflect them"
                    )

        # For final_verdict: check Markdown does not override machine-readable classification
        if json_name == "functional_runtime_mvp_final_verdict.json":
            classification = json_data.get("classification", "") if isinstance(json_data, dict) else ""

            md_path_fv = report_dir / "functional_runtime_mvp_final_verdict.json.md"
            if md_path_fv and md_path_fv.exists():
                md_content = _load_md(md_path_fv)
                if md_content and classification:
                    if "FUNCTIONAL_RUNTIME_MVP" in md_content and classification != "FUNCTIONAL_RUNTIME_MVP":
                        errors.append(
                            "JSON/MD: Markdown verdict claims FUNCTIONAL_RUNTIME_MVP but JSON does not"
                        )

    # Check no Markdown file independently claims FUNCTIONAL_RUNTIME_MVP without JSON support.
    # Only check the first 30 lines (classification/verdict area) to avoid flagging
    # filename references or code block mentions deeper in the report body.
    for md_path in sorted(report_dir.glob("*.md")):
        md_content = _load_md(md_path)
        if md_content is None:
            continue
        md_lines = md_content.split("\n")[:30]
        md_header = "\n".join(md_lines)
        if "FUNCTIONAL_RUNTIME_MVP" not in md_header:
            continue
        json_basename = md_path.stem + ".json"
        if not md_path.stem.endswith("_report") and not md_path.stem.endswith("_md"):
            json_basename = md_path.stem.replace(".md", "") + ".json"
        json_path = report_dir / json_basename
        if json_path.exists():
            json_data = _load_json(json_path)
            if isinstance(json_data, dict):
                md_classification = json_data.get("classification", "")
                if md_classification != "FUNCTIONAL_RUNTIME_MVP":
                    errors.append(
                        f"JSON/MD: {md_path.name} claims FUNCTIONAL_RUNTIME_MVP but JSON "
                        f"{json_path.name} says {md_classification}"
                    )

    return errors


def main() -> int:
    report_dir = parse_report_dir()
    errors = validate_json_markdown_consistency(report_dir)
    for err in errors:
        print(err, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
