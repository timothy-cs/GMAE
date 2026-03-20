"""LocalTime model — reused from Ellis's individual GuildQuest assignment.

Handles realm-local time offsets and day-length multipliers.
"""

from __future__ import annotations
from dataclasses import dataclass
from gmae.reused.ellis.world_time import WorldTime


@dataclass
class LocalTime:
    days: int = 0
    hours: int = 0
    minutes: int = 0

    def __str__(self) -> str:
        return f"Day {self.days}, {self.hours:02d}:{self.minutes:02d} (local)"


@dataclass
class LocalTimeRule:
    offset_minutes: int = 0
    day_length_multiplier: float = 1.0

    def to_local(self, world_time: WorldTime) -> LocalTime:
        total = world_time.to_total_minutes()
        adjusted = int(total * self.day_length_multiplier) + self.offset_minutes
        if adjusted < 0:
            adjusted = 0
        days = adjusted // 1440
        remaining = adjusted % 1440
        hours = remaining // 60
        minutes = remaining % 60
        return LocalTime(days, hours, minutes)
