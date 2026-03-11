"""
RealmAdapter — Adapter Pattern (Non-Security).

Wraps the GuildQuest Realm subsystem and adds a grid-based game layer on top,
without modifying the original Realm class.

  Adaptee : core.realm.Realm  (GuildQuest Part 1 subsystem)
  Target   : Grid-aware realm interface consumed by mini-adventures

Why an adapter?
  The original Realm stores entities in a flat list and has no concept of
  grid coordinates. The GMAE mini-adventures need grid-based placement and
  movement. Rather than changing Realm (which would break the reuse contract),
  the adapter extends behaviour by composing a grid dict on top of the
  original object.

Reuse source : Ethan Votran — GuildQuest Part 1 (core.realm.Realm)
Used by      : RelicHunt, EscortQuest, GMAE_Engine
"""

from __future__ import annotations
from typing import Any, Dict, Optional, Tuple
from core.realm import Realm, TimeRule
from core.world_clock import WorldClock


class RealmAdapter:
    """
    Adapter that extends a Realm with grid-coordinate-based entity placement.

    The adapter delegates identity/time calls to the wrapped Realm and adds
    a separate dict-based grid for positioning game entities.
    """

    def __init__(self, realm: Realm) -> None:
        self._realm = realm
        self._grid: Dict[Tuple[int, int], Any] = {}  # (x, y) -> entity

    # ------------------------------------------------------------------
    # Delegation — original Realm interface
    # ------------------------------------------------------------------

    @property
    def realm_id(self) -> str:
        return self._realm.realm_id

    @property
    def name(self) -> str:
        return self._realm.name

    @property
    def description(self) -> str:
        return self._realm.description

    def get_local_time(self, world_clock: WorldClock) -> WorldClock:
        return self._realm.get_local_time(world_clock)

    def get_grid_width(self) -> int:
        return self._realm.grid_width

    def get_grid_height(self) -> int:
        return self._realm.grid_height

    def is_valid_position(self, x: int, y: int) -> bool:
        return self._realm.is_valid_position(x, y)

    # ------------------------------------------------------------------
    # Extended grid interface (GMAE-specific)
    # ------------------------------------------------------------------

    def place_entity(self, entity: Any, x: int, y: int) -> bool:
        """Place an entity at (x, y). Returns False if out of bounds."""
        if not self._realm.is_valid_position(x, y):
            return False
        self._grid[(x, y)] = entity
        return True

    def remove_entity_at(self, x: int, y: int) -> Optional[Any]:
        return self._grid.pop((x, y), None)

    def get_entity_at(self, x: int, y: int) -> Optional[Any]:
        return self._grid.get((x, y))

    def move_entity(
        self, from_x: int, from_y: int, to_x: int, to_y: int
    ) -> bool:
        """Move entity from one cell to another. Returns False if invalid."""
        if not self._realm.is_valid_position(to_x, to_y):
            return False
        entity = self._grid.pop((from_x, from_y), None)
        if entity is None:
            return False
        self._grid[(to_x, to_y)] = entity
        return True

    def is_occupied(self, x: int, y: int) -> bool:
        return (x, y) in self._grid

    def clear_grid(self) -> None:
        self._grid.clear()

    # ------------------------------------------------------------------
    # Rendering helper
    # ------------------------------------------------------------------

    def render_grid(self, markers: Optional[Dict[Tuple[int, int], str]] = None) -> str:
        """
        Return an ASCII representation of the realm grid.

        markers: optional dict of {(x,y): single_char} to overlay on the grid.
                 Takes precedence over placed entities.
        """
        markers = markers or {}
        w = self._realm.grid_width
        h = self._realm.grid_height
        lines = [f"=== {self.name} ===", "  " + "".join(str(x % 10) for x in range(w))]
        for y in range(h):
            row = f"{y % 10} "
            for x in range(w):
                if (x, y) in markers:
                    row += markers[(x, y)]
                elif self.is_occupied(x, y):
                    row += "E"
                else:
                    row += "."
            lines.append(row)
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def create(
        cls,
        realm_id: str,
        name: str,
        description: str = "",
        offset_minutes: int = 0,
        day_length_multiplier: float = 1.0,
        grid_width: int = 10,
        grid_height: int = 10,
    ) -> "RealmAdapter":
        """Convenience factory: build a RealmAdapter from plain parameters."""
        time_rule = TimeRule(
            offset_minutes=offset_minutes,
            day_length_multiplier=day_length_multiplier,
        )
        realm = Realm(realm_id, name, description, time_rule, grid_width, grid_height)
        return cls(realm)

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        return str(self._realm)

    def __repr__(self) -> str:
        return f"RealmAdapter(realm={self._realm!r})"
