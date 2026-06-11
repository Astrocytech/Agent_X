# Command Reference

## Test Commands

| Command | Description |
|---------|-------------|
| `python3 -m pytest tests/quick/ -v` | Run all unit tests |
| `python3 -m pytest tests/release/ -v` | Run all integration tests |
| `python3 -m pytest tests/release/ -v` | Run all system tests |
| `python3 -m pytest tests/release/ -v` | Run all regression tests |
| `python3 -m pytest tests/ -v` | Run all tests |

## Example Agent Commands

| Command | Description |
|---------|-------------|
| `python3 -m examples.umbrella_agent.runtime` | Run umbrella agent |
| `python3 -m examples.clothing_advice_agent.runtime` | Run clothing agent |
| `python3 -m examples.daily_planning_agent.runtime` | Run planning agent |

## Infrastructure Commands

| Command | Description |
|---------|-------------|
| `python3 -m pytest tests/release/test_governance_benchmarks.py -v` | Run governance benchmarks |
| `python3 -m pytest tests/release/test_text_file_formatting.py -v` | Run file formatting checks |
