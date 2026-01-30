from __future__ import annotations

from typing import Any
import requests

from .config import AppConfig


def send_hook_message(config: AppConfig, text: str) -> dict[str, Any]:
    if not config.openclaw_hook_url or not config.openclaw_hook_token:
        return {"sent": False, "reason": "not_configured"}

    payload: dict[str, Any] = {"text": text}
    if config.openclaw_hook_to:
        payload["to"] = config.openclaw_hook_to

    headers = {"Authorization": f"Bearer {config.openclaw_hook_token}"}
    response = requests.post(config.openclaw_hook_url, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    return {"sent": True, "status": response.status_code}
