"""
IMiniAdventure — The GMAE extensibility interface.

Every mini-adventure must implement this abstract base class.  The GMAE_Engine
holds a reference of type IMiniAdventure and calls its methods without knowing
which concrete adventure is running — this is the Strategy Pattern.

Strategy Pattern (Non-Security):
  - Context  : GMAE_Engine  (holds self.current_adventure: IMiniAdventure)
  - Strategy : IMiniAdventure  (this interface)
  - Concrete : RelicHunt, EscortQuest  (and any future adventure plugins)
  Swapping adventures at runtime is a single assignment:
      engine.current_adventure = some_other_adventure

HOW TO ADD A NEW MINI-ADVENTURE
================================
1. Create a new Python file in adventures/ (e.g., adventures/dungeon_run.py).
2. Define a class that extends IMiniAdventure and implement all six abstract
   methods: initialize, handle_input, update, check_completion, get_status,
   and reset. Also provide the name and description properties.
3. In main.py, import your class and call engine.register_adventure(DungeonRun()).
4. The engine's menu will automatically list it — no other changes needed.

Interface capabilities:
  initialize(players, realm)  — set up the adventure
  handle_input(player_id, action, **kwargs) → str  — process one player action
  update(delta_time)          — advance game logic (time/turn-based)
  check_completion() → bool   — true when the adventure is over
  get_status() → dict         — snapshot for the UI to display
  reset()                     — restore to initial state
  name (property)             — human-readable title shown in menu
  description (property)      — one-line description shown in menu
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List


class IMiniAdventure(ABC):
    """
    Abstract base class for all GMAE mini-adventures.

    Implementing this interface is the only requirement to add a new
    mini-adventure to the GMAE.  See module docstring for step-by-step
    instructions.
    """

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    @abstractmethod
    def initialize(self, players: List, realm: Any) -> None:
        """
        Set up the adventure environment.

        Args:
            players : List of PlayerProfileProxy objects (one per player).
            realm   : A RealmAdapter providing the game grid and local time.
        """

    @abstractmethod
    def reset(self) -> None:
        """Restore the adventure to its initial state so it can be replayed."""

    # ------------------------------------------------------------------
    # Per-turn logic
    # ------------------------------------------------------------------

    @abstractmethod
    def handle_input(self, player_id: str, action: str, **kwargs: Any) -> str:
        """
        Process a single player action.

        Args:
            player_id : The user_id of the acting player.
            action    : A string command (e.g., "w", "e", "attack").
            **kwargs  : Optional extra data (e.g., target coordinates).

        Returns:
            A human-readable message describing the result of the action.
        """

    @abstractmethod
    def update(self, delta_time: int = 1) -> None:
        """
        Advance game logic by delta_time ticks.

        For turn-based adventures this is typically a no-op (logic lives in
        handle_input). For real-time adventures, this drives AI movement,
        timers, and world events.
        """

    # ------------------------------------------------------------------
    # State queries
    # ------------------------------------------------------------------

    @abstractmethod
    def check_completion(self) -> bool:
        """Return True when the adventure has ended (win, lose, or draw)."""

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """
        Return a dict snapshot of the current game state.

        The dict must always include at minimum:
            "adventure"    : str  — adventure name
            "done"         : bool — whether the adventure has ended
            "last_message" : str  — most recent event/action message
        Additional keys are adventure-specific.
        """

    # ------------------------------------------------------------------
    # Metadata (properties)
    # ------------------------------------------------------------------

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable title shown in the mini-adventure selection menu."""

    @property
    @abstractmethod
    def description(self) -> str:
        """One-line description shown below the title in the menu."""
