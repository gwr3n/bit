from __future__ import annotations

import sys

import pytest

from bit import cli
from bit.config import Config, ConfigError
from bit.ollama import OllamaError


def test_main_prints_generated_command(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "argv", ["bit", "create", "folder", "new_folder"])
    monkeypatch.setattr(
        cli, "load_config", lambda: Config(model="llama3", host="http://host")
    )
    monkeypatch.setattr(cli, "generate_command", lambda **kwargs: "mkdir new_folder")

    assert cli.main() == 0
    captured = capsys.readouterr()
    assert captured.out == "mkdir new_folder\n"
    assert captured.err == ""


def test_main_activate_prints_script(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "argv", ["bit", "--activate", "zsh"])
    monkeypatch.setattr(
        cli,
        "get_shell_integration_script",
        lambda shell_name, mode: f"{shell_name}:{mode}\n",
    )

    assert cli.main() == 0
    assert capsys.readouterr().out == "zsh:activate\n"


def test_main_deactivate_prints_script(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "argv", ["bit", "--deactivate", "bash"])
    monkeypatch.setattr(
        cli,
        "get_shell_integration_script",
        lambda shell_name, mode: f"{shell_name}:{mode}\n",
    )

    assert cli.main() == 0
    assert capsys.readouterr().out == "bash:deactivate\n"


def test_main_returns_error_for_config_failure(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "argv", ["bit", "list", "files"])
    monkeypatch.setattr(
        cli, "load_config", lambda: (_ for _ in ()).throw(ConfigError("missing config"))
    )

    assert cli.main() == 1
    assert "bit: missing config" in capsys.readouterr().err


def test_main_returns_error_for_ollama_failure(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "argv", ["bit", "list", "files"])
    monkeypatch.setattr(
        cli, "load_config", lambda: Config(model="llama3", host="http://host")
    )
    monkeypatch.setattr(
        cli,
        "generate_command",
        lambda **kwargs: (_ for _ in ()).throw(OllamaError("boom")),
    )

    assert cli.main() == 1
    assert "bit: boom" in capsys.readouterr().err


def test_main_returns_130_on_keyboard_interrupt(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "argv", ["bit", "list", "files"])
    monkeypatch.setattr(
        cli, "load_config", lambda: Config(model="llama3", host="http://host")
    )
    monkeypatch.setattr(
        cli,
        "generate_command",
        lambda **kwargs: (_ for _ in ()).throw(KeyboardInterrupt()),
    )

    assert cli.main() == 130
    assert "bit: interrupted" in capsys.readouterr().err


def test_run_setup_saves_selected_model(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    saved: dict[str, object] = {}
    monkeypatch.setattr(cli, "list_models", lambda host: ["llama3", "mistral"])
    monkeypatch.setattr(
        cli, "save_config", lambda config: saved.setdefault("config", config)
    )
    monkeypatch.setattr("builtins.input", lambda prompt="": "2")

    assert cli._run_setup() == 0
    assert saved["config"] == Config(model="mistral", host=cli.DEFAULT_HOST)
    assert "Installed OLLAMA models:" in capsys.readouterr().out


def test_run_setup_raises_when_no_models(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "list_models", lambda host: [])

    with pytest.raises(OllamaError, match="No installed OLLAMA models"):
        cli._run_setup()


def test_prompt_for_selection_retries_until_valid(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    responses = iter(["", "abc", "9", "2"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    assert cli._prompt_for_selection(3) == 2
    stderr = capsys.readouterr().err
    assert "Enter a number." in stderr
    assert "Enter a number between 1 and 3." in stderr


def test_detect_shell_name_prefers_shell_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(sys, "argv", ["/usr/local/bin/bit"])
    monkeypatch.setenv("SHELL", "/bin/zsh")

    assert cli._detect_shell_name() == "zsh"


@pytest.mark.parametrize(
    ("command", "expected"),
    [
        (" ls -la ", "ls -la"),
        ("pwd\n", "pwd"),
    ],
)
def test_sanitize_command_returns_single_line(command: str, expected: str) -> None:
    assert cli._sanitize_command(command) == expected


@pytest.mark.parametrize(
    ("command", "message"),
    [
        ("```bash\nls\n```", "Markdown fences"),
        ("bad\x00command", "null bytes"),
        ("echo one\necho two", "exactly one non-empty line"),
        ('"ls -la"', "quoted string"),
    ],
)
def test_sanitize_command_rejects_invalid_output(command: str, message: str) -> None:
    with pytest.raises(OllamaError, match=message):
        cli._sanitize_command(command)
