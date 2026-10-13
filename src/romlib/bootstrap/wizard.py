"""First-run wizard and desktop UI bootstrap.

UI itself lives in an optional PySide6 dependency; if it's missing we fall
back to a Rich TUI so the tool is still usable headless.
"""
from __future__ import annotations

import logging
from pathlib import Path

from romlib.core.host import RomHost
from romlib.utils.config_loader import write_default_config

log = logging.getLogger("romlib.wizard")


def first_run(config_path: Path) -> None:
    log.info("first run — writing default config to %s", config_path)
    write_default_config(config_path)


def launch_ui(host: RomHost) -> None:
    try:
        from romlib.bootstrap.ui_desktop import run_desktop  # type: ignore[import-not-found]
    except ImportError:
        log.warning("PySide6 not installed — falling back to TUI")
        from romlib.bootstrap.ui_tui import run_tui
        run_tui(host)
    else:
        run_desktop(host)