"""Realm model — reused from Ghalib's individual GuildQuest assignment.

Represents a realm/location in the GuildQuest world with a grid-based layout.
Adapted for GMAE: added grid dimensions and coordinate helpers.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Realm:
    realm_id: str
    name: str
    description: str
    rows: int = 10
    cols: int = 10

    def in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.rows and 0 <= col < self.cols

    def __str__(self) -> str:
        return f"{self.name} ({self.rows}x{self.cols})"


# Pre-built realms available in the GMAE
REALMS = {
    "verdant_grove": Realm("verdant_grove", "Verdant Grove",
                           "A lush forest realm teeming with wildlife and ancient trees.", 10, 10),
    "ember_wastes": Realm("ember_wastes", "Ember Wastes",
                          "A scorched volcanic landscape with rivers of lava and ash storms.", 12, 12),
    "crystal_caverns": Realm("crystal_caverns", "Crystal Caverns",
                             "Underground caverns lit by glowing crystals and inhabited by cave dwellers.", 8, 14),
    "skyreach_peaks": Realm("skyreach_peaks", "Skyreach Peaks",
                            "Towering mountain peaks above the clouds, home to wind spirits.", 10, 10),
}
