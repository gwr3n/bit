from __future__ import annotations

import json
from urllib import error, request


class OllamaError(RuntimeError):
    """Raised when the local OLLAMA service cannot satisfy a request."""


SYSTEM_PROMPT = (
    "You translate natural-language Linux shell tasks into exactly one shell command. "
    "Return only the command. Do not add explanations, Markdown, code fences, quotes, "
    "numbering, or multiple alternatives. Target a standard Linux shell environment."
)


def list_models(host: str) -> list[str]:
    payload = _request_json(f"{host.rstrip('/')}/api/tags")
    models = payload.get("models", [])
    result = []
    for entry in models:
        name = str(entry.get("name", "")).strip()
        if name:
            result.append(name)
    return result


def generate_command(*, host: str, model: str, instruction: str) -> str:
    body = {
        "model": model,
        "system": SYSTEM_PROMPT,
        "prompt": instruction,
        "stream": False,
        "options": {
            "temperature": 0,
        },
    }
    payload = _request_json(
        f"{host.rstrip('/')}/api/generate",
        data=body,
        method="POST",
    )
    response = str(payload.get("response", "")).strip()
    if not response:
        raise OllamaError("OLLAMA returned an empty response.")
    return response


def _request_json(url: str, data: dict[str, object] | None = None, method: str = "GET") -> dict[str, object]:
    encoded = None
    headers = {"Accept": "application/json"}
    if data is not None:
        encoded = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = request.Request(url, data=encoded, method=method, headers=headers)
    try:
        with request.urlopen(req, timeout=20) as response:
            raw = response.read().decode("utf-8")
    except error.HTTPError as exc:
        message = exc.read().decode("utf-8", errors="replace")
        raise OllamaError(
            f"OLLAMA request failed with HTTP {exc.code}: {message.strip() or exc.reason}"
        ) from exc
    except error.URLError as exc:
        reason = getattr(exc, "reason", exc)
        raise OllamaError(
            "Unable to contact OLLAMA. Ensure it is installed and serving requests. "
            f"Details: {reason}"
        ) from exc

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise OllamaError(f"OLLAMA returned invalid JSON: {exc}") from exc

    if not isinstance(payload, dict):
        raise OllamaError("OLLAMA returned an unexpected response payload.")
    return payload