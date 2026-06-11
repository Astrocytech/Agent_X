from __future__ import annotations

from agentx_evolve.io.result_envelope import MvpResultEnvelope, validate_envelope


def validate_raw_output(data: dict) -> tuple[bool, list[str]]:
    return validate_envelope(data)


def ensure_envelope(data: dict) -> MvpResultEnvelope:
    ok, issues = validate_envelope(data)
    if not ok:
        msg = "; ".join(issues)
        raise ValueError(f"Invalid envelope: {msg}")
    return MvpResultEnvelope.from_dict(data)
