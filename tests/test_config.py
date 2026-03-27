import tomllib
from pathlib import Path

import pytest

from precifique.config import get_config


class TestDataDir:
    def test_default_data_dir(self, monkeypatch, tmp_path):
        monkeypatch.delenv("PRECIFIQUE_DATA_DIR", raising=False)
        config = get_config(config_file=tmp_path / "nonexistent.toml")
        assert config.data_dir == Path.home() / ".precifique" / "data"

    def test_env_var_overrides_default(self, monkeypatch, tmp_path):
        monkeypatch.setenv("PRECIFIQUE_DATA_DIR", str(tmp_path / "custom"))
        config = get_config(config_file=tmp_path / "nonexistent.toml")
        assert config.data_dir == tmp_path / "custom"

    def test_config_file_overrides_default(self, monkeypatch, tmp_path):
        monkeypatch.delenv("PRECIFIQUE_DATA_DIR", raising=False)
        config_file = tmp_path / "config.toml"
        config_file.write_text(f'data_dir = "{tmp_path / "from_toml"}"\n')
        config = get_config(config_file=config_file)
        assert config.data_dir == tmp_path / "from_toml"

    def test_env_var_takes_precedence_over_config_file(self, monkeypatch, tmp_path):
        monkeypatch.setenv("PRECIFIQUE_DATA_DIR", str(tmp_path / "from_env"))
        config_file = tmp_path / "config.toml"
        config_file.write_text(f'data_dir = "{tmp_path / "from_toml"}"\n')
        config = get_config(config_file=config_file)
        assert config.data_dir == tmp_path / "from_env"


class TestCurrency:
    def test_default_currency_is_brl(self, monkeypatch, tmp_path):
        monkeypatch.delenv("PRECIFIQUE_CURRENCY", raising=False)
        config = get_config(config_file=tmp_path / "nonexistent.toml")
        assert config.currency == "BRL"

    def test_env_var_overrides_currency(self, monkeypatch, tmp_path):
        monkeypatch.setenv("PRECIFIQUE_CURRENCY", "USD")
        config = get_config(config_file=tmp_path / "nonexistent.toml")
        assert config.currency == "USD"
