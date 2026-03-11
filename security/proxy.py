"""
PlayerProfileProxy — Protection Proxy (Security Pattern).

Wraps a User object and acts as the sole interface through which mini-adventures
and the engine interact with player profile data.

Security design rationale:
  - Mini-adventures receive PlayerProfileProxy instances, never raw User objects.
  - Read access is allowed freely (username, character name, role).
  - Write access is controlled: only safe append-style operations are exposed
    (record quest completion, award achievement, grant item).
  - Destructive operations (deleting history, changing role, removing characters)
    are simply absent from the proxy interface — mini-adventures cannot call them.
  - The underlying User is stored in a name-mangled private attribute (__user)
    to prevent accidental direct access even via attribute lookup.
  - get_user() is intentionally NOT exposed to mini-adventures; it is called only
    by GMAE_Engine internally (documented clearly).

Used by : GMAE_Engine (wraps all User objects on add_player()),
          IMiniAdventure implementations (receive proxies as player list)
"""

from __future__ import annotations
from typing import Optional
from core.user import User
from core.inventory import Item


class PlayerProfileProxy:
    """
    Protection Proxy for the User/PlayerProfile.

    Exposes only safe read and controlled write operations.
    Mini-adventures interact with players exclusively through this class.
    """

    def __init__(self, user: User) -> None:
        # Name-mangled: inaccessible as proxy.__user from outside the class
        self.__user = user

    # ------------------------------------------------------------------
    # Read-only access (safe to expose to mini-adventures)
    # ------------------------------------------------------------------

    def get_username(self) -> str:
        return self.__user.username

    def get_user_id(self) -> str:
        return self.__user.user_id

    def get_role(self) -> str:
        return self.__user.role

    def get_character_name(self) -> Optional[str]:
        if self.__user.active_character:
            return self.__user.active_character.name
        return None

    def get_character_class(self) -> Optional[str]:
        if self.__user.active_character:
            return self.__user.active_character.class_type
        return None

    def get_character_level(self) -> Optional[int]:
        if self.__user.active_character:
            return self.__user.active_character.level
        return None

    def get_profile_summary(self) -> str:
        return self.__user.get_profile_summary()

    # Expose user_id as a property so adventures can use proxy.user_id
    @property
    def user_id(self) -> str:
        return self.__user.user_id

    @property
    def username(self) -> str:
        return self.__user.username

    # ------------------------------------------------------------------
    # Controlled write operations (append-only / non-destructive)
    # ------------------------------------------------------------------

    def record_quest_completion(self, quest_name: str) -> None:
        """Appends to quest history. Does not allow removal or editing."""
        self.__user.history.add_completed_quest(quest_name)

    def award_achievement(self, achievement: str) -> None:
        """Appends an achievement. Does not allow removal or editing."""
        self.__user.history.add_achievement(achievement)

    def grant_item_to_character(self, item: Item) -> bool:
        """
        Adds an item to the active character's inventory.
        Returns False if no active character is set.
        """
        if self.__user.active_character:
            self.__user.active_character.gain_item(item)
            return True
        return False

    # ------------------------------------------------------------------
    # Engine-internal access — NOT part of the mini-adventure API
    # ------------------------------------------------------------------

    def get_user(self) -> User:
        """
        Returns the underlying User object.

        INTERNAL ENGINE USE ONLY. This method must not be called from
        mini-adventure code. Mini-adventures only receive proxies.
        """
        return self.__user

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        return f"PlayerProfileProxy({self.__user.username})"

    def __repr__(self) -> str:
        return f"PlayerProfileProxy(user_id={self.__user.user_id!r})"
