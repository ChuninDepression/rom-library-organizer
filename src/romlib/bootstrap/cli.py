"""`romlib` command-line entry point.

Subcommands:
    scan      walk a library root and register ROMs
    organize  apply a layout rule to the registered library
    plugins   list / enable / disable / install plugins
    serve     launch the desktop UI (PySide6 optional dependency)
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from romlib.core.host import RomHost
from romlib.utils.logging import configure_logging

log = logging.getLogger("romlib.cli")


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="romlib", description="ROM library organizer")
    p.add_argument("--config", type=Path, default=None, help="Path to host.toml")
    p.add_argument("--verbose", "-v", action="count", default=0)
    sub = p.add_subparsers(dest="cmd", required=True)

    scan = sub.add_parser("scan", help="Scan a library root")
    scan.add_argument("root", type=Path)

    org = sub.add_parser("organize", help="Apply a layout rule")
    org.add_argument("--rule", default="NoIntro")
    org.add_argument("--dry-run", action="store_true")

    plug = sub.add_parser("plugins", help="Manage plugins")
    plug.add_argument("action", choices=["list", "enable", "disable", "install"])
    plug.add_argument("name", nargs="?")

    sub.add_parser("serve", help="Launch desktop UI")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    configure_logging(verbosity=args.verbose)

    host = RomHost.from_config(args.config) if args.config else RomHost.discover()
    host.start()

    try:
        if args.cmd == "scan":
            count = host.scan_library(args.root)
            log.info("registered %d roms under %s", count, args.root)
        elif args.cmd == "organize":
            moved = host.organize(rule=args.rule, dry_run=args.dry_run)
            log.info("organize: %d files %s", moved, "would move" if args.dry_run else "moved")
        elif args.cmd == "plugins":
            host.plugins.dispatch_cli(args.action, args.name)
        elif args.cmd == "serve":
            from romlib.bootstrap.wizard import launch_ui
            launch_ui(host)
    finally:
        host.stop()
    return 0


if __name__ == "__main__":
    sys.exit(main())