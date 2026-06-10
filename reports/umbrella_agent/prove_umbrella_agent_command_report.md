# Prove Umbrella Agent Command Report

## Makefile Target
`make prove-umbrella-agent`

## Script
`scripts/prove-umbrella-agent.sh`

## Steps Verified
1. pass_0..pass_3 baseline snapshots exist
2. Schema files exist (input, weather_fixture, output)
3. `weather.fixture.read` capability registered
4. Canary patch tests pass (safe+LIVE, unsafe+L0, unsafe+traversal)
5. Evidence helper modules exist
6. Makefile target exists

## Exit Code
Exit code 0 = all checks pass, non-zero = failure.

## Conclusion
**PASS** — All proof checks pass.
