from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from .config import Config, ConfigError, DEFAULT_HOST, load_config, save_config
from .ollama import OllamaError, generate_command, list_models
from .shell import get_shell_integration_script
from .terminal import inject_command_into_prompt


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    try:
        if args.setup:
            return _run_setup()

        if args.print_shell_integration:
            return _print_shell_integration(args.print_shell_integration)

        instruction = " ".join(args.instruction).strip()
        if not instruction:
            parser.error("an instruction is required unless --setup is used")

        config = load_config()
        command = generate_command(
            host=config.host,
            model=config.model,
            instruction=instruction,
        )
        sanitized = _sanitize_command(command)
        if args.print_only or not inject_command_into_prompt(sanitized):
            print(sanitized)
        return 0
    except (ConfigError, OllamaError) as exc:
        print(f"bit: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("bit: interrupted", file=sys.stderr)
        return 130


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bit",
        description=(
            "Translate natural-language shell instructions into a Linux command using a local OLLAMA model."
        ),
        epilog=(
            "Normal mode prints the generated command to stdout or injects it into an interactive prompt. "
            "For shell widgets, run 'source <(bit --print-shell-integration bash)' in Bash or "
            "'source <(bit --print-shell-integration zsh)' in Zsh."
        ),
    )
    parser.add_argument("instruction", nargs="*", help="natural-language instruction to translate")
    parser.add_argument(
        "--setup",
        action="store_true",
        help="interactively select an installed OLLAMA model and save it to ~/.bit",
    )
    parser.add_argument(
        "--print-shell-integration",
        choices=["bash", "zsh"],
        metavar="SHELL",
        help="print shell integration helper code for the selected shell",
    )
    parser.add_argument(
        "--print-only",
        action="store_true",
        help="always print the generated command to stdout instead of trying interactive prompt insertion",
    )
    return parser


def _run_setup() -> int:
    models = list_models(DEFAULT_HOST)
    if not models:
        raise OllamaError(
            "No installed OLLAMA models were found. Pull a model first, for example 'ollama pull llama3.1:8b'."
        )

    print("Installed OLLAMA models:")
    for index, model in enumerate(models, start=1):
        print(f"{index}. {model}")

    choice = _prompt_for_selection(len(models))
    selected_model = models[choice - 1]
    save_config(Config(model=selected_model, host=DEFAULT_HOST))
    print(f"Saved configuration to ~/.bit using model '{selected_model}'.")
    return 0


def _prompt_for_selection(option_count: int) -> int:
    while True:
        raw = input(f"Select a model [1-{option_count}]: ").strip()
        if not raw:
            continue
        try:
            value = int(raw)
        except ValueError:
            print("Enter a number.", file=sys.stderr)
            continue
        if 1 <= value <= option_count:
            return value
        print(f"Enter a number between 1 and {option_count}.", file=sys.stderr)


def _print_shell_integration(shell_name: str) -> int:
    selected_shell = shell_name or _detect_shell_name()
    try:
        print(get_shell_integration_script(selected_shell), end="")
    except ValueError as exc:
        raise ConfigError(str(exc)) from exc
    return 0


def _detect_shell_name() -> str:
    shell_env = Path(sys.argv[0]).name
    parent_shell = Path(os.environ.get("SHELL", "")).name
    for candidate in (parent_shell, shell_env):
        if candidate in {"bash", "zsh"}:
            return candidate
    return "bash"


def _sanitize_command(command: str) -> str:
    value = command.strip()
    if value.startswith("```"):
        raise OllamaError("Model output used Markdown fences instead of a raw shell command.")
    if "\x00" in value:
        raise OllamaError("Model output contains invalid null bytes.")

    lines = [line.strip() for line in value.splitlines() if line.strip()]
    if len(lines) != 1:
        raise OllamaError("Model output must contain exactly one non-empty line.")

    sanitized = lines[0]
    if sanitized.startswith(("'", '"')) and sanitized.endswith(("'", '"')) and len(sanitized) > 1:
        raise OllamaError("Model output must be a command, not a quoted string.")
    return sanitized


if __name__ == "__main__":
    raise SystemExit(main())