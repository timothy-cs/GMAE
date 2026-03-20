"""Entity classes for the adventure grid.

Represents all objects that can exist on the adventure map.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from gmae.reused.ghalib.inventory import InventoryItem


@dataclass
class Entity:
    """Base class for anything placed on the adventure grid."""
    entity_id: str
    name: str
    symbol: str  # Single character for grid display
    row: int = 0
    col: int = 0
    blocking: bool = False

    def position(self) -> tuple[int, int]:
        return (self.row, self.col)

    def move_to(self, row: int, col: int) -> None:
        self.row = row
        self.col = col


@dataclass
class PlayerEntity(Entity):
    """A player on the grid."""
    player_number: int = 1
    health: int = 100
    max_health: int = 100
    shield_active: bool = False
    items: list[InventoryItem] = field(default_factory=list)
    score: int = 0

    def take_damage(self, amount: int) -> int:
        if self.shield_active:
            self.shield_active = False
            return 0
        actual = min(amount, self.health)
        self.health -= actual
        return actual

    def heal(self, amount: int) -> None:
        self.health = min(self.max_health, self.health + amount)

    def is_alive(self) -> bool:
        return self.health > 0


@dataclass
class NPCEntity(Entity):
    """An NPC on the grid (e.g., the escort target)."""
    health: int = 80
    max_health: int = 80
    target_row: int = 0
    target_col: int = 0

    def take_damage(self, amount: int) -> int:
        actual = min(amount, self.health)
        self.health -= actual
        return actual

    def is_alive(self) -> bool:
        return self.health > 0


@dataclass
class HazardEntity(Entity):
    """A hazard that can damage players/NPCs."""
    damage: int = 15
    stunned_turns: int = 0
    patrol_direction: int = 1  # 1 or -1 for movement

    def is_stunned(self) -> bool:
        return self.stunned_turns > 0


@dataclass
class ItemEntity(Entity):
    """A collectible item placed on the grid."""
    item: Optional[InventoryItem] = None
    collected: bool = False


@dataclass
class RelicEntity(Entity):
    """A relic placed on the grid for Relic Hunt."""
    points: int = 1
    collected: bool = False
    collected_by: Optional[int] = None  # player_number
