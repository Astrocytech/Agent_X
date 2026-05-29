# L2 Profile Model

Each L2 profile is a YAML document with the following shape:

```yaml
profile:
  profile_id: "L2-PROFILE-XXX"
  name: ""
  status: "draft|active|deprecated"
  purpose: ""
  specialization_type: "coding|research|symbolic-regression|repo-maintenance|orchestration"
  allowed_inputs: []
  expected_outputs: []
  required_l1_units: []
  forbidden_actions:
    - "modify L0 directly"
    - "modify L1 directly without L1 FIC"
    - "execute tools directly"
    - "perform autonomous patching"
  evaluation_refs: []
  integration_refs: []
  risk_level: "low|medium|high|critical"
```

## Field Descriptions

| Field | Required | Description |
|-------|----------|-------------|
| `profile_id` | Yes | Unique identifier within L2 portfolio |
| `name` | Yes | Human-readable name |
| `status` | Yes | Lifecycle status |
| `purpose` | Yes | Why this profile exists |
| `specialization_type` | Yes | Category of specialization |
| `allowed_inputs` | Yes | What this profile can receive |
| `expected_outputs` | Yes | What this profile produces |
| `required_l1_units` | Yes | L1 units needed to implement this profile |
| `forbidden_actions` | Yes | Actions this profile must never perform |
| `evaluation_refs` | No | Links to evaluation specs |
| `integration_refs` | No | Links to integration boundary specs |
| `risk_level` | Yes | Estimated risk of implementing this profile |

## Status Lifecycle

```
draft → active → deprecated
  ↑        |
  └────────┘ (revision)
```

- **draft**: Profile is proposed but not ready for L1 handoff.
- **active**: Profile is approved and ready for L1 FIC creation.
- **deprecated**: Profile is no longer recommended. Existing implementations may remain.
