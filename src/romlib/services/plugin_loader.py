"""Discovers plugin folders, reads manifests, imports entry modules."""
from __future__ import annotations

import importlib.util
import logging
import sys
from pathlib import Path

from romlib.contracts.plugin_api import API_VERSION, PluginContext, RomPlugin
from romlib.models.host_config import HostConfig
from romlib.services.plugin_registry import PluginRegistry
from romlib.core.event_bus import EventBus
from romlib.utils.manifest_parser import load_manifest

log = logging.getLogger("romlib.loader")


class PluginLoader:
    def __init__(self, registry: PluginRegistry, bus: EventBus, config: HostConfig) -> None:
        self.registry = registry
        self.bus = bus
        self.config = config
        self._loaded: list[RomPlugin] = []

    def load_all(self) -> None:
        for plugin_dir in self.registry.iter_plugin_dirs():
            try:
                self._load_one(plugin_dir)
            except Exception:  # noqa: BLE001
                log.exception("failed to load plugin at %s", plugin_dir)

    def _load_one(self, plugin_dir: Path) -> None:
        manifest_path = plugin_dir / "manifest.toml"
        if not manifest_path.exists():
            log.warning("no manifest.toml in %s — skipping", plugin_dir)
            return
        manifest = load_manifest(manifest_path)
        if manifest.api_version != API_VERSION:
            log.error("plugin %s wants api %s, host is %s — skipping",
                      manifest.name, manifest.api_version, API_VERSION)
            return

        entry_path = plugin_dir / manifest.entry
        spec = importlib.util.spec_from_file_location(f"romlib_plugin_{manifest.name}", entry_path)
        if spec is None or spec.loader is None:
            log.error("cannot import %s", entry_path)
            return
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

        plugin: RomPlugin = module.PLUGIN
        ctx = PluginContext(
            config=self.config,
            bus_publish=self.bus.publish,
            index_query=None,
            logger_name=f"romlib.plugin.{manifest.name}",
        )
        plugin.on_load(ctx)
        self.registry.add(plugin)
        self._loaded.append(plugin)

    def unload_all(self) -> None:
        for plugin in reversed(self._loaded):
            try:
                plugin.on_unload()
            except Exception:  # noqa: BLE001
                log.exception("plugin %s failed to unload", plugin.manifest.name)
        self._loaded.clear()