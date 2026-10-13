"""Stable plugin API surface. Bump `API_VERSION` on breaking changes."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

API_VERSION = "0.6"


class HookPoint(str, Enum):
    ON_SCAN = "on_scan"
    ON_ROM_FOUND = "on_rom_found"
    ON_ROM_MOVED = "on_rom_moved"
    PROVIDE_LAYOUT = "provide_layout"
    PROVIDE_METADATA = "provide_metadata"


@dataclass(slots=True)
class RomRecord:
    rom_id: str
    path: Path
    system: str
    title_raw: str
    title_clean: str | None = None
    size_bytes: int = 0
    crc32: str | None = None
    xxh3: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PluginManifest:
    name: str
    version: str
    api_version: str
    entry: str
    description: str = ""
    scopes: list[str] = field(default_factory=list)
    writes_rom_files: bool = False
    telemetry: bool = False


@dataclass(slots=True)
class PluginContext:
    """Everything a plugin is allowed to touch."""

    config: Any
    bus_publish: Any
    index_query: Any
    logger_name: str

    def log(self, msg: str, *args: Any) -> None:
        import logging
        logging.getLogger(self.logger_name).info(msg, *args)


@runtime_checkable
class RomPlugin(Protocol):
    manifest: PluginManifest
    hooks: set[HookPoint]

    def on_load(self, ctx: PluginContext) -> None: ...
    def on_unload(self) -> None: ...
    def handle(self, hook: HookPoint, payload: dict[str, Any]) -> dict[str, Any] | None: ...