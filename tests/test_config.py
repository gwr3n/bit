from __future__ import annotations

from pathlib import Path

import pytest

from bit.config import DEFAULT_HOST, Config, ConfigError, load_config, save_config


def test_load_config_missing_file_raises(tmp_path: Path) -> None:
    missing = tmp_path / ".bit"

    with pytest.raises(ConfigError, match="Configuration file not found"):
        load_config(missing)


def test_load_config_invalid_toml_raises(tmp_path: Path) -> None:
    path = tmp_path / ".bit"
    path.write_text('model = "unterminated\n', encoding="utf-8")

    with pytest.raises(ConfigError, match="Invalid TOML"):
        load_config(path)


def test_load_config_requires_model(tmp_path: Path) -> None:
    path = tmp_path / ".bit"
    path.write_text('host = "http://localhost:11434"\n', encoding="utf-8")

    with pytest.raises(ConfigError, match="does not define a model"):
        load_config(path)


def test_load_config_uses_default_host_when_omitted(tmp_path: Path) -> None:
    path = tmp_path / ".bit"
    path.write_text('model = "llama3.1:8b"\n', encoding="utf-8")

    config = load_config(path)

    assert config == Config(model="llama3.1:8b", host=DEFAULT_HOST)


def test_load_config_uses_default_host_when_blank(tmp_path: Path) -> None:
    path = tmp_path / ".bit"
    path.write_text('model = "llama3.1:8b"\nhost = "  "\n', encoding="utf-8")

    config = load_config(path)

    assert config.host == DEFAULT_HOST


def test_save_config_round_trips_special_characters(tmp_path: Path) -> None:
    path = tmp_path / ".bit"
    original = Config(model='model"name\\test', host='http://host\\path"quoted')

    save_config(original, path)
    loaded = load_config(path)

    assert loaded == original
