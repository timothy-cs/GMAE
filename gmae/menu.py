"""MiniAdventureMenu — GMAE Core.

Displays available mini-adventures and allows players to select one.
"""

from __future__ import annotations
from typing import List, Optional
from gmae.interfaces import IMiniAdventure


class MiniAdventureMenu:
    def __init__(self) -> None:
        self._adventures: List[IMiniAdventure] = []

    def register(self, adventure: IMiniAdventure) -> None:
        self._adventures.append(adventure)

    @property
    def adventures(self) -> List[IMiniAdventure]:
        return list(self._adventures)

    def display(self) -> str:
        lines = ["\n===== MINI-ADVENTURE MENU =====\n"]
        if not self._adventures:
            lines.append("  No adventures available.")
        for i, adv in enumerate(self._adventures, start=1):
            lines.append(f"  [{i}] {adv.name} ({adv.mode})")
            lines.append(f"      {adv.description}\n")
        lines.append("===============================")
        return "\n".join(lines)

    def select(self, index: int) -> Optional[IMiniAdventure]:
        if 1 <= index <= len(self._adventures):
            return self._adventures[index - 1]
        return None

    def count(self) -> int:
        return len(self._adventures)
