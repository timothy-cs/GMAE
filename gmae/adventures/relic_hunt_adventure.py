"""Relic Hunt — Competitive Mini-Adventure.

Two players compete to collect relics scattered across a realm. Each relic has
a point value. The player with the most points when all relics are collected
(or when time runs out) wins. Hazards roam the map and can stun players.

Implements IMiniAdventure (Strategy Pattern concrete strategy).
Uses Realm (Ghalib), InventoryItem (Ghalib), QuestEvent (Ellis), WorldClock (Ellis).
"""

from __future__ import annotations
import random
from typing import Optional, List, TYPE_CHECKING
from gmae.interfaces import IMiniAdventure
from gmae.enums import AdventureStatus, RarityType
from gmae.entities import (
    Entity, PlayerEntity, HazardEntity, RelicEntity,
)
from gmae.reused.ghalib.realm import Realm, REALMS
from gmae.reused.ghalib.inventory import InventoryItem, ITEMS
from gmae.reused.ellis.quest_event import QuestEvent
from gmae.reused.ellis.world_time import WorldTime
from gmae.reused.ellis.world_clock import WorldClock
from gmae.observer import game_events

if TYPE_CHECKING:
    from gmae.session import GameSession, AdventureState

DIRECTIONS = {
    "north": (-1, 0), "south": (1, 0), "east": (0, 1), "west": (0, -1),
    "n": (-1, 0), "s": (1, 0), "e": (0, 1), "w": (0, -1),
}


class RelicHuntAdventure(IMiniAdventure):
    """Competitive relic collection race."""

    def __init__(self, realm: Optional[Realm] = None, target_score: int = 30,
                 max_turns: int = 40, num_relics: int = 10, num_hazards: int = 2):
        self._realm = realm or REALMS["crystal_caverns"]
        self._target_score = target_score
        self._max_turns = max_turns
        self._num_relics = num_relics
        self._num_hazards = num_hazards
        self._session: Optional[GameSession] = None
        self._players: dict[int, PlayerEntity] = {}
        self._relics: List[RelicEntity] = []
        self._hazards: List[HazardEntity] = []
        self._turn_count = 0
        self._status = AdventureStatus.NOT_STARTED
        self._quest_event: Optional[QuestEvent] = None
        self._clock = WorldClock()
        self._rng = random.Random()

    @property
    def name(self) -> str:
        return "Relic Hunt"

    @property
    def description(self) -> str:
        return (f"Competitive: Race to collect relics in {self._realm.name}! "
                f"First to {self._target_score} points wins.")

    @property
    def mode(self) -> str:
        return "competitive"

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

        occupied: set[tuple[int, int]] = set()

        # Place players at opposite corners
        p1_pos = (0, 0)
        p2_pos = (self._realm.rows - 1, self._realm.cols - 1)
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

        # Place relics with varying point values
        self._relics.clear()
        relic_defs = [
            (ITEMS["ancient_relic_a"], 10),  # Legendary = 10 pts
            (ITEMS["ancient_relic_b"], 8),   # Ultra Rare = 8 pts
            (ITEMS["ancient_relic_c"], 5),   # Rare = 5 pts
        ]
        for i in range(self._num_relics):
            r, c = self._random_empty_cell(occupied)
            occupied.add((r, c))
            relic_item, pts = relic_defs[i % len(relic_defs)]
            relic = RelicEntity(
                entity_id=f"relic_{i}", name=f"{relic_item.name} #{i+1}",
                symbol="R", row=r, col=c, points=pts,
            )
            self._relics.append(relic)

        # Place hazards
        self._hazards.clear()
        for i in range(self._num_hazards):
            r, c = self._random_empty_cell(occupied)
            occupied.add((r, c))
            h = HazardEntity(
                entity_id=f"haz_{i}", name=f"Crystal Golem {i+1}",
                symbol="H", row=r, col=c, damage=0,
                patrol_direction=self._rng.choice([-1, 1]),
            )
            self._hazards.append(h)

        # Create quest event
        start_time = WorldTime(0, 12, 0)
        end_time = WorldTime(0, 12 + (self._max_turns * 10) // 60,
                             (self._max_turns * 10) % 60)
        self._quest_event = QuestEvent(
            title="Grand Relic Hunt",
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

        # Check if player is stunned
        if not player.is_alive():
            return f"{player.name} is stunned and cannot act this turn."

        parts = action.lower().split()
        cmd = parts[0] if parts else ""

        if cmd in DIRECTIONS:
            return self._move_player(player, cmd)
        elif cmd == "wait":
            return f"{player.name} waits."
        else:
            return f"Unknown action: '{action}'. Valid: north/south/east/west, wait"

    def _move_player(self, player: PlayerEntity, direction: str) -> str:
        dr, dc = DIRECTIONS[direction]
        new_r = player.row + dr
        new_c = player.col + dc
        if not self._realm.in_bounds(new_r, new_c):
            return f"{player.name} can't move there — out of bounds."
        player.move_to(new_r, new_c)
        msg = f"{player.name} moves {direction}."

        # Check relic pickup
        for relic in self._relics:
            if not relic.collected and relic.position() == player.position():
                relic.collected = True
                relic.collected_by = player.player_number
                player.score += relic.points
                msg += f" Found {relic.name} (+{relic.points} pts, total: {player.score})!"
                game_events.publish("relic_collected",
                                    player=player.name,
                                    relic=relic.name,
                                    points=relic.points)
        return msg

    def advance_turn(self) -> list[str]:
        messages: list[str] = []
        self._turn_count += 1
        self._clock.advance(10)

        # Move hazards horizontally
        for h in self._hazards:
            if h.is_stunned():
                h.stunned_turns -= 1
                continue
            new_c = h.col + h.patrol_direction
            if not self._realm.in_bounds(h.row, new_c):
                h.patrol_direction *= -1
                new_c = h.col + h.patrol_direction
            if self._realm.in_bounds(h.row, new_c):
                h.move_to(h.row, new_c)

        # Hazard collision = stun player for 1 turn (lose next turn's health as indicator)
        for h in self._hazards:
            for p in self._players.values():
                if h.position() == p.position() and p.is_alive():
                    # Stun: temporarily set health to 0, restore next turn
                    messages.append(f"{h.name} stuns {p.name}! They lose their next turn.")
                    p.health = 0  # Mark as stunned

        # Restore stunned players after processing
        for p in self._players.values():
            if p.health == 0:
                p.health = p.max_health  # Recover immediately but action was lost

        # Score update
        p1 = self._players[1]
        p2 = self._players[2]
        relics_left = sum(1 for r in self._relics if not r.collected)
        messages.append(f"--- Turn {self._turn_count}/{self._max_turns} | "
                        f"P1 Score: {p1.score} | P2 Score: {p2.score} | "
                        f"Relics left: {relics_left} ---")
        return messages

    def get_state(self) -> AdventureState:
        from gmae.session import AdventureState
        entities: list[Entity] = []
        entities.extend(self._players.values())
        entities.extend(self._hazards)
        entities.extend([r for r in self._relics if not r.collected])
        objectives = [
            f"First to {self._target_score} points wins!",
            f"P1 Score: {self._players[1].score}",
            f"P2 Score: {self._players[2].score}",
            f"Relics remaining: {sum(1 for r in self._relics if not r.collected)}",
            f"Turns remaining: {self._max_turns - self._turn_count}",
        ]
        return AdventureState(
            turn_count=self._turn_count,
            entities=entities,
            objectives=objectives,
            time_remaining=self._max_turns - self._turn_count,
        )

    def check_completion(self) -> AdventureStatus:
        if self._status != AdventureStatus.IN_PROGRESS:
            return self._status
        p1 = self._players[1]
        p2 = self._players[2]

        # Check target score reached
        if p1.score >= self._target_score or p2.score >= self._target_score:
            self._status = AdventureStatus.WIN
            if self._quest_event:
                self._quest_event.mark_completed()
            game_events.publish("adventure_completed", adventure=self.name, result="WIN")
            return self._status

        # Check all relics collected
        if all(r.collected for r in self._relics):
            if p1.score != p2.score:
                self._status = AdventureStatus.WIN
            else:
                self._status = AdventureStatus.DRAW
            if self._quest_event:
                self._quest_event.mark_completed()
            game_events.publish("adventure_completed", adventure=self.name,
                                result=self._status.value)
            return self._status

        # Check out of turns
        if self._turn_count >= self._max_turns:
            if p1.score != p2.score:
                self._status = AdventureStatus.WIN
            else:
                self._status = AdventureStatus.DRAW
            if self._quest_event:
                self._quest_event.mark_completed()
            game_events.publish("adventure_completed", adventure=self.name,
                                result=self._status.value)
            return self._status

        return self._status

    def get_winner(self) -> Optional[int]:
        """Returns the player_number of the winner, or None for draw/in-progress."""
        p1 = self._players.get(1)
        p2 = self._players.get(2)
        if not p1 or not p2:
            return None
        if p1.score > p2.score:
            return 1
        elif p2.score > p1.score:
            return 2
        return None

    def reset(self) -> None:
        self._turn_count = 0
        self._status = AdventureStatus.NOT_STARTED
        self._players.clear()
        self._relics.clear()
        self._hazards.clear()
        self._quest_event = None

    def render(self) -> str:
        grid = [["." for _ in range(self._realm.cols)]
                for _ in range(self._realm.rows)]

        # Place uncollected relics
        for relic in self._relics:
            if not relic.collected:
                grid[relic.row][relic.col] = "R"

        # Place hazards
        for h in self._hazards:
            grid[h.row][h.col] = "H"

        # Place players
        for pnum, p in self._players.items():
            grid[p.row][p.col] = str(pnum)

        # Build display
        lines = [f"\n  {self._realm.name} — Relic Hunt (Turn {self._turn_count}/{self._max_turns})"]
        lines.append("  " + " ".join(f"{c}" for c in range(self._realm.cols)))
        for r in range(self._realm.rows):
            row_str = " ".join(grid[r])
            lines.append(f"{r} {row_str}")
        lines.append("")
        lines.append(f"  Legend: 1=P1, 2=P2, R=Relic, H=Hazard")
        p1 = self._players.get(1)
        p2 = self._players.get(2)
        if p1:
            lines.append(f"  P1 {p1.name}: Score {p1.score}")
        if p2:
            lines.append(f"  P2 {p2.name}: Score {p2.score}")
        relics_left = sum(1 for r in self._relics if not r.collected)
        lines.append(f"  Relics remaining: {relics_left} | Target: {self._target_score} pts")
        return "\n".join(lines)

    def get_valid_actions(self, player_number: int) -> list[str]:
        return ["north", "south", "east", "west", "wait"]
