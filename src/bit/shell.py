from __future__ import annotations

from importlib import resources


def get_bash_integration_script() -> str:
    return resources.files("bit").joinpath("shell/bash_integration.sh").read_text(encoding="utf-8")