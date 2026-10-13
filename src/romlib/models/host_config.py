"""Host configuration model. Loaded from host.toml."""
from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class LibraryConfig(BaseModel):
    root: Path = Path.home() / "ROMs"
    db_path: Path = Path.home() / ".romlib" / "rom-library.db"
    allow_writes: bool = False


class PluginsConfig(BaseModel):
    dirs: list[Path] = Field(default_factory=lambda: [Path.home() / ".romlib" / "plugins"])
    autoload: bool = True


class SigningConfig(BaseModel):
    enforce: bool = False
    trusted_keys: list[str] = Field(default_factory=list)


class HostConfig(BaseModel):
    library: LibraryConfig = Field(default_factory=LibraryConfig)
    plugins: PluginsConfig = Field(default_factory=PluginsConfig)
    signing: SigningConfig = Field(default_factory=SigningConfig)
    log_level: str = "INFO"