# Umbrella Rule Test Results

**Gate:** 4
**JSON data:** `reports/umbrella_agent/umbrella_rule_test_results.json`

## Results

| Rule | Status |
|---|---|
| yes by precipitation >= 60 | PASS |
| yes by rain condition | PASS |
| yes by shower condition | PASS |
| yes by thunderstorm condition | PASS |
| yes by severe alert | PASS |
| maybe by precip >= 30 and < 60 | PASS |
| maybe by drizzle | PASS |
| maybe by possible precip alert | PASS |
| no by clear weather, low prob | PASS |
| unknown by missing data | PASS |
| unknown by malformed data | PASS |
| unknown by malformed alert object | PASS |
| deterministic today resolution | PASS |

## Status: PASS (13/13)
