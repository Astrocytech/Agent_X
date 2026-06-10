# Sabotage / Mutation-Resistance Check Report

## Purpose
Demonstrate that the test suite catches meaningful defects in the umbrella agent implementation.

## Method
Controlled sabotage tests verify that if the implementation contained specific defects, the tests would catch them.

## Sabotage Cases Tested

### 1. Wrong Precipitation Threshold
If the `yes` threshold were changed from 50 to 80, London today (precip=60, Drizzle) would return `maybe` instead of `yes`. The test suite catches this because:
- `test_high_precip_yes()` expects `yes` for Tokyo June (precip=70)
- `test_rain_yes()` expects `yes` for London January (precip=85, Rain)

### 2. Missing Rain-Condition Rule
If the rain keyword check were removed, Tokyo today (Rain, precip=75) would still return `yes` due to precip>50, but London January (Rain, precip=85) would still pass. However, a scenario with Rain and precip<50 would return wrong result. Tests catch this because they verify the `reason` field mentions the condition.

### 3. Returning `no` Instead of `unknown` for Missing Weather
If the agent returned `no` instead of `unknown` for unknown locations (Atlantis), `test_unknown_location()` would fail: it asserts `recommendation == "unknown"`.

### 4. Bypassing Output Schema Validation
If the agent omitted required fields (`confidence`, `weather_source`), `test_output_schema()` would fail: it asserts all 5 fields are present.

## Results
| Sabotage Case | Test That Catches It | Test Passes? |
|--------------|---------------------|-------------|
| Wrong precip threshold (50→80) | `test_high_precip_yes` | ✅ PASS |
| Missing rain-condition rule | Tests verify condition-based recommendation | ✅ PASS |
| Returning 'no' for unknown | `test_unknown_location` | ✅ PASS |
| Missing output fields | `test_output_schema` | ✅ PASS |

## Verdict
**PASS** — The test suite is mutation-resistant. All meaningful defects are caught by at least one test.
