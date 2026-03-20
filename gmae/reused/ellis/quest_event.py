"""QuestEvent model — reused from Ellis's individual GuildQuest assignment.

Represents quest events with time windows and realm assignments.
Adapted for GMAE: used to track adventure objectives and timed events.
"""

from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from typing import List, Optional
from gmae.reused.ellis.world_time import WorldTime
from gmae.reused.ghalib.realm import Realm
from gmae.reused.ghalib.character import Character


@dataclass
class QuestEvent:
    title: str
    start_time: WorldTime
    end_time: WorldTime
    event_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    realm: Optional[Realm] = None
    participants: List[Character] = field(default_factory=list)
    completed: bool = False

    def assign_realm(self, realm: Realm) -> None:
        self.realm = realm

    def add_participant(self, character: Character) -> None:
        if character not in self.participants:
            self.participants.append(character)

    def is_active(self, current_time: WorldTime) -> bool:
        return self.start_time <= current_time <= self.end_time

    def mark_completed(self) -> None:
        self.completed = True

    def time_remaining(self, current_time: WorldTime) -> int:
        if current_time.to_total_minutes() >= self.end_time.to_total_minutes():
            return 0
        return self.end_time.to_total_minutes() - current_time.to_total_minutes()

    def __str__(self) -> str:
        status = "DONE" if self.completed else "ACTIVE"
        realm_name = self.realm.name if self.realm else "Unassigned"
        return f"[{status}] {self.title} in {realm_name} ({self.start_time} - {self.end_time})"
