Create a Python project called `bit`, a command-line tool that translates natural-language shell instructions into Linux shell commands by using a locally running OLLAMA model.

## Objective

The tool should let a user type a command such as:

```bash
bit create folder new_folder
```

and receive the corresponding shell command:

```bash
mkdir new_folder
```

The output must be suitable for immediate use in the shell.

## Core Behavior

1. `bit` accepts a free-form natural-language instruction as CLI arguments.
2. `bit` sends the instruction to a local OLLAMA installation and requests a single Linux shell command as output.
3. The tool prints only the translated shell command to stdout in normal operation.
4. Example:
	- Input: `bit create folder new_folder`
	- Output: `mkdir new_folder`

## Important Shell UX Requirement

The intended UX is that the translated command should appear in the user's shell, ready to execute by pressing Enter.

Because a standalone CLI process cannot directly edit the current shell's command line after it starts, implement this in a practical way:

1. The Python CLI must print the translated command to stdout.
2. The project must also document a shell integration approach for Bash-compatible shells so the command can be inserted into the current prompt, not just printed.
3. Prefer a simple integration pattern such as a shell function, wrapper, or readline-compatible helper that allows the user to invoke `bit` and place the generated command into the current command buffer.
4. If full interactive insertion is not implemented in Python alone, document the exact shell setup required and make the default CLI behavior still useful and correct.

## Configuration

Store user configuration in `~/.bit`.

Configuration should include at minimum:

1. The OLLAMA model name to use.
2. Any other settings needed for local inference, if applicable.

Use a structured and maintainable format for this file, preferably TOML.

## Setup Flow

Implement:

```bash
bit --setup
```

This command should:

1. Detect or query locally installed OLLAMA models.
2. Present the installed models to the user.
3. Let the user select one model interactively.
4. Save the selected model into `~/.bit`.

If OLLAMA is not installed, not running, or no models are available, provide a clear error message with actionable guidance.

## Help Output

Implement:

```bash
bit --help
```

The help output should clearly describe:

1. Basic usage.
2. The setup command.
3. How configuration works.
4. How shell integration works.
5. Any limitations or assumptions.

## Implementation Requirements

1. Implement the project in Python.
2. Package it so it can be installed with `pip`.
3. After installation, the command `bit` must be available directly on the command line.
4. Use modern Python packaging with appropriate project metadata.
5. Include all files needed to build a distributable package.

## Project Files

Create a complete, buildable Python package including the appropriate supporting files, such as:

1. `pyproject.toml`
2. package source files
3. `README.md`
4. manifest/package-inclusion configuration if needed
5. any shell integration helper scripts or examples

Only include files that are actually needed by the chosen packaging approach.

## Build Requirement

It must be possible to build a distribution with:

```bash
python -m build
```

The result should produce a valid installable distribution.

## Documentation Requirements

The `README.md` should include:

1. Project overview.
2. Installation instructions.
3. OLLAMA prerequisites.
4. Initial setup with `bit --setup`.
5. Usage examples.
6. Shell integration instructions.
7. Build instructions.
8. Limitations and security notes.

## Reliability and Safety Expectations

1. The model should be instructed to return only one shell command, with no explanation or Markdown.
2. The program should validate and sanitize responses as appropriate before presenting them.
3. Error handling should be clear for cases such as missing config, missing OLLAMA, unavailable models, failed inference, or malformed model output.
4. The implementation should favor predictable, minimal output suitable for shell use.

## Deliverable

Produce a complete, installable Python CLI project for `bit` that satisfies the requirements above, including packaging, configuration handling, setup flow, help text, OLLAMA integration, and documentation.