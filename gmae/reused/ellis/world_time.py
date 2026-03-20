"""WorldTime model — reused from Ellis's individual GuildQuest assignment.

Represents time in the GuildQuest world using days, hours, and minutes.
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class WorldTime:
    days: int = 0
    hours: int = 0
    minutes: int = 0

    def to_total_minutes(self) -> int:
        return self.days * 1440 + self.hours * 60 + self.minutes

    @staticmethod
    def from_total_minutes(total: int) -> WorldTime:
        days = total // 1440
        remaining = total % 1440
        hours = remaining // 60
        minutes = remaining % 60
        return WorldTime(days, hours, minutes)

    def __str__(self) -> str:
        return f"Day {self.days}, {self.hours:02d}:{self.minutes:02d}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WorldTime):
            return NotImplemented
        return self.to_total_minutes() == other.to_total_minutes()

    def __lt__(self, other: WorldTime) -> bool:
        return self.to_total_minutes() < other.to_total_minutes()

    def __le__(self, other: WorldTime) -> bool:
        return self.to_total_minutes() <= other.to_total_minutes()
