"""Parse a plugin's manifest.toml into a PluginManifest."""
from __future__ import annotations

import tomllib
from pathlib import Path

from romlib.contracts.plugin_api import PluginManifest


class ManifestError(ValueError):
    """Raised on malformed manifest.toml."""


def load_manifest(path: Path) -> PluginManifest:
    try:
        with path.open("rb") as fh:
            data = tomllib.load(fh)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ManifestError(f"cannot parse {path}: {exc}") from exc

    try:
        return PluginManifest(
            name=data["name"],
            version=data["version"],
            api_version=data["api_version"],
            entry=data["entry"],
            description=data.get("description", ""),
            scopes=list(data.get("scopes", [])),
            writes_rom_files=bool(data.get("writes_rom_files", False)),
            telemetry=bool(data.get("telemetry", False)),
        )
    except KeyError as exc:
        raise ManifestError(f"{path}: missing key {exc}") from exc