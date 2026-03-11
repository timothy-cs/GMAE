"""Inventory model — reused from Ghalib's individual GuildQuest assignment.

Represents items and inventory entries in the GuildQuest world.
Adapted for GMAE: added effect types for mini-adventure item usage.
"""

from __future__ import annotations
from dataclasses import dataclass
from gmae.enums import RarityType


@dataclass
class InventoryItem:
    item_id: str
    name: str
    rarity: RarityType
    item_type: str  # "weapon", "potion", "shield", "relic", "key", etc.
    description: str
    effect_value: int = 0  # Numeric effect (damage, heal amount, etc.)

    def __str__(self) -> str:
        return f"{self.name} [{self.rarity.value}] - {self.description}"


@dataclass
class InventoryEntry:
    item: InventoryItem
    quantity: int = 1

    def use_one(self) -> bool:
        if self.quantity > 0:
            self.quantity -= 1
            return True
        return False

    def __str__(self) -> str:
        return f"{self.item.name} x{self.quantity}"


# Pre-built items available in the GMAE
ITEMS = {
    "health_potion": InventoryItem("health_potion", "Health Potion", RarityType.COMMON,
                                   "potion", "Restores 30 HP.", effect_value=30),
    "shield_charm": InventoryItem("shield_charm", "Shield Charm", RarityType.RARE,
                                  "shield", "Blocks the next hazard hit.", effect_value=1),
    "speed_boots": InventoryItem("speed_boots", "Speed Boots", RarityType.RARE,
                                 "boots", "Allows moving 2 spaces in one turn.", effect_value=2),
    "ancient_relic_a": InventoryItem("ancient_relic_a", "Relic of Dawn", RarityType.LEGENDARY,
                                     "relic", "A glowing relic from the Age of Dawn.", effect_value=10),
    "ancient_relic_b": InventoryItem("ancient_relic_b", "Relic of Dusk", RarityType.ULTRA_RARE,
                                     "relic", "A shimmering relic from the Twilight Era.", effect_value=8),
    "ancient_relic_c": InventoryItem("ancient_relic_c", "Relic of Storm", RarityType.RARE,
                                     "relic", "A crackling relic charged with storm energy.", effect_value=5),
    "smoke_bomb": InventoryItem("smoke_bomb", "Smoke Bomb", RarityType.COMMON,
                                "tactical", "Stuns nearby hazards for 1 turn.", effect_value=1),
}
