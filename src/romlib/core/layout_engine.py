"""Applies a naming layout to the library index.

Layouts are registered by plugins (see `plugins/layout_nointro/`). The
engine walks the index, asks the active layout for a target path, and
moves the file if it's safe.
"""
from __future__ import annotations

import logging
import shutil
from pathlib import Path

from romlib.core.event_bus import EventBus
from romlib.services.library_index import LibraryIndex

log = logging.getLogger("romlib.layout")


class LayoutEngine:
    def __init__(self, index: LibraryIndex, bus: EventBus) -> None:
        self.index = index
        self.bus = bus
        self._layouts: dict[str, "LayoutRule"] = {}

    def register(self, rule: "LayoutRule") -> None:
        self._layouts[rule.name] = rule

    def apply(self, rule_name: str, dry_run: bool = False) -> int:
        rule = self._layouts.get(rule_name)
        if rule is None:
            raise KeyError(f"unknown layout rule: {rule_name!r}")

        moved = 0
        for entry in self.index.iter_roms():
            target = rule.target_path(entry)
            if target == entry.path:
                continue
            if dry_run:
                log.info("[dry] %s -> %s", entry.path, target)
                moved += 1
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(entry.path), str(target))
            self.index.update_path(entry.rom_id, target)
            self.bus.publish("rom.moved", {"rom_id": entry.rom_id, "to": target})
            moved += 1
        return moved


class LayoutRule:
    """Contract implemented by layout plugins."""

    name: str = "unnamed"

    def target_path(self, entry: object) -> Path:
        raise NotImplementedError