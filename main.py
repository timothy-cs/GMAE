#!/usr/bin/env python3
"""GuildQuest Mini-Adventure Environment (GMAE) — Main Entry Point.

Run this file to start the GMAE. Two local players create profiles,
choose a mini-adventure, and play through it turn-by-turn in the terminal.

Usage:
    python main.py
"""

from __future__ import annotations
import os
import sys

from gmae.engine import GMEngine
from gmae.profile import PlayerProfile
from gmae.enums import AdventureStatus
from gmae.reused.ghalib.realm import REALMS
from gmae.reused.ghalib.character import Character
from gmae.observer import game_events
from gmae.security import AccessControl

# Adventure implementations
from gmae.adventures.escort_adventure import EscortAdventure
from gmae.adventures.relic_hunt_adventure import RelicHuntAdventure


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def print_banner() -> None:
    print("=" * 60)
    print("   GuildQuest Mini-Adventure Environment (GMAE)")
    print("=" * 60)
    print()


def input_safe(prompt: str) -> str:
    """Read input safely, stripping whitespace."""
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye!")
        sys.exit(0)


# ── Observer: log events to console ──────────────────────────
def _log_event(**kwargs):
    details = ", ".join(f"{k}={v}" for k, v in kwargs.items())
    print(f"  [EVENT] {details}")


game_events.subscribe("adventure_completed", _log_event)


# ── Profile creation ─────────────────────────────────────────
CHARACTER_CLASSES = ["Warrior", "Mage", "Ranger", "Rogue", "Cleric"]
REALM_CHOICES = list(REALMS.values())


def create_profile(player_label: str) -> PlayerProfile:
    print(f"\n--- {player_label} Profile Setup ---")
    raw_name = input_safe("  Enter your display name: ")
    display_name = PlayerProfile.sanitize_name(raw_name)
    if display_name != raw_name:
        print(f"  (Name sanitized to: {display_name})")

    # Character class
    print("  Choose a character class:")
    for i, cls in enumerate(CHARACTER_CLASSES, 1):
        print(f"    [{i}] {cls}")
    while True:
        choice = input_safe("  Class number: ")
        if choice.isdigit() and 1 <= int(choice) <= len(CHARACTER_CLASSES):
            char_class = CHARACTER_CLASSES[int(choice) - 1]
            break
        print("  Invalid choice, try again.")

    # Preferred realm
    print("  Choose your preferred realm:")
    for i, realm in enumerate(REALM_CHOICES, 1):
        print(f"    [{i}] {realm.name} — {realm.description}")
    while True:
        choice = input_safe("  Realm number: ")
        if choice.isdigit() and 1 <= int(choice) <= len(REALM_CHOICES):
            pref_realm = REALM_CHOICES[int(choice) - 1]
            break
        print("  Invalid choice, try again.")

    character = Character(
        character_id=display_name.lower().replace(" ", "_"),
        name=display_name,
        character_class=char_class,
        level=1,
    )
    profile = PlayerProfile(
        display_name=display_name,
        preferred_realm=pref_realm,
        character=character,
    )
    print(f"  Profile created: {profile}")
    return profile


# ── Game loop ─────────────────────────────────────────────────
def run_game_loop(engine: GMEngine) -> None:
    clear_screen()
    print_banner()
    # Create profiles
    p1 = create_profile("Player 1")
    p2 = create_profile("Player 2")
    while True:
        # Show adventure menu
        print(engine.menu.display())
        while True:
            choice = input_safe("Select an adventure (number): ")
            if choice.isdigit():
                adventure = engine.menu.select(int(choice))
                if adventure:
                    break
            print("Invalid selection, try again.")

        # Start session
        session = engine.start_session(p1, p2, adventure)
        print(f"\n  Starting: {adventure.name}")
        print(f"  Players: {p1.display_name} & {p2.display_name}")
        input_safe("\n  Press Enter to begin...")

        # Turn loop
        while session.status == AdventureStatus.IN_PROGRESS:
            clear_screen()
            print(adventure.render())
            print()

            # Show valid actions
            p1_actions = adventure.get_valid_actions(1)
            p2_actions = adventure.get_valid_actions(2)
            print(f"  P1 actions: {', '.join(p1_actions)}")
            print(f"  P2 actions: {', '.join(p2_actions)}")
            print()

            # Access control check
            ac_err = AccessControl.validate_session_action(session.status, 1)
            if ac_err:
                print(f"  {ac_err}")
                break

            # Get inputs
            p1_action = input_safe(f"  [{p1.display_name}] Action: ")
            p2_action = input_safe(f"  [{p2.display_name}] Action: ")

            # Process turn
            messages = session.process_turn(p1_action, p2_action)
            print()
            for msg in messages:
                print(f"  {msg}")
            input_safe("\n  Press Enter for next turn...")

        # Show results
        clear_screen()
        print(adventure.render())
        result = session.end()
        print(f"\n{'=' * 50}")
        print(f"  ADVENTURE OVER — {session.status.value}")
        print(f"  {result.summary}")
        print(f"  Duration: {result.duration_turns} turns")
        if result.completed_at:
            print(f"  World time: {result.completed_at}")

        # Adventure-specific results
        if hasattr(adventure, '_real'):
            real_adv = adventure._real  # type: ignore[attr-defined]
        else:
            real_adv = adventure

        if hasattr(real_adv, 'get_winner'):
            winner_num = real_adv.get_winner()
            if winner_num == 1:
                print(f"  Winner: {p1.display_name}!")
                p1.add_achievement(f"Won {real_adv.name}")
            elif winner_num == 2:
                print(f"  Winner: {p2.display_name}!")
                p2.add_achievement(f"Won {real_adv.name}")
            else:
                print("  It's a draw!")
        elif session.status == AdventureStatus.WIN:
            print(f"  Both players win! Great teamwork!")
            p1.add_achievement(f"Completed {real_adv.name}")
            p2.add_achievement(f"Completed {real_adv.name}")

        # Update quest histories
        p1.update_history(adventure.name)
        p2.update_history(adventure.name)

        print(f"\n  {p1.display_name}: {p1.achievements}")
        print(f"  {p2.display_name}: {p2.achievements}")
        print(f"{'=' * 50}")

        # Play again?
        again = input_safe("\n  Play again? (y/n): ")
        if again.lower() not in ("y", "yes"):
            print("\n  Thanks for playing GuildQuest! Farewell, adventurers.\n")
            break


# ── Main ──────────────────────────────────────────────────────
def main() -> None:
    engine = GMEngine()

    # Register available mini-adventures
    engine.register_adventure(EscortAdventure(
        realm=REALMS["verdant_grove"], max_turns=30, num_hazards=3, num_items=3,
    ))
    engine.register_adventure(RelicHuntAdventure(
        realm=REALMS["crystal_caverns"], target_score=30, max_turns=40,
        num_relics=10, num_hazards=2,
    ))

    run_game_loop(engine)


if __name__ == "__main__":
    main()
