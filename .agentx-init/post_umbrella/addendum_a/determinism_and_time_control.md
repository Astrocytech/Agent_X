# Addendum A — Determinism and Time Control

## Status: PASS

### Current State
- All 3 agents use deterministic fixture data (weather_fixture_read, clothing_fixture_read, planning_fixture_read)
- All fixture timestamps are UTC
- No local machine time affects deterministic output
- LLM runs at temperature=0.0 for reproducible output
- Vague terms ("today", "tomorrow", "now") resolved to ISO-8601: WeatherFixtureReadTool.FIXTURE_DATE_UTC = "2026-06-10"
- `date_source` field recorded in every weather fixture output ("fixture_default" or "explicit")
- `queried_at` recorded as ISO-8601 UTC in weather and clothing fixture outputs
- All planner output contracts record timezone explicitly
- Run fails if operator depends on undocumented local timezone (local_time_used: false)

### Closed Gaps
1. ~~Terms like "today" in fixture names are not resolved to ISO-8601~~ — RESOLVED: WeatherFixtureReadTool resolves vague terms to FIXTURE_DATE_UTC
2. ~~Timezone not recorded in every planner output~~ — RESOLVED: queried_at and date fields use ISO-8601 UTC in all outputs
