from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EVIDENCE_DIR = REPO_ROOT / "reports" / "umbrella_agent"

UMBRELLA_OUT_DIR = "examples/umbrella_agent"

RECOMMENDATION_ENGINE_SRC = '''
from __future__ import annotations

RAIN_LIKE = {"rain", "shower", "thunderstorm"}
ALERT_CONDITIONS = {"storm", "heavy rain", "freezing rain", "sleet", "hail"}


def recommend(weather: dict) -> dict:
    result = {
        "recommendation": "unknown",
        "answer": "",
        "reason": "",
        "weather_source": "",
        "confidence": 0.0,
    }

    if not isinstance(weather, dict):
        result["answer"] = "No weather data provided."
        result["reason"] = "Input was not a dictionary."
        return result

    condition = weather.get("condition")
    precip = weather.get("precipitation_probability")
    source = weather.get("source") or weather.get("provider") or "unknown"
    result["weather_source"] = source

    if weather.get("success") is False:
        result["answer"] = weather.get("error", "Weather provider returned an error.")
        result["reason"] = "Provider returned failure status."
        return result

    if condition is None:
        result["answer"] = "Weather data is incomplete — condition field missing."
        result["reason"] = "Missing condition in weather payload."
        return result

    if not isinstance(condition, str):
        result["answer"] = "Weather data is malformed — condition is not a string."
        result["reason"] = "Condition field had unexpected type."
        return result

    cond_lower = condition.strip().lower()

    if precip is None or not isinstance(precip, (int, float)):
        result["answer"] = f"Weather data is incomplete — probability missing for condition '{condition}'."
        result["reason"] = "Missing or invalid precipitation_probability."
        return result

    if cond_lower in ALERT_CONDITIONS:
        result["recommendation"] = "alert"
        result["answer"] = f"{condition.title()} conditions detected. Stay indoors and avoid travel."
        result["reason"] = f"High-severity weather condition: {condition}."
        result["confidence"] = 0.9
        return result

    if cond_lower == "drizzle":
        result["recommendation"] = "maybe"
        result["answer"] = "Light drizzle possible. A light jacket or small umbrella recommended."
        result["reason"] = f"Drizzle with {precip}% probability."
        result["confidence"] = 0.4
        return result

    if cond_lower in RAIN_LIKE:
        if precip >= 70:
            result["recommendation"] = "yes"
            result["answer"] = f"{condition.title()} very likely ({precip}%). Definitely bring an umbrella."
            result["reason"] = f"High-probability {condition}."
            result["confidence"] = 0.8
        elif precip >= 40:
            result["recommendation"] = "yes"
            result["answer"] = f"{condition.title()} probable ({precip}%). Bring an umbrella to be safe."
            result["reason"] = f"Moderate-probability {condition}."
            result["confidence"] = 0.6
        else:
            result["recommendation"] = "maybe"
            result["answer"] = f"{condition.title()} possible ({precip}%). Consider bringing an umbrella."
            result["reason"] = f"Low-probability {condition} but condition warrants caution."
            result["confidence"] = 0.4
        return result

    if cond_lower == "snow":
        if precip >= 30:
            result["recommendation"] = "yes"
            result["answer"] = f"Snow expected ({precip}%). Bring an umbrella and warm clothing."
            result["reason"] = f"Significant snow probability: {precip}%."
            result["confidence"] = 0.7
        elif precip >= 10:
            result["recommendation"] = "maybe"
            result["answer"] = f"Light snow possible ({precip}%). A hat or umbrella may help."
            result["reason"] = f"Low snow probability: {precip}%."
            result["confidence"] = 0.4
        else:
            result["recommendation"] = "no"
            result["answer"] = f"Snow unlikely ({precip}%). No umbrella needed."
            result["reason"] = f"Very low snow probability: {precip}%."
            result["confidence"] = 0.8
        return result

    if cond_lower in ("cloudy", "overcast", "fog", "mist"):
        if precip >= 50:
            result["recommendation"] = "maybe"
            result["answer"] = f"{condition.title()} with {precip}% chance of precipitation. Consider an umbrella."
            result["reason"] = f"Overcast with moderate precipitation risk."
            result["confidence"] = 0.4
        else:
            result["recommendation"] = "no"
            result["answer"] = f"{condition.title()} but precipitation unlikely ({precip}%). No umbrella needed."
            result["reason"] = f"Low precipitation risk under overcast skies."
            result["confidence"] = 0.7
        return result

    if cond_lower == "clear":
        if precip > 0:
            result["recommendation"] = "no"
            result["answer"] = f"Clear skies but slight precipitation chance ({precip}%). Umbrella probably not needed."
            result["reason"] = f"Clear skies with minimal precipitation risk."
            result["confidence"] = 0.8
        else:
            result["recommendation"] = "no"
            result["answer"] = "Clear skies, no precipitation expected. No umbrella needed."
            result["reason"] = "Clear weather with zero precipitation probability."
            result["confidence"] = 0.9
        return result

    if precip >= 60:
        result["recommendation"] = "yes"
        result["answer"] = f"High precipitation probability ({precip}%) despite '{condition}' conditions. Bring an umbrella."
        result["reason"] = f"Fallback: high precipitation probability ({precip}%) with condition '{condition}'."
        result["confidence"] = 0.5
        return result

    if precip >= 30:
        result["recommendation"] = "maybe"
        result["answer"] = f"Moderate precipitation probability ({precip}%) with '{condition}' conditions. Consider an umbrella."
        result["reason"] = f"Fallback: moderate precipitation probability ({precip}%) with unknown condition '{condition}'."
        result["confidence"] = 0.3
        return result

    result["recommendation"] = "no"
    result["answer"] = f"Low precipitation probability ({precip}%) with '{condition}' conditions. No umbrella needed."
    result["reason"] = f"Fallback: low precipitation probability ({precip}%) with condition '{condition}'."
    result["confidence"] = 0.6
    return result
'''

RUNTIME_SRC = '''
from __future__ import annotations

from pathlib import Path
from umbrella_agent.recommendation_engine import recommend
from agentx_evolve.fixtures.weather_fixture_provider import WeatherFixtureProvider


class UmbrellaAgentRuntime:
    def __init__(self, provider: WeatherFixtureProvider | None = None) -> None:
        self._provider = provider or WeatherFixtureProvider()

    def answer(self, location: str, date: str = "today") -> dict:
        if not location or not isinstance(location, str):
            return {
                "recommendation": "unknown",
                "confidence": 0.0,
                "answer": "A location is required.",
                "condition": None,
                "precipitation_probability": None,
                "temperature_c": None,
                "location": location,
                "date": date,
                "weather_source": "",
                "reason": "No location provided.",
            }

        weather_result = self._provider.fetch(location, date)
        if not weather_result.get("success"):
            weather_data = weather_result
        else:
            weather_data = weather_result["data"]

        rec = recommend(weather_data)

        return {
            "recommendation": rec["recommendation"],
            "answer": rec["answer"],
            "reason": rec["reason"],
            "weather_source": rec["weather_source"],
            "confidence": rec["confidence"],
            "condition": weather_data.get("condition") if isinstance(weather_data, dict) else None,
            "precipitation_probability": weather_data.get("precipitation_probability") if isinstance(weather_data, dict) else None,
            "temperature_c": weather_data.get("temperature_c") if isinstance(weather_data, dict) else None,
            "location": location,
            "date": weather_data.get("date", date) if isinstance(weather_data, dict) else date,
        }
'''

INIT_SRC = '''
from umbrella_agent.runtime import UmbrellaAgentRuntime


def ask_umbrella(location: str, date: str = "today") -> dict:
    return UmbrellaAgentRuntime().answer(location, date)
'''

TEST_SRC = '''
from __future__ import annotations

import pytest
from umbrella_agent.recommendation_engine import recommend


def test_rain_high_prob_yes():
    r = recommend({"condition": "rain", "precipitation_probability": 80})
    assert r["recommendation"] == "yes"
    assert r["confidence"] >= 0.6


def test_rain_moderate_yes():
    r = recommend({"condition": "rain", "precipitation_probability": 50})
    assert r["recommendation"] == "yes"


def test_rain_low_prob_maybe():
    r = recommend({"condition": "rain", "precipitation_probability": 20})
    assert r["recommendation"] == "maybe"


def test_shower_yes():
    r = recommend({"condition": "shower", "precipitation_probability": 60})
    assert r["recommendation"] == "yes"


def test_thunderstorm_yes():
    r = recommend({"condition": "thunderstorm", "precipitation_probability": 50})
    assert r["recommendation"] == "yes"


def test_drizzle_maybe():
    r = recommend({"condition": "drizzle", "precipitation_probability": 35})
    assert r["recommendation"] == "maybe"


def test_storm_alert():
    r = recommend({"condition": "storm", "precipitation_probability": 90})
    assert r["recommendation"] == "alert"
    assert r["confidence"] == 0.9


def test_heavy_rain_alert():
    r = recommend({"condition": "heavy rain", "precipitation_probability": 80})
    assert r["recommendation"] == "alert"


def test_freezing_rain_alert():
    r = recommend({"condition": "freezing rain", "precipitation_probability": 70})
    assert r["recommendation"] == "alert"


def test_sleet_alert():
    r = recommend({"condition": "sleet", "precipitation_probability": 60})
    assert r["recommendation"] == "alert"


def test_hail_alert():
    r = recommend({"condition": "hail", "precipitation_probability": 50})
    assert r["recommendation"] == "alert"


def test_clear_no():
    r = recommend({"condition": "clear", "precipitation_probability": 0})
    assert r["recommendation"] == "no"
    assert r["confidence"] >= 0.8


def test_clear_low_precip_no():
    r = recommend({"condition": "clear", "precipitation_probability": 5})
    assert r["recommendation"] == "no"


def test_cloudy_low_precip_no():
    r = recommend({"condition": "cloudy", "precipitation_probability": 10})
    assert r["recommendation"] == "no"


def test_cloudy_high_precip_maybe():
    r = recommend({"condition": "cloudy", "precipitation_probability": 60})
    assert r["recommendation"] == "maybe"


def test_snow_high_precip_yes():
    r = recommend({"condition": "snow", "precipitation_probability": 50})
    assert r["recommendation"] == "yes"


def test_snow_low_precip_no():
    r = recommend({"condition": "snow", "precipitation_probability": 5})
    assert r["recommendation"] == "no"


def test_malformed_non_string_condition():
    r = recommend({"condition": 42, "precipitation_probability": 50})
    assert r["recommendation"] == "unknown"


def test_malformed_missing_condition():
    r = recommend({"precipitation_probability": 50})
    assert r["recommendation"] == "unknown"


def test_missing_precip():
    r = recommend({"condition": "rain"})
    assert r["recommendation"] == "unknown"


def test_none_input():
    r = recommend(None)
    assert r["recommendation"] == "unknown"


def test_empty_dict():
    r = recommend({})
    assert r["recommendation"] == "unknown"


def test_provider_failure():
    r = recommend({"success": False, "error": "provider timeout"})
    assert r["recommendation"] == "unknown"


def test_output_has_all_fields():
    r = recommend({"condition": "rain", "precipitation_probability": 80})
    for field in ("recommendation", "answer", "reason", "weather_source", "confidence"):
        assert field in r


def test_deterministic():
    data = {"condition": "rain", "precipitation_probability": 75}
    r1 = recommend(data)
    r2 = recommend(data)
    assert r1 == r2


def test_weather_source_propagated():
    r = recommend({"condition": "rain", "precipitation_probability": 60, "source": "fixture"})
    assert r["weather_source"] == "fixture"


def test_weather_source_fallback():
    r = recommend({"condition": "rain", "precipitation_probability": 60, "provider": "test_prov"})
    assert r["weather_source"] == "test_prov"


def test_edge_precip_boundary_59():
    r = recommend({"condition": "rain", "precipitation_probability": 59})
    assert r["recommendation"] == "yes"


def test_edge_precip_boundary_60():
    r = recommend({"condition": "rain", "precipitation_probability": 60})
    assert r["recommendation"] == "yes"


def test_oslo_fixture():
    r = recommend({"condition": "cloudy", "precipitation_probability": 55, "source": "fixture"})
    assert r["recommendation"] in ("maybe", "no")


def test_unknown_condition_high_precip():
    r = recommend({"condition": "monsoon", "precipitation_probability": 80})
    assert r["recommendation"] == "yes"


def test_unknown_condition_low_precip():
    r = recommend({"condition": "monsoon", "precipitation_probability": 10})
    assert r["recommendation"] == "no"
'''


def _current_commit() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=str(REPO_ROOT)
    ).decode().strip()


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _new_id(prefix: str = "gen") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def _file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.lstrip("\n"), encoding="utf-8")


def _generate_source_files(workspace: Path) -> list[dict]:
    files = []

    agent_dir = workspace / UMBRELLA_OUT_DIR
    agent_dir.mkdir(parents=True, exist_ok=True)

    src_map = {
        f"{UMBRELLA_OUT_DIR}/recommendation_engine.py": RECOMMENDATION_ENGINE_SRC,
        f"{UMBRELLA_OUT_DIR}/runtime.py": RUNTIME_SRC,
        f"{UMBRELLA_OUT_DIR}/__init__.py": INIT_SRC,
    }

    for rel_path, source in src_map.items():
        target = workspace / rel_path
        _write_file(target, source)
        files.append({
            "target_path": rel_path,
            "sha256": _file_sha256(target),
            "size": target.stat().st_size,
        })

    test_dir = workspace / "tests" / "quick" / "umbrella_agent"
    test_dir.mkdir(parents=True, exist_ok=True)
    test_file = test_dir / "test_recommendation_engine.py"
    _write_file(test_file, TEST_SRC)
    files.append({
        "target_path": "tests/quick/umbrella_agent/test_recommendation_engine.py",
        "sha256": _file_sha256(test_file),
        "size": test_file.stat().st_size,
    })

    return files


def _build_patch_operations(generated_files: list[dict], workspace: Path) -> list:
    from agentx_evolve.patch_execution.patch_models import PatchOperation, OP_WRITE_FILE

    ops = []
    for f in generated_files:
        src = workspace / f["target_path"]
        if not src.is_file():
            continue
        ops.append(PatchOperation(
            operation_id=_new_id("op"),
            operation_type=OP_WRITE_FILE,
            target_path=f["target_path"],
            content=src.read_text(encoding="utf-8"),
        ))
    return ops


def _governed_patch_apply(operations: list, mode: str) -> dict:
    from agentx_evolve.patch_execution.patch_execution_service import execute_governed_patch
    from agentx_evolve.patch_execution.patch_models import MODE_DRY_RUN, MODE_LIVE, to_dict
    from agentx_evolve.patch_execution.initiator_patch_compat import InitiatorPatchCompat
    from agentx_evolve.security.path_boundary_service import policy_for_phase, PHASE_UMBRELLA_STAGE_B

    sandbox_policy = policy_for_phase(PHASE_UMBRELLA_STAGE_B, REPO_ROOT)
    compat = InitiatorPatchCompat(repo_root=REPO_ROOT)

    validation_commands = None
    if mode == MODE_LIVE:
        validation_commands = [
            ["python3", "-m", "pytest", "tests/quick/umbrella_agent/",
             "-q", "--tb=short", "-p", "no:cacheprovider"],
        ]

    session = execute_governed_patch(
        repo_root=REPO_ROOT,
        operations=operations,
        approved_paths=sandbox_policy.allowlisted_write_paths,
        proposal_id="proposal-umbrella-gen-001",
        governance_decision_id="gov-umbrella-gen-001",
        mode=mode,
        validation_commands=validation_commands,
        sandbox_policy=sandbox_policy,
        compat=compat,
    )

    return {
        "session_id": session.session_id,
        "status": session.status,
        "final_decision": session.final_decision,
        "errors": session.errors,
        "changed_paths": session.changed_paths,
        "rollback_snapshot_id": session.rollback_snapshot_id,
        "rollback_record_id": session.rollback_record_id,
        "session_dict": to_dict(session),
    }


def _write_governance_artifacts(proposal_id: str, session_id: str) -> dict[str, str]:
    now = _utc_now()
    artifacts = {}

    def _write(name: str, data: dict) -> str:
        path = EVIDENCE_DIR / name
        EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        artifacts[name] = str(path)
        return str(path)

    ts = now

    _write("proposal.json", {
        "artifact_type": "proposal",
        "proposal_id": proposal_id,
        "session_id": session_id,
        "title": "Generate Umbrella Agent with Full Deterministic Behavior",
        "description": (
            "Generate umbrella agent source with condition-aware "
            "recommendation logic, alert handling, malformed data detection, "
            "and structured output formatting."
        ),
        "risk_classification": "bounded",
        "submitted_by": f"generate_umbrella_agent pipeline (session {session_id})",
        "submitted_at": ts,
        "status": "approved",
    })

    _write("risk_classification.json", {
        "artifact_type": "risk_classification",
        "proposal_id": proposal_id,
        "session_id": session_id,
        "risk_level": "bounded",
        "risk_justification": [
            "Changes in examples/ path (non-L0, non-protected)",
            "Deterministic fixture-based generation",
            "No live API calls required",
            "Controlled via governed patch executor (rollback available)",
        ],
        "requires_human_review": False,
        "allows_auto_promotion": False,
        "classification_timestamp": ts,
    })

    _write("context_packet.json", {
        "artifact_type": "context_packet",
        "proposal_id": proposal_id,
        "session_id": session_id,
        "target_component": "umbrella_agent",
        "generation_strategy": "template-based",
        "weather_provider": "tools/agentx_evolve/providers/weather_fixture.py",
        "condition_categories": {
            "rain_like": ["rain", "shower", "thunderstorm"],
            "alert": ["storm", "heavy rain", "freezing rain", "sleet", "hail"],
            "drizzle": ["drizzle"],
            "snow": ["snow"],
            "clear": ["clear"],
            "overcast": ["cloudy", "overcast", "fog", "mist"],
        },
        "output_fields": [
            "recommendation", "answer", "reason",
            "weather_source", "confidence",
        ],
        "created_at": ts,
    })

    _write("prompt_contract.json", {
        "artifact_type": "prompt_contract",
        "proposal_id": proposal_id,
        "session_id": session_id,
        "input_schema": {
            "location": "string (required)",
            "date": "string (optional, defaults to today)",
        },
        "output_schema": {
            "recommendation": "string: yes | no | maybe | alert | unknown",
            "answer": "string (human-readable explanation)",
            "reason": "string (why this recommendation was made)",
            "weather_source": "string",
            "confidence": "float 0.0-1.0",
            "condition": "string or null",
            "precipitation_probability": "float or null",
            "temperature_c": "int or null",
            "location": "string",
            "date": "string",
        },
        "behavior_rules": [
            "rain/shower/thunderstorm with precip>=40 -> yes",
            "rain/shower/thunderstorm with precip<40 -> maybe",
            "drizzle -> maybe",
            "storm/heavy rain/freezing rain/sleet/hail -> alert",
            "clear with precip<=5 -> no, confidence 0.9",
            "snow with precip>=30 -> yes",
            "malformed/missing condition -> unknown",
            "provider failure -> unknown",
            "missing precip -> unknown",
        ],
        "contract_version": "1.0",
        "created_at": ts,
    })

    return artifacts


def _run_pytest_on_generated(test_path: str) -> dict:
    env = os.environ.copy()
    env["PYTHONPATH"] = (
        f"L0/CODE:L1:L2:tools/agentx_initiator:"
        f"tools/agentx_evolve:tools:examples:{REPO_ROOT}"
    )
    try:
        result = subprocess.run(
            ["python3", "-m", "pytest", test_path, "-q", "--tb=short", "-p", "no:cacheprovider"],
            capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=120, env=env,
        )
        last_line = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else ""
        passed = result.returncode == 0 and "passed" in last_line
        return {
            "exit_code": result.returncode,
            "summary": last_line,
            "passed": passed,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except subprocess.TimeoutExpired:
        return {"exit_code": -1, "summary": "timeout", "passed": False, "stdout": "", "stderr": ""}


def _build_evidence(workspace: Path, generated_files: list[dict],
                    patch_payload: dict, test_result: dict) -> dict:
    from agentx_evolve.models import (
        ProvenanceRecord,
        ProvenanceChain,
        ORIGIN_STAGE_B,
        STATUS_PASS,
        STATUS_FAIL,
        PERSISTENCE_EPHEMERAL,
        PERSISTENCE_PERMANENT,
    )

    commit = _current_commit()
    now = _utc_now()
    session_id = patch_payload.get("live_session_id", _new_id("IMP"))

    chain = ProvenanceChain()
    chain.append(ProvenanceRecord(
        path="temp_workspace",
        sha256="",
        origin=ORIGIN_STAGE_B,
        stage="umbrella_b",
        persistence=PERSISTENCE_EPHEMERAL,
        status=STATUS_PASS,
        metadata={"description": "Temp workspace created"},
    ))
    for f in generated_files:
        rel = f.get("target_path", f.get("path", ""))
        content = f.get("content", "")
        sha = hashlib.sha256(content.encode()).hexdigest() if content else ""
        chain.append(ProvenanceRecord(
            path=rel,
            sha256=sha,
            origin=ORIGIN_STAGE_B,
            stage="umbrella_b",
            persistence=PERSISTENCE_EPHEMERAL,
            status=STATUS_PASS,
            metadata={"size": len(content)},
        ))
    chain.append(ProvenanceRecord(
        path="governed_patch_dry_run",
        sha256="",
        origin=ORIGIN_STAGE_B,
        stage="umbrella_b",
        persistence=PERSISTENCE_EPHEMERAL,
        status=STATUS_PASS if patch_payload.get("dry_run_status") == "PASS" else STATUS_FAIL,
        metadata={"session_id": patch_payload.get("dry_run_session_id", "")},
    ))
    chain.append(ProvenanceRecord(
        path="governed_patch_live",
        sha256="",
        origin=ORIGIN_STAGE_B,
        stage="umbrella_b",
        persistence=PERSISTENCE_EPHEMERAL,
        status=STATUS_PASS if patch_payload.get("live_final_decision") == "ACCEPT" else STATUS_FAIL,
        metadata={"session_id": patch_payload.get("live_session_id", "")},
    ))
    chain.append(ProvenanceRecord(
        path="pytest_verification",
        sha256="",
        origin=ORIGIN_STAGE_B,
        stage="umbrella_b",
        persistence=PERSISTENCE_EPHEMERAL,
        status=STATUS_PASS if test_result.get("passed") else STATUS_FAIL,
        metadata={"summary": test_result.get("summary", "")},
    ))
    chain.append(ProvenanceRecord(
        path=str(EVIDENCE_DIR / "umbrella_generation_evidence.json"),
        sha256="",
        origin=ORIGIN_STAGE_B,
        stage="umbrella_b",
        persistence=PERSISTENCE_PERMANENT,
        status=STATUS_PASS,
        metadata={"description": "Evidence report retained"},
    ))

    evidence = {
        "generation_run": {
            "session_id": session_id,
            "proposal_id": patch_payload.get("proposal_id"),
            "dry_run_session_id": patch_payload.get("dry_run_session_id"),
            "commit": commit,
            "generated_at": now,
            "workspace": str(workspace),
            "workspace_cleaned": not workspace.exists(),
        },
        "proposal": {
            "proposal_id": f"proposal-{session_id}",
            "governance_decision_id": patch_payload.get("governance_decision_id"),
            "title": "Generate Umbrella Agent with Full Deterministic Behavior",
            "description": (
                "Generate umbrella agent source with condition-aware "
                "recommendation logic, alert handling, malformed data detection, "
                "and structured output formatting."
            ),
            "risk_classification": "bounded",
            "created_at": now,
        },
        "context_packet": {
            "packet_id": f"ctx-{session_id}",
            "target_component": "umbrella_agent",
            "generation_strategy": "template-based",
            "weather_provider": "tools/agentx_evolve/fixtures/weather_fixture_provider.py",
            "condition_categories": {
                "rain_like": ["rain", "shower", "thunderstorm"],
                "alert": ["storm", "heavy rain", "freezing rain", "sleet", "hail"],
                "drizzle": ["drizzle"],
                "snow": ["snow"],
                "clear": ["clear"],
                "overcast": ["cloudy", "overcast", "fog", "mist"],
            },
            "output_fields": [
                "recommendation", "answer", "reason",
                "weather_source", "confidence",
            ],
        },
        "prompt_contract": {
            "contract_id": f"pc-{session_id}",
            "input_schema": {
                "location": "string (required)",
                "date": "string (optional, defaults to today)",
            },
            "output_schema": {
                "recommendation": "string: yes | no | maybe | alert | unknown",
                "answer": "string (human-readable explanation)",
                "reason": "string (why this recommendation was made)",
                "weather_source": "string",
                "confidence": "float 0.0-1.0",
                "condition": "string or null",
                "precipitation_probability": "float or null",
                "temperature_c": "int or null",
                "location": "string",
                "date": "string",
            },
            "behavior_rules": [
                "rain/shower/thunderstorm with precip>=40 -> yes",
                "rain/shower/thunderstorm with precip<40 -> maybe",
                "drizzle -> maybe",
                "storm/heavy rain/freezing rain/sleet/hail -> alert",
                "clear with precip<=5 -> no, confidence 0.9",
                "snow with precip>=30 -> yes",
                "malformed/missing condition -> unknown",
                "provider failure -> unknown",
                "missing precip -> unknown",
            ],
        },
        "generated_files": generated_files,
        "patch_execution": {
            "session_id": session_id,
            "mode": "LIVE",
            "governance_decision_id": patch_payload.get("governance_decision_id"),
            "approved_paths": ["examples/", "tests/quick/umbrella_agent/"],
            "dry_run_status": patch_payload.get("dry_run_status"),
            "live_status": patch_payload.get("live_status"),
            "live_final_decision": patch_payload.get("live_final_decision"),
            "rollback_snapshot_id": patch_payload.get("rollback_snapshot_id"),
            "files_attempted": len(generated_files),
            "changed_paths": patch_payload.get("changed_paths", []),
            "errors": patch_payload.get("errors", []),
        },
        "verification": {
            "pytest_run": test_result,
            "tests_passed": test_result.get("passed", False),
        },
        "provenance": {
            "proof_target": "umbrella_agent_generation",
            "commit": commit,
            "verified_at": now,
            "provenance_chain": chain.to_dict(),
        },
    }

    return evidence


def run() -> dict:
    from agentx_evolve.patch_execution.patch_models import MODE_DRY_RUN, MODE_LIVE
    from agentx_evolve.evidence.event_logger import log_event, read_event_log, validate_event_log

    now = _utc_now()
    commit = _current_commit()
    session_id = _new_id("UMB")
    proposal_id = f"P-{_new_id('PROP')}"
    governance_decision_id = f"GOV-{_new_id('GOV')}"
    workspace = Path(tempfile.mkdtemp(suffix="-umbrella-gen"))

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    event_log_path = EVIDENCE_DIR / f"events_{session_id}.jsonl"
    seq = 0

    def _emit(stage: str, obj_id: str = "", result: str = "created"):
        nonlocal seq
        seq += 1
        log_event({
            "event_id": f"{session_id}-{seq:04d}",
            "run_id": session_id,
            "stage": stage,
            "object_id": obj_id,
            "result": result,
            "actor": "generate_umbrella_agent pipeline",
            "timestamp": _utc_now(),
        }, event_log_path)

    print(f"[{now[11:19]}] Creating temp workspace: {workspace}")
    print(f"[{now[11:19]}] Commit: {commit}")
    print(f"[{now[11:19]}] Session: {session_id}, Proposal: {proposal_id}")

    print(f"[{now[11:19]}] Writing governance artifacts...")
    gov_artifacts = _write_governance_artifacts(proposal_id, session_id)
    for name, path in gov_artifacts.items():
        print(f"  governance artifact: {name} -> {path}")
    _emit("proposal", proposal_id)
    _emit("risk", proposal_id)
    _emit("context", f"ctx-{session_id}")
    _emit("prompt", f"pc-{session_id}")

    print(f"[{now[11:19]}] Generating umbrella agent source...")
    generated_files = _generate_source_files(workspace)

    print(f"[{now[11:19]}] Building patch operations...")
    operations = _build_patch_operations(generated_files, workspace)

    print(f"[{now[11:19]}] Creating patch candidate lifecycle record...")
    from agentx_evolve.patch_execution.patch_models import PatchCandidate
    patch_candidate = PatchCandidate(
        proposal_id=proposal_id,
        context_packet_id=f"ctx-{session_id}",
        prompt_contract_id=f"pc-{session_id}",
        risk_classification_id=proposal_id,
        governance_decision_id=governance_decision_id,
        session_id=session_id,
        created_at=now,
        source_commit=commit,
        operations=operations,
        allowed_paths=["examples/", "tests/quick/umbrella_agent/"],
        blocked_paths=["L0/", "L1/", "L2/", "tools/agentx_evolve/security/", "schemas/"],
        rollback_plan="Snapshot and restore via governed patch executor rollback",
        status="CREATED",
        validation_commands=[
            "python3 -m pytest tests/quick/umbrella_agent/ -q --tb=short",
        ],
    )
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    pc_path = EVIDENCE_DIR / "patch_candidate.json"
    with open(pc_path, "w") as f:
        json.dump(patch_candidate.to_dict(), f, indent=2)
    print(f"  patch candidate -> {pc_path}")
    _emit("patch_candidate", patch_candidate.candidate_id)

    print(f"[{now[11:19]}] Validating patch candidate (DRY_RUN)...")
    dry_result = _governed_patch_apply(operations, MODE_DRY_RUN)
    patch_candidate.validation_status = "PASS" if dry_result["final_decision"] not in ("REJECT", "ROLLBACK") else "FAIL"
    patch_candidate.status = "VALIDATED" if patch_candidate.validation_status == "PASS" else "REJECTED"
    with open(pc_path, "w") as f:
        json.dump(patch_candidate.to_dict(), f, indent=2)
    print(f"  candidate validation: {patch_candidate.validation_status}")
    _emit("patch_validation", patch_candidate.candidate_id, patch_candidate.validation_status)

    if dry_result["final_decision"] in ("REJECT", "ROLLBACK"):
        print(f"  DRY_RUN FAILED: {dry_result['errors']}")
        if workspace.exists():
            shutil.rmtree(workspace, ignore_errors=True)
        return {"status": "FAIL", "stage": "dry_run", "errors": dry_result["errors"]}

    print(f"  DRY_RUN: session={dry_result['session_id']}, status={dry_result['status']}")

    print(f"[{now[11:19]}] LIVE: applying patch via governed patch executor...")
    live_result = _governed_patch_apply(operations, MODE_LIVE)

    if live_result["final_decision"] == "ROLLBACK":
        print(f"  LIVE FAILED — rolled back: {live_result['errors']}")
        if workspace.exists():
            shutil.rmtree(workspace, ignore_errors=True)
        return {"status": "FAIL", "stage": "live", "errors": live_result["errors"]}

    if live_result["final_decision"] != "ACCEPT":
        print(f"  LIVE FAILED: {live_result['errors']}")
        if workspace.exists():
            shutil.rmtree(workspace, ignore_errors=True)
        return {"status": "FAIL", "stage": "live", "errors": live_result["errors"]}

    for path in live_result["changed_paths"]:
        print(f"  patched  {path}")

    print(f"[{now[11:19]}] All governed patching passed. session={live_result['session_id']}")
    _emit("patch_execution", live_result["session_id"], "ACCEPT")

    print(f"[{now[11:19]}] Running post-patch tests on generated agent...")
    test_path = str(REPO_ROOT / "tests" / "quick" / "umbrella_agent" / "test_recommendation_engine.py")
    test_result = _run_pytest_on_generated(test_path)

    print(f"  pytest: {test_result['summary']}")
    if not test_result["passed"]:
        print(f"  stderr: {test_result['stderr'][:500]}")
    _emit("test", "pytest", "PASS" if test_result.get("passed") else "FAIL")

    print(f"[{now[11:19]}] Building evidence report...")
    patch_payload = {
        "dry_run_session_id": dry_result["session_id"],
        "live_session_id": live_result["session_id"],
        "governance_decision_id": governance_decision_id,
        "proposal_id": proposal_id,
        "session_id": session_id,
        "dry_run_status": dry_result["status"],
        "live_status": live_result["status"],
        "live_final_decision": live_result["final_decision"],
        "changed_paths": live_result["changed_paths"],
        "rollback_snapshot_id": live_result["rollback_snapshot_id"],
        "errors": live_result["errors"],
    }
    evidence = _build_evidence(workspace, generated_files, patch_payload, test_result)

    print(f"[{now[11:19]}] Cleaning up temp workspace...")
    if workspace.exists():
        shutil.rmtree(workspace, ignore_errors=True)

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    ev_path = EVIDENCE_DIR / "umbrella_generation_evidence.json"
    with open(ev_path, "w") as f:
        json.dump(evidence, f, indent=2)
    print(f"  evidence -> reports/umbrella_agent/umbrella_generation_evidence.json")
    _emit("evidence", "umbrella_generation_evidence.json", "written")

    ev_errors = validate_event_log(read_event_log(event_log_path))
    if ev_errors:
        print(f"  event log warnings: {ev_errors}")

    summary = {
        "status": "PASS" if test_result["passed"] else "FAIL",
        "session_id": session_id,
        "proposal_id": proposal_id,
        "governance_decision_id": governance_decision_id,
        "commit": commit,
        "files_generated": len(generated_files),
        "files_applied": len(live_result.get("changed_paths", [])),
        "pytest_passed": test_result["passed"],
        "pytest_summary": test_result["summary"],
        "verified_at": now,
    }

    print(f"\n=== Generation {'PASS' if test_result['passed'] else 'FAIL'} ===")
    return summary


def run_and_report() -> None:
    summary = run()
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    path = EVIDENCE_DIR / "stage_b_generation_summary.json"
    with open(path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"  summary -> reports/umbrella_agent/stage_b_generation_summary.json")


if __name__ == "__main__":
    run_and_report()
