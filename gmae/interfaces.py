"""IMiniAdventure interface — the core abstraction all mini-adventures implement.

Design Pattern: Strategy Pattern
Each mini-adventure is a concrete strategy implementing the IMiniAdventure interface.
The GameSession delegates adventure-specific logic to whichever adventure was selected,
enabling the GMAE to run any adventure without knowing its internals.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gmae.session import GameSession, AdventureState
    from gmae.enums import AdventureStatus


class IMiniAdventure(ABC):
    """Interface that all mini-adventures must implement."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of this mini-adventure."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Short description shown in the adventure menu."""
        ...

    @property
    @abstractmethod
    def mode(self) -> str:
        """'co-op' or 'competitive'."""
        ...

    @abstractmethod
    def initialize(self, session: GameSession) -> None:
        """Set up the adventure for the given session (place entities, set objectives)."""
        ...

    @abstractmethod
    def accept_input(self, player_number: int, action: str) -> str:
        """Process a player action. Returns feedback message."""
        ...

    @abstractmethod
    def advance_turn(self) -> list[str]:
        """Advance the adventure by one turn (NPC/hazard AI, time progression).
        Returns a list of event messages."""
        ...

    @abstractmethod
    def get_state(self) -> AdventureState:
        """Return the current adventure state for display."""
        ...

    @abstractmethod
    def check_completion(self) -> AdventureStatus:
        """Check whether the adventure is completed. Returns the current status."""
        ...

    @abstractmethod
    def reset(self) -> None:
        """Reset the adventure to its initial state."""
        ...

    @abstractmethod
    def render(self) -> str:
        """Return a string rendering of the current game board/state for display."""
        ...

    @abstractmethod
    def get_valid_actions(self, player_number: int) -> list[str]:
        """Return the list of valid actions for the given player."""
        ...
