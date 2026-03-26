from __future__ import annotations

from importlib import resources


def get_shell_integration_script(shell_name: str, *, mode: str = "activate") -> str:
    script_name = {
        ("bash", "activate"): "bash_integration.sh",
        ("bash", "deactivate"): "bash_deactivation.sh",
        ("zsh", "activate"): "zsh_integration.sh",
        ("zsh", "deactivate"): "zsh_deactivation.sh",
    }.get((shell_name, mode))
    if script_name is None:
        raise ValueError(f"Unsupported shell integration target: {shell_name} ({mode})")
    return (
        resources.files("bit")
        .joinpath(f"shell/{script_name}")
        .read_text(encoding="utf-8")
    )
