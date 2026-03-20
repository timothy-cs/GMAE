"""Observer Pattern — Non-security design pattern #2.

Provides an event system for the GMAE. Components can subscribe to events
(e.g., "turn_advanced", "item_collected", "player_damaged") and be notified
when they occur. This decouples game logic from UI updates, logging, and
achievement tracking.

Pattern roles:
  - EventSystem: the Subject that maintains subscribers and dispatches events.
  - Callable subscribers: Observers that react to published events.
"""

from __future__ import annotations
from collections import defaultdict
from typing import Callable, Any


class EventSystem:
    """Central pub/sub event bus for the GMAE."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable[..., None]]] = defaultdict(list)

    def subscribe(self, event_type: str, callback: Callable[..., None]) -> None:
        self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable[..., None]) -> None:
        if callback in self._subscribers[event_type]:
            self._subscribers[event_type].remove(callback)

    def publish(self, event_type: str, **kwargs: Any) -> None:
        for callback in self._subscribers[event_type]:
            callback(**kwargs)


# Global event system instance used across the GMAE
game_events = EventSystem()
