from __future__ import annotations

import pytest

from bit.shell import get_shell_integration_script


@pytest.mark.parametrize(
    ("shell_name", "mode", "needle"),
    [
        ("bash", "activate", "bind -x"),
        ("bash", "deactivate", "unset -f __bit_widget"),
        ("zsh", "activate", "function bit()"),
        ("zsh", "deactivate", "unfunction bit"),
    ],
)
def test_get_shell_integration_script_returns_expected_content(
    shell_name: str, mode: str, needle: str
) -> None:
    script = get_shell_integration_script(shell_name, mode=mode)

    assert needle in script


def test_get_shell_integration_script_rejects_unsupported_target() -> None:
    with pytest.raises(ValueError, match="Unsupported shell integration target"):
        get_shell_integration_script("fish", mode="activate")
