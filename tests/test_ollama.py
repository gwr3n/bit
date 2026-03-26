from __future__ import annotations

import io
import json
from urllib import error

import pytest

from bit import ollama
from bit.ollama import OllamaError


class FakeResponse:
    def __init__(self, payload: str) -> None:
        self._payload = payload.encode("utf-8")

    def read(self) -> bytes:
        return self._payload

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


def test_list_models_filters_empty_names(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        ollama,
        "_request_json",
        lambda url: {
            "models": [{"name": " llama3.1:8b "}, {"name": ""}, {}, {"name": "mistral"}]
        },
    )

    assert ollama.list_models("http://127.0.0.1:11434") == ["llama3.1:8b", "mistral"]


def test_generate_command_returns_trimmed_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def fake_request_json(
        url: str, data: dict[str, object], method: str
    ) -> dict[str, object]:
        captured["url"] = url
        captured["data"] = data
        captured["method"] = method
        return {"response": "  ls -la  \n"}

    monkeypatch.setattr(ollama, "_request_json", fake_request_json)

    result = ollama.generate_command(
        host="http://127.0.0.1:11434",
        model="llama3.1:8b",
        instruction="list files",
    )

    assert result == "ls -la"
    assert captured["url"] == "http://127.0.0.1:11434/api/generate"
    assert captured["method"] == "POST"
    assert captured["data"]["model"] == "llama3.1:8b"


def test_generate_command_rejects_empty_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        ollama, "_request_json", lambda *args, **kwargs: {"response": "   "}
    )

    with pytest.raises(OllamaError, match="empty response"):
        ollama.generate_command(host="http://host", model="m", instruction="do thing")


def test_request_json_get_success(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_urlopen(req, timeout: int):
        captured["url"] = req.full_url
        captured["method"] = req.get_method()
        captured["accept"] = req.headers["Accept"]
        captured["timeout"] = timeout
        return FakeResponse('{"models": []}')

    monkeypatch.setattr(ollama.request, "urlopen", fake_urlopen)

    payload = ollama._request_json("http://host/api/tags")

    assert payload == {"models": []}
    assert captured == {
        "url": "http://host/api/tags",
        "method": "GET",
        "accept": "application/json",
        "timeout": 20,
    }


def test_request_json_post_success(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_urlopen(req, timeout: int):
        captured["url"] = req.full_url
        captured["method"] = req.get_method()
        captured["content_type"] = dict(req.header_items())["Content-type"]
        captured["data"] = json.loads(req.data.decode("utf-8"))
        return FakeResponse('{"response": "pwd"}')

    monkeypatch.setattr(ollama.request, "urlopen", fake_urlopen)

    payload = ollama._request_json(
        "http://host/api/generate", data={"prompt": "pwd"}, method="POST"
    )

    assert payload == {"response": "pwd"}
    assert captured["method"] == "POST"
    assert captured["content_type"] == "application/json"
    assert captured["data"] == {"prompt": "pwd"}


def test_request_json_http_error_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    http_error = error.HTTPError(
        url="http://host/api/generate",
        code=500,
        msg="boom",
        hdrs=None,
        fp=io.BytesIO(b"server exploded"),
    )

    def fake_urlopen(req, timeout: int):
        raise http_error

    monkeypatch.setattr(ollama.request, "urlopen", fake_urlopen)

    with pytest.raises(OllamaError, match="HTTP 500: server exploded"):
        ollama._request_json("http://host/api/generate")


def test_request_json_url_error_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(req, timeout: int):
        raise error.URLError("connection refused")

    monkeypatch.setattr(ollama.request, "urlopen", fake_urlopen)

    with pytest.raises(OllamaError, match="Unable to contact OLLAMA"):
        ollama._request_json("http://host/api/tags")


def test_request_json_invalid_json_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        ollama.request, "urlopen", lambda req, timeout: FakeResponse("not json")
    )

    with pytest.raises(OllamaError, match="invalid JSON"):
        ollama._request_json("http://host/api/tags")


def test_request_json_non_dict_payload_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        ollama.request, "urlopen", lambda req, timeout: FakeResponse("[]")
    )

    with pytest.raises(OllamaError, match="unexpected response payload"):
        ollama._request_json("http://host/api/tags")
