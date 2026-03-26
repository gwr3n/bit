from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

CONFIG_PATH = Path.home() / ".bit"
DEFAULT_HOST = "http://127.0.0.1:11434"


class ConfigError(RuntimeError):
    """Raised when configuration is missing or invalid."""


@dataclass(slots=True)
class Config:
    model: str
    host: str = DEFAULT_HOST


def load_config(path: Path = CONFIG_PATH) -> Config:
    if not path.exists():
        raise ConfigError(
            f"Configuration file not found at {path}. Run 'bit --setup' first."
        )

    try:
        with path.open("rb") as handle:
            payload = tomllib.load(handle)
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"Invalid TOML in {path}: {exc}") from exc
    except OSError as exc:
        raise ConfigError(f"Unable to read configuration file {path}: {exc}") from exc

    model = str(payload.get("model", "")).strip()
    host = str(payload.get("host", DEFAULT_HOST)).strip() or DEFAULT_HOST
    if not model:
        raise ConfigError(f"Configuration file {path} does not define a model.")
    return Config(model=model, host=host)


def save_config(config: Config, path: Path = CONFIG_PATH) -> None:
    content = f'model = "{_escape_toml_string(config.model)}"\n'
    content += f'host = "{_escape_toml_string(config.host)}"\n'
    try:
        path.write_text(content, encoding="utf-8")
    except OSError as exc:
        raise ConfigError(f"Unable to write configuration file {path}: {exc}") from exc


def _escape_toml_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')
