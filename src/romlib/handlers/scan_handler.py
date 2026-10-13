"""Bridges on_scan / on_rom_found hooks between scanner and plugins."""
from __future__ import annotations

import logging
from typing import Any

from romlib.contracts.plugin_api import HookPoint
from romlib.core.event_bus import EventBus
from romlib.services.plugin_registry import PluginRegistry

log = logging.getLogger("romlib.handler.scan")


class ScanHandler:
    def __init__(self, registry: PluginRegistry, bus: EventBus) -> None:
        self.registry = registry
        self.bus = bus
        bus.subscribe("scan.started", self._on_started)
        bus.subscribe("scan.rom_found", self._on_rom_found)

    def _on_started(self, _topic: str, payload: dict[str, Any]) -> None:
        self._dispatch(HookPoint.ON_SCAN, payload)

    def _on_rom_found(self, _topic: str, payload: dict[str, Any]) -> None:
        self._dispatch(HookPoint.ON_ROM_FOUND, payload)

    def _dispatch(self, hook: HookPoint, payload: dict[str, Any]) -> None:
        for plugin in self.registry.plugins_for(hook):
            try:
                plugin.handle(hook, payload)
            except Exception:  # noqa: BLE001
                log.exception("plugin %s failed in %s", plugin.manifest.name, hook)