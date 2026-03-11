"""
Menu — Main UI loop for the GMAE.

Handles:
  1. Title screen
  2. Two-player profile setup (via ProfileManager)
  3. Adventure selection menu
  4. The in-game turn loop (alternating player inputs per round)
  5. Post-game summary and play-again flow

Two-player local input model:
  Each "round" Player 1 enters their action, then Player 2 enters theirs.
  After both inputs the grid is re-rendered and the next round begins.
  This keeps the game playable on a single shared keyboard/terminal.
"""

from __future__ import annotations
import os
from typing import TYPE_CHECKING

from adapters.realm_adapter import RealmAdapter
from profiles.profile_manager import setup_player, save_profile

if TYPE_CHECKING:
    from engine.gmae_engine import GMAE_Engine


def _clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def _banner() -> None:
    print("=" * 60)
    print("    ██████╗ ███╗   ███╗ █████╗ ███████╗")
    print("   ██╔════╝ ████╗ ████║██╔══██╗██╔════╝")
    print("   ██║  ███╗██╔████╔██║███████║█████╗  ")
    print("   ██║   ██║██║╚██╔╝██║██╔══██║██╔══╝  ")
    print("   ╚██████╔╝██║ ╚═╝ ██║██║  ██║███████╗")
    print("    ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝")
    print()
    print("  GuildQuest Mini-Adventure Environment (GMAE)")
    print("  INF 122 — Final Project")
    print("=" * 60)


class Menu:
    """Main menu controller wired to a GMAE_Engine instance."""

    def __init__(self, engine: "GMAE_Engine") -> None:
        self._engine = engine

    # ------------------------------------------------------------------
    # Top-level loop
    # ------------------------------------------------------------------

    def main_loop(self) -> None:
        _clear()
        _banner()

        # Step 1: Set up two player profiles
        print("\n  Welcome to the GuildQuest Mini-Adventure Environment!")
        print("  Two players are required to play.\n")
        input("  Press ENTER to begin player setup...")

        self._setup_players()

        # Step 2: Adventure selection + play loop
        while True:
            _clear()
            _banner()
            self._show_player_profiles()

            choice = self._adventure_menu()
            if choice == "quit":
                self._quit()
                return

            # Load selected adventure
            self._engine.load_adventure(choice)
            realm = self._create_realm_for_adventure(choice)

            try:
                self._engine.start_adventure(realm)
            except PermissionError as e:
                print(f"\n  Access denied: {e}")
                input("  Press ENTER to return to menu...")
                continue

            # Play the adventure
            self._play_adventure()

            # Post-game
            if not self._ask_play_again():
                self._quit()
                return

    # ------------------------------------------------------------------
    # Player setup
    # ------------------------------------------------------------------

    def _setup_players(self) -> None:
        from core.user import User

        p1_user = setup_player(1)
        p2_user = setup_player(2)

        self._engine.add_player(p1_user)
        self._engine.add_player(p2_user)

        self._p1_id = p1_user.user_id
        self._p2_id = p2_user.user_id

        print(f"\n  Players ready: {p1_user.username}  vs  {p2_user.username}")
        input("  Press ENTER to continue...")

    # ------------------------------------------------------------------
    # Adventure menu
    # ------------------------------------------------------------------

    def _adventure_menu(self) -> int | str:
        adventures = self._engine.available_adventures
        print("\n  ┌─────────────────────────────────────────┐")
        print("  │         MINI-ADVENTURE MENU             │")
        print("  └─────────────────────────────────────────┘")
        for i, adv in enumerate(adventures):
            print(f"  [{i + 1}] {adv.name}")
            print(f"       {adv.description}")
        print(f"  [Q] Quit")
        print()

        while True:
            raw = input("  Select an adventure: ").strip().lower()
            if raw == "q":
                return "quit"
            if raw.isdigit():
                idx = int(raw) - 1
                if 0 <= idx < len(adventures):
                    return idx
            print(f"  Invalid choice. Enter 1–{len(adventures)} or Q.")

    # ------------------------------------------------------------------
    # In-game loop
    # ------------------------------------------------------------------

    def _play_adventure(self) -> None:
        engine = self._engine
        adventure = engine.current_adventure
        proxies = list(engine.players.values())
        p1_proxy = proxies[0]
        p2_proxy = proxies[1]

        self._print_controls(adventure.name)
        input("  Press ENTER to start...")

        abandoned = False
        while not adventure.check_completion():
            _clear()
            print(f"\n  === {adventure.name} ===")
            print()

            # Render the grid if the adventure supports it
            if hasattr(adventure, "render"):
                print(adventure.render())
            print()

            # Player 1 input
            p1_action = input(
                f"  {p1_proxy.username} (P1) action [or 'q' to quit]: "
            ).strip()
            if p1_action.lower() in ("q", "quit"):
                abandoned = True
                break
            msg1 = adventure.handle_input(p1_proxy.user_id, p1_action)
            print(f"  → {msg1}")

            if adventure.check_completion():
                break

            # Player 2 input
            p2_action = input(
                f"  {p2_proxy.username} (P2) action [or 'q' to quit]: "
            ).strip()
            if p2_action.lower() in ("q", "quit"):
                abandoned = True
                break
            msg2 = adventure.handle_input(p2_proxy.user_id, p2_action)
            print(f"  → {msg2}")

        if abandoned:
            print("\n  Adventure abandoned. Returning to menu...")
            adventure.reset()
            input("  Press ENTER to continue...")
            return

        # Adventure over — show result
        _clear()
        print(f"\n  === {adventure.name} — GAME OVER ===\n")
        if hasattr(adventure, "render"):
            print(adventure.render())
        print()
        status = adventure.get_status()
        print(f"  {status.get('last_message', '')}")
        print()

        # Award achievements and save profiles
        self._post_game_awards(status)
        for proxy in proxies:
            save_profile(proxy.get_user())

        input("  Press ENTER to continue...")

    # ------------------------------------------------------------------
    # Post-game
    # ------------------------------------------------------------------

    def _post_game_awards(self, status: dict) -> None:
        """Grant achievements and quest completions based on outcome."""
        proxies = list(self._engine.players.values())
        adventure_name = status.get("adventure", "Adventure")

        winner_name = status.get("winner")  # RelicHunt
        won = status.get("won")  # EscortQuest

        for proxy in proxies:
            proxy.record_quest_completion(adventure_name)

            if winner_name and proxy.username == winner_name:
                proxy.award_achievement(f"Relic Hunter — Won {adventure_name}")
            if won is True:
                proxy.award_achievement(f"Guardian — Completed {adventure_name}")

    def _ask_play_again(self) -> bool:
        while True:
            raw = input("  Play again? (y/n): ").strip().lower()
            if raw == "y":
                # Reset the current adventure
                if self._engine.current_adventure:
                    self._engine.current_adventure.reset()
                return True
            if raw == "n":
                return False

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _show_player_profiles(self) -> None:
        print()
        for proxy in self._engine.players.values():
            print(f"  {proxy.get_profile_summary()}")
            print()

    def _create_realm_for_adventure(self, adventure_index: int) -> RealmAdapter:
        """Create an appropriate realm for the selected adventure."""
        realm_configs = [
            ("realm_relic",  "The Shattered Wastes",  "A barren field littered with ancient relics.", 0),
            ("realm_escort", "The Verdant Crossing",  "A dangerous forest road leading to sanctuary.", 60),
        ]
        if adventure_index < len(realm_configs):
            rid, rname, rdesc, offset = realm_configs[adventure_index]
        else:
            rid, rname, rdesc, offset = "realm_default", "The Unknown Realm", "", 0

        return RealmAdapter.create(
            realm_id=rid,
            name=rname,
            description=rdesc,
            offset_minutes=offset,
            grid_width=8,
            grid_height=8,
        )

    def _print_controls(self, adventure_name: str) -> None:
        print(f"\n  Controls for {adventure_name}:")
        print("  ┌──────────────────────────────────────────────┐")
        print("  │ Player 1  │  W=up  A=left  S=down  D=right  │")
        print("  │           │  E = collect / push NPC         │")
        print("  ├──────────────────────────────────────────────┤")
        print("  │ Player 2  │  I=up  J=left  K=down  L=right  │")
        print("  │           │  U = collect / push NPC         │")
        print("  └──────────────────────────────────────────────┘")

    def _quit(self) -> None:
        _clear()
        _banner()
        print("\n  Thanks for playing GuildQuest! Farewell, heroes.\n")
