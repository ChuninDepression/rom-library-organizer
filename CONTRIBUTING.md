# Contributing to rom-library-organizer

Thanks for wanting to help tidy up the shelf. This project is a plugin-host
ROM manager for Windows — the host is thin, the plugins do the heavy lifting.

## Ground rules

- Python 3.11+ on Windows 10/11. Linux/macOS run in "degraded" mode (no
  shell integration, no drive watcher).
- Every new capability lands as a **plugin**, not as a fork of the host.
- Plugins talk to the host through `romlib.contracts` only. No direct
  imports of `romlib.core.*` from a plugin — that's a hard rule, PRs that
  break it get bounced with a link to this paragraph.
- Type hints required on every public function. `mypy --strict` runs in CI.

## Plugin layout

```
plugins/
  <plugin_name>/
    __init__.py
    plugin.py         # subclass of RomPlugin
    manifest.toml     # name, version, api_version, entry
```

See `plugins/scraper_screenScraper/` for a reference implementation.

## Local dev

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pre-commit install
pytest -q
```

## Commit style

Conventional commits. `feat(scraper): add screenscraper plugin`,
`fix(loader): handle missing manifest.toml gracefully`, etc.

## What we merge

- New plugins (scrapers, hashers, importers, exporters, launchers).
- Host fixes that keep the API stable.
- Tests. If your PR adds a plugin without a test, it gets bounced.

## What we don't merge

- Anything that mutates a user's ROM files in place without an explicit
  `--allow-destructive` flag. The library is sacred.
- Anything that phones home. Plugin telemetry is opt-in per plugin, off by
  default, and must be declared in `manifest.toml`.

## Code of conduct

Be decent. We're all here for the same reason — the shelf got out of hand.