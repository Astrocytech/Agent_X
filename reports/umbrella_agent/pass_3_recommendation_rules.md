# Pass 3 — Deterministic Recommendation Rules

The umbrella recommendation must be made by deterministic code, not unconstrained model judgment.

## `yes`
Return `yes` if any of the following are true:
- `precipitation_probability >= 60`
- condition contains `rain`
- condition contains `shower`
- condition contains `thunderstorm`
- severe weather alert indicates rain, storm, freezing rain, sleet, hail, or heavy precipitation

## `maybe`
Return `maybe` if no `yes` rule is triggered and any of the following are true:
- `precipitation_probability >= 30` and `< 60`
- condition contains `drizzle`
- condition indicates uncertain precipitation
- alerts mention possible precipitation but are not severe

## `no`
Return `no` if all of the following are true:
- `precipitation_probability < 30`
- no rain-like condition exists
- no relevant alert exists

## `unknown`
Return `unknown` if:
- weather data is missing
- weather data is malformed
- both precipitation probability and condition are unavailable
- weather provider/tool fails
- schema validation fails

## Required Rule Tests
- yes by probability
- yes by rain condition
- yes by storm alert
- maybe by probability
- maybe by drizzle
- no by clear low-probability weather
- unknown by missing data
- unknown by malformed data
