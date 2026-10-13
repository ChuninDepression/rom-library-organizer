"""SQLite-backed ROM index. Thread-safe via a single connection + lock."""
from __future__ import annotations

import logging
import sqlite3
import threading
from collections.abc import Iterator
from pathlib import Path

from romlib.contracts.plugin_api import RomRecord

log = logging.getLogger("romlib.index")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS roms (
    rom_id      TEXT PRIMARY KEY,
    path        TEXT NOT NULL UNIQUE,
    system      TEXT NOT NULL,
    title_raw   TEXT NOT NULL,
    title_clean TEXT,
    size_bytes  INTEGER NOT NULL DEFAULT 0,
    crc32       TEXT,
    xxh3        TEXT
);
CREATE INDEX IF NOT EXISTS idx_roms_system ON roms(system);
CREATE INDEX IF NOT EXISTS idx_roms_title  ON roms(title_clean);
"""


class LibraryIndex:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._conn: sqlite3.Connection | None = None
        self._lock = threading.RLock()

    def open(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def upsert(self, record: RomRecord) -> None:
        assert self._conn is not None
        with self._lock:
            self._conn.execute(
                """INSERT INTO roms (rom_id, path, system, title_raw, title_clean,
                                    size_bytes, crc32, xxh3)
                   VALUES (?,?,?,?,?,?,?,?)
                   ON CONFLICT(rom_id) DO UPDATE SET
                       path=excluded.path, title_clean=excluded.title_clean,
                       size_bytes=excluded.size_bytes, crc32=excluded.crc32,
                       xxh3=excluded.xxh3""",
                (
                    record.rom_id, str(record.path), record.system, record.title_raw,
                    record.title_clean, record.size_bytes, record.crc32, record.xxh3,
                ),
            )
            self._conn.commit()

    def update_path(self, rom_id: str, new_path: Path) -> None:
        assert self._conn is not None
        with self._lock:
            self._conn.execute("UPDATE roms SET path=? WHERE rom_id=?", (str(new_path), rom_id))
            self._conn.commit()

    def iter_roms(self) -> Iterator[RomRecord]:
        assert self._conn is not None
        with self._lock:
            cur = self._conn.execute(
                "SELECT rom_id, path, system, title_raw, title_clean, size_bytes, crc32, xxh3 FROM roms"
            )
            rows = cur.fetchall()
        for row in rows:
            yield RomRecord(
                rom_id=row[0], path=Path(row[1]), system=row[2], title_raw=row[3],
                title_clean=row[4], size_bytes=row[5], crc32=row[6], xxh3=row[7],
            )