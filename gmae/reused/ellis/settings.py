"""Settings model — reused from Ellis's individual GuildQuest assignment.

Stores player/session display settings.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from gmae.enums import ThemeType, VisibilityType
from gmae.reused.ghalib.realm import Realm


@dataclass
class Settings:
    theme: ThemeType = ThemeType.CLASSIC
    time_display: str = "24h"
    visibility: VisibilityType = VisibilityType.PUBLIC
    current_realm: Optional[Realm] = None

    def __str__(self) -> str:
        realm_name = self.current_realm.name if self.current_realm else "None"
        return f"Theme: {self.theme.value}, Time: {self.time_display}, Realm: {realm_name}"
