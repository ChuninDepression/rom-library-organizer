"""Routes PROVIDE_METADATA hooks; collects the first non-None result."""
from __future__ import annotations

import logging
from typing import Any

from romlib.contracts.plugin_api import HookPoint
from romlib.services.plugin_registry import PluginRegistry

log = logging.getLogger("romlib.handler.metadata")


class MetadataHandler:
    def __init__(self, registry: PluginRegistry) -> None:
        self.registry = registry

    def enrich(self, payload: dict[str, Any]) -> dict[str, Any]:
        enriched = dict(payload)
        for plugin in self.registry.plugins_for(HookPoint.PROVIDE_METADATA):
            try:
                result = plugin.handle(HookPoint.PROVIDE_METADATA, enriched)
            except Exception:  # noqa: BLE001
                log.exception("metadata plugin %s failed", plugin.manifest.name)
                continue
            if result:
                enriched.update(result)
        return enriched