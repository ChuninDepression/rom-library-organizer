"""Recursive library scanner. Emits scan.rom_found per ROM."""
from __future__ import annotations

import logging
import uuid
from pathlib import Path

from romlib.core.event_bus import EventBus
from romlib.contracts.plugin_api import RomRecord
from romlib.services.library_index import LibraryIndex
from romlib.utils.rom_naming import guess_system, strip_region_tags

log = logging.getLogger("romlib.scanner")

_ROM_EXT = {".nes", ".snes", ".sfc", ".gb", ".gbc", ".gba", ".n64", ".z64",
            ".md", ".gen", ".sms", ".gg", ".iso", ".bin", ".cue", ".chd",
            ".pbp", ".zip", ".7z"}


class Scanner:
    def __init__(self, index: LibraryIndex, bus: EventBus) -> None:
        self.index = index
        self.bus = bus

    def scan(self, root: Path) -> int:
        self.bus.publish("scan.started", {"root": str(root)})
        count = 0
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in _ROM_EXT:
                continue
            record = self._record(path)
            self.index.upsert(record)
            self.bus.publish("scan.rom_found", {"rom_id": record.rom_id, "path": str(path)})
            count += 1
        self.bus.publish("scan.finished", {"root": str(root), "count": count})
        return count

    def _record(self, path: Path) -> RomRecord:
        raw = path.stem
        return RomRecord(
            rom_id=uuid.uuid4().hex,
            path=path,
            system=guess_system(path),
            title_raw=raw,
            title_clean=strip_region_tags(raw),
            size_bytes=path.stat().st_size,
        )