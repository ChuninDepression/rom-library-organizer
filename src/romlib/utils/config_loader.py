"""Load / write host.toml. Falls back to defaults on missing file."""
from __future__ import annotations

import logging
import tomllib
from pathlib import Path

import tomli_w

from romlib.models.host_config import HostConfig

log = logging.getLogger("romlib.config")

DEFAULT_PATH = Path.home() / ".romlib" / "host.toml"


def load_config(path: Path) -> HostConfig:
    if not path.exists():
        log.warning("config %s missing — using defaults", path)
        return HostConfig()
    with path.open("rb") as fh:
        data = tomllib.load(fh)
    return HostConfig.model_validate(data)


def load_or_default() -> HostConfig:
    return load_config(DEFAULT_PATH)


def write_default_config(path: Path = DEFAULT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = HostConfig().model_dump(mode="json")
    with path.open("wb") as fh:
        tomli_w.dump(data, fh)
    log.info("wrote default config to %s", path)