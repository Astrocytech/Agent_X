import warnings
from typing import Any


class RedactionEngine:
    def redact(self, data: dict, keys_to_redact: set[str] | None = None) -> dict:
        if keys_to_redact is None:
            keys_to_redact = {"secret", "password", "token", "api_key", "private_key"}
        return redact_sensitive_data(data, keys_to_redact)


def redact_sensitive_data(data: dict, keys_to_redact: set[str] | None = None) -> dict:
    if keys_to_redact is None:
        keys_to_redact = {"secret", "password", "token", "api_key", "private_key"}
    result: dict[str, Any] = {}
    for k, v in data.items():
        if k.lower() in keys_to_redact:
            result[k] = "***REDACTED***"
        elif isinstance(v, dict):
            result[k] = redact_sensitive_data(v, keys_to_redact)
        elif isinstance(v, list):
            result[k] = [
                redact_sensitive_data(item, keys_to_redact) if isinstance(item, dict) else item
                for item in v
            ]
        else:
            result[k] = v
    return result


warnings.warn(
    "agentx_evolve.monitoring.redaction is deprecated; "
    "use agentx_evolve.monitoring.monitoring_utils instead",
    DeprecationWarning, stacklevel=2,
)

__all__ = ["RedactionEngine", "redact_sensitive_data"]
