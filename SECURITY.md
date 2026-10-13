# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.6.x   | ✅        |
| 0.5.x   | ⚠️ critical fixes only |
| < 0.5   | ❌        |

## Reporting a vulnerability

Email `security@rom-library-organizer.dev` (PGP key in `docs/pgp.txt` in
release tarballs). Do **not** open a public issue for anything that could
let a malicious plugin escape the sandbox.

## Threat model

The host is a **plugin host**. Plugins are untrusted code by default.

- Plugins run in-process. There is no OS-level sandbox yet (tracked in
  `#418`, milestone 0.7). Until then, only install plugins you trust.
- Plugin signatures are checked if `[signing] enforce = true` in
  `config/host.toml`. Unsigned plugins still load but log a warning.
- The ROM library directory is opened read-only unless a plugin declares
  `writes_rom_files = true` in its manifest AND the user has flipped
  `library.allow_writes = true` in config.

## In scope

- Path traversal in the importer / exporter plugins.
- Manifest parser crashes on malformed `manifest.toml`.
- Signature bypass in `romlib.services.plugin_registry`.
- Anything that lets a plugin read outside its declared `scopes`.

## Out of scope

- Users installing a plugin from a random pastebin. That's on them.
- Detection of your ROM files by third-party anti-tamper. We don't do
  that. We organize.

## Disclosure

90-day coordinated disclosure. We'll credit you in the release notes
unless you ask us not to.