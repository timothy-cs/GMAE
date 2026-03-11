"""
Character — GuildQuest domain model (Reused from GuildQuest Part 1).

Represents a player-owned character with a class, level, and inventory.

Reuse source : Ethan Votran — GuildQuest Part 1
Used by      : User (active_character), PlayerProfileProxy (item grants)
"""

from __future__ import annotations
from core.inventory import Inventory, Item

CLASS_TYPES: list[str] = ["Warrior", "Mage", "Rogue", "Ranger", "Cleric"]


class Character:
    """A playable character belonging to a User."""

    def __init__(
        self,
        name: str,
        class_type: str = "Warrior",
        level: int = 1,
    ) -> None:
        if class_type not in CLASS_TYPES:
            raise ValueError(
                f"Invalid class '{class_type}'. Choose from: {CLASS_TYPES}"
            )
        self.name = name
        self.class_type = class_type
        self.level = level
        self.inventory = Inventory()

    # ------------------------------------------------------------------
    # Inventory helpers
    # ------------------------------------------------------------------

    def gain_item(self, item: Item) -> None:
        self.inventory.add_item(item)

    def lose_item(self, item: Item) -> bool:
        return self.inventory.remove_item(item)

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        return f"{self.name} (Lvl {self.level} {self.class_type})"

    def __repr__(self) -> str:
        return f"Character(name={self.name!r}, class={self.class_type!r}, level={self.level})"
