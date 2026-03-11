"""
QuestEventAdapter — Adapter Pattern (Non-Security).

Wraps the GuildQuest QuestEvent subsystem and exposes a simplified interface
for use inside GMAE mini-adventures.

  Adaptee : core.quest_event.QuestEvent  (GuildQuest Part 1 subsystem)
  Target  : Lightweight event-polling/subscription interface for adventures

Why an adapter?
  QuestEvent was designed for campaign management (start/end absolute times
  relative to a persisted WorldClock). Inside a mini-adventure we deal with
  turn-relative times and need convenient factory creation, clean
  subscribe/unsubscribe naming, and is_active() window queries. The adapter
  adds those without touching the original class.

Reuse source : Ethan Votran — GuildQuest Part 1 (core.quest_event.QuestEvent)
Used by      : EscortQuest (midpoint warning), RelicHunt (extensible hooks)
"""

from __future__ import annotations
from typing import Callable, Optional
from core.quest_event import QuestEvent
from core.world_clock import WorldClock


class QuestEventAdapter:
    """
    Adapter around QuestEvent for use in GMAE mini-adventures.

    Exposes the Observer subscription interface with cleaner names and adds
    convenience helpers (is_active, poll, factory create).
    """

    def __init__(self, quest_event: QuestEvent) -> None:
        self._event = quest_event

    # ------------------------------------------------------------------
    # Delegation — read-only properties
    # ------------------------------------------------------------------

    @property
    def event_id(self) -> str:
        return self._event.event_id

    @property
    def name(self) -> str:
        return self._event.name

    @property
    def start_time(self) -> WorldClock:
        return self._event.start_time

    @property
    def end_time(self) -> Optional[WorldClock]:
        return self._event.end_time

    # ------------------------------------------------------------------
    # Observer Pattern — clean subscribe/unsubscribe API
    # ------------------------------------------------------------------

    def subscribe(self, callback: Callable[[QuestEvent], None]) -> None:
        """Register a callback to be notified when this event triggers."""
        self._event.add_observer(callback)

    def unsubscribe(self, callback: Callable[[QuestEvent], None]) -> None:
        self._event.remove_observer(callback)

    # ------------------------------------------------------------------
    # Extended helpers
    # ------------------------------------------------------------------

    def poll(self, current_time: WorldClock) -> bool:
        """
        Check whether this event fires at current_time.
        Delegates to QuestEvent.check_triggers() which notifies observers.
        """
        return self._event.check_triggers(current_time)

    def is_active(self, current_time: WorldClock) -> bool:
        """Return True if current_time is within [start_time, end_time]."""
        if current_time < self._event.start_time:
            return False
        if self._event.end_time is not None and current_time > self._event.end_time:
            return False
        return True

    def reset(self) -> None:
        """Allow the event to fire again (used on adventure reset)."""
        self._event.reset()

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def create(
        cls,
        event_id: str,
        name: str,
        start_minutes: int,
        end_minutes: Optional[int] = None,
        realm=None,
    ) -> "QuestEventAdapter":
        """Create a QuestEventAdapter directly from plain parameters."""
        start = WorldClock(start_minutes)
        end = WorldClock(end_minutes) if end_minutes is not None else None
        event = QuestEvent(event_id, name, start, end, realm)
        return cls(event)

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        return str(self._event)

    def __repr__(self) -> str:
        return f"QuestEventAdapter(event={self._event!r})"
