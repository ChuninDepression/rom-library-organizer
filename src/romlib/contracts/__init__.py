"""Shared contracts between host and plugins.

Plugins import from here — never from `romlib.core.*`.
"""
from romlib.contracts.plugin_api import (
    HookPoint,
    PluginContext,
    PluginManifest,
    RomPlugin,
    RomRecord,
)

__all__ = ["HookPoint", "PluginContext", "PluginManifest", "RomPlugin", "RomRecord"]