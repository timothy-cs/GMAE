"""PlayerProfile — GMAE Core.

Represents a player's persistent profile in the GuildQuest domain.
"""

from __future__ import annotations
import uuid
import re
from dataclasses import dataclass, field
from typing import Optional, List
from gmae.reused.ghalib.realm import Realm
from gmae.reused.ghalib.character import Character
from gmae.reused.ellis.settings import Settings


@dataclass
class PlayerProfile:
    display_name: str
    profile_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    preferred_realm: Optional[Realm] = None
    character: Optional[Character] = None
    quest_history: List[str] = field(default_factory=list)
    achievements: List[str] = field(default_factory=list)
    settings: Settings = field(default_factory=Settings)

    def update_history(self, quest_name: str) -> None:
        self.quest_history.append(quest_name)

    def add_achievement(self, achievement: str) -> None:
        if achievement not in self.achievements:
            self.achievements.append(achievement)

    def __str__(self) -> str:
        realm_name = self.preferred_realm.name if self.preferred_realm else "None"
        char_name = self.character.name if self.character else "None"
        return (f"[{self.display_name}] Character: {char_name}, "
                f"Realm: {realm_name}, Quests: {len(self.quest_history)}, "
                f"Achievements: {len(self.achievements)}")

    @staticmethod
    def sanitize_name(name: str) -> str:
        """Security: sanitize display names to prevent injection/invalid characters."""
        sanitized = re.sub(r'[^a-zA-Z0-9 _\-]', '', name)
        return sanitized[:30].strip() or "Adventurer"
