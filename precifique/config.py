import os
import tomllib
from pathlib import Path

from pydantic import BaseModel


class Config(BaseModel):
    data_dir: Path
    currency: str


def get_config(config_file: Path | None = None) -> Config:
    if config_file is None:
        config_file = Path.home() / ".precifique" / "config.toml"

    data_dir = _resolve_data_dir(config_file)
    currency = os.environ.get("PRECIFIQUE_CURRENCY", "BRL")

    return Config(data_dir=data_dir, currency=currency)


def _resolve_data_dir(config_file: Path) -> Path:
    if env_val := os.environ.get("PRECIFIQUE_DATA_DIR"):
        return Path(env_val)

    if config_file.exists():
        with open(config_file, "rb") as f:
            data = tomllib.load(f)
        if "data_dir" in data:
            return Path(data["data_dir"])

    return Path.home() / ".precifique" / "data"
