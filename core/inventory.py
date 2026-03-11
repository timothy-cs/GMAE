"""
Inventory & Item — GuildQuest subsystem (Reused from GuildQuest Part 1).

Provides item representation and per-character inventory management.

Reuse source : Ethan Votran — GuildQuest Part 1
Used by      : Character, PlayerProfileProxy (grant_item_to_character)
"""

from __future__ import annotations
from typing import List, Optional


class Item:
    """A single item in the GuildQuest world."""

    def __init__(
        self,
        item_id: str,
        name: str,
        rarity: str = "common",
        item_type: str = "misc",
        description: str = "",
    ) -> None:
        self.item_id = item_id
        self.name = name
        self.rarity = rarity
        self.item_type = item_type
        self.description = description

    def __str__(self) -> str:
        return f"{self.name} [{self.rarity}]"

    def __repr__(self) -> str:
        return f"Item(item_id={self.item_id!r}, name={self.name!r})"


class Inventory:
    """Holds a character's collection of items."""

    def __init__(self) -> None:
        self._items: List[Item] = []

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def add_item(self, item: Item) -> None:
        self._items.append(item)

    def remove_item(self, item: Item) -> bool:
        if item in self._items:
            self._items.remove(item)
            return True
        return False

    def remove_item_by_id(self, item_id: str) -> Optional[Item]:
        for item in self._items:
            if item.item_id == item_id:
                self._items.remove(item)
                return item
        return None

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_item_by_id(self, item_id: str) -> Optional[Item]:
        for item in self._items:
            if item.item_id == item_id:
                return item
        return None

    @property
    def items(self) -> List[Item]:
        return list(self._items)

    def __len__(self) -> int:
        return len(self._items)

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        if not self._items:
            return "  (empty)"
        return "\n  ".join(str(i) for i in self._items)
