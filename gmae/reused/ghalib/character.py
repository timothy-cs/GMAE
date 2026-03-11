"""Character model — reused from Ghalib's individual GuildQuest assignment.

Represents a character (player-controlled or NPC) in the GuildQuest world.
Adapted for GMAE: added health, position tracking, and movement helpers.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from gmae.reused.ghalib.inventory import InventoryEntry


@dataclass
class Character:
    character_id: str
    name: str
    character_class: str
    level: int = 1
    health: int = 100
    max_health: int = 100
    row: int = 0
    col: int = 0
    inventory: List[InventoryEntry] = field(default_factory=list)

    def is_alive(self) -> bool:
        return self.health > 0

    def take_damage(self, amount: int) -> None:
        self.health = max(0, self.health - amount)

    def heal(self, amount: int) -> None:
        self.health = min(self.max_health, self.health + amount)

    def move_to(self, row: int, col: int) -> None:
        self.row = row
        self.col = col

    def position(self) -> tuple[int, int]:
        return (self.row, self.col)

    def __str__(self) -> str:
        return f"{self.name} (Lv.{self.level} {self.character_class}) HP:{self.health}/{self.max_health}"
