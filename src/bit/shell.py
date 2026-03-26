from __future__ import annotations

from importlib import resources


def get_shell_integration_script(shell_name: str) -> str:
    script_name = {
        "bash": "bash_integration.sh",
        "zsh": "zsh_integration.sh",
    }.get(shell_name)
    if script_name is None:
        raise ValueError(f"Unsupported shell integration target: {shell_name}")
    return resources.files("bit").joinpath(f"shell/{script_name}").read_text(encoding="utf-8")