from __future__ import annotations

import argparse
import sys

from .config import Config, ConfigError, DEFAULT_HOST, load_config, save_config
from .ollama import OllamaError, generate_command, list_models
from .shell import get_bash_integration_script


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
            "Normal mode prints the generated command to stdout. For prompt-buffer insertion in Bash, "
            "run 'bit --print-shell-integration bash' and source the result."
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
        choices=["bash"],
        metavar="SHELL",
        help="print shell integration helper code for the selected shell",
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
    if shell_name != "bash":
        raise ConfigError(f"Unsupported shell integration target: {shell_name}")
    print(get_bash_integration_script(), end="")
    return 0


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