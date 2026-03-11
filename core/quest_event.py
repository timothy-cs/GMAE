"""
QuestEvent — GuildQuest subsystem (Reused from GuildQuest Part 1).

An event within a quest that has a name, time window, realm reference, and
a list of observer callbacks that fire when the event triggers.

Observer Pattern (Non-Security):
  QuestEvent is the Subject. Observers (callables) are registered via
  add_observer() and notified automatically when check_triggers() fires.
  This decouples game logic (e.g., UI updates, hazard spawns) from time checks.

Reuse source : Ethan Votran — GuildQuest Part 1
Used by      : QuestEventAdapter, EscortQuest (midpoint warning event)
"""

from __future__ import annotations
from typing import Callable, List, Optional
from core.world_clock import WorldClock


class QuestEvent:
    """
    A timed event in the GuildQuest world.

    Fires observer callbacks when the current WorldClock time enters the
    event's [start_time, end_time] window for the first time.
    """

    def __init__(
        self,
        event_id: str,
        name: str,
        start_time: WorldClock,
        end_time: Optional[WorldClock] = None,
        realm=None,
    ) -> None:
        self.event_id = event_id
        self.name = name
        self.start_time: WorldClock = start_time
        self.end_time: Optional[WorldClock] = end_time
        self.realm = realm

        self._observers: List[Callable[["QuestEvent"], None]] = []
        self._triggered: bool = False

    # ------------------------------------------------------------------
    # Observer Pattern — Subject interface
    # ------------------------------------------------------------------

    def add_observer(self, callback: Callable[["QuestEvent"], None]) -> None:
        """Register a callable to be notified when this event triggers."""
        if callback not in self._observers:
            self._observers.append(callback)

    def remove_observer(self, callback: Callable[["QuestEvent"], None]) -> None:
        if callback in self._observers:
            self._observers.remove(callback)

    def _notify_observers(self) -> None:
        for observer in self._observers:
            observer(self)

    # ------------------------------------------------------------------
    # Trigger logic
    # ------------------------------------------------------------------

    def check_triggers(self, current_time: WorldClock) -> bool:
        """
        Return True and notify observers if current_time is within the event
        window and the event has not yet fired. Idempotent after first trigger.
        """
        if self._triggered:
            return False
        in_window = current_time >= self.start_time
        if self.end_time is not None:
            in_window = in_window and current_time <= self.end_time
        if in_window:
            self._triggered = True
            self._notify_observers()
            return True
        return False

    def reset(self) -> None:
        """Allow the event to trigger again (e.g., on adventure reset)."""
        self._triggered = False

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        realm_name = self.realm.name if self.realm else "Unknown"
        end_str = f" → {self.end_time}" if self.end_time else ""
        return f"[{self.event_id}] {self.name} @ {self.start_time}{end_str} in {realm_name}"

    def __repr__(self) -> str:
        return f"QuestEvent(event_id={self.event_id!r}, name={self.name!r})"
