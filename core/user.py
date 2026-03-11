"""
User (PlayerProfile) — GuildQuest domain model.

Represents a player account with GuildQuest-domain data: active character,
quest history, achievements, and display preferences.

This class is the underlying data object. In the GMAE it is always accessed
through a PlayerProfileProxy (see security/proxy.py) so that mini-adventures
cannot directly mutate profile state.
"""

from __future__ import annotations
from typing import List, Optional
from core.character import Character, CLASS_TYPES


class Settings:
    """User display and gameplay preferences."""

    def __init__(self) -> None:
        self.current_realm_id: Optional[str] = None
        self.theme: str = "classic"
        self.time_display: str = "world"  # "world" | "local" | "both"


class QuestHistory:
    """Tracks completed quests and earned achievements for a User."""

    def __init__(self) -> None:
        self.completed_quests: List[str] = []
        self.achievements: List[str] = []

    def add_completed_quest(self, quest_name: str) -> None:
        if quest_name not in self.completed_quests:
            self.completed_quests.append(quest_name)

    def add_achievement(self, achievement: str) -> None:
        if achievement not in self.achievements:
            self.achievements.append(achievement)


class User:
    """
    Player profile in the GMAE.

    Meaningfully connected to the GuildQuest domain via:
      - active_character  : the character they are playing as
      - history           : completed quests and achievements
      - preferences       : realm, theme, time-display settings
      - role              : used by RBACService for permission checks
    """

    def __init__(
        self,
        user_id: str,
        username: str,
        role: str = "hero",
    ) -> None:
        self.user_id = user_id
        self.username = username
        self.role = role  # "guest" | "hero" — consumed by RBACService
        self.active_character: Optional[Character] = None
        self.characters: List[Character] = []
        self.preferences = Settings()
        self.history = QuestHistory()

    # ------------------------------------------------------------------
    # Character management
    # ------------------------------------------------------------------

    def create_character(
        self,
        name: str,
        class_type: str = "Warrior",
        level: int = 1,
    ) -> Character:
        char = Character(name, class_type, level)
        self.characters.append(char)
        if self.active_character is None:
            self.active_character = char
        return char

    def set_active_character(self, name: str) -> bool:
        for char in self.characters:
            if char.name == name:
                self.active_character = char
                return True
        return False

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def get_profile_summary(self) -> str:
        char_str = (
            str(self.active_character)
            if self.active_character
            else "No character selected"
        )
        return (
            f"User     : {self.username}  [{self.role.upper()}]\n"
            f"Character: {char_str}\n"
            f"Quests   : {len(self.history.completed_quests)} completed\n"
            f"Achievements: {len(self.history.achievements)}"
        )

    def __str__(self) -> str:
        return f"{self.username} ({self.role})"

    def __repr__(self) -> str:
        return f"User(user_id={self.user_id!r}, username={self.username!r})"
