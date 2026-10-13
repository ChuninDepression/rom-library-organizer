"""In-memory registry of loaded plugins + hook index."""
from __future__ import annotations

import logging
from collections import defaultdict
from collections.abc import Iterator
from pathlib import Path

from romlib.contracts.plugin_api import HookPoint, RomPlugin

log = logging.getLogger("romlib.registry")


class PluginRegistry:
    def __init__(self, plugin_dirs: list[Path]) -> None:
        self.plugin_dirs = plugin_dirs
        self._by_name: dict[str, RomPlugin] = {}
        self._by_hook: dict[HookPoint, list[RomPlugin]] = defaultdict(list)

    def __len__(self) -> int:
        return len(self._by_name)

    def add(self, plugin: RomPlugin) -> None:
        name = plugin.manifest.name
        self._by_name[name] = plugin
        for hook in plugin.hooks:
            self._by_hook[hook].append(plugin)

    def plugins_for(self, hook: HookPoint) -> list[RomPlugin]:
        return list(self._by_hook.get(hook, ()))

    def iter_plugin_dirs(self) -> Iterator[Path]:
        for base in self.plugin_dirs:
            if not base.is_dir():
                continue
            for child in sorted(base.iterdir()):
                if child.is_dir() and (child / "manifest.toml").exists():
                    yield child

    def dispatch_cli(self, action: str, name: str | None) -> None:
        if action == "list":
            for plugin in self._by_name.values():
                m = plugin.manifest
                print(f"{m.name:<24} {m.version:<10} {m.description}")
            return
        if name is None:
            log.error("%s needs a plugin name", action)
            return
        plugin = self._by_name.get(name)
        if plugin is None:
            log.error("no such plugin: %s", name)
            return
        log.info("%s: %s (config-only in 0.6)", action, name)