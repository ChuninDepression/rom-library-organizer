"""RomHost — the plugin host process.

Owns:
    - config (host.toml)
    - the plugin registry + loader
    - the library index (SQLite)
    - the scanner / organizer services

Lifecycle: discover() -> start() -> ... -> stop()
"""
from __future__ import annotations

import logging
from pathlib import Path

from romlib.core.event_bus import EventBus
from romlib.core.layout_engine import LayoutEngine
from romlib.models.host_config import HostConfig
from romlib.services.library_index import LibraryIndex
from romlib.services.plugin_loader import PluginLoader
from romlib.services.plugin_registry import PluginRegistry
from romlib.services.scanner import Scanner

log = logging.getLogger("romlib.host")


class RomHost:
    def __init__(self, config: HostConfig) -> None:
        self.config = config
        self.bus = EventBus()
        self.index = LibraryIndex(config.library.db_path)
        self.registry = PluginRegistry(config.plugins.dirs)
        self.loader = PluginLoader(self.registry, self.bus, config)
        self.scanner = Scanner(self.index, self.bus)
        self.layout = LayoutEngine(self.index, self.bus)
        self._started = False

    @classmethod
    def discover(cls) -> "RomHost":
        from romlib.utils.config_loader import load_or_default
        return cls(load_or_default())

    @classmethod
    def from_config(cls, path: Path) -> "RomHost":
        from romlib.utils.config_loader import load_config
        return cls(load_config(path))

    @property
    def plugins(self) -> PluginRegistry:
        return self.registry

    def start(self) -> None:
        if self._started:
            return
        self.index.open()
        self.loader.load_all()
        self.bus.publish("host.started", {"plugins": len(self.registry)})
        self._started = True
        log.info("host started with %d plugins", len(self.registry))

    def stop(self) -> None:
        if not self._started:
            return
        self.bus.publish("host.stopping", {})
        self.loader.unload_all()
        self.index.close()
        self._started = False

    def scan_library(self, root: Path) -> int:
        return self.scanner.scan(root)

    def organize(self, rule: str, dry_run: bool = False) -> int:
        return self.layout.apply(rule, dry_run=dry_run)