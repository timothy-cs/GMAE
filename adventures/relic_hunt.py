"""
RelicHunt — Mini-Adventure 1 (Competitive).

Two players race across a grid realm to collect relics. The first player to
collect RELICS_TO_WIN relics wins. Relics are scattered randomly at the start.

Rules
-----
- The realm is an 8x8 grid.
- Player 1 starts at (0,0), Player 2 starts at (7,7).
- NUM_RELICS relics (*) are scattered randomly (not on starting positions).
- Each round both players enter one action before the display updates.
- Moving off the grid is blocked with a message.
- Collecting requires the player to be on the same cell as a relic.
- First to RELICS_TO_WIN relics wins.

Controls
--------
  Player 1: W (up)  A (left)  S (down)  D (right)  E (collect)
  Player 2: I (up)  J (left)  K (down)  L (right)  U (collect)
"""

from __future__ import annotations
import random
from typing import Any, Dict, List, Tuple

from engine.interface import IMiniAdventure


class RelicHunt(IMiniAdventure):
    """Competitive relic-collection mini-adventure for 2 local players."""

    RELICS_TO_WIN: int = 3
    NUM_RELICS: int = 6
    GRID_W: int = 8
    GRID_H: int = 8

    # Player 1 uses WASD+E, Player 2 uses IJKL+U
    _MOVE_MAP: Dict[str, Tuple[int, int]] = {
        "w": (0, -1), "a": (-1, 0), "s": (0, 1), "d": (1, 0),
        "i": (0, -1), "j": (-1, 0), "k": (0, 1), "l": (1, 0),
    }
    _P1_COLLECT = "e"
    _P2_COLLECT = "u"

    def __init__(self) -> None:
        self._players: List = []
        self._realm = None
        self._scores: Dict[str, int] = {}
        self._positions: Dict[str, Tuple[int, int]] = {}
        self._relics: List[Tuple[int, int]] = []
        self._done: bool = False
        self._winner_id: str | None = None
        self._log: List[str] = []

    # ------------------------------------------------------------------
    # IMiniAdventure interface
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        return "Relic Hunt"

    @property
    def description(self) -> str:
        return "Competitive: Race to collect 3 relics before your opponent!"

    def initialize(self, players: List, realm: Any) -> None:
        self._players = players
        self._realm = realm
        self._scores = {p.user_id: 0 for p in players}
        self._positions = {}
        self._relics = []
        self._done = False
        self._winner_id = None
        self._log = []

        # Place players at opposite corners
        p1, p2 = players[0], players[1]
        self._positions[p1.user_id] = (0, 0)
        self._positions[p2.user_id] = (self.GRID_W - 1, self.GRID_H - 1)

        # Scatter relics randomly, avoiding starting positions
        occupied: set = set(self._positions.values())
        attempts = 0
        while len(self._relics) < self.NUM_RELICS and attempts < 200:
            rx, ry = random.randint(0, self.GRID_W - 1), random.randint(0, self.GRID_H - 1)
            if (rx, ry) not in occupied:
                self._relics.append((rx, ry))
                occupied.add((rx, ry))
            attempts += 1

        self._log.append(
            f"=== Relic Hunt begins! Collect {self.RELICS_TO_WIN} relics to win! ==="
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

        elif action in (self._P1_COLLECT, self._P2_COLLECT):
            pos = self._positions[player_id]
            if pos in self._relics:
                self._relics.remove(pos)
                self._scores[player_id] += 1
                score = self._scores[player_id]
                msg = f"{pname} collected a relic! ({score}/{self.RELICS_TO_WIN})"
                if score >= self.RELICS_TO_WIN:
                    self._done = True
                    self._winner_id = player_id
                    msg += f"\n*** {pname} wins Relic Hunt! ***"
            else:
                msg = f"{pname} searches... no relic here."

        else:
            msg = f"Unknown action '{action}'. Use WASD/IJKL to move, E/U to collect."

        self._log.append(msg)
        return msg

    def update(self, delta_time: int = 1) -> None:
        # Turn-based: no autonomous updates needed
        pass

    def check_completion(self) -> bool:
        return self._done

    def get_status(self) -> Dict[str, Any]:
        return {
            "adventure": self.name,
            "scores": {
                self._name_of(uid): score
                for uid, score in self._scores.items()
            },
            "relics_remaining": len(self._relics),
            "positions": {
                self._name_of(uid): pos
                for uid, pos in self._positions.items()
            },
            "done": self._done,
            "winner": self._name_of(self._winner_id) if self._winner_id else None,
            "last_message": self._log[-1] if self._log else "",
        }

    def reset(self) -> None:
        if self._players and self._realm is not None:
            self.initialize(self._players, self._realm)

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def render(self) -> str:
        """Return an ASCII grid showing player positions and relics."""
        markers: Dict[Tuple[int, int], str] = {}
        for pos in self._relics:
            markers[pos] = "*"
        for i, p in enumerate(self._players):
            pos = self._positions[p.user_id]
            markers[pos] = str(i + 1)  # "1" or "2" overwrites "*" if on relic

        header = f"  {''.join(str(x % 10) for x in range(self.GRID_W))}"
        rows = [header]
        for y in range(self.GRID_H):
            row = f"{y % 10} "
            for x in range(self.GRID_W):
                row += markers.get((x, y), ".")
            rows.append(row)

        p1, p2 = self._players[0], self._players[1]
        score_line = (
            f"  {p1.username}: {self._scores[p1.user_id]}  |  "
            f"{p2.username}: {self._scores[p2.user_id]}  |  "
            f"Relics left: {len(self._relics)}"
        )
        rows.append(score_line)
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
