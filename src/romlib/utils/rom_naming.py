"""Heuristics for system detection and cleaning No-Intro style titles."""
from __future__ import annotations

import re
from pathlib import Path

_REGION = re.compile(r"\s*\((USA|Europe|Japan|World|Rev \d+|Beta|Proto)[^)]*\)")
_EXT_SYSTEM = {
    ".nes": "nes", ".snes": "snes", ".sfc": "snes",
    ".gb": "gb", ".gbc": "gbc", ".gba": "gba",
    ".n64": "n64", ".z64": "n64",
    ".md": "genesis", ".gen": "genesis",
    ".sms": "sms", ".gg": "gg",
    ".iso": "disc", ".bin": "disc", ".cue": "disc",
    ".chd": "disc", ".pbp": "disc",
}


def guess_system(path: Path) -> str:
    return _EXT_SYSTEM.get(path.suffix.lower(), "unknown")


def strip_region_tags(title: str) -> str:
    return _REGION.sub("", title).strip()