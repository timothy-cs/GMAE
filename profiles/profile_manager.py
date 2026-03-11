"""
ProfileManager — Player profile creation and persistence.

Handles interactive profile setup for two local players: entering a username,
creating a character (name + class), and optionally loading a saved profile
from a lightweight JSON file.

Persistence uses the standard library json module — no external dependencies.
Saved profiles live in profiles/saves/ relative to the project root.
"""

from __future__ import annotations
import json
import os
from typing import Optional

from core.user import User
from core.character import CLASS_TYPES

# Directory where profile JSON files are stored
_SAVE_DIR = os.path.join(os.path.dirname(__file__), "saves")


def _ensure_save_dir() -> None:
    os.makedirs(_SAVE_DIR, exist_ok=True)


def _profile_path(username: str) -> str:
    safe = "".join(c for c in username if c.isalnum() or c in "-_")
    return os.path.join(_SAVE_DIR, f"{safe}.json")


# ------------------------------------------------------------------
# Save / Load
# ------------------------------------------------------------------

def save_profile(user: User) -> None:
    """Persist a User's profile to a JSON file."""
    _ensure_save_dir()
    data: dict = {
        "user_id": user.user_id,
        "username": user.username,
        "role": user.role,
        "preferences": {
            "theme": user.preferences.theme,
            "time_display": user.preferences.time_display,
            "current_realm_id": user.preferences.current_realm_id,
        },
        "history": {
            "completed_quests": user.history.completed_quests,
            "achievements": user.history.achievements,
        },
        "characters": [
            {
                "name": c.name,
                "class_type": c.class_type,
                "level": c.level,
            }
            for c in user.characters
        ],
        "active_character": (
            user.active_character.name if user.active_character else None
        ),
    }
    with open(_profile_path(user.username), "w") as f:
        json.dump(data, f, indent=2)


def load_profile(username: str) -> Optional[User]:
    """Load a User profile from disk. Returns None if not found."""
    path = _profile_path(username)
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            data = json.load(f)
        user = User(data["user_id"], data["username"], data.get("role", "hero"))
        prefs = data.get("preferences", {})
        user.preferences.theme = prefs.get("theme", "classic")
        user.preferences.time_display = prefs.get("time_display", "world")
        user.preferences.current_realm_id = prefs.get("current_realm_id")
        hist = data.get("history", {})
        for q in hist.get("completed_quests", []):
            user.history.add_completed_quest(q)
        for a in hist.get("achievements", []):
            user.history.add_achievement(a)
        for c_data in data.get("characters", []):
            try:
                user.create_character(
                    c_data["name"], c_data.get("class_type", "Warrior"), c_data.get("level", 1)
                )
            except ValueError:
                pass  # skip malformed character entries
        active_name = data.get("active_character")
        if active_name:
            user.set_active_character(active_name)
        return user
    except (json.JSONDecodeError, KeyError):
        return None


# ------------------------------------------------------------------
# Interactive setup
# ------------------------------------------------------------------

def setup_player(player_number: int) -> User:
    """
    Interactively collect profile information for one player.
    Tries to load an existing profile first; falls back to creating a new one.
    """
    print(f"\n{'='*40}")
    print(f"  PLAYER {player_number} SETUP")
    print(f"{'='*40}")

    username = _prompt_non_empty("Enter your username: ").strip()

    # Try to load existing profile
    existing = load_profile(username)
    if existing:
        print(f"\n  Welcome back, {existing.username}!")
        print(existing.get_profile_summary())
        choice = input("  Load this profile? (y/n): ").strip().lower()
        if choice == "y":
            return existing

    # Create a new profile
    import uuid
    user_id = str(uuid.uuid4())[:8]
    user = User(user_id, username, role="hero")

    print(f"\n  Creating new profile for '{username}'...")
    char_name = _prompt_non_empty("  Character name: ").strip()

    print(f"  Class options: {', '.join(CLASS_TYPES)}")
    class_type = _prompt_choice("  Choose class: ", CLASS_TYPES)

    user.create_character(char_name, class_type, level=1)
    print(f"  Character created: {user.active_character}")

    save_profile(user)
    print(f"  Profile saved!")
    return user


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _prompt_non_empty(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("  Input cannot be empty. Please try again.")


def _prompt_choice(prompt: str, options: list) -> str:
    normalized = [o.lower() for o in options]
    while True:
        value = input(prompt).strip()
        if value.lower() in normalized:
            return options[normalized.index(value.lower())]
        print(f"  Please choose one of: {', '.join(options)}")
