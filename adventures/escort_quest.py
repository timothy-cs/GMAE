"""
EscortQuest — Mini-Adventure 2 (Co-operative).

Two players work together to escort an NPC (N) to the target zone (X) before
time runs out. Hazards (@) roam the grid and must be avoided. Both players
can push the NPC one step toward the target when adjacent to it.

Observer Pattern integration:
  A QuestEventAdapter (wrapping QuestEvent) fires at the midpoint turn and
  notifies the adventure via _on_midpoint(), which increases hazard speed.
  This demonstrates the Observer Pattern with the reused QuestEvent subsystem.

Rules
-----
- The realm is an 8x8 grid.
- P1 starts at (0,0), P2 starts at (0,1). NPC starts at (0,3).
- Target is (7,7). Hazards spawn at random positions.
- Each player enters one action per round. After both act, hazards move.
- Win : NPC reaches the target.
- Lose: A hazard occupies the same cell as the NPC or a player, OR turns run out.

Controls
--------
  Player 1: W (up)  A (left)  S (down)  D (right)  E (push NPC)
  Player 2: I (up)  J (left)  K (down)  L (right)  U (push NPC)
"""

from __future__ import annotations
import random
from typing import Any, Dict, List, Tuple

from engine.interface import IMiniAdventure
from adapters.quest_adapter import QuestEventAdapter
from core.world_clock import WorldClock


class EscortQuest(IMiniAdventure):
    """Co-operative NPC escort mini-adventure for 2 local players."""

    GRID_W: int = 8
    GRID_H: int = 8
    MAX_TURNS: int = 40
    NUM_HAZARDS: int = 3

    _MOVE_MAP: Dict[str, Tuple[int, int]] = {
        "w": (0, -1), "a": (-1, 0), "s": (0, 1), "d": (1, 0),
        "i": (0, -1), "j": (-1, 0), "k": (0, 1), "l": (1, 0),
    }
    _COLLECT_KEYS = {"e", "u"}

    def __init__(self) -> None:
        self._players: List = []
        self._realm = None
        self._positions: Dict[str, Tuple[int, int]] = {}
        self._npc_pos: Tuple[int, int] = (0, 3)
        self._target_pos: Tuple[int, int] = (7, 7)
        self._hazards: List[Tuple[int, int]] = []
        self._turn: int = 0
        self._actions_this_round: int = 0
        self._done: bool = False
        self._won: bool = False
        self._log: List[str] = []
        self._midpoint_event: QuestEventAdapter | None = None

    # ------------------------------------------------------------------
    # IMiniAdventure interface
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        return "Escort Across the Realm"

    @property
    def description(self) -> str:
        return "Co-op: Guide the NPC to safety before time runs out!"

    def initialize(self, players: List, realm: Any) -> None:
        self._players = players
        self._realm = realm
        self._done = False
        self._won = False
        self._turn = 0
        self._actions_this_round = 0
        self._log = []

        # Starting positions
        self._positions = {
            players[0].user_id: (0, 0),
            players[1].user_id: (0, 1),
        }
        self._npc_pos = (0, 3)
        self._target_pos = (self.GRID_W - 1, self.GRID_H - 1)

        # Place hazards, avoiding all occupied cells
        occupied: set = (
            set(self._positions.values())
            | {self._npc_pos, self._target_pos}
        )
        self._hazards = []
        attempts = 0
        while len(self._hazards) < self.NUM_HAZARDS and attempts < 200:
            hx = random.randint(0, self.GRID_W - 1)
            hy = random.randint(0, self.GRID_H - 1)
            if (hx, hy) not in occupied:
                self._hazards.append((hx, hy))
                occupied.add((hx, hy))
            attempts += 1

        # QuestEventAdapter: midpoint warning fires at turn 20
        # Demonstrates Observer Pattern reuse of the QuestEvent subsystem
        self._midpoint_event = QuestEventAdapter.create(
            event_id="midpoint_warning",
            name="Halfway Warning",
            start_minutes=self.MAX_TURNS // 2,
            end_minutes=self.MAX_TURNS // 2 + 1,
        )
        self._midpoint_event.subscribe(self._on_midpoint)

        self._log.append(
            f"=== Escort Quest begins! Guide the NPC (N) to the target (X)! ==="
        )
        self._log.append(
            f"NPC starts at {self._npc_pos}. Target: {self._target_pos}. "
            f"Turns remaining: {self.MAX_TURNS}"
        )
        self._log.append("Hazards (@) roam the grid. Work together!")

    def _on_midpoint(self, event) -> None:
        """Observer callback: called when the midpoint QuestEvent fires."""
        self._log.append(
            ">>> HALFWAY POINT: Hazards are moving faster! Stay alert! <<<"
        )

    def handle_input(self, player_id: str, action: str, **kwargs: Any) -> str:
        if self._done:
            return "The adventure is over. Select 'Reset' to play again."
        if player_id not in self._positions:
            return f"Unknown player ID: {player_id}"

        action = action.strip().lower()
        x, y = self._positions[player_id]
        pname = self._name_of(player_id)
        msg = ""

        if action in self._MOVE_MAP:
            dx, dy = self._MOVE_MAP[action]
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.GRID_W and 0 <= ny < self.GRID_H:
                self._positions[player_id] = (nx, ny)
                msg = f"{pname} moves to ({nx},{ny})"
            else:
                msg = f"{pname} can't move that way — boundary!"

        elif action in self._COLLECT_KEYS:
            px, py = self._positions[player_id]
            nx, ny = self._npc_pos
            # Must be adjacent (Manhattan distance ≤ 1) to push the NPC
            if abs(px - nx) + abs(py - ny) <= 1:
                new_npc = self._step_toward(self._npc_pos, self._target_pos)
                self._npc_pos = new_npc
                msg = f"{pname} pushes the NPC toward the target → {self._npc_pos}"
            else:
                msg = f"{pname} is too far from the NPC to push! Get adjacent first."

        else:
            msg = f"Unknown action '{action}'. Use WASD/IJKL to move, E/U to push NPC."

        self._log.append(msg)

        # After each player action, advance turn counter and move hazards
        self._actions_this_round += 1
        if self._actions_this_round >= 2:
            self._actions_this_round = 0
            self._turn += 1
            self._advance_hazards()
            self._poll_events()
            self._check_state()

        return msg

    def update(self, delta_time: int = 1) -> None:
        # Input-driven; autonomous updates are handled in handle_input
        pass

    def check_completion(self) -> bool:
        return self._done

    def get_status(self) -> Dict[str, Any]:
        return {
            "adventure": self.name,
            "turn": self._turn,
            "max_turns": self.MAX_TURNS,
            "turns_remaining": self.MAX_TURNS - self._turn,
            "npc_position": self._npc_pos,
            "target_position": self._target_pos,
            "hazards": list(self._hazards),
            "positions": {
                self._name_of(uid): pos
                for uid, pos in self._positions.items()
            },
            "done": self._done,
            "won": self._won,
            "last_message": self._log[-1] if self._log else "",
        }

    def reset(self) -> None:
        if self._players and self._realm is not None:
            self.initialize(self._players, self._realm)

    # ------------------------------------------------------------------
    # Internal logic
    # ------------------------------------------------------------------

    def _step_toward(
        self, origin: Tuple[int, int], target: Tuple[int, int]
    ) -> Tuple[int, int]:
        """Move origin one step toward target (horizontal first)."""
        ox, oy = origin
        tx, ty = target
        if ox != tx:
            return (ox + (1 if tx > ox else -1), oy)
        if oy != ty:
            return (ox, oy + (1 if ty > oy else -1))
        return origin

    def _advance_hazards(self) -> None:
        """Move each hazard one step (two steps after the midpoint)."""
        steps = 2 if self._turn >= self.MAX_TURNS // 2 else 1
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        new_hazards: List[Tuple[int, int]] = []
        for hx, hy in self._hazards:
            for _ in range(steps):
                dx, dy = random.choice(directions)
                nx, ny = hx + dx, hy + dy
                if 0 <= nx < self.GRID_W and 0 <= ny < self.GRID_H:
                    hx, hy = nx, ny
            new_hazards.append((hx, hy))
        self._hazards = new_hazards

    def _poll_events(self) -> None:
        """Poll the QuestEventAdapter to check if the midpoint event fires."""
        if self._midpoint_event:
            self._midpoint_event.poll(WorldClock(self._turn))

    def _check_state(self) -> None:
        """Evaluate win/lose conditions after every completed round."""
        # Win: NPC reached target
        if self._npc_pos == self._target_pos:
            self._done = True
            self._won = True
            self._log.append(
                "*** The NPC reached safety! YOU WIN! Well done, heroes! ***"
            )
            return

        # Lose: hazard on NPC
        if self._npc_pos in self._hazards:
            self._done = True
            self._won = False
            self._log.append("*** A hazard caught the NPC! YOU LOSE! ***")
            return

        # Lose: hazard on a player
        for p in self._players:
            if self._positions.get(p.user_id) in self._hazards:
                self._done = True
                self._won = False
                self._log.append(
                    f"*** {p.username} was caught by a hazard! YOU LOSE! ***"
                )
                return

        # Lose: out of turns
        if self._turn >= self.MAX_TURNS:
            self._done = True
            self._won = False
            self._log.append(
                f"*** Time's up after {self.MAX_TURNS} turns! YOU LOSE! ***"
            )

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def render(self) -> str:
        """Return an ASCII grid showing all entities."""
        markers: Dict[Tuple[int, int], str] = {}
        markers[self._target_pos] = "X"
        for hpos in self._hazards:
            if hpos not in markers:
                markers[hpos] = "@"
        if self._npc_pos not in markers:
            markers[self._npc_pos] = "N"
        for i, p in enumerate(self._players):
            pos = self._positions[p.user_id]
            if pos not in markers:
                markers[pos] = str(i + 1)

        header = f"  {''.join(str(x % 10) for x in range(self.GRID_W))}"
        rows = [header]
        for y in range(self.GRID_H):
            row = f"{y % 10} "
            for x in range(self.GRID_W):
                row += markers.get((x, y), ".")
            rows.append(row)

        rows.append(
            f"  Turn: {self._turn}/{self.MAX_TURNS}  |  "
            f"NPC: {self._npc_pos}  |  Target: {self._target_pos}"
        )
        rows.append("  Legend: 1=P1  2=P2  N=NPC  X=Target  @=Hazard  .=Empty")
        return "\n".join(rows)

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------

    def _name_of(self, player_id: str | None) -> str:
        if player_id is None:
            return "Nobody"
        for p in self._players:
            if p.user_id == player_id:
                return p.username
        return player_id
