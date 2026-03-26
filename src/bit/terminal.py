from __future__ import annotations

import fcntl
import os
import sys
import termios


def inject_command_into_prompt(command: str) -> bool:
    if not _supports_tty_injection():
        return False

    try:
        fd = os.open("/dev/tty", os.O_RDWR)
    except OSError:
        return False

    try:
        for byte in command.encode("utf-8"):
            fcntl.ioctl(fd, termios.TIOCSTI, bytes([byte]))
    except OSError:
        return False
    finally:
        os.close(fd)

    return True


def _supports_tty_injection() -> bool:
    if not hasattr(termios, "TIOCSTI"):
        return False
    return sys.stdin.isatty() and sys.stdout.isatty() and sys.stderr.isatty()