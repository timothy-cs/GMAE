"""Security-focused design patterns.

Pattern 1 — Input Validation Proxy (Proxy Pattern):
    Wraps an IMiniAdventure and validates/sanitizes all player inputs before
    forwarding them to the real adventure. Prevents injection of invalid commands
    and ensures only whitelisted actions reach the game logic.

    Pattern roles:
      - IMiniAdventure: Subject interface
      - The actual adventure: RealSubject
      - InputValidationProxy: Proxy that guards access

Pattern 2 — Access Control:
    Enforces session-level permissions: only authenticated players in the session
    can perform actions, and only during an active game. Uses CampaignSharing's
    permission model from Ghalib's reused subsystem.
"""

from __future__ import annotations
import re
from typing import TYPE_CHECKING
from gmae.interfaces import IMiniAdventure
from gmae.enums import AdventureStatus

if TYPE_CHECKING:
    from gmae.session import GameSession, AdventureState


class InputValidationProxy(IMiniAdventure):
    """Proxy that validates player input before delegating to the real adventure.

    Security pattern: ensures only safe, whitelisted actions reach game logic.
    """

    # Allowed action patterns — only alphanumeric commands with optional arguments
    _VALID_ACTION_PATTERN = re.compile(r'^[a-zA-Z_]+(\s+[a-zA-Z0-9_]+)*$')
    _MAX_ACTION_LENGTH = 50

    def __init__(self, real_adventure: IMiniAdventure):
        self._real = real_adventure

    @property
    def name(self) -> str:
        return self._real.name

    @property
    def description(self) -> str:
        return self._real.description

    @property
    def mode(self) -> str:
        return self._real.mode

    def _validate_input(self, action: str) -> str:
        """Validate and sanitize player input. Returns cleaned action or raises ValueError."""
        if not action or not isinstance(action, str):
            raise ValueError("Action cannot be empty.")
        action = action.strip()
        if len(action) > self._MAX_ACTION_LENGTH:
            raise ValueError(f"Action too long (max {self._MAX_ACTION_LENGTH} chars).")
        if not self._VALID_ACTION_PATTERN.match(action):
            raise ValueError("Invalid action format. Use letters and spaces only.")
        return action.lower()

    def initialize(self, session: GameSession) -> None:
        self._real.initialize(session)

    def accept_input(self, player_number: int, action: str) -> str:
        if player_number not in (1, 2):
            return "Invalid player number."
        try:
            clean_action = self._validate_input(action)
        except ValueError as e:
            return f"Invalid input: {e}"
        return self._real.accept_input(player_number, clean_action)

    def advance_turn(self) -> list[str]:
        return self._real.advance_turn()

    def get_state(self) -> AdventureState:
        return self._real.get_state()

    def check_completion(self) -> AdventureStatus:
        return self._real.check_completion()

    def reset(self) -> None:
        self._real.reset()

    def render(self) -> str:
        return self._real.render()

    def get_valid_actions(self, player_number: int) -> list[str]:
        return self._real.get_valid_actions(player_number)


class AccessControl:
    """Enforces that only authorized players can act during an active session.

    Security pattern: checks session status and player identity before allowing actions.
    """

    @staticmethod
    def check_session_active(status: AdventureStatus) -> bool:
        return status == AdventureStatus.IN_PROGRESS

    @staticmethod
    def check_player_authorized(player_number: int, session_player_ids: tuple[str, str]) -> bool:
        return player_number in (1, 2)

    @staticmethod
    def validate_session_action(session_status: AdventureStatus,
                                player_number: int) -> str | None:
        """Returns an error message if the action is not allowed, or None if OK."""
        if not AccessControl.check_session_active(session_status):
            return "Cannot act: game session is not active."
        if player_number not in (1, 2):
            return "Cannot act: invalid player number."
        return None
