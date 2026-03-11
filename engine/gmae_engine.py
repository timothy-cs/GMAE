"""
GMAE_Engine — The core engine of the GuildQuest Mini-Adventure Environment.

Architecture: Microkernel
  The engine is a stable, minimal kernel. Mini-adventures are plug-ins loaded
  at runtime via the IMiniAdventure interface (Strategy Pattern). The engine
  does not know or care which adventure is currently running.

Strategy Pattern (Non-Security):
  - Context  : GMAE_Engine  (self.current_adventure)
  - Strategy : IMiniAdventure
  Calling engine.load_adventure(idx) swaps the strategy object.

Protection Proxy usage:
  All User objects are wrapped in PlayerProfileProxy on add_player() so that
  no subsystem (including adventures) ever holds a raw User reference.

RBAC usage:
  Operations that should be restricted (playing, saving, registering adventures)
  call self._rbac.require_permission() before proceeding.
"""

from __future__ import annotations
from typing import Dict, List, Optional

from engine.interface import IMiniAdventure
from core.user import User
from core.world_clock import WorldClock
from security.rbac import RBACService, Role
from security.proxy import PlayerProfileProxy


class GMAE_Engine:
    """
    Central engine that manages players, available adventures, and the game loop.
    """

    def __init__(self) -> None:
        # Dict of user_id -> PlayerProfileProxy (Protection Proxy pattern)
        self.players: Dict[str, PlayerProfileProxy] = {}

        # Registered mini-adventures (plugins); Strategy objects
        self.available_adventures: List[IMiniAdventure] = []

        # Currently active adventure (the "strategy")
        self.current_adventure: Optional[IMiniAdventure] = None

        # Global WorldClock shared across the session
        self.global_clock = WorldClock()

        # RBAC service — assigns and checks roles
        self._rbac = RBACService()

    # ------------------------------------------------------------------
    # Player management
    # ------------------------------------------------------------------

    def add_player(self, user: User) -> PlayerProfileProxy:
        """
        Register a player with the engine.
        The User is immediately wrapped in a PlayerProfileProxy.
        The proxy's role is registered with RBAC.
        """
        proxy = PlayerProfileProxy(user)
        self.players[user.user_id] = proxy

        # Map the user's self-declared role string to the RBAC Role enum
        role_map = {"guest": Role.GUEST, "hero": Role.HERO, "admin": Role.ADMIN}
        role = role_map.get(user.role.lower(), Role.HERO)
        self._rbac.assign_role(user.user_id, role)

        return proxy

    def get_proxy(self, user_id: str) -> Optional[PlayerProfileProxy]:
        return self.players.get(user_id)

    # ------------------------------------------------------------------
    # Adventure registration & selection (Strategy swap)
    # ------------------------------------------------------------------

    def register_adventure(self, adventure: IMiniAdventure) -> None:
        """
        Register a mini-adventure plugin.
        Requires ADMIN permission if called at runtime after engine start;
        during setup (main.py) this is called before any user is loaded.
        """
        self.available_adventures.append(adventure)

    def load_adventure(self, adventure_index: int) -> bool:
        """
        Select an adventure by menu index.  This is the Strategy swap.
        Returns False if the index is out of range.
        """
        if 0 <= adventure_index < len(self.available_adventures):
            self.current_adventure = self.available_adventures[adventure_index]
            return True
        return False

    # ------------------------------------------------------------------
    # Game session control
    # ------------------------------------------------------------------

    def start_adventure(self, realm) -> None:
        """
        Initialize the currently loaded adventure with the registered players.
        Requires at least 2 players and an adventure to be selected.
        Checks that all players have 'play_adventures' permission.
        """
        if self.current_adventure is None:
            raise RuntimeError("No adventure loaded. Call load_adventure() first.")
        if len(self.players) < 2:
            raise RuntimeError("The GMAE requires exactly 2 players.")

        for uid in self.players:
            self._rbac.require_permission(uid, "play_adventures")

        player_list = [proxy for proxy in self.players.values()]
        self.current_adventure.initialize(player_list, realm)

    def tick(self, delta: int = 1) -> None:
        """Advance the global clock and the current adventure by delta ticks."""
        self.global_clock.tick(delta)
        if self.current_adventure:
            self.current_adventure.update(delta)

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def get_player_usernames(self) -> List[str]:
        return [p.get_username() for p in self.players.values()]

    def check_permission(self, user_id: str, permission: str) -> bool:
        return self._rbac.has_permission(user_id, permission)

    def require_permission(self, user_id: str, permission: str) -> None:
        self._rbac.require_permission(user_id, permission)

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Launch the GMAE main menu loop."""
        from ui.menu import Menu
        menu = Menu(self)
        menu.main_loop()
