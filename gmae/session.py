"""GameSession, AdventureState, AdventureResult — GMAE Core.

Manages a single play session between two players and one mini-adventure.
"""

from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from typing import Optional, List
from gmae.enums import AdventureStatus
from gmae.profile import PlayerProfile
from gmae.interfaces import IMiniAdventure
from gmae.entities import Entity
from gmae.reused.ellis.world_time import WorldTime
from gmae.reused.ellis.world_clock import WorldClock


@dataclass
class AdventureState:
    turn_count: int = 0
    entities: List[Entity] = field(default_factory=list)
    objectives: List[str] = field(default_factory=list)
    time_remaining: int = 0
    messages: List[str] = field(default_factory=list)


@dataclass
class AdventureResult:
    winner: Optional[PlayerProfile] = None
    duration_turns: int = 0
    completed_at: Optional[WorldTime] = None
    summary: str = ""


class GameSession:
    def __init__(self, player1: PlayerProfile, player2: PlayerProfile,
                 adventure: IMiniAdventure):
        self.session_id = str(uuid.uuid4())[:8]
        self.player1 = player1
        self.player2 = player2
        self.adventure = adventure
        self.status = AdventureStatus.NOT_STARTED
        self.clock = WorldClock()
        self.start_time = self.clock.current_time
        self.result: Optional[AdventureResult] = None
        self._turn_count = 0

    def start(self) -> None:
        self.status = AdventureStatus.IN_PROGRESS
        self.adventure.initialize(self)

    def process_turn(self, p1_action: str, p2_action: str) -> list[str]:
        """Process one full turn: both player actions + adventure advancement."""
        messages = []
        msg1 = self.adventure.accept_input(1, p1_action)
        messages.append(f"P1: {msg1}")
        msg2 = self.adventure.accept_input(2, p2_action)
        messages.append(f"P2: {msg2}")

        turn_events = self.adventure.advance_turn()
        messages.extend(turn_events)

        self._turn_count += 1
        self.clock.advance(10)

        self.status = self.adventure.check_completion()
        return messages

    def end(self) -> AdventureResult:
        self.result = AdventureResult(
            duration_turns=self._turn_count,
            completed_at=self.clock.current_time,
        )
        if self.status == AdventureStatus.WIN:
            state = self.adventure.get_state()
            self.result.summary = "Adventure completed successfully!"
        elif self.status == AdventureStatus.LOSE:
            self.result.summary = "Adventure failed."
        elif self.status == AdventureStatus.DRAW:
            self.result.summary = "The adventure ended in a draw."
        else:
            self.result.summary = "Adventure ended."
        return self.result

    @property
    def turn_count(self) -> int:
        return self._turn_count

    def __str__(self) -> str:
        return (f"Session {self.session_id}: {self.player1.display_name} & "
                f"{self.player2.display_name} playing {self.adventure.name} "
                f"[{self.status.value}]")
