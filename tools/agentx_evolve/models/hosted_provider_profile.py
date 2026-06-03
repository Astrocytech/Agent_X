from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "HostedProviderProfile",
    "check_connectivity",
]


@dataclass
class HostedProviderProfile:
    provider: str = ""
    model: str = ""
    endpoint: str = ""
    api_key_env: str = ""
    timeout_seconds: int = 30
    metadata: dict[str, Any] = field(default_factory=dict)

    def resolve_api_key(self) -> str | None:
        return os.environ.get(self.api_key_env) if self.api_key_env else None


def check_connectivity(profile: HostedProviderProfile) -> dict[str, Any]:
    result: dict[str, Any] = {
        "provider": profile.provider,
        "endpoint": profile.endpoint,
        "reachable": False,
        "status_code": None,
        "error": None,
    }
    api_key = profile.resolve_api_key()
    if not api_key:
        result["error"] = f"API key not found in env var '{profile.api_key_env}'"
        return result

    try:
        import urllib.request
        import urllib.error

        req = urllib.request.Request(
            profile.endpoint,
            method="HEAD",
            headers={"Authorization": f"Bearer {api_key}"},
        )
        resp = urllib.request.urlopen(req, timeout=profile.timeout_seconds)
        result["reachable"] = True
        result["status_code"] = resp.status
    except urllib.error.HTTPError as exc:
        result["reachable"] = exc.code in (200, 401, 403)
        result["status_code"] = exc.code
        result["error"] = str(exc)
    except Exception as exc:
        result["error"] = str(exc)
    return result
