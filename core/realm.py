"""
Realm — GuildQuest subsystem (Reused from GuildQuest Part 1).

Physical locations in the GuildQuest world/universe. Each realm has a name,
a unique ID, an optional description, a local-time rule, and a grid size for
positioning entities.

Reuse source : Ethan Votran — GuildQuest Part 1
Used by      : RealmAdapter (GMAE grid layer), IMiniAdventure implementations,
               QuestEvent (realm reference on events)
"""

from __future__ import annotations
from core.world_clock import WorldClock


class TimeRule:
    """
    Defines how a Realm's local time relates to the universal WorldClock.

    local_minutes = floor(world_minutes * day_length_multiplier) + offset_minutes
    """

    def __init__(
        self,
        offset_minutes: int = 0,
        day_length_multiplier: float = 1.0,
    ) -> None:
        self.offset_minutes = offset_minutes
        self.day_length_multiplier = day_length_multiplier

    def apply(self, world_clock: WorldClock) -> int:
        """Return this realm's local time in total minutes."""
        adjusted = int(world_clock.total_minutes * self.day_length_multiplier)
        return adjusted + self.offset_minutes

    def __repr__(self) -> str:
        return (
            f"TimeRule(offset={self.offset_minutes}, "
            f"multiplier={self.day_length_multiplier})"
        )


class Realm:
    """
    A physical location in the GuildQuest world.

    Contains a grid of configurable size used for placing entities (players,
    NPCs, items, hazards). Local time is derived from the realm's TimeRule.
    """

    def __init__(
        self,
        realm_id: str,
        name: str,
        description: str = "",
        local_time_rules: TimeRule | None = None,
        grid_width: int = 10,
        grid_height: int = 10,
    ) -> None:
        self.realm_id = realm_id
        self.name = name
        self.description = description
        self.local_time_rules: TimeRule = local_time_rules or TimeRule()
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.entities: list = []

    # ------------------------------------------------------------------
    # Time helpers
    # ------------------------------------------------------------------

    def get_local_time(self, world_clock: WorldClock) -> WorldClock:
        """Return a new WorldClock set to this realm's local time."""
        local_minutes = self.local_time_rules.apply(world_clock)
        return WorldClock(max(0, local_minutes))

    # ------------------------------------------------------------------
    # Entity management
    # ------------------------------------------------------------------

    def add_entity(self, entity: object) -> None:
        self.entities.append(entity)

    def remove_entity(self, entity: object) -> bool:
        if entity in self.entities:
            self.entities.remove(entity)
            return True
        return False

    # ------------------------------------------------------------------
    # Grid helpers
    # ------------------------------------------------------------------

    def is_valid_position(self, x: int, y: int) -> bool:
        return 0 <= x < self.grid_width and 0 <= y < self.grid_height

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        return f"{self.name} (ID: {self.realm_id})"

    def __repr__(self) -> str:
        return (
            f"Realm(realm_id={self.realm_id!r}, name={self.name!r}, "
            f"grid={self.grid_width}x{self.grid_height})"
        )
