# Makefile Target Verification

## File
`Makefile` (5347 bytes)

## Key Targets
- `help`
- `install`
- `seed-boot`
- `prove-seed`
- `prove-l1`
- `prove-l2`
- `prove-format`
- `prove-all`
- `audit-structure`
- `prove-organization`
- `test-smoke`
- `test-l0`
- `test-l1`
- `test-l2`
- `test-initiator`
- `test-evolve`
- `test-integration`
- `test-system`
- `test-regression`
- `test-all`
- `test-live`
- `prove-hygiene`
- `prove-umbrella-agent`
- `run`
- `build-seed`
- `clean`

## prove-umbrella-agent Target
Target: `make prove-umbrella-agent`
Script: `scripts/prove-umbrella-agent.sh`
Present: ✅ YES
Meaningful checks: ✅ (validates infrastructure, schemas, policy registry, canary tests)

## Verification
All Makefile targets parse correctly. The `prove-umbrella-agent` target runs meaningful assertions and exits non-zero on failure.
