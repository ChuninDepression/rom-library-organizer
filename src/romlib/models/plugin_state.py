"""Per-plugin state persisted between sessions."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class PluginState(BaseModel):
    name: str
    enabled: bool = True
    last_loaded: datetime | None = None
    error_count: int = 0
    notes: dict[str, str] = Field(default_factory=dict)