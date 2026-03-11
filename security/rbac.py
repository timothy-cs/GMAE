"""
RBACService — Role-Based Access Control (Security Pattern).

Controls what operations users are permitted to perform in the GMAE based on
their assigned role. Roles are assigned once at login and checked before any
sensitive operation (playing adventures, saving profiles, registering adventures).

Security design rationale:
  - Separates authorization logic from business logic.
  - A "Guest" account can browse the menu but cannot play or save progress.
  - A "Hero" (logged-in player) has full gameplay permissions.
  - An "Admin" can additionally register new adventures at runtime.
  - Permission strings are checked via require_permission(); failed checks
    raise PermissionError so callers handle the error explicitly rather than
    silently ignoring denied operations.

Used by : GMAE_Engine, Menu (login flow), ProfileManager
"""

from __future__ import annotations
from enum import Enum
from typing import Dict, Set


class Role(Enum):
    GUEST = "guest"
    HERO = "hero"
    ADMIN = "admin"


# Permissions granted to each role (additive, not inherited)
ROLE_PERMISSIONS: Dict[Role, Set[str]] = {
    Role.GUEST: {
        "view_adventure_menu",
        "view_leaderboard",
    },
    Role.HERO: {
        "view_adventure_menu",
        "view_leaderboard",
        "play_adventures",
        "save_profile",
        "view_quest_history",
        "edit_character",
        "create_character",
    },
    Role.ADMIN: {
        "view_adventure_menu",
        "view_leaderboard",
        "play_adventures",
        "save_profile",
        "view_quest_history",
        "edit_character",
        "create_character",
        "register_adventure",
        "manage_users",
    },
}


class RBACService:
    """
    Manages user roles and checks permissions.

    Typical usage:
        rbac = RBACService()
        rbac.assign_role("u1", Role.HERO)
        rbac.require_permission("u1", "play_adventures")  # no-op if allowed
        rbac.require_permission("u1", "manage_users")     # raises PermissionError
    """

    def __init__(self) -> None:
        self._user_roles: Dict[str, Role] = {}

    # ------------------------------------------------------------------
    # Role management
    # ------------------------------------------------------------------

    def assign_role(self, user_id: str, role: Role) -> None:
        self._user_roles[user_id] = role

    def get_role(self, user_id: str) -> Role:
        return self._user_roles.get(user_id, Role.GUEST)

    # ------------------------------------------------------------------
    # Permission checks
    # ------------------------------------------------------------------

    def has_permission(self, user_id: str, permission: str) -> bool:
        role = self.get_role(user_id)
        return permission in ROLE_PERMISSIONS.get(role, set())

    def require_permission(self, user_id: str, permission: str) -> None:
        """
        Assert the user has a permission.
        Raises PermissionError with a descriptive message if denied.
        """
        if not self.has_permission(user_id, permission):
            role = self.get_role(user_id)
            raise PermissionError(
                f"User '{user_id}' (role={role.value}) "
                f"does not have permission '{permission}'."
            )

    def list_permissions(self, user_id: str) -> Set[str]:
        role = self.get_role(user_id)
        return set(ROLE_PERMISSIONS.get(role, set()))
