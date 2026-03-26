# bit

`bit` is a Python CLI that translates natural-language shell instructions into Linux shell commands by calling a locally running OLLAMA model.

Example:

```bash
$ bit create folder new_folder
mkdir new_folder
```

## Features

- Translates free-form instructions into one shell command.
- Stores configuration in `~/.bit` using TOML.
- Supports interactive model selection with `bit --setup`.
- Exposes shell integration instructions for Bash so generated commands can be inserted into the prompt buffer.
- Builds as a standard Python package with `python -m build`.

## Requirements

- Python 3.11 or newer.
- A local OLLAMA installation.
- An OLLAMA server available at `http://127.0.0.1:11434`.
- At least one installed OLLAMA model.

## Installation

Build and install locally:

```bash
python -m build
python -m pip install dist/bit_cli-0.1.0-py3-none-any.whl
```

Or install in editable mode while developing:

```bash
python -m pip install -e .
```

After installation, the `bit` command is available directly on the command line.

## Initial Setup

Run:

```bash
bit --setup
```

This command:

1. Queries the local OLLAMA instance for installed models.
2. Displays them as a numbered list.
3. Prompts you to select one.
4. Saves the result in `~/.bit`.

The config file is TOML and looks like this:

```toml
model = "llama3.1:8b"
host = "http://127.0.0.1:11434"
```

## Usage

Translate an instruction:

```bash
bit create folder new_folder
bit find large log files in current directory
bit show disk usage for home directory
```

Print Bash integration helper:

```bash
bit --print-shell-integration bash
```

Show help:

```bash
bit --help
```

## Bash Shell Integration

A normal CLI process cannot directly replace the current interactive shell input buffer after it has already been invoked. Because of that, `bit` always prints the generated command to stdout, and Bash prompt insertion is handled through a readline widget.

To enable that widget in Bash:

```bash
source <(bit --print-shell-integration bash)
```

Then press `Ctrl-x Ctrl-b` at a Bash prompt. The widget will:

1. Prompt for a natural-language instruction.
2. Call the installed `bit` CLI.
3. Insert the generated command into the current command line.

Nothing is executed automatically. You can edit the inserted command and then press Enter yourself.

To load this automatically, add the `source <(bit --print-shell-integration bash)` line to your shell startup file.

## Build

Create a source distribution and wheel:

```bash
python -m build
```

## Limitations and Security Notes

- The tool asks the model for a single shell command, but model output is still untrusted text.
- `bit` rejects obvious malformed multi-line and fenced responses, but it does not prove a generated command is safe.
- Review generated commands before executing them.
- Shell insertion into the current prompt requires shell-specific integration; it cannot be done by a standalone Python process alone.
- The default target is Linux shell syntax even if the tool is run elsewhere.