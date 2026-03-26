from __future__ import annotations

import json
import os
import subprocess
import sysconfig
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest


class OllamaStubServer:
    def __init__(self) -> None:
        self.tags_response = {"models": []}
        self.generate_response = {"response": "echo placeholder"}
        self.last_generate_request: dict[str, object] | None = None
        self.last_path: str | None = None
        self._server = ThreadingHTTPServer(("127.0.0.1", 0), self._make_handler())
        self.thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    @property
    def host(self) -> str:
        return f"http://127.0.0.1:{self._server.server_address[1]}"

    def _make_handler(self):
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802
                outer.last_path = self.path
                if self.path != "/api/tags":
                    self.send_error(404)
                    return
                self._send_json(outer.tags_response)

            def do_POST(self) -> None:  # noqa: N802
                outer.last_path = self.path
                if self.path != "/api/generate":
                    self.send_error(404)
                    return
                length = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
                outer.last_generate_request = payload
                self._send_json(outer.generate_response)

            def _send_json(self, payload: dict[str, object]) -> None:
                encoded = json.dumps(payload).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)

            def log_message(self, format: str, *args) -> None:  # noqa: A003
                return

        return Handler

    def __enter__(self) -> OllamaStubServer:
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self._server.shutdown()
        self._server.server_close()
        self.thread.join(timeout=2)


def _bit_executable() -> Path:
    candidate = Path(sysconfig.get_path("scripts")) / "bit"
    if not candidate.exists():
        pytest.skip("Installed bit console script not found in current environment")
    return candidate


def _env_with_home(home: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["HOME"] = str(home)
    return env


def _write_config(home: Path, *, model: str, host: str) -> None:
    (home / ".bit").write_text(
        f'model = "{model}"\nhost = "{host}"\n', encoding="utf-8"
    )


def test_console_script_generates_command_via_subprocess(tmp_path: Path) -> None:
    bit_executable = _bit_executable()

    with OllamaStubServer() as server:
        server.generate_response = {"response": "mkdir new_folder"}
        _write_config(tmp_path, model="llama3.1:8b", host=server.host)

        result = subprocess.run(
            [str(bit_executable), "create", "folder", "new_folder"],
            capture_output=True,
            text=True,
            env=_env_with_home(tmp_path),
            check=False,
        )

    assert result.returncode == 0
    assert result.stdout == "mkdir new_folder\n"
    assert result.stderr == ""
    assert server.last_path == "/api/generate"
    assert server.last_generate_request is not None
    assert server.last_generate_request["model"] == "llama3.1:8b"
    assert server.last_generate_request["prompt"] == "create folder new_folder"


def test_console_script_missing_config_returns_error(tmp_path: Path) -> None:
    bit_executable = _bit_executable()

    result = subprocess.run(
        [str(bit_executable), "count", "files"],
        capture_output=True,
        text=True,
        env=_env_with_home(tmp_path),
        check=False,
    )

    assert result.returncode == 1
    assert result.stdout == ""
    assert "Run 'bit --setup' first" in result.stderr


@pytest.mark.parametrize(
    ("args", "needle"),
    [
        (["--activate", "zsh"], "function bit()"),
        (["--deactivate", "zsh"], "unfunction bit"),
        (["--activate", "bash"], "bind -x"),
    ],
)
def test_console_script_shell_helpers_are_available(
    tmp_path: Path, args: list[str], needle: str
) -> None:
    bit_executable = _bit_executable()

    result = subprocess.run(
        [str(bit_executable), *args],
        capture_output=True,
        text=True,
        env=_env_with_home(tmp_path),
        check=False,
    )

    assert result.returncode == 0
    assert needle in result.stdout
    assert result.stderr == ""
