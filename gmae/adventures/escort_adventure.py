"""Escort Across the Realm — Co-op Mini-Adventure.

Two players work together to escort an NPC from a starting position to a target
coordinate on a grid-based realm. Hazards patrol the map and damage the NPC
and players. Players can move, use items, or guard the NPC.

Implements IMiniAdventure (Strategy Pattern concrete strategy).
Uses Realm (Ghalib), Character (Ghalib), InventoryItem (Ghalib),
QuestEvent (Ellis), WorldClock (Ellis).
"""

from __future__ import annotations
import random
from typing import Optional, List, TYPE_CHECKING
from gmae.interfaces import IMiniAdventure
from gmae.enums import AdventureStatus
from gmae.entities import (
    Entity, PlayerEntity, NPCEntity, HazardEntity, ItemEntity,
)
from gmae.reused.ghalib.realm import Realm, REALMS
from gmae.reused.ghalib.character import Character
from gmae.reused.ghalib.inventory import InventoryItem, ITEMS
from gmae.reused.ellis.quest_event import QuestEvent
from gmae.reused.ellis.world_time import WorldTime
from gmae.reused.ellis.world_clock import WorldClock
from gmae.observer import game_events

if TYPE_CHECKING:
    from gmae.session import GameSession, AdventureState


# Direction map
DIRECTIONS = {
    "north": (-1, 0), "south": (1, 0), "east": (0, 1), "west": (0, -1),
    "n": (-1, 0), "s": (1, 0), "e": (0, 1), "w": (0, -1),
}


class EscortAdventure(IMiniAdventure):
    """Co-op escort mission: guide the NPC to the target location."""

    def __init__(self, realm: Optional[Realm] = None, max_turns: int = 30,
                 num_hazards: int = 3, num_items: int = 3):
        self._realm = realm or REALMS["verdant_grove"]
        self._max_turns = max_turns
        self._num_hazards = num_hazards
        self._num_items = num_items
        self._session: Optional[GameSession] = None
        self._players: dict[int, PlayerEntity] = {}
        self._npc: Optional[NPCEntity] = None
        self._hazards: List[HazardEntity] = []
        self._items: List[ItemEntity] = []
        self._turn_count = 0
        self._status = AdventureStatus.NOT_STARTED
        self._quest_event: Optional[QuestEvent] = None
        self._clock = WorldClock()
        self._messages: List[str] = []
        self._rng = random.Random()

    @property
    def name(self) -> str:
        return "Escort Across the Realm"

    @property
    def description(self) -> str:
        return (f"Co-op: Escort the NPC safely to the target in {self._realm.name}. "
                f"Avoid hazards and use items to protect your charge!")

    @property
    def mode(self) -> str:
        return "co-op"

    def _random_empty_cell(self, occupied: set[tuple[int, int]]) -> tuple[int, int]:
        while True:
            r = self._rng.randint(0, self._realm.rows - 1)
            c = self._rng.randint(0, self._realm.cols - 1)
            if (r, c) not in occupied:
                return r, c

    def initialize(self, session: GameSession) -> None:
        self._session = session
        self._turn_count = 0
        self._status = AdventureStatus.IN_PROGRESS
        self._messages.clear()

        occupied: set[tuple[int, int]] = set()

        # Place players
        p1_pos = (0, 0)
        p2_pos = (0, 1)
        occupied.update([p1_pos, p2_pos])
        self._players[1] = PlayerEntity(
            entity_id="p1", name=session.player1.display_name,
            symbol="1", row=p1_pos[0], col=p1_pos[1], player_number=1,
            health=100, max_health=100,
        )
        self._players[2] = PlayerEntity(
            entity_id="p2", name=session.player2.display_name,
            symbol="2", row=p2_pos[0], col=p2_pos[1], player_number=2,
            health=100, max_health=100,
        )

        # Place NPC near players
        npc_pos = (1, 0)
        occupied.add(npc_pos)
        target_row = self._realm.rows - 1
        target_col = self._realm.cols - 1
        self._npc = NPCEntity(
            entity_id="npc", name="Elara the Merchant",
            symbol="N", row=npc_pos[0], col=npc_pos[1],
            health=80, max_health=80,
            target_row=target_row, target_col=target_col,
        )
        occupied.add((target_row, target_col))

        # Place hazards
        self._hazards.clear()
        for i in range(self._num_hazards):
            r, c = self._random_empty_cell(occupied)
            occupied.add((r, c))
            h = HazardEntity(
                entity_id=f"haz_{i}", name=f"Shadow Beast {i+1}",
                symbol="H", row=r, col=c, damage=15,
                patrol_direction=self._rng.choice([-1, 1]),
            )
            self._hazards.append(h)

        # Place items
        self._items.clear()
        available_items = [ITEMS["health_potion"], ITEMS["shield_charm"], ITEMS["smoke_bomb"]]
        for i in range(self._num_items):
            r, c = self._random_empty_cell(occupied)
            occupied.add((r, c))
            item = available_items[i % len(available_items)]
            ie = ItemEntity(
                entity_id=f"item_{i}", name=item.name,
                symbol="I", row=r, col=c, item=item,
            )
            self._items.append(ie)

        # Create quest event
        start_time = WorldTime(0, 6, 0)
        end_time = WorldTime(0, 6 + (self._max_turns * 10) // 60,
                             (self._max_turns * 10) % 60)
        self._quest_event = QuestEvent(
            title="Escort Elara Safely",
            start_time=start_time,
            end_time=end_time,
        )
        self._quest_event.assign_realm(self._realm)

        game_events.publish("adventure_initialized", adventure=self.name)

    def accept_input(self, player_number: int, action: str) -> str:
        if self._status != AdventureStatus.IN_PROGRESS:
            return "The adventure is not active."
        player = self._players.get(player_number)
        if not player:
            return "Invalid player."
        if not player.is_alive():
            return f"{player.name} is incapacitated and cannot act."

        parts = action.lower().split()
        cmd = parts[0] if parts else ""

        if cmd in DIRECTIONS:
            return self._move_player(player, cmd)
        elif cmd == "use" and len(parts) > 1:
            return self._use_item(player, parts[1])
        elif cmd == "guard":
            return self._guard_npc(player)
        elif cmd == "wait":
            return f"{player.name} waits."
        else:
            return f"Unknown action: '{action}'. Valid: north/south/east/west, use <item>, guard, wait"

    def _move_player(self, player: PlayerEntity, direction: str) -> str:
        dr, dc = DIRECTIONS[direction]
        new_r = player.row + dr
        new_c = player.col + dc
        if not self._realm.in_bounds(new_r, new_c):
            return f"{player.name} can't move there — out of bounds."
        player.move_to(new_r, new_c)
        msg = f"{player.name} moves {direction}."

        # Check item pickup
        for item_e in self._items:
            if not item_e.collected and item_e.position() == player.position():
                item_e.collected = True
                if item_e.item:
                    player.items.append(item_e.item)
                msg += f" Picked up {item_e.name}!"
                game_events.publish("item_collected",
                                    player=player.name, item=item_e.name)
        return msg

    def _use_item(self, player: PlayerEntity, item_keyword: str) -> str:
        for i, item in enumerate(player.items):
            if item_keyword in item.name.lower().replace(" ", "_"):
                player.items.pop(i)
                if item.item_type == "potion":
                    if self._npc and self._npc.is_alive():
                        healed = min(item.effect_value,
                                     self._npc.max_health - self._npc.health)
                        self._npc.health += healed
                        return f"{player.name} uses {item.name} on Elara, healing {healed} HP."
                    else:
                        player.heal(item.effect_value)
                        return f"{player.name} uses {item.name}, healing {item.effect_value} HP."
                elif item.item_type == "shield":
                    player.shield_active = True
                    return f"{player.name} activates {item.name}! Next hit is blocked."
                elif item.item_type == "tactical":
                    for h in self._hazards:
                        if abs(h.row - player.row) <= 2 and abs(h.col - player.col) <= 2:
                            h.stunned_turns = 2
                    return f"{player.name} throws a {item.name}! Nearby hazards are stunned."
                else:
                    return f"{player.name} uses {item.name}."
        return f"No item matching '{item_keyword}' in inventory."

    def _guard_npc(self, player: PlayerEntity) -> str:
        if self._npc is None:
            return "No NPC to guard."
        player.shield_active = True
        return f"{player.name} takes a defensive stance guarding Elara."

    def advance_turn(self) -> list[str]:
        messages: list[str] = []
        self._turn_count += 1
        self._clock.advance(10)

        if self._npc is None or not self._npc.is_alive():
            return messages

        # Move NPC toward target
        npc = self._npc
        dr = 0 if npc.row == npc.target_row else (1 if npc.row < npc.target_row else -1)
        dc = 0 if npc.col == npc.target_col else (1 if npc.col < npc.target_col else -1)
        # Prefer the axis with greater distance
        row_dist = abs(npc.target_row - npc.row)
        col_dist = abs(npc.target_col - npc.col)
        if row_dist >= col_dist and dr != 0:
            new_r, new_c = npc.row + dr, npc.col
        elif dc != 0:
            new_r, new_c = npc.row, npc.col + dc
        else:
            new_r, new_c = npc.row + dr, npc.col + dc
        if self._realm.in_bounds(new_r, new_c):
            npc.move_to(new_r, new_c)
            messages.append(f"Elara moves toward the target.")

        # Move hazards
        for h in self._hazards:
            if h.is_stunned():
                h.stunned_turns -= 1
                continue
            # Hazards patrol vertically
            new_r = h.row + h.patrol_direction
            if not self._realm.in_bounds(new_r, h.col):
                h.patrol_direction *= -1
                new_r = h.row + h.patrol_direction
            if self._realm.in_bounds(new_r, h.col):
                h.move_to(new_r, h.col)

        # Check hazard collisions with NPC and players
        for h in self._hazards:
            if h.is_stunned():
                continue
            if h.position() == npc.position():
                dmg = npc.take_damage(h.damage)
                messages.append(f"{h.name} attacks Elara for {dmg} damage! "
                                f"(HP: {npc.health}/{npc.max_health})")
                game_events.publish("npc_damaged", npc="Elara", damage=dmg)
            for p in self._players.values():
                if p.is_alive() and h.position() == p.position():
                    dmg = p.take_damage(h.damage)
                    if dmg == 0:
                        messages.append(f"{p.name}'s shield blocks {h.name}'s attack!")
                    else:
                        messages.append(f"{h.name} attacks {p.name} for {dmg} damage! "
                                        f"(HP: {p.health}/{p.max_health})")
                        game_events.publish("player_damaged",
                                            player=p.name, damage=dmg)

        # Status update
        messages.append(f"--- Turn {self._turn_count}/{self._max_turns} | "
                        f"Elara HP: {npc.health}/{npc.max_health} | "
                        f"Target: ({npc.target_row},{npc.target_col}) ---")
        return messages

    def get_state(self) -> AdventureState:
        from gmae.session import AdventureState
        entities: list[Entity] = []
        entities.extend(self._players.values())
        if self._npc:
            entities.append(self._npc)
        entities.extend(self._hazards)
        entities.extend([i for i in self._items if not i.collected])
        objectives = []
        if self._npc:
            objectives.append(f"Escort Elara to ({self._npc.target_row},{self._npc.target_col})")
            objectives.append(f"Elara HP: {self._npc.health}/{self._npc.max_health}")
        objectives.append(f"Turns remaining: {self._max_turns - self._turn_count}")
        return AdventureState(
            turn_count=self._turn_count,
            entities=entities,
            objectives=objectives,
            time_remaining=self._max_turns - self._turn_count,
        )

    def check_completion(self) -> AdventureStatus:
        if self._status != AdventureStatus.IN_PROGRESS:
            return self._status
        if self._npc is None:
            self._status = AdventureStatus.LOSE
            return self._status
        # Win: NPC reached target
        if (self._npc.row == self._npc.target_row and
                self._npc.col == self._npc.target_col):
            self._status = AdventureStatus.WIN
            if self._quest_event:
                self._quest_event.mark_completed()
            game_events.publish("adventure_completed", adventure=self.name, result="WIN")
            return self._status
        # Lose: NPC died
        if not self._npc.is_alive():
            self._status = AdventureStatus.LOSE
            game_events.publish("adventure_completed", adventure=self.name, result="LOSE")
            return self._status
        # Lose: out of turns
        if self._turn_count >= self._max_turns:
            self._status = AdventureStatus.LOSE
            game_events.publish("adventure_completed", adventure=self.name, result="LOSE")
            return self._status
        return self._status

    def reset(self) -> None:
        self._turn_count = 0
        self._status = AdventureStatus.NOT_STARTED
        self._players.clear()
        self._npc = None
        self._hazards.clear()
        self._items.clear()
        self._messages.clear()
        self._quest_event = None

    def render(self) -> str:
        grid = [["." for _ in range(self._realm.cols)]
                for _ in range(self._realm.rows)]

        # Mark target
        if self._npc:
            tr, tc = self._npc.target_row, self._npc.target_col
            if self._realm.in_bounds(tr, tc):
                grid[tr][tc] = "T"

        # Place uncollected items
        for item_e in self._items:
            if not item_e.collected:
                grid[item_e.row][item_e.col] = "I"

        # Place hazards
        for h in self._hazards:
            grid[h.row][h.col] = "H" if not h.is_stunned() else "z"

        # Place NPC
        if self._npc and self._npc.is_alive():
            grid[self._npc.row][self._npc.col] = "N"

        # Place players
        for pnum, p in self._players.items():
            if p.is_alive():
                grid[p.row][p.col] = str(pnum)

        # Build display
        lines = [f"\n  {self._realm.name} — Escort Mission (Turn {self._turn_count}/{self._max_turns})"]
        lines.append("  " + " ".join(str(c) for c in range(self._realm.cols)))
        for r in range(self._realm.rows):
            row_str = " ".join(grid[r])
            lines.append(f"{r} {row_str}")
        lines.append("")
        lines.append(f"  Legend: 1=P1, 2=P2, N=NPC, H=Hazard, z=Stunned, I=Item, T=Target")
        if self._npc:
            lines.append(f"  Elara HP: {self._npc.health}/{self._npc.max_health} | "
                         f"Target: ({self._npc.target_row},{self._npc.target_col})")
        for pnum, p in self._players.items():
            items_str = ", ".join(i.name for i in p.items) if p.items else "none"
            shield = " [SHIELD]" if p.shield_active else ""
            lines.append(f"  P{pnum} {p.name}: HP {p.health}/{p.max_health}{shield} | Items: {items_str}")
        return "\n".join(lines)

    def get_valid_actions(self, player_number: int) -> list[str]:
        actions = ["north", "south", "east", "west", "guard", "wait"]
        player = self._players.get(player_number)
        if player and player.items:
            for item in player.items:
                keyword = item.name.lower().replace(" ", "_")
                actions.append(f"use {keyword}")
        return actions
