# Pass 2 — Umbrella Agent Contract

## Agent Identity
- **Name:** Umbrella Recommendation Agent
- **Milestone:** UMBRELLA_AGENT_REAL_SELF_EVOLUTION_MVP
- **Purpose:** Answer "Should I bring an umbrella today?" using deterministic weather fixture data

## Schemas

### Input Schema
Path: `schemas/umbrella_agent_input.schema.json`
- `question`: non-empty string
- `location`: non-empty string
- `date`: `"today"` or ISO date string (deterministic resolution via injected clock)

### Weather Fixture Schema
Path: `schemas/umbrella_weather_fixture.schema.json`
- `location`: non-empty string
- `date`: ISO date string
- `condition`: string or null
- `precipitation_probability`: number (0–100) or null
- `temperature_c`: number or null
- `wind_kph`: number or null
- `alerts`: list of strings or objects

### Output Schema
Path: `schemas/umbrella_agent_output.schema.json`
- `recommendation`: `yes` | `no` | `maybe` | `unknown`
- `answer`: string
- `reason`: string
- `weather_source`: `"fixture"`
- `confidence`: `high` | `medium` | `low` | `unknown`

## Recommendation Rules
See pass_3_recommendation_rules.md for full deterministic rule set.

## Failure Modes
- Missing/malformed weather data → `unknown` recommendation
- Provider failure → `unknown` recommendation
- Schema validation failure → `unknown` recommendation

## Safety Restrictions
- No live weather API
- No network access
- No subprocess execution
- No credential access
- Source writes limited to approved paths only
- `L0/` mutation blocked

## Entry Point
```python
def answer_umbrella_question(request: dict, weather_provider: object) -> dict:
    """Return umbrella recommendation based on weather data."""
```

## Determinism Expectations
- Same input → same output every time
- `today` resolved through injected clock
- No system time calls in core logic
- No location inference from IP, env, browser, or locale

## Schema Path Mapping
The governing document specifies `schemas/umbrella_agent_*.schema.json` at the top level. This milestone creates a top-level `schemas/` directory at the repository root (`schemas/umbrella_agent_*.schema.json`). The canonical schema directory under `tools/agentx_evolve/schemas/` (478 files) remains the primary schema store; the top-level `schemas/` directory is created specifically for this milestone's umbrella agent contract schemas.
