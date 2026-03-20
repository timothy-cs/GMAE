"""GMEngine — GMAE Core.

The main engine that orchestrates the GuildQuest Mini-Adventure Environment.
Manages adventure registration, player profiles, sessions, and the game loop.
"""

from __future__ import annotations
from typing import List, Optional
from gmae.interfaces import IMiniAdventure
from gmae.menu import MiniAdventureMenu
from gmae.session import GameSession
from gmae.profile import PlayerProfile
from gmae.security import InputValidationProxy
from gmae.observer import game_events


class GMEngine:
    def __init__(self) -> None:
        self._menu = MiniAdventureMenu()
        self._sessions: List[GameSession] = []

    @property
    def menu(self) -> MiniAdventureMenu:
        return self._menu

    def register_adventure(self, adventure: IMiniAdventure) -> None:
        """Register a mini-adventure, wrapping it with the input validation proxy."""
        wrapped = InputValidationProxy(adventure)
        self._menu.register(wrapped)
        game_events.publish("adventure_registered", name=adventure.name)

    def start_session(self, player1: PlayerProfile, player2: PlayerProfile,
                      adventure: IMiniAdventure) -> GameSession:
        session = GameSession(player1, player2, adventure)
        self._sessions.append(session)
        session.start()
        game_events.publish("session_started",
                            session_id=session.session_id,
                            p1=player1.display_name,
                            p2=player2.display_name,
                            adventure=adventure.name)
        return session

    @property
    def sessions(self) -> List[GameSession]:
        return list(self._sessions)
