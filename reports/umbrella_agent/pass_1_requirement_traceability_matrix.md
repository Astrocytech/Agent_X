# Pass 1 — Requirement Traceability Matrix

| ID | Requirement | Source | Test | Schema | Command | Evidence | Status |
|---|---|---|---|---|---|---|---|
| UA-POL-001 | `weather.fixture.read` capability registered | `capability_registry.py` | `test_policy_umbrella_capability.py` | — | `make test-evolve` | — | PASS |
| UA-SCH-001 | Umbrella input schema | — | — | `umbrella_agent_input.schema.json` | `jsonschema` | — | PASS |
| UA-SCH-002 | Weather fixture schema | — | — | `umbrella_weather_fixture.schema.json` | — | — | PASS |
| UA-SCH-003 | Umbrella output schema | — | — | `umbrella_agent_output.schema.json` | — | — | PASS |
| UA-CAN-001 | Canary patch support | `patch_execution_service.py`, `patch_applier.py` | `test_canary_patch_flow.py` | — | `make test-integration` | — | PASS |
| UA-EVI-001 | Evidence helpers | `evidence_writer.py`, `event_logger.py`, `manifest_builder.py` | `test_evidence_helpers.py` | — | `pytest -k evidence` | — | PASS |
| UA-MAK-001 | Makefile prove-umbrella-agent | `Makefile`, `prove-umbrella-agent.sh` | — | — | `make prove-umbrella-agent` | — | PASS |
| UA-AGT-001 | Umbrella agent in temp workspace | — | — | — | — | `stage_b_patch_provenance.json`, `file_provenance_manifest.json` | PASS |
