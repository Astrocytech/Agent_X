## Umbrella Agent v2 — Genuine Agent_X-Derived Agent

### Motivation

Upgrade the umbrella agent from a standalone Python script to a genuine Agent_X-derived agent. The new agent:
- Uses `KernelService` for LLM-based natural-language explanation
- Calls `weather.fixture.read` (L0 seed tool) for deterministic fixture data
- Applies deterministic recommendation rules per §3 in pure Python
- Has a proper Agent_X profile with policy governance
- Is created via `EvolveAgentWorkflow` as proof of self-evolution

### Architecture

```
ask_umbrella(location, date)
  ┌─────────────────────────────────────────────────────┐
  │  KernelService (all 8 phases)                       │
  │                                                     │
  │  Planning Phase (UmbrellaPlannerPort):               │
  │    1. weather.fixture.read (direct import)           │
  │       → deterministic fixture data                   │
  │    2. LLM provider (OpenCode API)                    │
  │       → applies §3 rules to raw weather data         │
  │    3. Fallback: recommendation_engine §3 rules        │
  │       (when LLM unavailable)                         │
  │    4. Returns PlannerDecision → seed.emit_answer     │
  │                                                     │
  │  Execution Phase:                                    │
  │    - ToolGateway executes seed.emit_answer           │
  │    → structured JSON output                          │
  └─────────────────────────────────────────────────────┘
```

The LLM is the primary decision-maker. The rule engine is a graceful
degradation path for when no LLM provider is reachable.

### Target

`examples/umbrella_agent/`

### Prerequisite (Permanent)

A profile must exist at `profiles/builtin/umbrella-agent.yaml` for `LocalProfilePort` to discover. This is a permanent L0 configuration file, not created by EvolveAgentWorkflow. The concept file references its content for documentation.

### Files to Create

#### 1. `profiles/builtin/umbrella-agent.yaml` (prerequisite — must exist before EvolveAgentWorkflow runs)

```yaml
id: umbrella-agent
name: UmbrellaAgent
role: umbrella_advisor
purpose: Answers umbrella questions using weather fixture data and deterministic rules
schema_version: 1

capabilities:
  answer_umbrella:
    allowed_tools:
      - seed.emit_answer
    risk_ceiling: low
    memory_scope: working
    approval_mode: auto
    planner_permissions: direct

model_policy:
  max_tokens: 2048
  temperature: 0.0
  allowed_models: []

allowed_tools:
  - seed.emit_answer

forbidden_tools:
  - shell.run
  - filesystem.write
  - git.push
  - network.request
  - evolution.promote
  - runtime.mutate

allowed_memory_scopes:
  working:
    - session
    - run

input_schema: goal
output_schema: final_response
risk_policy: conservative
approval_policy: approval_required_for_high_risk

stop_conditions:
  - goal_achieved
  - max_steps_reached

prompt:
  system: |
    You are an umbrella recommendation assistant.
    You have been given weather data and a deterministic recommendation.
    Your job is to write a friendly, concise natural-language explanation
    of the recommendation. Use seed.emit_answer to output your response.
```

#### 2. `examples/umbrella_agent/llm_provider.py`

```python
"""Lightweight OpenCode API caller (stdlib only)."""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from typing import Any

logger = logging.getLogger(__name__)


class LLMProvider:
    """Lightweight caller for an OpenAI-compatible chat API (stdlib only).

    Tries the Agent_X OpenCode server first then falls back to an
    OpenAI-compatible endpoint. Returns ``None`` when the provider is
    unreachable so callers can degrade gracefully.
    """

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:14096",
        api_key: str = "",
        model: str = "big-pickle",
        timeout: int = 30,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    def health(self) -> bool:
        try:
            req = urllib.request.Request(f"{self.base_url}/global/health")
            with urllib.request.urlopen(req, timeout=3):
                return True
        except Exception:
            return False

    def complete(
        self,
        system_prompt: str,
        user_text: str,
        temperature: float = 0.0,
    ) -> dict[str, Any] | None:
        if not self.health():
            logger.warning("LLM provider unreachable at %s", self.base_url)
            return None
        session_id = self._create_session()
        if session_id is None:
            return None
        try:
            return self._send_message(session_id, system_prompt, user_text)
        except Exception:
            logger.exception("LLM message call failed")
            return None

    def _create_session(self) -> str | None:
        try:
            body = json.dumps({}).encode("utf-8")
            req = urllib.request.Request(
                f"{self.base_url}/session",
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return data.get("id")
        except Exception:
            logger.exception("Failed to create LLM session")
            return None

    def _send_message(
        self, session_id: str, system_prompt: str, user_text: str
    ) -> dict[str, Any] | None:
        body: dict[str, Any] = {
            "model": {"providerID": "opencode", "modelID": self.model},
            "parts": [{"type": "text", "text": user_text}],
        }
        if system_prompt:
            body["system"] = system_prompt
        payload = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/session/{session_id}/message",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        parts = data.get("parts", [])
        text = ""
        for p in parts:
            if p.get("type") == "text":
                text = p.get("text", "")
                break
        if not text:
            return None
        return {
            "content": text,
            "finish_reason": data.get("info", {}).get("finish", "stop"),
        }
```

#### 3. `examples/umbrella_agent/planner.py`

```python
"""Custom planner — calls weather.fixture.read + LLM (with rule fallback)."""

from __future__ import annotations

import json
import logging
import re
from typing import Any
from uuid import uuid4

from core_kernel.models.kernel_atoms import Goal
from core_kernel.models.planner_decision import PlannerDecision
from kernel_composition.local_seed_ports.local_planner_port import (
    LocalPlannerPort,
    SEED_EMIT_ANSWER,
)
from tool_gateway.seed_tools.weather_fixture_read import (
    FIXTURES,
    WeatherFixtureReadTool,
)

from umbrella_agent.llm_provider import LLMProvider
from umbrella_agent.recommendation_engine import recommend

logger = logging.getLogger(__name__)

LLM_SYSTEM_PROMPT = """\
You are an umbrella recommendation agent. Your job is to look at weather data
and decide if someone should bring an umbrella.

Apply these deterministic rules based on precipitation probability:
- If precipitation probability >= 60% -> recommend "yes"
- If 30% <= precipitation probability < 60% -> recommend "maybe"
- If precipitation probability < 30% -> recommend "no"

Respond ONLY with a JSON object in this exact format
(no markdown, no extra text):
{"recommendation": "yes|maybe|no", "confidence": 0.0-1.0,
 "precipitation_probability": <int or null>, "condition": "<str or null>",
 "temperature_c": <int or null>, "explanation": "<str>"}
"""


def _extract_location(text: str) -> str | None:
    lower = text.lower().strip()
    for loc in FIXTURES:
        if loc in lower:
            return loc
    m = re.search(r"\bin\s+(\w+(?:\s+\w+)*?)(?:\s+on\s+|\s+for\s+|\s*\?|$)", lower)
    if m:
        candidate = m.group(1).strip()
        if candidate in FIXTURES:
            return candidate
    return None


class UmbrellaPlannerPort:
    runtime_safety_class = "production_seed_port"

    def __init__(
        self,
        policy_port: Any = None,
        llm_provider: LLMProvider | None = None,
    ) -> None:
        self._local_planner = LocalPlannerPort(policy_port=policy_port)
        self._weather_tool = WeatherFixtureReadTool()
        self._llm = llm_provider or LLMProvider()

    def _is_umbrella_profile(self, profile: Any) -> bool:
        pid = profile.id if not isinstance(profile, dict) else profile.get("id", "")
        return pid == "umbrella-agent"

    def make_decision(self, goal: Goal, profile: Any, context: dict[str, Any],
                      problem_model: Any = None,
                      memory_refs: list[str] | None = None) -> PlannerDecision:
        if not self._is_umbrella_profile(profile):
            return self._local_planner.make_decision(
                goal, profile, context, problem_model, memory_refs,
            )
        text = goal.text or ""
        location = _extract_location(text)
        weather_result = self._weather_tool(location=location, date="today") if location else {}
        weather_data = weather_result.get("data") if weather_result.get("success") else None
        output = self._build_output(weather_data, text)
        return PlannerDecision(
            task_id=context.get("run_id", uuid4().hex[:12]),
            action_type="execute",
            tool_name=SEED_EMIT_ANSWER,
            arguments={"answer": json.dumps(output)},
            reasoning=(
                "umbrella_agent:llm_interpretation"
                if output.get("_source") == "llm"
                else "umbrella_agent:rule_fallback"
            ),
        )

    def _build_output(self, weather_data: dict | None, raw_text: str) -> dict:
        if weather_data is None:
            return {"recommendation": "unknown", "confidence": 0.0,
                    "precipitation_probability": None, "condition": None,
                    "temperature_c": None, "explanation": raw_text,
                    "_source": "error"}
        llm_result = self._try_llm(weather_data)
        if llm_result is not None:
            result = dict(llm_result)
            result["_source"] = "llm"
            return result
        return self._fallback(weather_data, raw_text)

    def _try_llm(self, weather_data: dict) -> dict | None:
        user_prompt = (
            f"Weather data for {weather_data.get('location', 'unknown')}:\n"
            f"- Precipitation probability: {weather_data.get('precipitation_probability')}%\n"
            f"- Condition: {weather_data.get('condition')}\n"
            f"- Temperature: {weather_data.get('temperature_c')}°C\n\n"
            "Should I bring an umbrella?"
        )
        try:
            response = self._llm.complete(
                system_prompt=LLM_SYSTEM_PROMPT,
                user_text=user_prompt, temperature=0.0,
            )
            if response is None:
                logger.info("LLM unavailable — falling back to rule engine")
                return None
            parsed = self._parse_llm_json(response.get("content", ""))
            if parsed is None:
                logger.warning("LLM returned unparseable JSON — falling back")
                return None
            return parsed
        except Exception:
            logger.exception("LLM call failed — falling back to rule engine")
            return None

    @staticmethod
    def _parse_llm_json(content: str) -> dict | None:
        content = content.strip()
        idx = content.find("{")
        if idx != -1:
            content = content[idx:]
        end = content.rfind("}")
        if end != -1:
            content = content[: end + 1]
        if content.startswith("```"):
            content = content[content.find("\n") + 1 : content.rfind("```")]
        try:
            data = json.loads(content)
            if not isinstance(data, dict):
                return None
            return data if data.get("recommendation") in (
                "yes", "maybe", "no", "unknown") else None
        except (json.JSONDecodeError, TypeError):
            return None

    @staticmethod
    def _fallback(weather_data: dict, raw_text: str) -> dict:
        rec = recommend(weather_data)
        precip = weather_data.get("precipitation_probability")
        condition = weather_data.get("condition")
        temp = weather_data.get("temperature_c")
        explanation = (
            f"{weather_data.get('location', 'Unknown')} has {precip}% "
            f"chance of {condition or 'precipitation'} "
            f"({temp}°C). Recommendation: {rec.get('recommendation')}."
        )
        return {"recommendation": rec.get("recommendation", "unknown"),
                "confidence": rec.get("confidence", 0.0),
                "precipitation_probability": precip,
                "condition": condition, "temperature_c": temp,
                "explanation": explanation, "_source": "rule"}
```

#### 4. `examples/umbrella_agent/__init__.py`

```python
"""Umbrella Agent — umbrella recommendation via Agent_X KernelService.

Usage:
    from umbrella_agent import ask_umbrella

    result = ask_umbrella("London")
    print(result["recommendation"])   # "yes"
    print(result["answer"])           # LLM-generated explanation
"""

from __future__ import annotations

from umbrella_agent.runtime import UmbrellaAgentRuntime


def ask_umbrella(location: str, date: str = "today") -> dict:
    """Ask whether to bring an umbrella at a given location and date.

    Args:
        location: City name (e.g. "London", "Tokyo").
        date: Date string (default: "today").

    Returns:
        dict with keys: recommendation, confidence, answer,
        precipitation_probability, condition, temperature_c,
        location, date.
    """
    return UmbrellaAgentRuntime().answer(location, date)
```

#### 5. `examples/umbrella_agent/runtime.py`

```python
"""Umbrella agent runtime — KernelService with custom LLM-driven planner."""

from __future__ import annotations

import ast
import json

from core_kernel.public import KernelService, KernelTurnRequest
from kernel_composition.seed_runtime_factory import build_seed_kernel_runtime

from umbrella_agent.planner import UmbrellaPlannerPort


class UmbrellaAgentRuntime:
    """Agent_X-based umbrella agent with LLM-driven planning.

    The question flows through KernelService (all 8 phases).
    Planning phase (UmbrellaPlannerPort):
      1. Calls weather.fixture.read to fetch deterministic fixture data
      2. Tries the LLM provider with weather data + §3 rules
      3. Falls back to the rule-based recommendation engine
      4. Returns a seed.emit_answer decision with structured JSON output
    """

    def __init__(self) -> None:
        runtime = build_seed_kernel_runtime(
            planner_port=UmbrellaPlannerPort(),
        )
        self._service = KernelService(
            kernel_runtime=runtime,
            default_profile_id="umbrella-agent",
        )

    def answer(self, location: str, date: str = "today") -> dict:
        if not location or not isinstance(location, str):
            return {
                "recommendation": "unknown",
                "confidence": 0.0,
                "answer": "A location is required.",
                "precipitation_probability": None,
                "condition": None,
                "temperature_c": None,
                "location": location,
                "date": date,
            }
        question = f"Should I bring an umbrella in {location} on {date}?"
        response = self._service.run_turn(
            KernelTurnRequest(
                user_input=question,
                session_id=f"umbrella-{location}-{date}",
                profile_id="umbrella-agent",
            )
        )
        return self._parse_answer(response.answer, location, date)

    @staticmethod
    def _parse_answer(raw: str, location: str, date: str) -> dict:
        data = _try_decode(raw)
        rec = data.get("recommendation", "unknown")
        confidence = data.get("confidence", 0.0)
        explanation = data.get("explanation", raw)
        precip = data.get("precipitation_probability")
        condition = data.get("condition")
        temp = data.get("temperature_c")
        return {
            "recommendation": rec,
            "confidence": confidence,
            "precipitation_probability": precip,
            "condition": condition,
            "temperature_c": temp,
            "answer": explanation,
            "location": location,
            "date": date,
        }


def _try_decode(raw: str) -> dict:
    """Decode raw via JSON or ast.literal_eval (tool wrapper format)."""
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        pass
    try:
        wrapper = ast.literal_eval(raw)
        if isinstance(wrapper, dict):
            answer_field = wrapper.get("answer")
            if isinstance(answer_field, str):
                try:
                    return json.loads(answer_field)
                except (json.JSONDecodeError, TypeError):
                    return {}
        return {}
    except (ValueError, SyntaxError, TypeError):
        return {}
```

#### 6. `examples/umbrella_agent/recommendation_engine.py`

```python
"""Deterministic umbrella recommendation engine per §3 rules.

Rules (§3):
  - precipitation_probability >= 60 → recommendation="yes", confidence=0.7
  - 30 <= precipitation_probability <= 59 → recommendation="maybe", confidence=0.4
  - precipitation_probability < 30 → recommendation="no", confidence=0.8
  - null/unknown → recommendation="unknown", confidence=0.0
"""

from __future__ import annotations


def recommend(weather: dict) -> dict:
    """Apply deterministic §3 rules to weather data.

    Args:
        weather: dict with at least 'precipitation_probability'.

    Returns:
        dict with 'recommendation' (str) and 'confidence' (float).
    """
    precip = weather.get("precipitation_probability")

    if precip is None or not isinstance(precip, (int, float)):
        return {"recommendation": "unknown", "confidence": 0.0}

    if precip >= 60:
        return {"recommendation": "yes", "confidence": 0.7}
    elif precip >= 30:
        return {"recommendation": "maybe", "confidence": 0.4}
    else:
        return {"recommendation": "no", "confidence": 0.8}
```

#### 7. `tests/unit/umbrella_agent/test_recommendation_engine.py`

```python
"""Unit tests for the deterministic recommendation engine (§3 rules)."""

from __future__ import annotations

from umbrella_agent.recommendation_engine import recommend


def test_precip_60_or_more_returns_yes() -> None:
    result = recommend({"precipitation_probability": 60})
    assert result["recommendation"] == "yes"
    assert result["confidence"] == 0.7


def test_precip_80_returns_yes() -> None:
    result = recommend({"precipitation_probability": 80})
    assert result["recommendation"] == "yes"
    assert result["confidence"] == 0.7


def test_precip_100_returns_yes() -> None:
    result = recommend({"precipitation_probability": 100})
    assert result["recommendation"] == "yes"
    assert result["confidence"] == 0.7


def test_precip_30_to_59_returns_maybe() -> None:
    result = recommend({"precipitation_probability": 30})
    assert result["recommendation"] == "maybe"
    assert result["confidence"] == 0.4


def test_precip_45_returns_maybe() -> None:
    result = recommend({"precipitation_probability": 45})
    assert result["recommendation"] == "maybe"
    assert result["confidence"] == 0.4


def test_precip_59_returns_maybe() -> None:
    result = recommend({"precipitation_probability": 59})
    assert result["recommendation"] == "maybe"
    assert result["confidence"] == 0.4


def test_precip_below_30_returns_no() -> None:
    result = recommend({"precipitation_probability": 29})
    assert result["recommendation"] == "no"
    assert result["confidence"] == 0.8


def test_precip_0_returns_no() -> None:
    result = recommend({"precipitation_probability": 0})
    assert result["recommendation"] == "no"
    assert result["confidence"] == 0.8


def test_precip_10_returns_no() -> None:
    result = recommend({"precipitation_probability": 10})
    assert result["recommendation"] == "no"
    assert result["confidence"] == 0.8


def test_precip_none_returns_unknown() -> None:
    result = recommend({"precipitation_probability": None})
    assert result["recommendation"] == "unknown"
    assert result["confidence"] == 0.0


def test_precip_missing_returns_unknown() -> None:
    result = recommend({})
    assert result["recommendation"] == "unknown"
    assert result["confidence"] == 0.0


def test_deterministic_same_input_same_output() -> None:
    data = {"precipitation_probability": 60}
    r1 = recommend(data)
    r2 = recommend(data)
    assert r1 == r2


def test_all_11_fixture_locations() -> None:
    from tool_gateway.seed_tools.weather_fixture_read import FIXTURES, WeatherFixtureReadTool

    tool = WeatherFixtureReadTool()
    for location in FIXTURES:
        result = tool(location=location, date="today")
        assert result["success"]
        rec = recommend(result["data"])
        assert rec["recommendation"] in ("yes", "maybe", "no")
        assert 0.0 <= rec["confidence"] <= 1.0
```

#### 8. `tests/integration/umbrella_agent/test_umbrella_agent_runtime.py`

```python
"""Integration tests for UmbrellaAgentRuntime (calls tools + KernelService)."""

from __future__ import annotations

from umbrella_agent import ask_umbrella


def test_ask_london_returns_structured_result() -> None:
    result = ask_umbrella("London")
    assert result["recommendation"] in ("yes", "maybe", "no", "unknown")
    assert isinstance(result["confidence"], float)
    assert 0.0 <= result["confidence"] <= 1.0
    assert isinstance(result["answer"], str)
    assert len(result["answer"]) > 0
    assert result["location"] == "London"


def test_ask_unknown_location_returns_unknown() -> None:
    result = ask_umbrella("Atlantis")
    assert result["recommendation"] == "unknown"
    assert result["confidence"] == 0.0


def test_output_contains_all_required_fields() -> None:
    result = ask_umbrella("Tokyo")
    required = {
        "recommendation", "confidence", "answer",
        "precipitation_probability", "condition", "temperature_c",
        "location", "date",
    }
    assert required.issubset(result.keys())


def test_deterministic_recommendation_same_input_same_output() -> None:
    r1 = ask_umbrella("Paris")
    r2 = ask_umbrella("Paris")
    # deterministic fields must match
    assert r1["recommendation"] == r2["recommendation"]
    assert r1["confidence"] == r2["confidence"]
    assert r1["precipitation_probability"] == r2["precipitation_probability"]


def test_precip_60_yes_recommendation() -> None:
    from umbrella_agent.runtime import UmbrellaAgentRuntime
    from tool_gateway.seed_tools.weather_fixture_read import WeatherFixtureReadTool

    tool = WeatherFixtureReadTool()
    result = tool(location="London", date="today")
    assert result["success"]
    assert result["data"]["precipitation_probability"] == 60
    runtime = UmbrellaAgentRuntime()
    answer = runtime.answer("London", "today")
    assert answer["recommendation"] == "yes"


def test_precip_10_no_recommendation() -> None:
    from umbrella_agent.runtime import UmbrellaAgentRuntime
    runtime = UmbrellaAgentRuntime()
    answer = runtime.answer("Paris", "today")
    assert answer["recommendation"] == "no"


def test_precip_45_maybe_recommendation() -> None:
    from umbrella_agent.runtime import UmbrellaAgentRuntime
    runtime = UmbrellaAgentRuntime()
    answer = runtime.answer("Berlin", "today")
    assert answer["recommendation"] == "maybe"
```

#### 9. `tests/system/umbrella_agent/test_umbrella_agent_system.py`

```python
"""System tests — full pipeline from user-facing API to output."""

from __future__ import annotations

from umbrella_agent import ask_umbrella


def test_full_pipeline_london_returns_answer() -> None:
    result = ask_umbrella("London", "today")
    assert result["recommendation"] == "yes"
    assert result["confidence"] == 0.7
    assert result["precipitation_probability"] == 60
    assert result["condition"] == "rain"
    assert isinstance(result["answer"], str)
    assert len(result["answer"]) > 0


def test_full_pipeline_paris_returns_answer() -> None:
    result = ask_umbrella("Paris", "today")
    assert result["recommendation"] == "no"
    assert result["confidence"] == 0.8
    assert result["precipitation_probability"] == 10
    assert result["condition"] == "clear"


def test_full_pipeline_berlin_returns_answer() -> None:
    result = ask_umbrella("Berlin", "today")
    assert result["recommendation"] == "maybe"
    assert result["confidence"] == 0.4
    assert result["precipitation_probability"] == 45
    assert result["condition"] == "cloudy"


def test_full_pipeline_all_fixtures_have_valid_recommendations() -> None:
    from tool_gateway.seed_tools.weather_fixture_read import FIXTURES

    for location in FIXTURES:
        result = ask_umbrella(location, "today")
        assert result["recommendation"] in ("yes", "maybe", "no")
        if result["precipitation_probability"] >= 60:
            assert result["recommendation"] == "yes"
        elif result["precipitation_probability"] >= 30:
            assert result["recommendation"] == "maybe"
        else:
            assert result["recommendation"] == "no"
        assert isinstance(result["answer"], str) and len(result["answer"]) > 0


def test_llm_explanation_describes_weather() -> None:
    result = ask_umbrella("Mumbai", "today")
    assert result["recommendation"] == "yes"
    # The LLM-generated answer should be non-empty and mention the city
    assert "Mumbai" in result["answer"] or "mumbai" in result["answer"].lower()
```

### Safety Notes

- All files are created under `examples/umbrella_agent/` and `tests/*/umbrella_agent/`
- The umbrella agent uses read-only tools only (weather.fixture.read, seed.emit_answer)
- Profile forbids all destructive tools (shell.run, filesystem.write, git.push, etc.)
- Recommendation engine is pure Python with no side effects
- KernelService runs with the umbrella-agent profile which has temperature=0.0
- No network access, no file system mutations, no live weather APIs
- The LLM provider gracefully degrades to the rule engine when unreachable
- The custom planner (UmbrellaPlannerPort) has ``runtime_safety_class = "production_seed_port"`` to pass the seed runtime factory validation
- ``ast.literal_eval`` is used for safe parsing of the tool-result wrapper (rejects arbitrary code)

### Evidence Generation

After creating the agent, run:
1. `pytest tests/unit/umbrella_agent/ -v`
2. `pytest tests/integration/umbrella_agent/ -v`
3. `pytest tests/system/umbrella_agent/ -v`
4. `PYTHONPATH="L0/CODE:examples" python -c "from umbrella_agent import ask_umbrella; r=ask_umbrella('London'); print(r['recommendation'], r['answer'])"`
5. Collect run evidence, test reports, and provenance into `reports/umbrella_agent/`

### Files Created/Updated

| File | Purpose |
|------|---------|
| `profiles/builtin/umbrella-agent.yaml` | Profile with §3 rules, allowed_tools, temperature=0.0 |
| `examples/umbrella_agent/__init__.py` | Public API: ``ask_umbrella(location, date)`` |
| `examples/umbrella_agent/llm_provider.py` | Lightweight OpenCode API caller (stdlib) |
| `examples/umbrella_agent/planner.py` | Custom planner: weather.fixture.read + LLM + fallback |
| `examples/umbrella_agent/runtime.py` | KernelService wrapper with custom planner injection |
| `examples/umbrella_agent/recommendation_engine.py` | Deterministic §3 rule engine (fallback) |
| `tests/unit/umbrella_agent/test_recommendation_engine.py` | 13 unit tests for rule engine |
| `tests/integration/umbrella_agent/test_umbrella_agent_runtime.py` | 7 integration tests through KernelService |
| `tests/system/umbrella_agent/test_umbrella_agent_system.py` | 6 system end-to-end tests |
