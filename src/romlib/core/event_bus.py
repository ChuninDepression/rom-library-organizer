"""Tiny synchronous pub/sub used between host and plugins."""
from __future__ import annotations

import logging
from collections import defaultdict
from collections.abc import Callable
from typing import Any

log = logging.getLogger("romlib.bus")

Handler = Callable[[str, dict[str, Any]], None]


class EventBus:
    def __init__(self) -> None:
        self._subs: dict[str, list[Handler]] = defaultdict(list)

    def subscribe(self, topic: str, handler: Handler) -> None:
        self._subs[topic].append(handler)

    def publish(self, topic: str, payload: dict[str, Any]) -> None:
        for handler in self._subs.get(topic, []):
            try:
                handler(topic, payload)
            except Exception:  # noqa: BLE001 — plugin bugs must not kill the host
                log.exception("handler for %s raised", topic)