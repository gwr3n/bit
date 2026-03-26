# bit

[![Codecov](https://img.shields.io/codecov/c/gh/gwr3n/bit/main)](https://codecov.io/gh/gwr3n/bit) [![Python package](https://img.shields.io/github/actions/workflow/status/gwr3n/bit/.github%2Fworkflows%2Fpython-package.yml)](https://github.com/gwr3n/bit/actions/workflows/python-package.yml) [![Lint and type-check](https://img.shields.io/github/actions/workflow/status/gwr3n/bit/.github%2Fworkflows%2Flint-type.yml?branch=main&label=lint%20%2B%20type-check)](https://github.com/gwr3n/bit/actions/workflows/lint-type.yml) 

[![PyPI - Version](https://img.shields.io/pypi/v/bit-wrangler)](https://pypi.org/project/bit-wrangler?cacheSeconds=300) [![Python versions](https://img.shields.io/pypi/pyversions/bit-wrangler)](https://pypi.org/project/bit-wrangler?cacheSeconds=300) [![License](https://img.shields.io/github/license/gwr3n/bit?cacheSeconds=300)](https://github.com/gwr3n/bit/blob/main/LICENSE) [![Downloads](https://static.pepy.tech/badge/bit-wrangler)](https://pepy.tech/project/bit-wrangler) [![Release](https://img.shields.io/github/v/release/gwr3n/bit)](https://github.com/gwr3n/bit/releases) [![Wheel](https://img.shields.io/pypi/wheel/bit-wrangler?cacheSeconds=300)](https://pypi.org/project/bit-wrangler)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000?logo=python)](https://github.com/psf/black) [![Ruff](https://img.shields.io/badge/lint-ruff-1f79ff?logo=python)](https://github.com/astral-sh/ruff) [![mypy](https://img.shields.io/badge/type--checked-mypy-blue?logo=python)](https://github.com/python/mypy)

[![Issues](https://img.shields.io/github/issues/gwr3n/bit)](https://github.com/gwr3n/bit/issues) [![PRs](https://img.shields.io/github/issues-pr/gwr3n/bit)](https://github.com/gwr3n/bit/pulls) [![Stars](https://img.shields.io/github/stars/gwr3n/bit?style=social)](https://github.com/gwr3n/bit/stargazers) [![Docs](https://img.shields.io/badge/docs-site-blue)](https://github.com/gwr3n/bit)

`bit` is a Python CLI that translates natural-language shell instructions into Linux shell commands by calling a locally running OLLAMA model.

## Quick Installation

```bash
pip install bit-wrangler
```

## Example Usage

```bash
$ bit create folder new_folder
mkdir new_folder
```

By default, `bit` prints the generated command to stdout. 

If you want `bit` to place the generated command into your current shell prompt for review, first enable the Bash or Zsh shell integration (this only has to be done once).

Activate shell integration:

```bash
# Bash
source <(bit --activate bash)    # alternatively replace bash with zsh
```

Option 1 (using Ctrl-x Ctrl-b):
```
find large log files in current directory
# press Ctrl-x Ctrl-b to replace the prompt with the generated command
```

Option 2 (using bit function):
```
bit find large log files in current directory
# the generated command is staged into the prompt for review
```

## Features

- Translates free-form instructions into one shell command.
- Stores configuration in `~/.bit` using TOML.
- Supports interactive model selection with `bit --setup`.
- Exposes shell integration instructions for Bash and Zsh so generated commands can be inserted into the prompt buffer.
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
python -m pip install dist/bit_wrangler-0.1.1-py3-none-any.whl
```

Or install in editable mode while developing:

```bash
python -m pip install -e .
```

After installation, the `bit` command is available directly on the command line.

## Development Tools

Install the development dependencies:

```bash
python -m pip install -e ".[dev]"
```

Run the formatter:

```bash
black src tests
```

Run Ruff:

```bash
ruff check src tests
```

Run Flake8:

```bash
flake8 src tests
```

Run mypy:

```bash
mypy src
```

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
bit --activate bash
```

Print Zsh integration helper:

```bash
bit --activate zsh
```

Print Bash deactivation helper:

```bash
bit --deactivate bash
```

Print Zsh deactivation helper:

```bash
bit --deactivate zsh
```

Show help:

```bash
bit --help
```

## Shell Integration

The standalone `bit` executable only prints commands. If you want generated commands staged into your current shell prompt so you can review and edit them before execution, source the appropriate shell integration.

To enable that widget in Bash:

```bash
source <(bit --activate bash)
```

To enable that widget in Zsh:

```bash
source <(bit --activate zsh)
```

To unload the integration in Bash:

```bash
source <(bit --deactivate bash)
```

To unload the integration in Zsh:

```bash
source <(bit --deactivate zsh)
```

After sourcing the Zsh integration, you can also invoke `bit` directly as a shell function:

```bash
bit create folder new_folder
```

That direct Zsh function call does not execute the generated command immediately. Instead, it stages the translated shell command into the next prompt so you can review or edit it before pressing Enter.

Then type a natural-language instruction directly at the shell prompt and press `Ctrl-x Ctrl-b`. The widget will:

1. Read the current command line buffer as the instruction.
2. Call the installed `bit` CLI.
3. Replace the current command line with the generated shell command.

Nothing is executed automatically. You can edit the generated command and then press Enter yourself.

To load this automatically, add the matching `source <(bit --activate ...)` line to your shell startup file.

In Zsh, sourcing the integration also defines a `bit` shell function that shadows the installed executable in that shell session. Administrative commands such as `bit --setup`, `bit --help`, `bit --activate zsh`, and `bit --deactivate zsh` still pass through to the real CLI.

## Build

Create a source distribution and wheel:

```bash
python -m build
```

## Limitations and Security Notes

- The tool asks the model for a single shell command, but model output is still untrusted text.
- `bit` rejects obvious malformed multi-line and fenced responses, but it does not prove a generated command is safe.
- Review generated commands before executing them.
- Prompt staging is available through sourced shell integration rather than the standalone executable.
- The default target is Linux shell syntax even if the tool is run elsewhere.